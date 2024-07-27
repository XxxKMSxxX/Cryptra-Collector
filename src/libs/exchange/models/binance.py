from __future__ import annotations

from ..exchange import Exchange
from pybotters.ws import ClientWebSocketResponse
from typing import List, Dict, Any


class Binance(Exchange):

    def __init__(self, contract: str, symbol: str) -> None:
        super().__init__(contract, symbol)

    @property
    def public_ws_url(self) -> str:
        if self._contract == "spot":
            return "wss://stream.binance.com:9443/stream"
        elif self._contract == "usdt_perpetual":
            return "wss://fstream.binance.com/stream"
        return ""

    @property
    def private_ws_url(self) -> str:
        # TODO: urlを調べて実装
        return ""

    @property
    def subscribe_message(self) -> Dict[str, Any]:
        symbol_lower = self._symbol.lower()

        return {
            "method": "SUBSCRIBE",
            "params": [
                f"{symbol_lower}@trade",
                # f"{symbol_lower}@ticker",
                # f"{symbol_lower}@depth",
            ],
            "id": 1
        }

    def on_message(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        """WebSocket API > Market data requests
        - https://binance-docs.github.io/apidocs/websocket_api/en/#recent-trades  # noqa: E501
        - https://binance-docs.github.io/apidocs/websocket_api/en/#24hr-ticker-price-change-statistics  # noqa: E501
        """
        if 'stream' in msg:
            topic: str = msg['stream']
            if topic.endswith('@trade'):
                self.trade.put_nowait(self._on_trade(msg))
            elif topic.endswith('@ticker'):
                pass
            elif topic.endswith('@depth'):
                pass

    def _on_trade(self, msg: Any) -> List:
        """
        {
            'stream': 'btcusdt@trade',
            'data': {
                'e': 'trade',
                'E': 1721554806084,
                's': 'BTCUSDT',
                't': 3694595677,
                'p': '66913.25000000',
                'q': '0.00011000',
                'T': 1721554806083,
                'm': True,
                'M': True
            }
        }
        """
        return [{
            'timestamp': int(msg['data']['T']),
            'side': 'BUY' if msg['data']['m'] else 'SELL',
            'price': float(msg['data']['p']),
            'size': float(msg['data']['p'])
        }]

    def _on_ticker(self, msg: Any) -> List:
        # TODO: tickeメッセージの処理を実装
        return []

    def _on_orderbook(self, msg: Any) -> List[Dict[str, Any]]:
        # TODO: Orderbookメッセージの処理を実装
        return []
