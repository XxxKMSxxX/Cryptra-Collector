import pytest
import pandas as pd
from datetime import datetime, timedelta, timezone
from src.libs.utils.candle import Candle


def test_candle_creation():
    # サンプルデータを生成
    now = datetime.now(timezone.utc)
    timestamps = [now + timedelta(seconds=i) for i in range(20)]
    sample_data = [
        (timestamps[0].timestamp(), 'BUY', 100.0, 1.0),
        (timestamps[1].timestamp(), 'SELL', 101.0, 2.0),
        (timestamps[2].timestamp(), 'BUY', 102.0, 1.5),
        (timestamps[3].timestamp(), 'SELL', 103.0, 2.5),
        (timestamps[4].timestamp(), 'BUY', 104.0, 3.0),
        (timestamps[5].timestamp(), 'SELL', 105.0, 1.0),
        (timestamps[6].timestamp(), 'BUY', 106.0, 2.0),
        (timestamps[7].timestamp(), 'SELL', 107.0, 1.0),
        (timestamps[8].timestamp(), 'BUY', 108.0, 2.5),
        (timestamps[9].timestamp(), 'SELL', 109.0, 3.0),
        (timestamps[10].timestamp(), 'BUY', 110.0, 1.0),
        (timestamps[11].timestamp(), 'SELL', 111.0, 2.0),
        (timestamps[12].timestamp(), 'BUY', 112.0, 1.5),
        (timestamps[13].timestamp(), 'SELL', 113.0, 2.5),
        (timestamps[14].timestamp(), 'BUY', 114.0, 3.0),
        (timestamps[15].timestamp(), 'SELL', 115.0, 1.0),
        (timestamps[16].timestamp(), 'BUY', 116.0, 2.0),
        (timestamps[17].timestamp(), 'SELL', 117.0, 1.0),
        (timestamps[18].timestamp(), 'BUY', 118.0, 2.5),
        (timestamps[19].timestamp(), 'SELL', 119.0, 3.0)
    ]

    # データフレームに変換
    df = pd.DataFrame(sample_data, columns=['timestamp', 'side', 'price', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)

    # 1秒ごとにリサンプリング
    resampled = df.resample('1s').agg({
        'price': ['first', 'max', 'min', 'last'],
        'volume': 'sum'
    })
    resampled.columns = ['open', 'high', 'low', 'close', 'volume']

    # Candleクラスのインスタンスを作成
    interval_sec = 1  # 1秒ごとにローソク足を確定
    results = []

    def on_candle_close(candle):
        results.append(candle)

    candle_maker = Candle(interval_sec, on_candle_close)

    # サンプルデータを処理
    for timestamp, side, price, volume in sample_data:
        candle_maker.process_execution(timestamp, side, price, volume)

    # 確定したローソク足を取得
    candles_df = pd.DataFrame(results).set_index('timestamp')
    candles_df_filtered = candles_df[['open', 'high', 'low', 'close', 'volume']]

    # テスト終了時にタイマーを停止
    candle_maker.stop()

    # リサンプリング結果と比較
    pd.testing.assert_frame_equal(resampled, candles_df_filtered)

if __name__ == "__main__":
    pytest.main()
