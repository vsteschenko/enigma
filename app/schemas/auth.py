from pydantic import BaseModel, EmailStr, Field

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str

class SignupSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class SignupResponse(BaseModel):
    message: str