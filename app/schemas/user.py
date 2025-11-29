from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    DEVELOPER = "Developer"
    DATA_SCIENTIST = "Data Scientist"
    RESEARCHER = "Researcher"
    TEAM_LEADER = "Team Leader"


class UserBase(BaseModel):
    user_name: str = Field(..., max_length=100)
    user_email: str = Field(..., max_length=200)
    role: UserRole
    department_id: str = Field(..., max_length=50)


class UserCreate(UserBase):
    user_id: str = Field(..., max_length=50)
    password: str = Field(..., max_length=100)


class UserUpdate(BaseModel):
    user_name: Optional[str] = Field(None, max_length=100)
    user_email: Optional[str] = Field(None, max_length=200)
    password: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[str] = Field(None, pattern="^[YN]$")
    department_id: Optional[str] = Field(None, max_length=50)


class UserResponse(UserBase):
    user_id: str
    is_active: str = "Y"
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserWithDepartment(UserResponse):
    department_name: Optional[str] = None
