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


# Q1: 배포 환경 조회 (동적 필터)
class DeploymentBasic(BaseModel):
    server_name: str
    gpu_count: int
    environment: DeploymentEnvironment
    status: DeploymentStatus


# Q2: 모델-데이터셋-배포 매핑
class ModelDatasetDeploymentMapping(BaseModel):
    model_name: str
    model_type: str
    server_name: str
    environment: DeploymentEnvironment
    dataset_learning_type: str
    dataset_path: Optional[str] = None


# Q4: GPU 수 기준 배포 조회
class DeploymentByGPU(BaseModel):
    deployment_id: str
    server_name: str
    gpu_count: int
    environment: DeploymentEnvironment


# Q8: 모델-설정-배포 관계
class ModelConfigDeployment(BaseModel):
    model_name: str
    config_name: str
    max_tokens: int
    temperature: float
    server_name: str
    gpu_count: int
    environment: DeploymentEnvironment


# Q1: 배포 상태별 집계 (웹 대시보드용)
class DeploymentStatusCount(BaseModel):
    status: DeploymentStatus
    count: int


# Q9: 환경별 총 GPU/배포 수
class EnvironmentStats(BaseModel):
    environment: DeploymentEnvironment
    deployment_count: int
    total_gpu_count: int  # Phase 3: AVG에서 SUM으로 변경 (웹 대시보드에서 환경별 총 GPU 개수 비교 필요)
    unique_models: int

