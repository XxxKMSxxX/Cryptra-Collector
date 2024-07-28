from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Callable, Deque, Dict


class LimitedSizeDefaultDict(defaultdict):
    """
    固定サイズのdefaultdictクラス

    新しいアイテムが追加されるときに最大サイズを超えた場合、
    最も古いアイテムが自動的に削除されるdefaultdict

    Attributes:
        max_size (int): 保持する最大アイテム数
        _keys (Deque[datetime]): 挿入順のキーを保持するデキュー
    """

    def __init__(self, default_factory: Callable[[], Dict[str, Any]], max_size: int):
        """
        コンストラクタ

        Args:
            default_factory (Callable[[], Dict[str, Any]]): デフォルト値を生成するファクトリ関数
            max_size (int): 保持する最大アイテム数
        """
        super().__init__(default_factory)
        self.max_size = max_size
        self._keys: Deque[datetime] = deque()

    def __setitem__(self, key: datetime, value: Dict[str, Any]):
        """
        アイテムを設定するメソッド

        Args:
            key (datetime): キー
            value (Dict[str, Any]): 値
        """
        if key not in self:
            if len(self._keys) >= self.max_size:
                oldest_key = self._keys.popleft()
                del self[oldest_key]
            self._keys.append(key)
        super().__setitem__(key, value)
