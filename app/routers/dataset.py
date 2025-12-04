from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.schemas.dataset import DatasetCreate, DatasetUpdate, DatasetResponse, LearningType
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["데이터셋 관리"])


@router.get("/", response_model=List[DatasetResponse])
def get_all_datasets(
    dataset_name: Optional[str] = Query(None, description="데이터셋 ID/이름 (부분 일치, 대소문자 무시)"),
    learning_type: Optional[LearningType] = Query(None, description="학습 유형 필터"),
):
    """모든 데이터셋 조회 (검색 및 필터링 가능)"""
    if dataset_name or learning_type:
        return DatasetService.search(dataset_name, learning_type)
    return DatasetService.get_all()


@router.get("/search", response_model=List[DatasetResponse])
def search_datasets(
    dataset_name: Optional[str] = Query(None, description="데이터셋 ID/이름 (부분 일치, 대소문자 무시)"),
    learning_type: Optional[LearningType] = Query(None, description="학습 유형 필터"),
):
    """데이터셋 검색: dataset_id(이름) 및 learning_type으로 필터링"""
    return DatasetService.search(dataset_name, learning_type)


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str):
    """데이터셋 ID로 조회"""
    dataset = DatasetService.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id '{dataset_id}' not found",
        )
    return dataset


@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(dataset: DatasetCreate):
    """데이터셋 추가"""
    try:
        return DatasetService.create(dataset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{dataset_id}", response_model=DatasetResponse)
def update_dataset(dataset_id: str, dataset: DatasetUpdate):
    """데이터셋 수정"""
    result = DatasetService.update(dataset_id, dataset)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id '{dataset_id}' not found",
        )
    return result


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: str):
    """데이터셋 삭제"""
    if not DatasetService.delete(dataset_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id '{dataset_id}' not found",
        )

