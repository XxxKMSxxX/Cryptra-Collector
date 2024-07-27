from __future__ import annotations

from ..exchange import Exchange
from pybotters.ws import ClientWebSocketResponse
from typing import List, Dict, Any


class Bybit(Exchange):

    def __init__(self, contract: str, symbol: str) -> None:
        super().__init__(contract, symbol)

    @property
    def public_ws_url(self) -> str:
        return f"wss://stream.bybit.com/v5/public/{self._contract}"

    @property
    def private_ws_url(self) -> str:
        return "wss://stream.bybit.com/v5/private"

    @property
    def subscribe_message(self) -> Dict[str, Any]:
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

    def on_message(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        """WebSocket Stream > Public
        - https://bybit-exchange.github.io/docs/v5/websocket/public/trade
        - https://bybit-exchange.github.io/docs/v5/websocket/public/ticker
        - https://bybit-exchange.github.io/docs/v5/websocket/public/liquidation
        """
        if 'topic' in msg:
            topic: str = msg['topic']
            if topic.startswith('publicTrade'):
                self.trade.put_nowait(self._on_trade(msg))
            elif topic.startswith('tickers'):
                pass
            elif topic.startswith('orderbook'):
                pass
            elif topic.startswith('liquidation'):
                pass

    def _on_trade(self, msg: Any) -> List:
        """
        {
            "topic": "publicTrade.BTCUSDT",
            "type": "snapshot",
            "ts": 1672304486868,
            "data": [
                {
                    "T": 1672304486865,
                    "s": "BTCUSDT",
                    "S": "Buy",
                    "v": "0.001",
                    "p": "16578.50",
                    "L": "PlusTick",
                    "i": "20f43950-d8dd-5b31-9112-a178eb6023af",
                    "BT": false
                }
            ]
        }
        """
        trades = []
        for trade in msg['data']:
            trades.append({
                'timestamp': int(trade['T']),
                'side': trade['S'],
                'price': float(trade['p']),
                'size': float(trade['v'])
            })
        return trades

    def _on_ticker(self, msg: Any) -> List:
        # TODO: tickeメッセージの処理を実装
        return []

    def _on_orderbook(self, msg: Any) -> List:
        # TODO: Orderbookメッセージの処理を実装
        return []

    def _on_liquidation(self, msg: Any) -> List:
        # TODO: Liquidationメッセージの処理を実装
        return []
