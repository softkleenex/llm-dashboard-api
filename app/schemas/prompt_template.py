from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskCategory(str, Enum):
    QUALITY_REVIEW = "품질검토"
    QNA = "질의응답"
    DOCUMENTATION = "문서화"
    CODING = "코딩"
    SUMMARIZATION = "요약"
    TRANSLATION = "번역"
    GENERATION = "생성"
    ANALYSIS = "분석"


class PromptTemplateBase(BaseModel):
    template_name: str = Field(..., max_length=200)
    prompt_s3_path: str = Field(..., max_length=500)
    description: Optional[str] = None
    task_category: TaskCategory
    variables: Optional[str] = None
    version: str = Field(..., max_length=50)


class PromptTemplateCreate(PromptTemplateBase):
    creator_user_id: str = Field(..., max_length=50)


class PromptTemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, max_length=200)
    prompt_s3_path: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    task_category: Optional[TaskCategory] = None
    variables: Optional[str] = None
    version: Optional[str] = Field(None, max_length=50)


class PromptTemplateResponse(PromptTemplateBase):
    template_id: str
    usage_count: int = 0
    created_at: Optional[datetime] = None
    creator_user_id: str
    creator_user_name: Optional[str] = None

    class Config:
        from_attributes = True


