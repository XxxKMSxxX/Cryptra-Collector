from __future__ import annotations

from ..exchange import Exchange
from datetime import datetime
from pybotters.ws import ClientWebSocketResponse
from typing import List, Dict, Any


class Bitflyer(Exchange):

    def __init__(self, contract: str, symbol: str) -> None:
        super().__init__(contract, symbol)

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

    def on_message(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if 'params' in msg:
            topic: str = msg['params']['channel']
            message: str = msg['params']['message']
            if topic.startswith('lightning_executions'):
                self.trade.put_nowait(self._on_trade(message))
            elif topic.startswith('lightning_ticker'):
                pass
            elif topic.startswith('lightning_board_snapshot'):
                pass
            elif topic.startswith('lightning_board'):
                pass

    def _on_trade(self, msg: Any) -> List:
        """
        [
            {
                'id': 2536423851,
                'side': 'SELL',
                'price': 10219989.0,
                'size': 0.01,
                'exec_date': '2024-07-19T13:42:21.8333232Z',
                'buy_child_order_acceptance_id': 'JRF20240719-134221-027595',
                'sell_child_order_acceptance_id': 'JRF20240719-134221-021437'
            }, {
                'id': 2536423852,
                'side': 'SELL',
                'price': 10219988.0,
                'size': 0.0351,
                'exec_date': '2024-07-19T13:42:21.8333232Z',
                'buy_child_order_acceptance_id': 'JRF20240719-134107-006998',
                'sell_child_order_acceptance_id': 'JRF20240719-134221-021437'
            }, {
                'id': 2536423853,
                'side': 'SELL',
                'price': 10219988.0,
                'size': 0.11957032,
                'exec_date': '2024-07-19T13:42:21.8333232Z',
                'buy_child_order_acceptance_id': 'JRF20240719-134107-006998',
                'sell_child_order_acceptance_id': 'JRF20240719-134221-021438'
            }
        ]
        """
        trades = []
        for trade in msg:
            exec_date = trade['exec_date']
            exec_date = exec_date.rstrip('Z')
            if '.' in exec_date:
                exec_date, microseconds = exec_date.split('.')
                microseconds = microseconds[:6].ljust(6, '0')
                exec_date = f"{exec_date}.{microseconds}"
            else:
                exec_date = f"{exec_date}.000000"
            dt = datetime.strptime(exec_date, '%Y-%m-%dT%H:%M:%S.%f')
            unix_time_ms = int(dt.timestamp() * 1000)
            trades.append({
                'timestamp': unix_time_ms,
                'side': trade['side'],
                'price': float(trade['price']),
                'size': float(trade['size'])
            })
        return trades

    def _on_ticker(self, msg: Any) -> List:
        # TODO: tickeメッセージの処理を実装
        return []

    def _on_orderbook_snapshot(self, msg: Any) -> List:
        # TODO: Orderbook(snapshot)メッセージの処理を実装
        return []

    def _on_orderbook(self, msg: Any) -> List:
        # TODO: Orderbookメッセージの処理を実装
        return []
