from __future__ import annotations

from ..exchange import Exchange
from datetime import datetime
from pybotters.ws import ClientWebSocketResponse
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

    def on_message(self, msg: Any, ws: ClientWebSocketResponse) -> None:
        if 'params' in msg:
            topic: str = msg['params']['channel']
            message: str = msg['params']['message']
            if topic.startswith('lightning_executions'):
                self.wsqueue.put_nowait(self._on_trade(message))
            elif topic.startswith('lightning_ticker'):
                self.wsqueue.put_nowait(self._on_ticker(message))
            elif topic.startswith('lightning_board_snapshot'):
                self.wsqueue.put_nowait(self._on_orderbook_snapshot(message))
            elif topic.startswith('lightning_board'):
                self.wsqueue.put_nowait(self._on_orderbook(message))

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
        executions = []
        for execution in msg:
            exec_date = execution['exec_date']
            # 'Z' を削除し、ミリ秒部分を6桁に切り捨てまたはパディング
            exec_date = exec_date.rstrip('Z')
            if '.' in exec_date:
                exec_date, microseconds = exec_date.split('.')
                microseconds = microseconds[:6].ljust(6, '0')  # ミリ秒部分を6桁に調整
                exec_date = f"{exec_date}.{microseconds}Z"
            else:
                exec_date = f"{exec_date}.000000Z"
            dt = datetime.strptime(exec_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            unix_time = dt.timestamp()
            executions.append({
                'timestamp': unix_time,
                'side': execution['side'],
                'price': execution['price'],
                'size': execution['size']
            })
        return executions

    def _on_ticker(self, msg: Any) -> List:
        return [msg]

    def _on_orderbook_snapshot(self, msg: Any) -> List[Dict[str, Any]]:
        # TODO: Orderbook(snapshot)メッセージの処理を実装
        return []

    def _on_orderbook(self, msg: Any) -> List[Dict[str, Any]]:
        # TODO: Orderbookメッセージの処理を実装
        return []
