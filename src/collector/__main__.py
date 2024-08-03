from __future__ import annotations

import asyncio
from argparse import ArgumentParser, Namespace

from pybotters import WebSocketQueue

from src.libs.aws.kinesis import Kinesis
from src.libs.exchange import load_exchange
from src.libs.utils import Candle, HealthCheck, LogManager, trace


@trace
async def main(args: Namespace) -> None:
    """
    メイン関数

    Args:
        args: コマンドライン引数
    """
    stream_name = "cryptra-collector"
    tags = {
        "exchange": args.exchange.lower(),
        "contract": args.contract.lower(),
        "symbol": args.symbol.lower(),
    }

    trade_queue = WebSocketQueue()
    candlestick_queue = WebSocketQueue()

    exchange = load_exchange(args, trade_queue)
    candle = Candle(trade_queue, candlestick_queue, args.frequency)
    kinesis = Kinesis(candlestick_queue)
    health_check = HealthCheck()

    tasks = [
        exchange.subscribe(),
        candle.generate(),
        kinesis.publish(stream_name, tags),
        health_check.start(),
    ]

    await asyncio.gather(*(asyncio.create_task(task) for task in tasks))


if __name__ == "__main__":
    try:
        parser = ArgumentParser()
        parser.add_argument("exchange", type=str)
        parser.add_argument("contract", type=str)
        parser.add_argument("symbol", type=str)
        parser.add_argument("--frequency", type=int, default=1)
        parser.add_argument(
            "--log_level",
            type=str,
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        args: Namespace = parser.parse_args()
        log_manager = LogManager(args.log_level.upper())
        logger = log_manager.get_logger(__name__)

        logger.info(f"Starting with args: {args}")
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected, exiting.")
    except Exception:
        logger.error("Exception occurred", exc_info=True)
