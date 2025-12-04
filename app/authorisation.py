from fastapi import Response, Depends, HTTPException, status, APIRouter
from authx import AuthX
from app.core.config import config
from app.schemas import LoginSchema, LoginResponse, SignupSchema, SignupResponse
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models import User
from passlib.context import CryptContext

router = APIRouter(prefix="", tags=["auth"])

security = AuthX(config=config)
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/signup", response_model=SignupResponse)
async def signup(
    credentials: SignupSchema,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    email = credentials.email.lower().strip()
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email exists"
        )
    hashed_password = hash_password(credentials.password)
    new_user = User(
        email = email,
        password = hashed_password,
    )
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email exists"
        )
    db.refresh(new_user)
    token = security.create_access_token(uid=str(new_user.id))
    security.set_access_cookies(token, response)
    return SignupResponse(
        message="Signup successful"
    )

@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginSchema,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    email = credentials.email.lower().strip()
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # if not user.is_verified:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Email is not verified",
    #     )

    token = security.create_access_token(uid=str(user.id))
    security.set_access_cookies(token, response)

    return LoginResponse(message="Login successfull")

@router.post("/logout")
async def logout(response: Response):
    security.unset_access_cookies(response)
    return {"message": "Logged out seccessfully"}