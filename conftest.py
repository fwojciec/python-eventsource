import asyncio
import pytest
import asyncpg


DSN = "postgres://filip@localhost:5432/event_source_test"
LOOP = asyncio.get_event_loop()


async def create_table(dsn: str):
    conn = await asyncpg.connect(dsn)
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
    await conn.close()


async def drop_table(dsn: str):
    conn = await asyncpg.connect(dsn)
    await conn.execute(
        """
        DROP TABLE events;
        DROP TABLE aggregates;
        """
    )
    await conn.close()


async def clear_table(dsn: str):
    conn = await asyncpg.connect(dsn)
    await conn.execute(
        """
        DELETE FROM events;
        DELETE FROM aggregates;
        """
    )
    await conn.close()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.fixture(scope="session", autouse=True)
async def table_setup(request, event_loop):
    def teardown():
        async def ateardown():
            await drop_table(DSN)

        event_loop.run_until_complete(ateardown())

    await create_table(DSN)
    request.addfinalizer(teardown)


@pytest.fixture(scope="function", autouse=True)
def table_clear(request, event_loop):
    def teardown():
        async def ateardown():
            await clear_table(DSN)

        event_loop.run_until_complete(ateardown())

    request.addfinalizer(teardown)


@pytest.fixture
async def pool():
    return await asyncpg.create_pool(DSN)
