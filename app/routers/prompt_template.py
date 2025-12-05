from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse,
    TaskCategory,
    PromptTemplateByCategory,
)
from app.services.prompt_template_service import PromptTemplateService


router = APIRouter(prefix="/prompt-templates", tags=["프롬프트 템플릿 관리"])


@router.get("/", response_model=List[PromptTemplateResponse])
def get_all_prompt_templates():
    """모든 프롬프트 템플릿 조회"""
    return PromptTemplateService.get_all()


@router.get("/search", response_model=List[PromptTemplateResponse])
def search_prompt_templates(
    template_name: Optional[str] = Query(
        None, description="템플릿명 (부분 일치, 대소문자 무시)"
    ),
    creator_user_name: Optional[str] = Query(
        None, description="생성자명 (부분 일치, 대소문자 무시)"
    ),
):
    """프롬프트 템플릿 검색: 템플릿명, 생성자명으로 필터링"""
    return PromptTemplateService.search(template_name, creator_user_name)


# ==========================
# 통계/분석 쿼리 엔드포인트 (for Phase 3 Mapping)
# 주의: /{template_id} 보다 먼저 정의해야 함!
# ==========================


@router.get("/stats/q6", response_model=List[PromptTemplateByCategory])
def query6_prompt_templates_by_category(
    categories: Optional[List[TaskCategory]] = Query(None, description="작업 카테고리 필터 (리스트)"),
):
    """Q6: 프롬프트 템플릿 카테고리 조회 (동적 필터)"""
    return PromptTemplateService.query6_prompt_templates_by_category(categories)


@router.get("/{template_id}", response_model=PromptTemplateResponse)
def get_prompt_template(template_id: str):
    """템플릿 ID로 조회"""
    tmpl = PromptTemplateService.get_by_id(template_id)
    if not tmpl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template with id '{template_id}' not found",
        )
    return tmpl


@router.post("/", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_prompt_template(template: PromptTemplateCreate):
    """프롬프트 템플릿 추가"""
    try:
        return PromptTemplateService.create(template)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{template_id}", response_model=PromptTemplateResponse)
def update_prompt_template(template_id: str, template: PromptTemplateUpdate):
    """프롬프트 템플릿 수정"""
    result = PromptTemplateService.update(template_id, template)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template with id '{template_id}' not found",
        )
    return result


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt_template(template_id: str):
    """프롬프트 템플릿 삭제"""
    if not PromptTemplateService.delete(template_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template with id '{template_id}' not found",
        )


