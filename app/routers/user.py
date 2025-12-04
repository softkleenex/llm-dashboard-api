from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithDepartment,
    UserByRole,
    UserBasic,
    UserWithSessionCount,
    UserIdOnly,
    UserRole,
)
from app.schemas.session import SessionStatus
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["사용자 관리"])


# ========================================
# 통계/분석 쿼리 (Phase 3 Mainmenu 1, 5)
# 주의: /{user_id} 보다 먼저 정의해야 함!
# ========================================


@router.get("/stats/by-role", response_model=List[UserByRole])
def get_users_by_role(role: str = Query(..., description="역할 (Admin, Developer, Data Scientist, Researcher, Team Leader)")):
    """[Q11] 특정 역할 사용자 조회"""
    return UserService.get_by_role(role)


@router.get("/stats/by-department-name", response_model=List[UserBasic])
def get_users_by_department_name(department_name: str = Query(..., description="부서명")):
    """[Q14] 특정 부서명으로 유저 조회 (서브쿼리 사용)"""
    return UserService.get_by_department_name(department_name)


@router.get("/stats/with-sessions", response_model=List[UserBasic])
def get_users_with_sessions(
    session_status: Optional[SessionStatus] = Query(
        None, description="세션 상태 (진행중, 완료, 오류, 중단)"
    )
):
    """[Q15] 특정 상태 세션을 보유한 유저 조회 (EXISTS 서브쿼리)"""
    return UserService.get_users_with_active_sessions(session_status)


@router.get("/stats/min-sessions", response_model=List[UserWithSessionCount])
def get_users_with_min_sessions(
    min_count: int = Query(5, ge=1, description="최소 세션 수 (기본값: 5)")
):
    """[Q17] 최소 세션 수 이상 보유 유저 조회 (인라인 뷰)"""
    return UserService.get_users_with_min_sessions(min_count)


@router.get("/stats/role-and-managers", response_model=List[UserIdOnly])
def get_role_users_and_managers(
    role: Optional[str] = Query(None, description="역할 (선택사항)")
):
    """[Q20] 특정 역할 유저와 부서 관리자 통합 조회 (UNION)"""
    return UserService.get_role_users_and_managers(role)


# ========================================
# 기본 CRUD (Mainmenu 1)
# ========================================


@router.get("/", response_model=List[UserWithDepartment])
def get_all_users(
    user_name: Optional[str] = Query(None, description="유저 이름 (정확히 일치)"),
    role: Optional[UserRole] = Query(None, description="역할 필터"),
):
    """모든 사용자 조회 (유저 이름 및 역할 필터링 가능)"""
    try:
        role_str = role.value if role else None
        return UserService.get_all(user_name, role_str)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/department/{department_id}", response_model=List[UserWithDepartment])
def get_users_by_department(
    department_id: str,
    user_name: Optional[str] = Query(None, description="유저 이름 (정확히 일치)"),
    role: Optional[UserRole] = Query(None, description="역할 필터"),
):
    """부서별 사용자 목록 조회 (유저 이름 및 역할 필터링 가능)"""
    role_str = role.value if role else None
    return UserService.get_by_department(department_id, user_name, role_str)


@router.get("/{user_id}", response_model=UserWithDepartment)
def get_user(user_id: str):
    """사용자 ID로 조회"""
    user = UserService.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """사용자 추가"""
    try:
        return UserService.create(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user: UserUpdate):
    """사용자 수정"""
    result = UserService.update(user_id, user)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
    return result


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    """사용자 삭제"""
    if not UserService.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )
