from fastapi import APIRouter, HTTPException, status
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
    result = DepartmentService.update(department_id, department)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with id '{department_id}' not found",
        )
    return result


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id: str):
    """부서 삭제"""
    if not DepartmentService.delete(department_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with id '{department_id}' not found",
        )
