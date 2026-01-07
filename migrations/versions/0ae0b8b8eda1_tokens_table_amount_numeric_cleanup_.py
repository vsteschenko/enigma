"""tokens table + amount numeric + cleanup users

Revision ID: 0ae0b8b8eda1
Revises: 23094246e0d9
Create Date: 2026-01-07 16:56:58.580197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ae0b8b8eda1'
down_revision: Union[str, Sequence[str], None] = '23094246e0d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    token_type_enum = sa.Enum(
        "verify_email", "reset_password", "delete_account",
        name="token_type",
    )
    token_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "user_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("token_type", token_type_enum, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_user_tokens_token", "user_tokens", ["token"], unique=True)
    op.create_index("ix_user_tokens_user_id", "user_tokens", ["user_id"])
    op.create_index("ix_user_tokens_token_type", "user_tokens", ["token_type"])
    op.create_index("ix_user_tokens_user_type", "user_tokens", ["user_id", "token_type"])

    op.drop_column("users", "verification_token")
    op.drop_column("users", "reset_token")
    op.drop_column("users", "delete_token")

    op.alter_column(
        "transactions",
        "amount",
        type_=sa.Numeric(12, 2),
        postgresql_using="amount::numeric(12,2)",
        existing_type=sa.Float(),
        existing_nullable=False,
    )

def downgrade() -> None:
    op.alter_column(
        "transactions",
        "amount",
        type_=sa.Float(),
        postgresql_using="amount::double precision",
        existing_type=sa.Numeric(12, 2),
        existing_nullable=False,
    )
    op.add_column("users", sa.Column("verification_token", sa.String(), nullable=True))
    op.add_column("users", sa.Column("reset_token", sa.String(), nullable=True))
    op.add_column("users", sa.Column("delete_token", sa.String(), nullable=True))

    op.drop_index("ix_user_tokens_user_type", table_name="user_tokens")
    op.drop_index("ix_user_tokens_token_type", table_name="user_tokens")
    op.drop_index("ix_user_tokens_user_id", table_name="user_tokens")
    op.drop_index("ix_user_tokens_token", table_name="user_tokens")
    op.drop_table("user_tokens")

    token_type_enum = sa.Enum(name="token_type")
    token_type_enum.drop(op.get_bind(), checkfirst=True)