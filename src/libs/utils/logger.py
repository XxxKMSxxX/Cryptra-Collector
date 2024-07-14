import logging
import logging.config
from typing import Any, Optional


class LoggerManager:
    DEFAULT_LOG_LEVEL = logging.INFO
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, level: int = DEFAULT_LOG_LEVEL) -> None:
        """LoggerManagerクラスの初期化

        Args:
            level (int): ログのレベル（デフォルトはDEFAULT_LOG_LEVEL）
        """
        self.level = level
        self.setup_logging()

    def setup_logging(self) -> None:
        """ロギングの設定を行う"""
        logging.basicConfig(
            level=self.level,
            format=(
                '%(asctime)s '
                '%(levelname)s '
                '[%(threadName)s] '
                '%(module)s.%(funcName)s: '
                '%(message)s'
            )
        )

    def get_logger(self, name: str = '') -> logging.Logger:
        """指定した名前のロガーを取得する

        Args:
            name (str): ロガーの名前（デフォルトは空文字列）

        Returns:
            logging.Logger: 指定した名前のロガー
        """
        return logging.getLogger(name)

    def debug(self, message: Any, exc_info: Optional[bool] = False) -> None:
        """DEBUGレベルのログメッセージを記録する

        Args:
            message (Any): ログメッセージ
            exc_info (Optional[bool]): 例外情報を含めるかどうか
        """
        logging.debug(message, exc_info=exc_info)

    def info(self, message: Any, exc_info: Optional[bool] = False) -> None:
        """INFOレベルのログメッセージを記録する

        Args:
            message (Any): ログメッセージ
            exc_info (Optional[bool]): 例外情報を含めるかどうか
        """
        logging.info(message, exc_info=exc_info)

    def warning(self, message: Any, exc_info: Optional[bool] = False) -> None:
        """WARNINGレベルのログメッセージを記録する

        Args:
            message (Any): ログメッセージ
            exc_info (Optional[bool]): 例外情報を含めるかどうか
        """
        logging.warning(message, exc_info=exc_info)

    def error(self, message: Any, exc_info: Optional[bool] = False) -> None:
        """ERRORレベルのログメッセージを記録する

        Args:
            message (Any): ログメッセージ
            exc_info (Optional[bool]): 例外情報を含めるかどうか
        """
        logging.error(message, exc_info=exc_info)

    def critical(self, message: Any, exc_info: Optional[bool] = False) -> None:
        """CRITICALレベルのログメッセージを記録する

        Args:
            message (Any): ログメッセージ
            exc_info (Optional[bool]): 例外情報を含めるかどうか
        """
        logging.critical(message, exc_info=exc_info)
