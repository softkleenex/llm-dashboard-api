from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    BUSINESS_ANALYST = "Business Analyst"
    CUSTOMER_SUCCESS = "Customer Success"
    DATA_ANALYST = "Data Analyst"
    DATA_SCIENTIST = "Data Scientist"
    DEVOPS_ENGINEER = "DevOps Engineer"
    ENGINEER = "Engineer"
    FINANCE_ANALYST = "Finance Analyst"
    HR_SPECIALIST = "HR Specialist"
    INTERN = "Intern"
    ML_ENGINEER = "ML Engineer"
    MLOPS_ENGINEER = "MLOps Engineer"
    OPERATIONS_MANAGER = "Operations Manager"
    PRODUCT_MANAGER = "Product Manager"
    QA_ENGINEER = "QA Engineer"
    QUALITY_ANALYST = "Quality Analyst"
    RESEARCH_SCIENTIST = "Research Scientist"
    SRE = "SRE"
    SECURITY_ANALYST = "Security Analyst"
    SECURITY_ENGINEER = "Security Engineer"
    SENIOR_ENGINEER = "Senior Engineer"
    SUPPORT_SPECIALIST = "Support Specialist"
    TEAM_LEADER = "Team Leader"
    UX_DESIGNER = "UX Designer"


class UserBase(BaseModel):
    user_name: str = Field(..., max_length=100)
    user_email: str = Field(..., max_length=200)
    role: UserRole
    department_id: str = Field(..., max_length=50)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    user_name: Optional[str] = Field(None, max_length=100)
    user_email: Optional[str] = Field(None, max_length=200)
    role: Optional[UserRole] = None
    is_active: Optional[str] = Field(None, pattern="^[YN]$")
    department_id: Optional[str] = Field(None, max_length=50)


class UserResponse(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    role: str  # Changed from UserRole enum to str for flexibility
    is_active: str = "Y"
    last_login: Optional[datetime] = None
    department_id: str

    class Config:
        from_attributes = True


class UserWithDepartment(UserResponse):
    department_name: Optional[str] = None


# 통계 쿼리용 스키마
class UserByRole(BaseModel):
    """Q11: 특정 역할 사용자 조회 결과"""
    user_id: str
    user_name: str
    user_email: str

    class Config:
        from_attributes = True


class UserBasic(BaseModel):
    """Q14, Q15: 기본 사용자 정보"""
    user_id: str
    user_name: str

    class Config:
        from_attributes = True


class UserWithSessionCount(BaseModel):
    """Q17: 세션 수 포함 사용자"""
    user_id: str
    user_name: str
    session_count: int

    class Config:
        from_attributes = True


class UserIdOnly(BaseModel):
    """Q20: 사용자 ID만"""
    user_id: str

    class Config:
        from_attributes = True


class UserRoleDistribution(BaseModel):
    """Q11: 모든 역할별 사용자 분포 (웹 대시보드용)"""
    role: str
    count: int

    class Config:
        from_attributes = True
