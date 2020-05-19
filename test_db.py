import uuid
import pytest
from asyncpg.pool import Pool
from event_store import PostgreSQLEventStore


@pytest.mark.asyncio
async def test_create_aggregate_if_doesnt_exist(pool: Pool):
    es = PostgreSQLEventStore(pool=pool)
    test_id = uuid.uuid4()
    await es.append_to_stream(test_id, None, [])
    async with pool.acquire() as conn:
        rows = await conn.fetch("select * from aggregates")
        assert len(rows) == 1
        assert rows[0]["uuid"] == str(test_id)
        assert rows[0]["version"] == 1


@pytest.mark.asyncio
async def test_aggregate_version_is_increased_if_already_exists(pool: Pool):
    es = PostgreSQLEventStore(pool=pool)
    test_id = uuid.uuid4()
    await es.append_to_stream(test_id, None, [])
    await es.append_to_stream(test_id, 1, [])
    async with pool.acquire() as conn:
        rows = await conn.fetch("select * from aggregates")
        assert len(rows) == 1
        assert rows[0]["uuid"] == str(test_id)
        assert rows[0]["version"] == 2
