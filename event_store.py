import abc
import uuid
from typing import Optional, List
from asyncpg.pool import Pool
from events import Event, EventStream


class ConcurrentStreamWriteError(RuntimeError):
    pass


class EventStore(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def load_stream(self, aggregate_uuid: uuid.UUID) -> EventStream:
        pass

    @abc.abstractmethod
    async def append_to_stream(
        self,
        aggregate_uuid: uuid.UUID,
        expected_version: Optional[int],
        events: List[Event],
    ) -> None:
        pass


class PostgreSQLEventStore(EventStore):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def load_stream(self, aggregate_uuid: uuid.UUID) -> EventStream:
        # query = """
        # SELECT * FROM
        # """
        # conn = await self.pool.acquire()
        # try:
        #     rows = await conn.fetch(query)

        # finally:
        #     self.pool.release(conn)
        pass

    async def append_to_stream(
        self,
        aggregate_uuid: uuid.UUID,
        expected_version: Optional[int],
        events: List[Event],
    ) -> None:
        conn = await self.pool.acquire()
        try:
            aggregate_id = str(aggregate_uuid)
            if expected_version:
                result = await conn.execute(
                    """
                    UPDATE aggregates
                    SET version=$1 + 1
                    WHERE version = $1 AND uuid = $2
                    """,
                    expected_version,
                    aggregate_id,
                )
                if result != "UPDATE 1":
                    raise ConcurrentStreamWriteError
            else:
                await conn.execute(
                    """
                    INSERT INTO aggregates (uuid, version)
                    VALUES ($1, $2)
                    """,
                    aggregate_id,
                    1,
                )

            for event in events:
                await conn.execute(
                    """
                    INSERT INTO events (uuid, aggregate_uuid, name, data)
                    VALUES ($1, $2, $3, $4)
                    """,
                    str(uuid.uuid4()),
                    aggregate_id,
                    event.__class__.__name__,
                    event.as_dict(),
                )
        finally:
            await self.pool.release(conn)
