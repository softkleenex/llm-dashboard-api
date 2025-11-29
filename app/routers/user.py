from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithDepartment,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["사용자 관리"])


@router.get("/", response_model=List[UserWithDepartment])
def get_all_users():
    """모든 사용자 조회"""
    return UserService.get_all()


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


@router.get("/department/{department_id}", response_model=List[UserWithDepartment])
def get_users_by_department(department_id: str):
    """부서별 사용자 목록 조회"""
    return UserService.get_by_department(department_id)


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
