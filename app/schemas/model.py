from pydantic import BaseModel, Field
from typing import Optional


class ModelBase(BaseModel):
    model_name: str = Field(..., max_length=200)
    model_type: str = Field(..., max_length=100)


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    model_name: Optional[str] = Field(None, max_length=200)
    model_type: Optional[str] = Field(None, max_length=100)


class ModelResponse(ModelBase):
    model_id: str

    class Config:
        from_attributes = True


# Q3: 모델 설정 및 배포 수
class ModelConfigDeploymentCount(BaseModel):
    model_name: str
    model_type: str
    config_count: int
    deployment_count: int


# Q7: 모델 평균 Temperature 및 배포 수
class ModelAvgTemperatureStats(BaseModel):
    model_name: str
    avg_temperature: float
    config_count: int
    deployment_count: int


# Q10: 배포되지 않은 모델
class UndeployedModel(BaseModel):
    model_id: str
    model_name: str
    model_type: str

