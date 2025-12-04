from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    project_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    creator_user_id: str = Field(..., max_length=50)
    department_id: str = Field(..., max_length=50)


class ProjectCreate(ProjectBase):
    project_id: str = Field(..., max_length=50)


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    project_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectWithCreatorAndDepartment(BaseModel):
    """Query 12: 프로젝트 생성자와 소속 부서 정보"""

    user_name: str
    department_name: str
    project_name: str

    class Config:
        from_attributes = True


class ProjectsByDepartment(BaseModel):
    """Query 13: 부서별 프로젝트 수"""

    department_name: str
    project_count: int

    class Config:
        from_attributes = True


class ProjectIdName(BaseModel):
    """Query 16: 관리자가 지정된 부서의 프로젝트"""

    project_id: str
    project_name: str

    class Config:
        from_attributes = True


