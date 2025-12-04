from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas.model_config import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigResponse,
)
from app.services.model_config_service import ModelConfigService

router = APIRouter(prefix="/model-configs", tags=["모델 설정 관리"])


@router.get("/", response_model=List[ModelConfigResponse])
def get_all_model_configs():
    """모든 모델 설정 조회"""
    return ModelConfigService.get_all()


@router.get("/{config_id}", response_model=ModelConfigResponse)
def get_model_config(config_id: str):
    """설정 ID로 조회"""
    config = ModelConfigService.get_by_id(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model config with id '{config_id}' not found",
        )
    return config


@router.post(
    "/", response_model=ModelConfigResponse, status_code=status.HTTP_201_CREATED
)
def create_model_config(config: ModelConfigCreate):
    """모델 설정 추가"""
    try:
        return ModelConfigService.create(config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{config_id}", response_model=ModelConfigResponse)
def update_model_config(config_id: str, config: ModelConfigUpdate):
    """모델 설정 수정"""
    result = ModelConfigService.update(config_id, config)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model config with id '{config_id}' not found",
        )
    return result


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model_config(config_id: str):
    """모델 설정 삭제"""
    if not ModelConfigService.delete(config_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model config with id '{config_id}' not found",
        )

