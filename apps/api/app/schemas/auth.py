from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "engineer@enterprise.com"})
    password: str = Field(..., min_length=8, max_length=128, json_schema_extra={"example": "SecureP@ssw0rd123"})
    full_name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Alex Mercer"})


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "engineer@enterprise.com"})
    password: str = Field(..., min_length=1, json_schema_extra={"example": "SecureP@ssw0rd123"})


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_platform_admin: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    user: UserResponse
    token: TokenResponse

