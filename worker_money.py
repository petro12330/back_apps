import asyncio
import json
import logging
import time
from datetime import datetime
from decimal import Decimal
from random import random
from typing import Dict, List, Tuple
from uuid import uuid4

import psycopg2
import uvicorn
import websockets
from decouple import config
from websockets.legacy.client import WebSocketClientProtocol


logger = logging.getLogger(__name__)
logging.basicConfig(level=config("LOGGING_LVL"))

DATABASE_CONFIG = {
    "database": config("NAME_DATABASE"),
    "user": config("USER_DATABASE"),
    "password": config("PASSWORD_DATABASE"),
    "host": config("HOST_DATABASE"),
    "port": config("PORT_DATABASE"),
}


def await_time(time_to_sleep=1):
    def _await_second(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            await func(*args, **kwargs)
            time.sleep(time_to_sleep - (time.time() - start_time))

        return wrapper

    return _await_second


def generate_movement() -> int:
    movement = -1 if random() < 0.5 else 1
    return movement


def get_data(cursor) -> List:
    logger.info(f"Try get initial data")
    cursor.execute(
        "SELECT created_at, id, name, last_price, updated_at FROM company_company;"
    )
    return cursor.fetchall()


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def create_data(cursor) -> None:
    logger.info(f"Try create initial data")
    values = ",".join(
        [
            f"('{datetime.now()}'::timestamptz, '{uuid4()}'::uuid, '{uuid4()}', '0', '{datetime.now()}'::timestamptz)"
            for i in range(100)
        ]
    )
    cursor.execute(
        f"INSERT INTO company_company (created_at, id, name, last_price, updated_at) VALUES {values}"
    )


def get_or_create_data() -> List[Tuple]:
    logger.info(f"Try connect to database with config {DATABASE_CONFIG}")
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    data = get_data(cursor)
    if not data:
        create_data(cursor)
        conn.commit()
        data = get_data(cursor)
    conn.commit()
    conn.close()
    return data


async def get_payload_data(data) -> Dict:
    logger.debug(f"Preparing payload_data")
    payload_data = {}
    for i, price in enumerate(data, 0):
        if isinstance(price, Tuple):
            data[i] = list(price)
        _, company_id, name, last_price, _ = price
        change_value = generate_movement()
        new_price = int(last_price) + change_value
        payload_data[company_id] = new_price
        data[i][-2] = new_price
    return payload_data


async def apps(scope, receive, send):
    time.sleep(5)
    data = get_or_create_data()
    try:
        url = f"ws://{config('BACK_HOST')}:{config('BACK_PORT')}/ws/company/"
        async with websockets.connect(url) as websocket:
            logger.info(f"Connect websocket {url}")
            while True:
                try:
                    await core(data, websocket)
                except Exception as e:
                    logger.error(f"Error send data. Error: {e}")
                    break
    except Exception as e:
        logger.error(f"Error connect. Error: {e}")


@await_time(config("AWAIT_PRICE_UPDATE", 1, cast=int))
async def core(data, websocket):
    payload_data = await get_payload_data(data)
    await send_data(payload_data, websocket)


async def send_data(payload_data: Dict, websocket: WebSocketClientProtocol):
    payload = {
        "action": "update_prices",
        "request_id": time.time(),
        "data": payload_data,
    }
    payload = json.dumps(payload, cls=DecimalEncoder)
    logger.debug(f"Send new prices")
    await websocket.send(payload)


async def main():
    config = uvicorn.Config("worker_money:apps", port=5000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
