"""add category check to transactions

Revision ID: 8f0e493f6715
Revises: 
Create Date: 2025-12-16 16:22:19.150090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f0e493f6715'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_transactions_category_allowed",
        "transactions",
        "(type = 'expense' AND category IN ('beauty', 'education', 'credit_card', 'dining', 'entertainment', 'gifts', 'grocery', 'health', 'home_maintenance', 'insurance', 'loans', 'pets', 'rent', 'savings', 'shopping', 'subscriptions', 'transport', 'travel', 'utilities', 'work', 'taxes', 'other')) "
        "OR (type = 'income' AND category IN ('business', 'dividends', 'freelance', 'gifts', 'government_benefits', 'investments', 'refunds', 'rental_income', 'salary', 'other'))"
    )

def downgrade() -> None:
    op.drop_constraint("ck_transactions_category_allowed", "transactions", type_="check")