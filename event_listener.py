import asyncio
import json
from typing import Callable, List, Tuple
import asyncpg
from asyncpg.pool import Pool
from main import Settings


ListenerCallback = Callable[[asyncpg.Connection, str, str, str], None]


class EventProcessor:
    def __init__(self, pool: Pool):
        self.pool = pool
        self.listeners: List[Tuple[asyncpg.Connection, str, ListenerCallback]] = []

    async def add_listener(self, channel: str, callback: ListenerCallback):
        conn = await self.pool.acquire()
        await conn.add_listener(channel, callback)
        self.listeners.append((conn, channel, callback))

    async def disconnect(self):
        while self.listeners:
            conn, channel, callback = self.listeners.pop()
            await conn.remove_listener(channel, callback)
            await self.pool.release(conn)


def callback(_conn: asyncpg.Connection, _pid: str, _channel: str, payload: str):
    # print(conn)
    # print(pid)
    # print(channel)
    print(json.loads(payload))


async def main():
    settings = Settings()
    pool = await asyncpg.create_pool(settings.pg_dsn)
    er = EventProcessor(pool)
    await er.add_listener("test", callback)

    while True:
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            await er.disconnect()
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("shutting down the listener...")
