from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse
from app.services.model_service import ModelService

router = APIRouter(prefix="/models", tags=["모델 관리"])


@router.get("/", response_model=List[ModelResponse])
def get_all_models():
    """모든 모델 조회"""
    return ModelService.get_all()


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: str):
    """모델 ID로 조회"""
    model = ModelService.get_by_id(model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with id '{model_id}' not found",
        )
    return model


@router.post("/", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(model: ModelCreate):
    """모델 추가"""
    try:
        return ModelService.create(model)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(model_id: str, model: ModelUpdate):
    """모델 수정"""
    result = ModelService.update(model_id, model)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with id '{model_id}' not found",
        )
    return result


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(model_id: str):
    """모델 삭제"""
    if not ModelService.delete(model_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with id '{model_id}' not found",
        )

