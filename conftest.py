import pytest
import asyncpg
from asyncpg.pool import Pool
from main import Settings


async def create_tables(pool: Pool):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE "aggregates" (
                uuid varchar(36) NOT NULL PRIMARY KEY,
                version int NOT NULL DEFAULT 1
            );

            CREATE TABLE "events" (
                uuid varchar(36) NOT NULL PRIMARY KEY,
                aggregate_uuid varchar(36) NOT NULL REFERENCES "aggregates" ("uuid"),
                name varchar(50) NOT NULL,
                data json
            );
            """
        )


async def drop_tables(pool: Pool):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            DROP TABLE events;
            DROP TABLE aggregates;
            """
        )


@pytest.fixture(scope="session")
def settings():
    yield Settings(_env_file=".env.test")


@pytest.fixture(scope="session")
def dsn(settings):
    yield settings.pg_dsn


@pytest.fixture
async def pool(dsn):
    pool = await asyncpg.create_pool(dsn)
    await create_tables(pool)
    yield pool
    await drop_tables(pool)
    pool.terminate()
