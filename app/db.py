from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import Annotated
from fastapi import Depends
from app.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, pool_size=40, max_overflow=20, pool_timeout=30, pool_pre_ping=True, echo=False, future=True)
new_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession,)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_db)]