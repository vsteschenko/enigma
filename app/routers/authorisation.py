from fastapi import APIRouter, Response, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.auth import SignupSchema, SignupResponse, LoginSchema, LoginResponse
from app.services.auth import signup, login, security

router = APIRouter(prefix="", tags=["auth"])

@router.post("/signup", response_model=SignupResponse)
async def signup_route(credentials: SignupSchema, response: Response, db: AsyncSession = Depends(get_db)):
    user, token = await signup(db, credentials.email, credentials.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=token)
    security.set_access_cookies(token, response)
    return SignupResponse(message="Signup successful")

@router.post("/login", response_model=LoginResponse)
async def login_route(credentials: LoginSchema, response: Response, db: AsyncSession = Depends(get_db)):
    user, token = await login(db, credentials.email, credentials.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=token)
    security.set_access_cookies(token, response)
    return LoginResponse(message="Login successfull")
