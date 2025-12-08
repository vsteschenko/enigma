from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.tx import TxCreateSchema, TxCreateResponseSchema, TxListResponseSchema
from app.crud.tx import create_tx, all_txs
from app.services.auth import security
from authx.schema import TokenPayload

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("", response_model=TxCreateResponseSchema, status_code=201)
async def add_tx(
    payload: TxCreateSchema, 
    db: AsyncSession = Depends(get_db),
    token: TokenPayload = Depends(security.access_token_required),
):
    try:
        user_id = int(token.sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    tx = await create_tx(db, user_id=user_id, **payload.model_dump())
    return {"message": "Transaction created", "transaction": tx}

@router.get("", response_model=TxListResponseSchema, status_code=200)
async def list_tx(
    db: AsyncSession = Depends(get_db),
    token: TokenPayload = Depends(security.access_token_required)
):
    try:
        user_id = int(token.sub)
    except(TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    txs = await all_txs(db, user_id=user_id)
    return {"message": "transactions received successfully", "transactions": txs}