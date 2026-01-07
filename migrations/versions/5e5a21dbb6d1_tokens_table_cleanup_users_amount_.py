"""tokens table + cleanup users + amount numeric (fix)

Revision ID: 5e5a21dbb6d1
Revises: 0ae0b8b8eda1
Create Date: 2026-01-07 20:36:49.088357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '5e5a21dbb6d1'
down_revision: Union[str, Sequence[str], None] = '0ae0b8b8eda1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Create enum only if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'token_type') THEN
            CREATE TYPE token_type AS ENUM ('verify_email', 'reset_password', 'delete_account');
        END IF;
    END$$;
    """)

    # 2) Define enum for SQLAlchemy without auto-create
    token_type_enum = postgresql.ENUM(
        "verify_email", "reset_password", "delete_account",
        name="token_type",
        create_type=False,
    )

    # 3) Create table if not exists (Alembic doesn't have if-not-exists for create_table, so we just attempt.
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

    # Drop legacy columns only if they exist (otherwise migration may fail)
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("users")}
    if "verification_token" in cols:
        op.drop_column("users", "verification_token")
    if "reset_token" in cols:
        op.drop_column("users", "reset_token")
    if "delete_token" in cols:
        op.drop_column("users", "delete_token")

    # Amount float -> numeric (safe even if already numeric? better check)
    tx_cols = {c["name"]: c for c in insp.get_columns("transactions")}
    if "amount" in tx_cols:
        # crude check: if already Numeric, skip
        if not isinstance(tx_cols["amount"]["type"], sa.Numeric):
            op.alter_column(
                "transactions",
                "amount",
                type_=sa.Numeric(12, 2),
                postgresql_using="amount::numeric(12,2)",
                existing_type=sa.Float(),
                existing_nullable=False,
            )

def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # revert amount if needed
    tx_cols = {c["name"]: c for c in insp.get_columns("transactions")}
    if "amount" in tx_cols and isinstance(tx_cols["amount"]["type"], sa.Numeric):
        op.alter_column(
            "transactions",
            "amount",
            type_=sa.Float(),
            postgresql_using="amount::double precision",
            existing_type=sa.Numeric(12, 2),
            existing_nullable=False,
        )

    # restore columns if missing
    user_cols = {c["name"] for c in insp.get_columns("users")}
    if "verification_token" not in user_cols:
        op.add_column("users", sa.Column("verification_token", sa.String(), nullable=True))
    if "reset_token" not in user_cols:
        op.add_column("users", sa.Column("reset_token", sa.String(), nullable=True))
    if "delete_token" not in user_cols:
        op.add_column("users", sa.Column("delete_token", sa.String(), nullable=True))

    # drop table + indexes if table exists
    tables = set(insp.get_table_names())
    if "user_tokens" in tables:
        op.drop_index("ix_user_tokens_user_type", table_name="user_tokens")
        op.drop_index("ix_user_tokens_token_type", table_name="user_tokens")
        op.drop_index("ix_user_tokens_user_id", table_name="user_tokens")
        op.drop_index("ix_user_tokens_token", table_name="user_tokens")
        op.drop_table("user_tokens")

    # drop enum only if no longer used and exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'token_type') THEN
            DROP TYPE token_type;
        END IF;
    END$$;
    """)

