import os
from datetime import timedelta
from authx import AuthXConfig
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR / "friendly-octo-spork.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

config = AuthXConfig()
config.JWT_SECRET_KEY = os.environ.get("SECRET_KEY")
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_SAMESITE = "lax"
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)