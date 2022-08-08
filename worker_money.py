import asyncio
import json
import time
from datetime import datetime
from decimal import Decimal
from random import random
from typing import Tuple
from uuid import uuid4
from decouple import config
import psycopg2
import uvicorn
import websockets


def generate_movement():
    movement = -1 if random() < 0.5 else 1
    return movement


def get_data(cursor):
    cursor.execute("SELECT * FROM company_company;")
    return cursor.fetchall()


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def create_data(cursor):
    values = ",".join(
        [
            f"('{datetime.now()}'::timestamptz, '{uuid4()}'::uuid, '{uuid4()}', '0', '{datetime.now()}'::timestamptz)"
            for i in range(100)
        ]
    )
    cursor.execute(
        f"INSERT INTO company_company (created_at, id, name, last_price, updated_at) VALUES {values}"
    )


def get_or_create_data():

    conn = psycopg2.connect(
        database=config("NAME_DATABASE"),
        user=config("USER_DATABASE"),
        password=config("PASSWORD_DATABASE"),
        host=config("HOST_DATABASE"),
        port=config("PORT_DATABASE"),
    )
    cursor = conn.cursor()
    data = get_data(cursor)
    if not data:
        create_data(cursor)
        conn.commit()
        data = get_data(cursor)
    conn.commit()
    conn.close()
    return data


async def apps(scope, receive, send):
    time.sleep(5)
    data = get_or_create_data()
    try:
        async with websockets.connect(
                f"ws://{config('BACK_HOST')}:{config('BACK_PORT')}/ws/company/"
        ) as websocket:
            while 1:
                try:
                    start_time = time.time()
                    payload = {
                        "action": "update_prices",
                        "request_id": time.time(),
                    }
                    payload_data = {}
                    for i, price in enumerate(data, 0):
                        if isinstance(price, Tuple):
                            data[i] = list(price)
                        _, company_id, name, last_price, _ = price
                        change_value = generate_movement()
                        new_price = last_price + change_value
                        payload_data[company_id] = new_price
                        data[i][-2] = new_price
                    payload["data"] = payload_data
                    payload = json.dumps(payload, cls=DecimalEncoder)
                    print("send_data")
                    await websocket.send(payload)
                    end_time = time.time() - start_time
                    print("send_data")
                    time.sleep(1 - end_time)  # wait and then do it again
                except Exception as e:
                    print(e)
                    time.sleep(5)  # wait and then do it again
    except Exception as e:
        print(e)


async def main():
    config = uvicorn.Config("worker_money:apps", port=5000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    print(-1)
    asyncio.run(main())
