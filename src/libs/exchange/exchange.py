from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import Namespace
from typing import List, Dict, Any
import importlib


class Exchange(ABC):

    def __init__(self, contract: str, symbol: str) -> None:
        self._contract = contract
        self._symbol = symbol

    @property
    @abstractmethod
    def public_ws_url(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def private_ws_url(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def subscribe_message(self) -> Dict[str, Any] | List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def on_message(self, msg: Any) -> List:
        raise NotImplementedError

    @abstractmethod
    def _on_trade(self, msg: Any) -> List:
        raise NotImplementedError

    @abstractmethod
    def _on_ticker(self, msg: Any) -> List:
        raise NotImplementedError

    @abstractmethod
    def _on_orderbook(self, msg: Any) -> List:
        raise NotImplementedError


def load_exchange(args: Namespace) -> Exchange:
    """指定された取引所のモジュールとクラスを動的にロードし、インスタンスを返却

    Args:
        args (Namespace): コマンドライン引数をパースしたNamespaceオブジェクト
        `exchange`,`contract`,`symbol`の属性が必要

    Returns:
        Exchange: 指定された取引所のExchangeクラスのインスタンス

    Raises:
        ValueError: サポートされていない取引所が指定された場合
        ValueError: 指定されたクラスがモジュール内に見つからない場合
        ValueError: その他の予期しないエラーが発生した場合
    """

    try:
        exchange_module = importlib.import_module(
            f"src.libs.exchange.models.{args.exchange.lower()}"
        )
        exchange_class = getattr(
            exchange_module,
            f"{args.exchange.capitalize()}"
        )
        return exchange_class(args.contract, args.symbol)
    except Exception:
        raise
