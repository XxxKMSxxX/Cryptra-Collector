from __future__ import annotations

from aiohttp import ClientWebSocketResponse
from argparse import ArgumentParser, Namespace
from src.libs.aws import Kinesis
from src.libs.exchange import load_exchange
from src.libs.utils import LoggerManager, WSHealthCheck
from typing import Any
import asyncio
import pybotters
import signal

logger_manager = LoggerManager(LoggerManager.INFO)
logger = logger_manager.get_logger(__name__)


async def main(args: Namespace) -> None:
    health_check = WSHealthCheck()
    health_check.run()

    exchange = load_exchange(args)
    kinesis = Kinesis(args.aws_region)
    KINESIS_STREAM_NAME = (
        f"{args.exchange}-{args.contract}-{args.symbol.upper()}"
    )

    def handler(msg: Any, ws: ClientWebSocketResponse) -> None:
        if not health_check.first_message_received:
            health_check.set_first_message_received(True)
        message = exchange.on_message(msg)
        if message:
            asyncio.create_task(
                kinesis.publish(KINESIS_STREAM_NAME, message)
            )
            logger_manager.info(message)

    async with pybotters.Client() as client:
        ws = await client.ws_connect(
            url=exchange.public_ws_url,
            send_json=exchange.subscribe_message,
            hdlr_json=handler,
        )
        await ws.wait()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.default_int_handler)

    try:
        parser = ArgumentParser()
        parser.add_argument('exchange', type=str, help='取引所の名前')
        parser.add_argument('contract', type=str, help='契約の種類')
        parser.add_argument('symbol', type=str, help='取引シンボル')
        parser.add_argument('aws_region', type=str, help='AWSリージョン')
        parser.add_argument('--log_level', type=str, default='INFO', choices=[
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        ], help='ログレベル')
        args: Namespace = parser.parse_args()

        log_level = getattr(LoggerManager, args.log_level)
        logger_manager = LoggerManager(log_level)
        logger = logger_manager.get_logger(__name__)

        logger.info(f"Starting with args: {args}")
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger_manager.warning("KeyboardInterrupt detected, exiting.")
    except Exception:
        logger_manager.error("Exception occurred", exc_info=True)
