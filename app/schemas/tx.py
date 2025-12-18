from datetime import datetime, timezone
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.utils.categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES

class TxBase(BaseModel):
    type: Literal["expense", "income"]
    amount: float
    category: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    place: Optional[str] = None

    @field_validator("amount")
    def normalise_amount(cls, v, info):
        tx_type = info.data.get("type")
        if tx_type not in ("expense", "income"):
            raise ValueError("type must be expense or income")
        return -abs(v) if tx_type == "expense" else abs(v)
        
    @field_validator("category")
    def validate_category(cls, v, info):
        tx_type = info.data.get("type")
        if tx_type not in ("expense", "income"):
            raise ValueError("type must be expense or income")
        allowed = EXPENSE_CATEGORIES if tx_type == "expense" else INCOME_CATEGORIES
        if v not in allowed:
            raise ValueError(f"category {v} not allowed")
        return v

class TxCreateSchema(TxBase):
    pass

class TxUpdateSchema(BaseModel):
    type: Optional[Literal["expense","income"]] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    timestamp: Optional[datetime] = None
    place: Optional[str] = None

    @field_validator("amount")
    def normalise_amount(cls, v, info):
        if v is None:
            return v
        tx_type = info.data.get("type")
        if tx_type not in ("expense", "income"):
            raise ValueError("type is required")
        return -abs(v) if tx_type == "expense" else abs(v)
    
    @field_validator("category")
    def validate_category(cls, v, info):
        if v is None:
            return v
        tx_type = info.data.get("type")
        if tx_type not in ("expense", "income"):
            raise ValueError("type is required")
        allowed = EXPENSE_CATEGORIES if tx_type == "expense" else INCOME_CATEGORIES
        if v not in allowed:
            raise ValueError(f"category {v} not allowed")
        return v

class TxOut(TxBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class TxCreateResponseSchema(BaseModel):
    message: str
    transaction: TxOut

class TxListResponseSchema(BaseModel):
    message: str
    transactions: List[TxOut]

class TxUpdateResponseSchema(BaseModel):
    message: str
    transaction: TxOut

class TxDeleteSchema(BaseModel):
    pass

class TxDeleteResponseSchema(BaseModel):
    message: str
    transaction: TxOut    