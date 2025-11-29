from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    IN_PROGRESS = "진행중"
    COMPLETED = "완료"
    ERROR = "오류"
    STOPPED = "중단"


class SessionType(str, Enum):
    CHAT = "Chat"
    COMPLETION = "Completion"
    EMBEDDING = "Embedding"
    FINE_TUNING = "Fine-tuning"


class SessionBase(BaseModel):
    session_type: SessionType
    status: SessionStatus
    user_id: str = Field(..., max_length=50)
    project_id: Optional[str] = Field(None, max_length=50)


class SessionCreate(SessionBase):
    session_id: str = Field(..., max_length=50)
    start_time: datetime


class SessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    status: Optional[SessionStatus] = None


class SessionResponse(SessionBase):
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionWithUser(SessionResponse):
    user_name: Optional[str] = None
    project_name: Optional[str] = None


class SessionLogBase(BaseModel):
    request_prompt_s3_path: str = Field(..., max_length=500)
    response_s3_path: str = Field(..., max_length=500)
    token_used: int
    config_id: Optional[str] = Field(None, max_length=50)
    deployment_id: str = Field(..., max_length=50)


class SessionLogCreate(SessionLogBase):
    session_id: str = Field(..., max_length=50)
    request_time: datetime
    response_time: datetime


class SessionLogResponse(SessionLogBase):
    session_id: str
    log_sequence: int
    request_time: datetime
    response_time: datetime

    class Config:
        from_attributes = True


class SessionLogWithDetails(SessionLogResponse):
    config_name: Optional[str] = None
    deployment_server: Optional[str] = None


# 통계 쿼리용 스키마
class SessionLogByToken(BaseModel):
    """Q18: 토큰 사용량 순 로그 조회 결과"""
    session_id: str
    log_sequence: int
    user_name: str
    token_used: int

    class Config:
        from_attributes = True


class UserSessionCount(BaseModel):
    """Q19: 유저별 세션 수 집계 결과"""
    user_name: str
    total_sessions: int

    class Config:
        from_attributes = True
