from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentResponse,
    DeploymentEnvironment,
    DeploymentStatus,
    DeploymentBasic,
    ModelDatasetDeploymentMapping,
    DeploymentByGPU,
    ModelConfigDeployment,
    EnvironmentStats,
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


# ==========================
# 통계/분석 쿼리 엔드포인트 (for Phase 3 Mapping)
# 주의: /{deployment_id} 보다 먼저 정의해야 함!
# ==========================


@router.get("/stats/q1", response_model=List[DeploymentBasic])
def query1_active_production_deployments(
    environment: Optional[DeploymentEnvironment] = Query(None, description="배포 환경 필터"),
    status: Optional[DeploymentStatus] = Query(None, description="배포 상태 필터"),
):
    """Q1: 배포 환경 조회 (동적 필터)"""
    return DeploymentService.query1_active_production_deployments(environment, status)


@router.get("/stats/q2", response_model=List[ModelDatasetDeploymentMapping])
def query2_model_dataset_deployment_mapping():
    """Q2: 모델-데이터셋-배포 매핑"""
    return DeploymentService.query2_model_dataset_deployment_mapping()


@router.get("/stats/q4", response_model=List[DeploymentByGPU])
def query4_deployments_above_avg_gpu(
    min_gpu_count: Optional[int] = Query(None, ge=0, description="최소 GPU 수"),
    use_average: Optional[bool] = Query(None, description="평균보다 많은 경우만 조회"),
):
    """Q4: GPU 수 기준 배포 조회 (동적 필터)"""
    return DeploymentService.query4_deployments_above_avg_gpu(min_gpu_count, use_average)


@router.get("/stats/q8", response_model=List[ModelConfigDeployment])
def query8_model_config_deployment_by_gpu(
    order_by: Optional[str] = Query(None, description="정렬 기준 (gpu_count, temperature, max_tokens, model_name)"),
    order_dir: Optional[str] = Query(None, description="정렬 방향 (ASC, DESC)"),
):
    """Q8: 모델-설정-배포 관계 (동적 정렬)"""
    return DeploymentService.query8_model_config_deployment_by_gpu(order_by, order_dir)


@router.get("/stats/q9", response_model=List[EnvironmentStats])
def query9_environment_avg_gpu_and_deployment_count(
    environment: Optional[DeploymentEnvironment] = Query(None, description="배포 환경 필터"),
    min_avg_gpu: Optional[float] = Query(None, ge=0, description="최소 평균 GPU 수"),
):
    """Q9: 환경별 평균 GPU/배포 수 (동적 필터)"""
    return DeploymentService.query9_environment_avg_gpu_and_deployment_count(environment, min_avg_gpu)


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

