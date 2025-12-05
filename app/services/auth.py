from authx import AuthX
from passlib.context import CryptContext
from app.core.config import config
from app.crud.user import get_user_by_email, create_user

security = AuthX(config=config)
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def signup(db, email: str, password: str):
    email = email.lower().strip()
    existing = await get_user_by_email(db, email)
    if existing:
        return None, "User with this email exists"
    user = await create_user(db, email, hash_password(password))
    token = security.create_access_token(uid=str(user.id))
    return user, token

async def login(db, email: str, password: str):
    email = email.lower().strip()
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password):
        return None, "Invalid email or password"
    token = security.create_access_token(uid=str(user.id))
    return user, token
