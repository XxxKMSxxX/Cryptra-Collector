from __future__ import annotations

from ..exchange import Exchange
from typing import List, Dict, Any


class Bitflyer(Exchange):

    def __init__(self, contract: str, symbol: str) -> None:
        super().__init__(contract, symbol)
        self._ticker: Dict = {}

    @property
    def public_ws_url(self) -> str:
        return "wss://ws.lightstream.bitflyer.com/json-rpc"

    @property
    def private_ws_url(self) -> str:
        # TODO: urlを調べて実装
        return ""

    @property
    def subscribe_message(self) -> List[Dict[str, Any]]:
        symbol_upper = self._symbol.upper()
        channels = [
            "lightning_executions",
            # "lightning_ticker",
            # "lightning_board_snapshot",
            # "lightning_board"
        ]
        return [
            {
                "method": "subscribe",
                "params": {"channel": f"{channel}_{symbol_upper}"},
                "id": idx + 1,
            }
            for idx, channel in enumerate(channels)
        ]

    def on_message(self, msg: Any) -> Dict[str, Any]:
        if 'params' in msg:
            topic: str = msg['params']['channel']
            message: str = msg['params']['message']
            if topic.startswith('lightning_executions'):
                return self.handle_message_with_hash(
                    self._on_trade(message)
                )
            elif topic.startswith('lightning_ticker'):
                return self.handle_message_with_hash(
                    self._on_ticker(message)
                )
            elif topic.startswith('lightning_board_snapshot'):
                return self.handle_message_with_hash(
                    self._on_orderbook_snapshot(message)
                )
            elif topic.startswith('lightning_board'):
                return self.handle_message_with_hash(
                    self._on_orderbook(message)
                )
        return {}

    def _on_trade(self, msg: Any) -> List:
        return msg

    def _on_ticker(self, msg: Any) -> List:
        return [msg]

    def _on_orderbook_snapshot(self, msg: Any) -> List[Dict[str, Any]]:
        # TODO: Orderbook(snapshot)メッセージの処理を実装
        return []

    def _on_orderbook(self, msg: Any) -> List[Dict[str, Any]]:
        # TODO: Orderbookメッセージの処理を実装
        return []
