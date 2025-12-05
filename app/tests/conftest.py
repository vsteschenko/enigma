import asyncio, pytest, pytest_asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db import get_db
from app.main import app
from app.models import Base
from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = (f"postgresql+asyncpg://ledger_user_dev:{os.environ.get('DB_PASSWORD')}@localhost:5432/ledger_dev")

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()

@pytest_asyncio.fixture(autouse=True)
async def clear_db():
    async with TestSessionLocal() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
    yield

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db
