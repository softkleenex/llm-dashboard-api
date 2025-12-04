from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DeploymentEnvironment(str, Enum):
    PRODUCTION = "프로덕션"
    DEVELOPMENT = "개발"
    TEST = "테스트"
    STAGING = "스테이징"


class DeploymentStatus(str, Enum):
    ACTIVE = "활성"
    INACTIVE = "비활성"
    ERROR = "오류"
    MAINTENANCE = "유지보수"


class DeploymentBase(BaseModel):
    server_name: str = Field(..., max_length=200)
    gpu_count: int = Field(..., ge=0)
    environment: DeploymentEnvironment
    status: DeploymentStatus
    model_id: str = Field(..., max_length=50)
    dataset_id: Optional[str] = Field(None, max_length=50)


class DeploymentCreate(DeploymentBase):
    pass


class DeploymentUpdate(BaseModel):
    server_name: Optional[str] = Field(None, max_length=200)
    gpu_count: Optional[int] = Field(None, ge=0)
    environment: Optional[DeploymentEnvironment] = None
    status: Optional[DeploymentStatus] = None
    dataset_id: Optional[str] = Field(None, max_length=50)


class DeploymentResponse(DeploymentBase):
    deployment_id: str

    class Config:
        from_attributes = True

