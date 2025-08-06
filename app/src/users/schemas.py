from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    external_id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    full_name: str
    role: Optional[str] = None
    model_config: ConfigDict = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)

    model_config: ConfigDict = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginData(BaseModel):
    email: EmailStr
    password: str
