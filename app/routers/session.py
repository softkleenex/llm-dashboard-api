from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.schemas.session import (
    SessionWithUser,
    SessionLogWithDetails,
    SessionLogByToken,
    UserSessionCount,
)
from app.services.session_service import SessionService, SessionLogService

router = APIRouter(prefix="/sessions", tags=["세션 및 로그 관리"])


@router.get("/", response_model=List[SessionWithUser])
def get_all_sessions():
    """모든 세션 조회"""
    return SessionService.get_all()


@router.get("/{session_id}", response_model=SessionWithUser)
def get_session(session_id: str):
    """세션 ID로 조회"""
    session = SessionService.get_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id '{session_id}' not found",
        )
    return session


@router.get("/user/{user_id}", response_model=List[SessionWithUser])
def get_sessions_by_user(user_id: str):
    """사용자별 세션 목록 조회"""
    return SessionService.get_by_user(user_id)


@router.get("/project/{project_id}", response_model=List[SessionWithUser])
def get_sessions_by_project(project_id: str):
    """프로젝트별 세션 목록 조회"""
    return SessionService.get_by_project(project_id)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str):
    """세션 삭제 (관련 로그도 CASCADE 삭제)"""
    if not SessionService.delete(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id '{session_id}' not found",
        )


# Session Logs
@router.get("/{session_id}/logs", response_model=List[SessionLogWithDetails])
def get_session_logs(session_id: str):
    """세션 로그 조회"""
    return SessionLogService.get_by_session(session_id)


@router.delete("/{session_id}/logs", status_code=status.HTTP_200_OK)
def delete_session_logs(session_id: str):
    """세션의 모든 로그 삭제"""
    deleted_count = SessionLogService.delete_by_session(session_id)
    return {"deleted_count": deleted_count}


@router.delete("/{session_id}/logs/{log_sequence}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_log(session_id: str, log_sequence: int):
    """특정 로그 삭제"""
    if not SessionLogService.delete_single(session_id, log_sequence):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log with session_id '{session_id}' and sequence '{log_sequence}' not found",
        )


# ========================================
# 통계/분석 쿼리 (Phase 3 Mainmenu 5)
# ========================================


@router.get("/stats/logs-by-token", response_model=List[SessionLogByToken])
def get_logs_by_token_usage(
    date_from: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    user_name: Optional[str] = Query(None, description="사용자명"),
    limit: Optional[int] = Query(None, ge=1, description="조회 개수 제한"),
):
    """[Q18] 세션 로그 토큰 사용량 순 조회 (동적 필터)"""
    return SessionLogService.get_logs_by_token_usage(date_from, date_to, user_name, limit)


@router.get("/stats/user-session-count", response_model=List[UserSessionCount])
def get_user_session_count(
    limit: Optional[int] = Query(None, ge=1, description="조회 개수 제한 (TopN)"),
):
    """[Q19] 유저별 세션 수 집계 및 정렬"""
    return SessionLogService.get_user_session_count(limit)
