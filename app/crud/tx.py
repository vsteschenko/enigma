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

async def update_tx(db: AsyncSession, tx_id: int, user_id: int, **data) -> Transactions:
    res = await db.execute(select(Transactions).where(Transactions.id == tx_id, Transactions.user_id == user_id,))
    tx = res.scalar_one_or_none()
    if tx is None:
        raise ValueError("Transaction not found")
    
    for field in ("amount", "category", "timestamp", "type", "place"):
        if field in data:
            setattr(tx, field, data[field])
    try:
        await db.commit()
        await db.refresh(tx)
        return tx
    except Exception:
        await db.rollback()
        raise

