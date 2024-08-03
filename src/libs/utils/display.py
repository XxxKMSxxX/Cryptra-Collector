from pybotters import WebSocketQueue

from src.libs.utils.health_check import HealthCheck
from src.libs.utils.logger import LogManager


class Display:
    def __init__(self, queue: WebSocketQueue):
        self._queue = queue
        self._logger = LogManager.get_logger(__name__)

    async def run(self) -> None:
        async for msg in self._queue:
            self._logger.info(msg)
            await HealthCheck.set_health_status(True)
