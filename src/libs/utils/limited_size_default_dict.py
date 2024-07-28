from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Callable, Deque, Dict


class LimitedSizeDefaultDict(defaultdict):
    def __init__(self, default_factory: Callable[[], Dict[str, Any]], max_size: int):
        super().__init__(default_factory)
        self.max_size = max_size
        self._keys: Deque[datetime] = deque()

    def __setitem__(self, key: datetime, value: Dict[str, Any]):
        if key not in self:
            if len(self._keys) >= self.max_size:
                oldest_key = self._keys.popleft()
                del self[oldest_key]
            self._keys.append(key)
        super().__setitem__(key, value)
