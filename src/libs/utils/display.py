from src.libs.utils.logger import LogManager

logger = LogManager.get_logger(__name__)


class Display:
    def __init__(self, queue) -> None:
        self._queue = queue

    async def run(self) -> None:
        async for msg in self._queue:
            logger.info(msg)
