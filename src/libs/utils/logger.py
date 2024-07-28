import logging
import logging.config
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Type

JST = timezone(timedelta(hours=9))


class JSTFormatter(logging.Formatter):
    """JSTで時間を表示するフォーマッタ"""

    def format_time(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, JST)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            t = dt.strftime(self.default_time_format)
            s = self.default_msec_format % (t, record.msecs)
        return s


class LogManager:
    DEFAULT_LOG_LEVEL = logging.INFO
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    _masked_credentials: Dict[str, Any] = {}

    def __init__(self, level: int = DEFAULT_LOG_LEVEL) -> None:
        self.level = level
        self._setup_logging()

    def _setup_logging(self) -> None:
        """ロギングの設定を行う"""
        handler = logging.StreamHandler()
        handler.setLevel(self.level)
        formatter = JSTFormatter(
            "%(asctime)s %(levelname)s [%(threadName)s] %(module)s.%(funcName)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logging.getLogger().handlers = [handler]
        logging.getLogger().setLevel(self.level)

    @staticmethod
    def get_logger(name: str = "") -> logging.Logger:
        """指定した名前のロガーを取得する

        Args:
            name (str): ロガーの名前（デフォルトは空文字列）

        Returns:
            logging.Logger: 指定した名前のロガー
        """
        return logging.getLogger(name)

    @classmethod
    def add_masked_credentials(cls, credentials: Dict[str, Any]) -> None:
        """既存のクレデンシャル情報に新しい情報を追加する"""
        cls._masked_credentials.update(credentials)

    @classmethod
    def mask_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                key: "***MASKED***" if key in cls._masked_credentials else value
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [cls.mask_data(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(cls.mask_data(item) for item in data)
        return data


def trace(func: Callable) -> Callable:
    logger = logging.getLogger(func.__module__)

    def wrapper(*args, **kwargs):
        masked_args = [LogManager.mask_data(arg) for arg in args]
        masked_kwargs = {k: LogManager.mask_data(v) for k, v in kwargs.items()}
        logger.debug(
            f"Entering: {func.__name__} with args: {masked_args}, kwargs: {masked_kwargs}"
        )
        result = func(*args, **kwargs)
        logger.debug(
            f"Exiting: {func.__name__} with result: {LogManager.mask_data(result)}"
        )
        return result

    return wrapper


def add_logging(cls: Type) -> Type:
    logger = logging.getLogger(cls.__name__)
    cls.logger = logger

    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value):
            setattr(cls, attr_name, trace(attr_value))

    return cls
