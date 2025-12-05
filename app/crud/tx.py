from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Transactions

async def create_tx(db: AsyncSession, **data) -> Transactions:
    tx = Transactions(**data)
    try:
        db.add(tx)
        await db.commit()
        await db.refresh(tx)
        return tx
    except Exception:
        await db.rollback()
        raise

async def all_txs(db: AsyncSession, user_id: int):
    res = await db.execute(select(Transactions).where(Transactions.user_id == user_id))
    return res.scalars().all()