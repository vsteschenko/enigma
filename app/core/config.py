import os
from datetime import timedelta
from authx import AuthXConfig
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = (f"postgresql+asyncpg://ledger_user:{os.environ.get('DB_PASSWORD')}@localhost:5432/ledger")

config = AuthXConfig()
config.JWT_SECRET_KEY = os.environ.get("SECRET_KEY")
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_SAMESITE = "lax"
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
config.JWT_COOKIE_SECURE = False
config.JWT_COOKIE_CSRF_PROTECT = False