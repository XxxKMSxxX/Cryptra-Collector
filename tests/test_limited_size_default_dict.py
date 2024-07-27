import pytest
from src.libs.utils.limited_size_default_dict import LimitedSizeDefaultDict
from datetime import datetime
from typing import Dict, Any


@pytest.fixture
def limited_size_default_dict() -> LimitedSizeDefaultDict:
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
    return LimitedSizeDefaultDict(factory, max_size)


def test_add_items_within_limit(limited_size_default_dict):
    for i in range(5):
        key = datetime(2024, 7, 20, 12, 0, i)
        limited_size_default_dict[key] = limited_size_default_dict.default_factory()
    assert len(limited_size_default_dict) == 5


def test_add_items_exceeding_limit(limited_size_default_dict):
    for i in range(10):
        key = datetime(2024, 7, 20, 12, 0, i)
        limited_size_default_dict[key] = limited_size_default_dict.default_factory()
    assert len(limited_size_default_dict) == 5
    assert datetime(2024, 7, 20, 12, 0, 0) not in limited_size_default_dict
    assert datetime(2024, 7, 20, 12, 0, 5) in limited_size_default_dict


def test_key_ordering(limited_size_default_dict):
    for i in range(10):
        key = datetime(2024, 7, 20, 12, 0, i)
        limited_size_default_dict[key] = limited_size_default_dict.default_factory()
    keys = list(limited_size_default_dict.keys())
    expected_keys = [
        datetime(2024, 7, 20, 12, 0, 5),
        datetime(2024, 7, 20, 12, 0, 6),
        datetime(2024, 7, 20, 12, 0, 7),
        datetime(2024, 7, 20, 12, 0, 8),
        datetime(2024, 7, 20, 12, 0, 9),
    ]
    assert keys == expected_keys


if __name__ == "__main__":
    pytest.main()
