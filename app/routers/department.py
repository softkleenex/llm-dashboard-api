from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentWithManager,
)
from app.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["부서 관리"])


@router.get("/", response_model=List[DepartmentWithManager])
def get_all_departments():
    """모든 부서 조회"""
    return DepartmentService.get_all()


@router.get("/{department_id}", response_model=DepartmentWithManager)
def get_department(department_id: str):
    """부서 ID로 조회"""
    department = DepartmentService.get_by_id(department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with id '{department_id}' not found",
        )
    return department


@router.get("/by-name/{department_name}", response_model=DepartmentWithManager)
def get_department_by_name(department_name: str):
    """부서 이름으로 조회"""
    department = DepartmentService.get_by_name(department_name)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with name '{department_name}' not found",
        )
    return department


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(department: DepartmentCreate):
    """부서 추가"""
    try:
        return DepartmentService.create(department)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(department_id: str, department: DepartmentUpdate):
    """부서 수정"""
    try:
        result = DepartmentService.update(department_id, department)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id '{department_id}' not found",
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{department_id}/manager", response_model=DepartmentResponse)
def update_department_manager(
    department_id: str,
    manager_user_id: str = Query(..., description="관리자로 설정할 user_id")
):
    """
    부서 관리자 설정
    해당 user_id가 이미 다른 부서의 관리자로 설정되어 있는지 검증합니다.
    """
    try:
        result = DepartmentService.update(
            department_id,
            DepartmentUpdate(manager_user_id=manager_user_id)
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id '{department_id}' not found",
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id: str):
    """부서 삭제"""
    if not DepartmentService.delete(department_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with id '{department_id}' not found",
        )
