import os
import random
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import User, Transactions
from app.utils.categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES
from app.services.auth import hash_password

load_dotenv()

def random_amount() -> Decimal:
    cents = random.randint(1, 100000)
    return (Decimal(cents) / Decimal(100)).quantize(Decimal("0.01"))

def random_ts(days_back: int = 180) -> datetime:
    now = datetime.now(timezone.utc)
    delta = timedelta(seconds=random.randint(0, days_back * 24 * 3600))
    return now - delta

def seed_transactions(db_url: str, n_users: int = 100, n_per_user: int = 3000):
    engine = create_engine(db_url, pool_pre_ping=True)
    with Session(engine) as session:
        exp_keys = list(EXPENSE_CATEGORIES.keys())
        inc_keys = list(INCOME_CATEGORIES.keys())
        for i in range(1, n_users + 1):
            email = f"loadtest{i}@example.com"
            user = session.query(User).filter_by(email=email).one_or_none()
            password = "12345678X"
            hash = hash_password(password)
            if not user:
                # CREATE 100 different users
                user = User(email=email, hashed_password=hash, is_verified=True)
                session.add(user)
                session.commit()
                session.refresh(user)
            print(user)
            rows = []
            for j in range(n_per_user):
                t = "expense" if random.random() < 0.7 else "income"
                category = random.choice(exp_keys if t == "expense" else inc_keys)

                place_val = f"p{random.randint(1, 5000)}"
                rows.append({
                    "user_id": user.id,
                    "amount": random_amount(),
                    "category": category,
                    "timestamp": random_ts(),
                    "type": t,
                    "place": place_val,
                })
                if len(rows) >= 10_000:
                    session.execute(Transactions.__table__.insert(), rows)
                    session.commit()
                    rows.clear()
            if rows:
                session.execute(Transactions.__table__.insert(), rows)
                session.commit()

if __name__ == "__main__":
    DATABASE_URL = f"postgresql+psycopg://ledger_user:{os.environ.get('DB_PASSWORD')}@localhost:5432/ledger"
    seed_transactions(DATABASE_URL, n_users=100, n_per_user=3000)
