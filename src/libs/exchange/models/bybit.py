from __future__ import annotations

from ..exchange import Exchange
from typing import List, Dict, Any


class Bybit(Exchange):

    def __init__(self, contract: str, symbol: str) -> None:
        super().__init__(contract, symbol)
        self._ticker: Dict = {}

    @property
    def aws_region(self) -> str:
        return 'ap-southeast-1'

    @property
    def public_ws_url(self) -> str:
        return f"wss://stream.bybit.com/v5/public/{self._contract}"

    @property
    def private_ws_url(self) -> str:
        return "wss://stream.bybit.com/v5/private"

    @property
    def subscribe_message(self) -> Dict[str, Any] | List[Dict[str, Any]]:
        symbol_upper = self._symbol.upper()
        return {
            "op": "subscribe",
            "args": [
                f"publicTrade.{symbol_upper}",
                # f"tickers.{symbol_upper}",
                # f"orderbook.50.{symbol_upper}",
                # f"liquidation.{symbol_upper}",
            ]
        }

    def on_message(self, msg: Any) -> List:
        """WebSocket Stream > Public
        - https://bybit-exchange.github.io/docs/v5/websocket/public/trade
        - https://bybit-exchange.github.io/docs/v5/websocket/public/ticker
        - https://bybit-exchange.github.io/docs/v5/websocket/public/liquidation
        """
        if 'topic' in msg:
            topic: str = msg['topic']
            if topic.startswith('publicTrade'):
                return self._on_trade(msg)
            elif topic.startswith('tickers'):
                return self._on_ticker(msg)
        return []

    def _on_trade(self, msg: Any) -> List:
        return msg['data']

    def _on_ticker(self, msg: Any) -> List:
        type: str = msg['type']
        if type == "delta":
            self._ticker.update(msg['data'])
        elif type == "snapshot":
            self._ticker = msg['data']
        return [self._ticker]

    def _on_orderbook(self, msg: Any):
        pass
