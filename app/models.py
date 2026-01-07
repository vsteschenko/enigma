from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Integer, DateTime, CheckConstraint, Index, Enum, Numeric
from datetime import datetime, timezone
from decimal import Decimal
import enum
from app.utils.categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES

expense_keys = "', '".join(EXPENSE_CATEGORIES)
income_keys = "', '".join(INCOME_CATEGORIES)

class Base(DeclarativeBase):
    pass

class TokenType(str, enum.Enum):
    verify_email = "verify_email"
    reset_password = "reset_password"
    delete_account = "delete_account"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True,  nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    tokens: Mapped[list["UserToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list["Transactions"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",
    )

class UserToken(Base):
    __tablename__ = "user_tokens"
    __table_args__ = (Index("ix_user_tokens_user_type", "user_id", "token_type"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    token_type: Mapped[TokenType] = mapped_column(Enum(TokenType, name="token_type"), index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user: Mapped["User"] = relationship(back_populates="tokens")

class Transactions(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            f"(type = 'expense' AND category IN ('{expense_keys}')) OR"
            f"(type = 'income' AND category IN ('{income_keys}'))",
            name="ck_transactions_category_allowed",
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,)
    type: Mapped[str] = mapped_column(String, nullable=False)
    place: Mapped[str] = mapped_column(String(100), nullable=True)
    user: Mapped["User"] = relationship(back_populates="transactions",)
