from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithCreatorAndDepartment,
    ProjectsByDepartment,
    ProjectIdName,
)
from app.services.project_service import ProjectService


router = APIRouter(prefix="/projects", tags=["프로젝트 관리"])


@router.get("/", response_model=List[ProjectResponse])
def get_all_projects():
    """모든 프로젝트 조회"""
    return ProjectService.get_all()


@router.get("/search", response_model=List[ProjectResponse])
def search_projects(
    department_name: Optional[str] = Query(
        None, description="부서명 (부분 일치, 대소문자 무시)"
    ),
    project_name: Optional[str] = Query(
        None, description="프로젝트명 (부분 일치, 대소문자 무시)"
    ),
    creator_user_name: Optional[str] = Query(
        None, description="생성자명 (부분 일치, 대소문자 무시)"
    ),
):
    """프로젝트 검색: 부서명, 프로젝트명, 생성자명으로 필터링"""
    return ProjectService.search(department_name, project_name, creator_user_name)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str):
    """프로젝트 ID로 조회"""
    project = ProjectService.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{project_id}' not found",
        )
    return project


@router.get("/department/{department_id}", response_model=List[ProjectResponse])
def get_projects_by_department(department_id: str):
    """부서별 프로젝트 목록 조회"""
    return ProjectService.get_by_department(department_id)


@router.get("/user/{user_id}", response_model=List[ProjectResponse])
def get_projects_by_creator(user_id: str):
    """사용자별 생성 프로젝트 목록 조회"""
    return ProjectService.get_by_creator(user_id)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate):
    """프로젝트 추가"""
    try:
        return ProjectService.create(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, project: ProjectUpdate):
    """프로젝트 수정"""
    result = ProjectService.update(project_id, project)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{project_id}' not found",
        )
    return result


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str):
    """프로젝트 삭제"""
    if not ProjectService.delete(project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{project_id}' not found",
        )


# ========================================
# 통계/분석 쿼리 
# ========================================


@router.get(
    "/stats/creator-and-department",
    response_model=List[ProjectWithCreatorAndDepartment],
)
def get_project_creator_and_department(
    department_name: Optional[str] = Query(
        None,
        description="부서명 (선택사항)",
    ),
    creator_user_name: Optional[str] = Query(
        None,
        description="생성자명 (선택사항)",
    ),
):
    """[Q12] 프로젝트 생성자와 소속 부서 정보"""
    return ProjectService.get_project_creator_and_department(
        department_name=department_name,
        creator_user_name=creator_user_name,
    )


@router.get(
    "/stats/by-department",
    response_model=List[ProjectsByDepartment],
)
def get_projects_by_department_stats(
    department_name: Optional[str] = Query(
        None,
        description="부서명 (선택사항)",
    ),
    min_count: Optional[int] = Query(
        None,
        ge=1,
        description="최소 프로젝트 수 (선택사항)",
    ),
):
    """[Q13] 부서별 프로젝트 수 집계"""
    return ProjectService.get_projects_by_department_stats(
        department_name=department_name,
        min_count=min_count,
    )


@router.get(
    "/stats/with-managers",
    response_model=List[ProjectIdName],
)
def get_projects_with_managers():
    """[Q16] 관리자가 지정된 부서의 프로젝트"""
    return ProjectService.get_projects_with_managers()


