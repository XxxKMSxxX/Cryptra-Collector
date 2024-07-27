from datetime import datetime, timezone
from pybotters import WebSocketQueue
from src.libs.utils.candle_generator import CandleGenerator
import asyncio
import pandas as pd
import pytest
import random


@pytest.fixture
def candle_generator():
    """CandleGeneratorのフィクスチャ"""
    async def callback(candle):
        print(candle)
    return CandleGenerator(freq=1, on_candle_close=callback)


def resample_candle(dummy_executions, freq):
    """ダミートレードデータを指定された頻度でローソク足にリサンプリングする

    Args:
        dummy_executions (list): ダミートレードデータのリスト
        freq (int): リサンプリングの頻度（秒単位）

    Returns:
        pd.DataFrame: リサンプリングされたローソク足データ
    """
    df = pd.DataFrame(dummy_executions)
    df['timestamp'] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df = df.set_index("timestamp").sort_index()
    df["value"] = df["price"] * df["size"]

    df_resampled = pd.concat([
        df["price"].resample(f'{freq}s').first(),
        df["price"].resample(f'{freq}s').max(),
        df["price"].resample(f'{freq}s').min(),
        df["price"].resample(f'{freq}s').last(),
        df["size"].resample(f'{freq}s').sum(),
        df["size"][df["side"] == "BUY"].resample(f'{freq}s').sum(),
        df["size"][df["side"] == "SELL"].resample(f'{freq}s').sum(),
        df["price"].resample(f'{freq}s').count(),
        df["price"][df["side"] == "BUY"].resample(f'{freq}s').count(),
        df["price"][df["side"] == "SELL"].resample(f'{freq}s').count(),
        df["value"].resample(f'{freq}s').sum(),
        df["value"][df["side"] == "BUY"].resample(f'{freq}s').sum(),
        df["value"][df["side"] == "SELL"].resample(f'{freq}s').sum(),
    ], axis=1)

    df_resampled.columns = [
        "open", "high", "low", "close",
        "volume", "buy_volume", "sell_volume",
        "count", "buy_count", "sell_count",
        "value", "buy_value", "sell_value"
    ]

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

    df_resampled = df_resampled.astype({
        'count': 'int64',
        'buy_count': 'int64',
        'sell_count': 'int64'
    })

    return df_resampled


@pytest.mark.asyncio
async def test_candle_generator_with_random_data(candle_generator):
    """ランダムデータを用いたCandleGeneratorのテスト"""
    freq = 1
    trade = WebSocketQueue()
    dummy_executions = []

    # CandleGeneratorの開始
    asyncio.create_task(candle_generator.start(trade))

    # ダミートレードデータの生成
    for _ in range(random.randint(50, 100)):
        messages = []

        for _ in range(random.randint(1, 3)):
            trade_data = {
                'timestamp': datetime.now(timezone.utc).timestamp(),
                'side': random.choice(['BUY', 'SELL']),
                'price': random.uniform(100.0, 120.0),
                'size': random.uniform(1.0, 10.0)
            }
            messages.append(trade_data)
            dummy_executions.append(trade_data)

        # 約定から受信までの遅延
        await asyncio.sleep(random.uniform(0, 0.2))
        trade.put_nowait(messages)

        # 次の約定が発生するまでの時間
        await asyncio.sleep(random.uniform(0, 3))

    # リサンプリングされたデータフレームの生成
    df_true = resample_candle(dummy_executions, freq)
    print(df_true)

    # CandleGeneratorの結果をデータフレームに変換
    results = candle_generator._candles
    df_test = pd.DataFrame.from_dict(results)
    df_test.columns = [
        'timestamp', 'open', 'high', 'low', 'close',
        'volume', 'buy_volume', 'sell_volume',
        'count', 'buy_count', 'sell_count',
        'value', 'buy_value', 'sell_value'
    ]
    df_test = df_test.set_index('timestamp').sort_index()
    print(df_test)

    # データフレームの比較
    pd.testing.assert_frame_equal(df_true, df_test)


if __name__ == "__main__":
    asyncio.run(test_candle_generator_with_random_data(candle_generator()))
