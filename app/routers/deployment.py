from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentResponse,
    DeploymentEnvironment,
)
from app.services.deployment_service import DeploymentService

router = APIRouter(prefix="/deployments", tags=["배포 환경 관리"])


@router.get("/", response_model=List[DeploymentResponse])
def get_all_deployments():
    """모든 배포 환경 조회"""
    return DeploymentService.get_all()


@router.get("/model/{model_id}", response_model=List[DeploymentResponse])
def get_deployments_by_model(model_id: str):
    """모델별 배포 환경 조회"""
    return DeploymentService.get_by_model(model_id)


@router.get("/environment/{environment}", response_model=List[DeploymentResponse])
def get_deployments_by_environment(environment: DeploymentEnvironment):
    """환경별 배포 환경 조회"""
    return DeploymentService.get_by_environment(environment)


@router.get("/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(deployment_id: str):
    """배포 ID로 조회"""
    deployment = DeploymentService.get_by_id(deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment with id '{deployment_id}' not found",
        )
    return deployment


@router.post("/", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
def create_deployment(deployment: DeploymentCreate):
    """배포 환경 추가"""
    try:
        return DeploymentService.create(deployment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{deployment_id}", response_model=DeploymentResponse)
def update_deployment(deployment_id: str, deployment: DeploymentUpdate):
    """배포 환경 수정"""
    result = DeploymentService.update(deployment_id, deployment)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment with id '{deployment_id}' not found",
        )
    return result


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deployment(deployment_id: str):
    """배포 환경 삭제"""
    if not DeploymentService.delete(deployment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment with id '{deployment_id}' not found",
        )

