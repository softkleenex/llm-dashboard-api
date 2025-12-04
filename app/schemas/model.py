from pydantic import BaseModel, Field
from typing import Optional


class ModelBase(BaseModel):
    model_name: str = Field(..., max_length=200)
    model_type: str = Field(..., max_length=100)


class ModelCreate(ModelBase):
    model_id: str = Field(..., max_length=50)


class ModelUpdate(BaseModel):
    model_name: Optional[str] = Field(None, max_length=200)
    model_type: Optional[str] = Field(None, max_length=100)


class ModelResponse(ModelBase):
    model_id: str

    class Config:
        from_attributes = True

