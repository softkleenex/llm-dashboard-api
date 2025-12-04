from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ModelConfigBase(BaseModel):
    config_name: str = Field(..., max_length=200)
    max_tokens: int = Field(..., ge=1)
    temperature: float = Field(..., ge=0.0, le=2.0)
    top_p: float = Field(..., ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, ge=0)
    model_id: str = Field(..., max_length=50)


class ModelConfigCreate(ModelConfigBase):
    config_id: str = Field(..., max_length=50)


class ModelConfigUpdate(BaseModel):
    config_name: Optional[str] = Field(None, max_length=200)
    max_tokens: Optional[int] = Field(None, ge=1)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, ge=0)


class ModelConfigResponse(ModelConfigBase):
    config_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

