from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Callable, Awaitable
import asyncio
from logging import Logger
from src.libs.utils.limited_size_default_dict import LimitedSizeDefaultDict

JST = timezone(timedelta(hours=9))


class CandleGenerator:
    def __init__(
        self,
        logger: Logger,
        freq: int,
        on_candle_close: Callable[[Dict[str, Any]], Awaitable[None]],
        max_candles: int = 100
    ):
        self._logger = logger
        self._freq = freq
        self._candles: Dict[datetime, Dict[str, Any]] = LimitedSizeDefaultDict(
            lambda: {
                "timestamp": None,
                "open": None,
                "high": float('-inf'),
                "low": float('inf'),
                "close": None,
                "volume": 0.0,
                "buy_volume": 0.0,
                "sell_volume": 0.0,
                "count": 0,
                "buy_count": 0,
                "sell_count": 0,
                "value": 0.0,
                "buy_value": 0.0,
                "sell_value": 0.0,
            },
            max_candles
        )
        self._on_candle_close = on_candle_close
        self._current_key = None
        self._last_key = None
        self._delay_seconds = 0.0

    async def start(self, trade):
        while True:
            messages = []
            try:
                messages = trade.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.001)  # CPUを使い果たさないように少し待つ
                pass

            # 約定履歴を受信した場合、ローソク足へ反映
            if messages:
                self._update_candle(messages)

            # ローソク足の確定時刻を迎えた場合、ローソク足を確定
            if self._current_key and self._is_reached_time_at_finalize():
                self._finalize_candle()

    def _get_candle_key(self, timestamp: datetime) -> datetime:
        return timestamp.replace(second=0, microsecond=0) + timedelta(
            seconds=(timestamp.second // self._freq) * self._freq
        )

    def _update_candle(self, trades: List[Dict[str, Any]]) -> None:
        for trade in trades:
            timestamp_dt = datetime.fromtimestamp(
                trade['timestamp'] / 1000.0, timezone.utc
            )

            key = self._get_candle_key(timestamp_dt)

            local_receipt_time = datetime.now(timezone.utc)
            delay = (local_receipt_time - timestamp_dt).total_seconds()
            self._delay_seconds = max(self._delay_seconds, delay)

            if self._current_key is None:
                self._current_key = key
            elif self._current_key > key:
                self._logger.warn(
                    f"確定済みローソク足の約定を受信: delay - {delay}"
                )

            candle = self._candles[key]

            if candle['timestamp'] is None:
                candle['timestamp'] = key.astimezone(JST).isoformat()
                candle['open'] = trade['price']

            candle['high'] = max(candle['high'], trade['price'])
            candle['low'] = min(candle['low'], trade['price'])
            candle['close'] = trade['price']

            candle['volume'] += trade['size']
            candle['count'] += 1
            candle['value'] += trade['price'] * trade['size']

            side_upper = trade['side'].upper()
            if side_upper == 'BUY':
                candle['buy_volume'] += trade['size']
                candle['buy_count'] += 1
                candle['buy_value'] += trade['price'] * trade['size']
            elif side_upper == 'SELL':
                candle['sell_volume'] += trade['size']
                candle['sell_count'] += 1
                candle['sell_value'] += trade['price'] * trade['size']

    def _is_reached_time_at_finalize(self) -> bool:
        if self._current_key is None:
            return False

        finalize_time = (
            self._current_key
            + timedelta(seconds=self._freq)
            + timedelta(seconds=self._delay_seconds)
            + timedelta(milliseconds=10)  # バッファ
        )
        return datetime.now(timezone.utc) >= finalize_time

    def _finalize_candle(self) -> None:
        if self._current_key is None:
            return

        current_candle = self._candles[self._current_key]
        if current_candle['timestamp'] is None:
            current_candle['timestamp'] = (
                self._current_key.astimezone(JST).isoformat()
            )

            if self._last_key:
                last_close = self._candles[self._last_key]['close']
                current_candle['open'] = last_close
                current_candle['high'] = last_close
                current_candle['low'] = last_close
                current_candle['close'] = last_close

        # 非同期でコールバック
        asyncio.create_task(
            self._on_candle_close(current_candle)
        )

        self._last_key = self._current_key
        self._current_key += timedelta(seconds=self._freq)
