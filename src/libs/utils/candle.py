from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from pybotters import WebSocketQueue

from src.libs.utils.limited_size_default_dict import LimitedSizeDefaultDict
from src.libs.utils.logger import LogManager, add_logging

JST = timezone(timedelta(hours=9))

@add_logging
class Candle:
    """
    ローソク足生成クラス

    Attributes:
        queue_in (WebSocketQueue): 入力となるWebSocketキュー
        queue_out (WebSocketQueue): 出力となるWebSocketキュー
        _freq (int): ローソク足の頻度（秒単位）
        _candles (Dict[datetime, Dict[str, Any]]): ローソク足データを格納する辞書
        _last_key (datetime): 最後に更新されたローソク足のキー
    """

    def __init__(
        self,
        queue_in: WebSocketQueue,
        queue_out: WebSocketQueue,
        freq: int = 1,
        max_candles: int = 100,
    ):
        """
        コンストラクタ

        Args:
            queue_in (WebSocketQueue): 入力となるWebSocketキュー
            queue_out (WebSocketQueue): 出力となるWebSocketキュー
            freq (int, optional): ローソク足の頻度（秒単位）。デフォルトは1
            max_candles (int, optional): 保持するローソク足の最大数。デフォルトは100
        """
        self._logger = LogManager.get_logger(__name__)

        self.queue_in = queue_in
        self.queue_out = queue_out
        self._freq = freq
        self._candles: Dict[datetime, Dict[str, Any]] = LimitedSizeDefaultDict(
            lambda: {
                "timestamp": None,
                "open": None,
                "high": float("-inf"),
                "low": float("inf"),
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
            max_candles,
        )
        self._last_key = None

    async def generate(self):
        """
        ローソク足生成を行う非同期メソッド

        WebSocketQueueからデータを受信し、ローソク足データを更新する
        """
        async for messages in self.queue_in:
            self._update_candle(messages)

    def _get_candle_key(self, timestamp: datetime) -> datetime:
        """
        ローソク足のキーを取得する

        Args:
            timestamp (datetime): タイムスタンプ

        Returns:
            datetime: ローソク足のキー
        """
        return timestamp.replace(second=0, microsecond=0) + timedelta(
            seconds=(timestamp.second // self._freq) * self._freq
        )

    def _update_candle(self, trades: List[Dict[str, Any]]) -> None:
        """
        ローソク足データを更新する

        Args:
            trades (List[Dict[str, Any]]): 取引データのリスト
        """
        for trade in trades:
            key = self._get_candle_key(datetime.fromtimestamp(
                trade["timestamp"] / 1000.0, timezone.utc
            ))

            candle = self._candles[key]

            if candle["open"] is None:
                candle["open"] = trade["price"]

            candle["high"] = max(candle["high"], trade["price"])
            candle["low"] = min(candle["low"], trade["price"])
            candle["close"] = trade["price"]

            candle["volume"] += trade["size"]
            candle["count"] += 1
            candle["value"] += trade["price"] * trade["size"]

            side_upper = trade["side"].upper()
            if side_upper == "BUY":
                candle["buy_volume"] += trade["size"]
                candle["buy_count"] += 1
                candle["buy_value"] += trade["price"] * trade["size"]
            elif side_upper == "SELL":
                candle["sell_volume"] += trade["size"]
                candle["sell_count"] += 1
                candle["sell_value"] += trade["price"] * trade["size"]

            if self._last_key is None:
                self._last_key = key
            elif key > self._last_key:
                self._finalize_candle()
                self._last_key = key
            elif key < self._last_key:
                self._logger.warn(
                    f"Received data for {key.astimezone(JST).isoformat()} is already finalized"
                )

    def _finalize_candle(self) -> None:
        """
        ローソク足を確定し、出力キューに送信する
        """
        if len(self._candles) > 1:
            current_candle = self._candles[self._last_key]
            if current_candle["timestamp"] is None:
                current_candle["timestamp"] = self._last_key.astimezone(JST).isoformat()
            self.queue_out.put_nowait(current_candle)
