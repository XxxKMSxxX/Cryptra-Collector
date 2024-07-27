from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, Any, Callable, Deque


class LimitedSizeDefaultDict(defaultdict):
    def __init__(
        self,
        default_factory: Callable[[], Dict[str, Any]],
        max_size: int
    ):
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


if __name__ == "__main__":
    def factory() -> Dict[str, Any]:
        return {
            "open": None,
            "high": float('-inf'),
            "low": float('inf'),
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
        }

    max_size = 5
    limited_dict = LimitedSizeDefaultDict(factory, max_size)

    for i in range(10):
        limited_dict[datetime(2024, 7, 20, 12, 0, i)] = factory()
        print(f"Added: {datetime(2024, 7, 20, 12, 0, i)}")
        print(f"Current keys: {list(limited_dict.keys())}")
