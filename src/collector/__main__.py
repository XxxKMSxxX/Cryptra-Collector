from __future__ import annotations

from argparse import ArgumentParser, Namespace
from src.libs.exchange import load_exchange
from src.libs.utils import CandleGenerator, LoggerManager
from typing import Any, Dict
import asyncio
import pybotters
import signal

logger_manager = LoggerManager(LoggerManager.INFO)
logger = logger_manager.get_logger(__name__)


async def on_candle_close(candle: Dict[str, Any]) -> None:
    logger.info(candle)


async def main(args: Namespace) -> None:
    """
    メイン関数

    Args:
        args: コマンドライン引数
    """
    exchange = load_exchange(args)
    candle_generator = CandleGenerator(
        logger=logger,
        freq=1,
        on_candle_close=on_candle_close
    )

    async with pybotters.Client() as client:
        ws = await client.ws_connect(
            url=exchange.public_ws_url,
            send_json=exchange.subscribe_message,
            hdlr_json=exchange.on_message,
        )

        await asyncio.gather(
            ws.wait(),
            candle_generator.start(exchange.trade),
        )

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.default_int_handler)

    try:
        parser = ArgumentParser()
        parser.add_argument('exchange', type=str)
        parser.add_argument('contract', type=str)
        parser.add_argument('symbol', type=str)
        parser.add_argument('--log_level', type=str, default='INFO', choices=[
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        ])
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
