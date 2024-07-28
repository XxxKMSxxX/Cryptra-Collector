from src.libs.utils.logger import LogManager


class Display:
    def __init__(self, queue) -> None:
        self._queue = queue
        self._logger = LogManager.get_logger(__name__)

    async def run(self) -> None:
        async for msg in self._queue:
            self._logger.info(msg)
