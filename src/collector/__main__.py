from __future__ import annotations

from argparse import ArgumentParser, Namespace
from src.libs.aws import Kinesis
from src.libs.exchange import load_exchange
from aiohttp import ClientWebSocketResponse
from typing import Any
import asyncio
import pybotters
import signal
import traceback


async def main(args: Namespace) -> None:

    KINESIS_STREAM_NAME = (
        f"{args.exchange}-{args.contract}-{args.symbol.upper()}"
    )
    exchange = load_exchange(args)
    kinesis = Kinesis(exchange.aws_region)

    def handler(msg: Any, ws: ClientWebSocketResponse) -> None:
        messages = exchange.on_message(msg)
        if messages:
            asyncio.create_task(
                kinesis.publish(KINESIS_STREAM_NAME, messages)
            )

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
        parser.add_argument('exchange', type=str)
        parser.add_argument('contract', type=str)
        parser.add_argument('symbol', type=str)
        args: Namespace = parser.parse_args()
        print(args)
        asyncio.run(main(args))
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
