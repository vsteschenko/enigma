from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.tx import TxCreateSchema, TxCreateResponseSchema, TxListResponseSchema, TxUpdateSchema, TxUpdateResponseSchema
from app.crud.tx import create_tx, all_txs, update_tx as update_tx_crud
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

@router.put("/{tx_id}", response_model=TxUpdateResponseSchema, status_code=200)
async def update_tx(
    tx_id: int,
    payload: TxUpdateSchema,
    db: AsyncSession = Depends(get_db),
    token: TokenPayload = Depends(security.access_token_required),
): 
    try:
        user_id = int(token.sub)
    except(TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        tx = await update_tx_crud(db, tx_id=tx_id, user_id=user_id, **data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"message": "Transactions updated", "transaction": tx}
