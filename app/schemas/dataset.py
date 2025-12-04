from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class LearningType(str, Enum):
    FINE_TUNING = "파인튜닝"
    PROMPT_LEARNING = "프롬프트학습"
    TRANSFER_LEARNING = "전이학습"
    REINFORCEMENT_LEARNING = "강화학습"


class DatasetBase(BaseModel):
    learning_type: LearningType
    description: Optional[str] = None
    s3_path: str = Field(..., max_length=500)


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(BaseModel):
    learning_type: Optional[LearningType] = None
    description: Optional[str] = None
    s3_path: Optional[str] = Field(None, max_length=500)


class DatasetResponse(DatasetBase):
    dataset_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
