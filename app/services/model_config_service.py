import uuid
from typing import List, Optional
from app.db.connection import get_cursor
from app.schemas.model_config import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigResponse,
)


class ModelConfigService:
    @staticmethod
    def get_all() -> List[ModelConfigResponse]:
        """모든 모델 설정 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT config_id, config_name, max_tokens, temperature, top_p, top_k, created_at, model_id
                FROM MODEL_CONFIG
                ORDER BY config_id
            """
            )
            rows = cursor.fetchall()
            return [
                ModelConfigResponse(
                    config_id=row[0],
                    config_name=row[1],
                    max_tokens=row[2],
                    temperature=row[3],
                    top_p=row[4],
                    top_k=row[5],
                    model_id=row[7],
                    created_at=row[6],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(config_id: str) -> Optional[ModelConfigResponse]:
        """설정 ID로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT config_id, config_name, max_tokens, temperature, top_p, top_k, created_at, model_id
                FROM MODEL_CONFIG
                WHERE config_id = :1
            """,
                [config_id],
            )
            row = cursor.fetchone()
            if row:
                return ModelConfigResponse(
                    config_id=row[0],
                    config_name=row[1],
                    max_tokens=row[2],
                    temperature=row[3],
                    top_p=row[4],
                    top_k=row[5],
                    model_id=row[7],
                    created_at=row[6],
                )
            return None

    @staticmethod
    def create(config: ModelConfigCreate) -> ModelConfigResponse:
        """모델 설정 추가"""
        config_id = str(uuid.uuid4())
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO MODEL_CONFIG (
                    config_id, config_name, max_tokens, temperature, top_p, top_k, model_id
                )
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """,
                [
                    config_id,
                    config.config_name,
                    config.max_tokens,
                    config.temperature,
                    config.top_p,
                    config.top_k,
                    config.model_id,
                ],
            )
            # created_at은 DB 기본값 사용
            return ModelConfigResponse(
                config_id=config_id,
                config_name=config.config_name,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k,
                model_id=config.model_id,
                created_at=None,
            )

    @staticmethod
    def update(
        config_id: str, config: ModelConfigUpdate
    ) -> Optional[ModelConfigResponse]:
        """
        모델 설정 수정
        동시성 제어: SELECT FOR UPDATE를 사용하여 Lost Update 문제를 방지합니다.
        """
        with get_cursor() as cursor:
            # 동시성 제어: SELECT FOR UPDATE로 행 레벨 잠금 획득
            # 다른 트랜잭션이 동시에 같은 설정을 수정하는 것을 방지
            cursor.execute(
                """
                SELECT config_name, max_tokens, temperature, top_p, top_k, created_at, model_id
                FROM MODEL_CONFIG
                WHERE config_id = :1 FOR UPDATE
            """,
                [config_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            (
                current_name,
                current_max_tokens,
                current_temperature,
                current_top_p,
                current_top_k,
                created_at,
                model_id,
            ) = row

            new_name = config.config_name or current_name
            new_max_tokens = (
                config.max_tokens if config.max_tokens is not None else current_max_tokens
            )
            new_temperature = (
                config.temperature
                if config.temperature is not None
                else current_temperature
            )
            new_top_p = config.top_p if config.top_p is not None else current_top_p
            new_top_k = config.top_k if config.top_k is not None else current_top_k

            cursor.execute(
                """
                UPDATE MODEL_CONFIG
                SET config_name = :1, max_tokens = :2, temperature = :3, top_p = :4, top_k = :5
                WHERE config_id = :6
            """,
                [
                    new_name,
                    new_max_tokens,
                    new_temperature,
                    new_top_p,
                    new_top_k,
                    config_id,
                ],
            )

            return ModelConfigResponse(
                config_id=config_id,
                config_name=new_name,
                max_tokens=new_max_tokens,
                temperature=new_temperature,
                top_p=new_top_p,
                top_k=new_top_k,
                model_id=model_id,
                created_at=created_at,
            )

    @staticmethod
    def delete(config_id: str) -> bool:
        """모델 설정 삭제"""
        with get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM MODEL_CONFIG WHERE config_id = :1", [config_id]
            )
            return cursor.rowcount > 0

