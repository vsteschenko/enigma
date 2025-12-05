from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import Annotated
from fastapi import Depends
from app.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
new_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession,)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_db)]