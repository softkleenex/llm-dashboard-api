from pydantic import BaseModel, Field
from typing import Optional


class DepartmentBase(BaseModel):
    department_name: str = Field(..., max_length=200)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = Field(None, max_length=200)
    manager_user_id: Optional[str] = Field(None, max_length=50)


class DepartmentResponse(DepartmentBase):
    department_id: str
    manager_user_id: Optional[str] = None

    class Config:
        from_attributes = True


class DepartmentWithManager(DepartmentResponse):
    manager_name: Optional[str] = None
