import abc
import dataclasses
import json
import uuid
from typing import Optional, List, Type
import asyncpg
import events
import models


class ConcurrentStreamWriteError(RuntimeError):
    pass


class NotFound(BaseException):
    pass


class EventStore(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def load_stream(self, aggregate_uuid: uuid.UUID) -> events.EventStream:
        pass

    @abc.abstractmethod
    async def append_to_stream(
        self,
        aggregate_uuid: uuid.UUID,
        expected_version: Optional[int],
        events: List[events.Event],
    ) -> None:
        pass


class PostgreSQLEventStore(EventStore):
    def __init__(self, pool: asyncpg.pool.Pool):
        self.pool = pool

    async def load_stream(self, aggregate_uuid: uuid.UUID) -> events.EventStream:
        conn = await self.pool.acquire()
        try:
            res = await conn.fetchrow(
                """
                SELECT aggregates.uuid, aggregates.version, ARRAY_AGG(events.*) as events
                FROM aggregates, events
                WHERE events.aggregate_uuid = aggregates.uuid AND aggregates.uuid = $1
                GROUP BY aggregates.uuid;
                """,
                str(aggregate_uuid),
            )
            if res is None:
                raise NotFound
        finally:
            await self.pool.release(conn)

        version = res["version"]
        event_list: List[events.Event] = [
            self._instantiate_event(
                models.Event(
                    uuid=event["uuid"],
                    aggregate_uuid=event["aggregate_uuid"],
                    name=event["name"],
                    data=json.loads(event["data"]),
                )
            )
            for event in res["events"]
        ]
        return events.EventStream(events=event_list, version=version)

    async def append_to_stream(
        self,
        aggregate_uuid: uuid.UUID,
        expected_version: Optional[int],
        events: List[events.Event],
    ) -> None:
        conn = await self.pool.acquire()
        try:
            aggregate_id = str(aggregate_uuid)
            if expected_version:
                result = await conn.execute(
                    """
                    UPDATE aggregates
                    SET version=$1 + 1
                    WHERE version = $1 AND uuid = $2;
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
                    VALUES ($1, $2);
                    """,
                    aggregate_id,
                    1,
                )

            for event in events:
                await conn.execute(
                    """
                    INSERT INTO events (uuid, aggregate_uuid, name, data)
                    VALUES ($1, $2, $3, $4);
                    """,
                    str(uuid.uuid4()),
                    aggregate_id,
                    event.__class__.__name__,
                    json.dumps(dataclasses.asdict(event)),
                )
        finally:
            await self.pool.release(conn)

    def _instantiate_event(self, event_model: models.Event) -> events.Event:
        class_name = event_model.name
        kwargs = event_model.data
        event_class: Type[events.Event] = getattr(events, class_name)
        return event_class(**kwargs)
