from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Callable
import concurrent.futures
import threading
import numpy as np

JST = timezone(timedelta(hours=9))


class Candle:
    def __init__(
        self,
        interval_sec: int,
        on_candle_close: Callable[[Dict[str, Any]], None]
    ):
        """
        初期化メソッド

        Args:
            interval_sec (int): リサンプリングのインターバル（秒）
            on_candle_close (Callable[[Dict[str, Any]], None]): ローソク足確定時の
            コールバック関数
        """
        self.interval_sec = interval_sec
        self.current_candle = None
        self.candles = []
        self.on_candle_close = on_candle_close
        self.timer = None
        self.network_delay_time = timedelta(0)
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def process_execution(
        self,
        timestamp: float,
        side: str,
        price: float,
        volume: float
    ) -> None:
        """
        受信した約定履歴を処理してローソク足を作成

        Args:
            timestamp (float): 約定履歴のタイムスタンプ（Unix時間）
            side (str): 売買の種類（'BUY' or 'SELL'）
            price (float): 価格
            volume (float): 取引量
        """
        local_time = datetime.now(timezone.utc)
        timestamp_dt = datetime.fromtimestamp(timestamp, timezone.utc)

        # ローソク足の開始時刻を設定
        candle_start_time = timestamp_dt.replace(
            second=(
                (timestamp_dt.second // self.interval_sec) * self.interval_sec
            ),
            microsecond=0
        )

        # ネットワーク遅延時間の計算
        self.network_delay_time = local_time - timestamp_dt

        # 初回受信の場合、ローソク足を新規作成
        if self.current_candle is None:
            self._create_new_candle(candle_start_time, side, price, volume)

        # 現在のローソク足に含めるべき約定履歴の場合、現在ローソク足を更新
        elif self.current_candle['timestamp'] == candle_start_time:
            self._update_candle(side, price, volume)

        # 次のローソク足に含めるべき約定履歴の場合、現在ローソク足を確定 + 次回ローソク足を新規作成
        elif self.current_candle['timestamp'] < candle_start_time:
            self._finalize_current_candle()
            self._create_new_candle(candle_start_time, side, price, volume)

        # 確定済みのローソク足に含めるべき約定履歴の場合、警告を表示（delayの見直しが必要）
        else:
            print(
                f"Warn: 確定済みローソク足の約定履歴を受信 "
                f"Delay: {local_time - self.last_finalize_time}",
                flush=True
            )

    def _create_new_candle(
        self,
        timestamp: datetime,
        side: str,
        price: float,
        volume: float
    ) -> None:
        """
        新しいローソク足を作成

        Args:
            timestamp (datetime): タイムスタンプ
            price (float): 価格
            volume (float): 取引量
            side (str): 売買の種類（'BUY' or 'SELL' or ''）
        """
        self.current_candle = {
            'timestamp': timestamp,
            'open': np.nan if side == '' else price,
            'high': -np.inf if side == '' else price,
            'low': np.inf if side == '' else price,
            'close': np.nan if side == '' else price,
            'volume': volume,
            'buy_volume': volume if side == 'BUY' else 0.0,
            'sell_volume': volume if side == 'SELL' else 0.0,
            'count': 0 if side == '' else 1,
            'buy_count': 1 if side == 'BUY' else 0,
            'sell_count': 1 if side == 'SELL' else 0,
            'value': 0 if side == '' else price * volume,
            'buy_value': price * volume if side == 'BUY' else 0.0,
            'sell_value': price * volume if side == 'SELL' else 0.0,
        }

        close_remaining_sec = (
            timestamp + timedelta(seconds=self.interval_sec) +
            self.network_delay_time + timedelta(milliseconds=100) -
            datetime.now(timezone.utc)
        ).total_seconds()
        self._schedule_candle_finalization(close_remaining_sec)

    def _update_candle(
        self,
        side: str,
        price: float,
        volume: float
    ) -> None:
        """
        現在のローソク足を更新

        Args:
            price (float): 価格
            volume (float): 取引量
            side (str): 売買の種類（'BUY' または 'SELL'）
        """
        if self.current_candle['open'] is np.nan:
            self.current_candle['open'] = price
        self.current_candle['high'] = max(self.current_candle['high'], price)
        self.current_candle['low'] = min(self.current_candle['low'], price)
        self.current_candle['close'] = price
        self.current_candle['volume'] += volume
        self.current_candle['count'] += 1
        self.current_candle['value'] += price * volume
        if side == 'BUY':
            self.current_candle['buy_volume'] += volume
            self.current_candle['buy_count'] += 1
            self.current_candle['buy_value'] += price * volume
        elif side == 'SELL':
            self.current_candle['sell_volume'] += volume
            self.current_candle['sell_count'] += 1
            self.current_candle['sell_value'] += price * volume

    def _finalize_current_candle(self) -> None:
        """
        現在のローソク足を確定し、リストに追加し、非同期でコールバックを呼び出す
        """

        if self.timer:
            self.timer.cancel()

        # 約定がなかった場合は、直前の終値で補完
        if self.current_candle['open'] is np.nan:
            self.current_candle['open'] = self.last_close
            self.current_candle['high'] = self.last_close
            self.current_candle['low'] = self.last_close
            self.current_candle['close'] = self.last_close
        else:
            self.last_close = self.current_candle['close']

        # 確定ローソク足のリストに追加
        self.candles.append(self.current_candle)

        # コールバック
        self.executor.submit(self.on_candle_close, self.current_candle)

        self.last_finalize_time = datetime.now(timezone.utc)

    def get_candles(self) -> List[Dict[str, Any]]:
        """
        確定したローソク足のリストを取得

        Returns:
            List[Dict[str, Any]]: 確定したローソク足のリスト
        """
        return self.candles

    def _schedule_candle_finalization(
        self,
        close_remaining_sec: float
    ) -> None:
        """
        次のローソク足確定をスケジュール

        Args:
            close_remaining_sec (float): 現在のローソク足が閉じるまでの残り秒数
        """

        if self.timer:
            self.timer.cancel()

        self.timer = threading.Timer(
            close_remaining_sec,
            self._finalize_current_candle
        )
        self.timer.start()

    def stop(self) -> None:
        """
        タイマーを停止
        """
        if self.timer:
            self.timer.cancel()
        self.executor.shutdown(wait=False)


if __name__ == "__main__":
    import pandas as pd
    import random
    import time
    from datetime import datetime, timezone, timedelta

    def callback(candle):
        pass

    interval_sec = 1
    dummy_executions = []
    num_data_points = random.randint(50, 100)
    candle = Candle(interval_sec=interval_sec, on_candle_close=callback)

    for _ in range(num_data_points):
        # 約定履歴のダミーデータ作成
        dummy_execution = {
            'timestamp': datetime.now(timezone.utc).timestamp(),
            'side': random.choice(['BUY', 'SELL']),
            'price': random.uniform(100.0, 120.0),
            'volume': random.uniform(1.0, 10.0)
        }
        dummy_executions.append(dummy_execution)

        # ネットワーク遅延
        time.sleep(random.uniform(0, 200) / 1000)

        # 約定履歴の受信
        candle.process_execution(
            dummy_execution['timestamp'],
            dummy_execution['side'],
            dummy_execution['price'],
            dummy_execution['volume']
        )

        # 次の約定が発生するまでの時間
        time.sleep(random.uniform(0, 5))

    candle.stop()

    def resample_candle(dummy_executions, interval_sec):
        df = pd.DataFrame(dummy_executions)
        print(df)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.sort_values("timestamp")
        df.index = pd.to_datetime(df["timestamp"], unit="s", utc=True)
        df["value"] = df["price"] * df["volume"]

        df_resampled = pd.concat([
            df["price"].resample(f'{interval_sec}s').first(),
            df["price"].resample(f'{interval_sec}s').max(),
            df["price"].resample(f'{interval_sec}s').min(),
            df["price"].resample(f'{interval_sec}s').last(),
            df["volume"].resample(f'{interval_sec}s').sum(),
            df["volume"][df["side"] == "BUY"].resample(f'{interval_sec}s').sum(),
            df["volume"][df["side"] == "SELL"].resample(f'{interval_sec}s').sum(),
            df["price"].resample(f'{interval_sec}s').count(),  # count
            df["price"][df["side"] == "BUY"].resample(f'{interval_sec}s').count(),
            df["price"][df["side"] == "SELL"].resample(f'{interval_sec}s').count(),
            df["value"].resample(f'{interval_sec}s').sum(),  # value
            df["value"][df["side"] == "BUY"].resample(f'{interval_sec}s').sum(),
            df["value"][df["side"] == "SELL"].resample(f'{interval_sec}s').sum(),
        ], axis=1)

        df_resampled.columns = [
            "open", "high", "low", "close",
            "volume", "buy_volume", "sell_volume",
            "count", "buy_count", "sell_count",
            "value", "buy_value", "sell_value"
        ]

        # 欠損値の補完
        df_resampled['close'] = df_resampled['close'].ffill()
        df_resampled['open'] = df_resampled['open'].fillna(df_resampled['close'])
        df_resampled['high'] = df_resampled['high'].fillna(df_resampled['close'])
        df_resampled['low'] = df_resampled['low'].fillna(df_resampled['close'])
        df_resampled['volume'] = df_resampled['volume'].fillna(0)
        df_resampled['buy_volume'] = df_resampled['buy_volume'].fillna(0)
        df_resampled['sell_volume'] = df_resampled['sell_volume'].fillna(0)
        df_resampled['count'] = df_resampled['count'].fillna(0)
        df_resampled['buy_count'] = df_resampled['buy_count'].fillna(0)
        df_resampled['sell_count'] = df_resampled['sell_count'].fillna(0)
        df_resampled['value'] = df_resampled['value'].fillna(0)
        df_resampled['buy_value'] = df_resampled['buy_value'].fillna(0)
        df_resampled['sell_value'] = df_resampled['sell_value'].fillna(0)

        return df_resampled

    # DataFrameに変換
    df_true = resample_candle(dummy_executions, 1).iloc[:-1]
    print(df_true)

    # Candleクラスからの結果を取得
    results = candle.get_candles()
    df_test = pd.DataFrame(results).set_index('timestamp')
    df_test = df_test[[
        "open", "high", "low", "close",
        "volume", "buy_volume", "sell_volume",
        "count", "buy_count", "sell_count",
        "value", "buy_value", "sell_value"
    ]]
    print(df_test)

    pd.testing.assert_frame_equal(df_true, df_test)

    print("テストが正常に完了しました。")
