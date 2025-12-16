from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Integer, Float, DateTime, CheckConstraint
from datetime import datetime, timezone
from app.utils.categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES

expense_keys = "', '".join(EXPENSE_CATEGORIES)
income_keys = "', '".join(INCOME_CATEGORIES)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True,  nullable=False)
    password: Mapped[str] =mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[str | None] = mapped_column(String, nullable=True)
    reset_token: Mapped[str | None] = mapped_column(String, nullable=True)
    delete_token: Mapped[str | None] = mapped_column(String, nullable=True)
    transactions: Mapped[list["Transactions"]] = relationship(back_populates="user", cascade="all, delete-orphan",)

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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,)
    type: Mapped[str] = mapped_column(String, nullable=False)
    place: Mapped[str] = mapped_column(String(100), default="Unknown")
    user: Mapped["User"] = relationship(back_populates="transactions",)
