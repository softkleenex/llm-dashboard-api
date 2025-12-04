from typing import List, Optional
from app.db.connection import get_cursor
from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse


class ModelService:
    @staticmethod
    def get_all() -> List[ModelResponse]:
        """모든 모델 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT model_id, model_name, model_type
                FROM MODEL
                ORDER BY model_id
            """
            )
            rows = cursor.fetchall()
            return [
                ModelResponse(
                    model_id=row[0],
                    model_name=row[1],
                    model_type=row[2],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(model_id: str) -> Optional[ModelResponse]:
        """모델 ID로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT model_id, model_name, model_type
                FROM MODEL
                WHERE model_id = :1
            """,
                [model_id],
            )
            row = cursor.fetchone()
            if row:
                return ModelResponse(
                    model_id=row[0],
                    model_name=row[1],
                    model_type=row[2],
                )
            return None

    @staticmethod
    def create(model: ModelCreate) -> ModelResponse:
        """모델 추가"""
        import uuid
        model_id = str(uuid.uuid4())
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO MODEL (model_id, model_name, model_type)
                VALUES (:1, :2, :3)
            """,
                [
                    model_id,
                    model.model_name,
                    model.model_type,
                ],
            )
            return ModelResponse(
                model_id=model_id,
                model_name=model.model_name,
                model_type=model.model_type,
            )

    @staticmethod
    def update(model_id: str, model: ModelUpdate) -> Optional[ModelResponse]:
        """모델 수정"""
        with get_cursor() as cursor:
            # 현재 데이터 조회
            cursor.execute(
                """
                SELECT model_name, model_type
                FROM MODEL
                WHERE model_id = :1
            """,
                [model_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            current_name, current_type = row

            new_name = model.model_name or current_name
            new_type = model.model_type or current_type

            cursor.execute(
                """
                UPDATE MODEL
                SET model_name = :1, model_type = :2
                WHERE model_id = :3
            """,
                [new_name, new_type, model_id],
            )

            return ModelResponse(
                model_id=model_id,
                model_name=new_name,
                model_type=new_type,
            )

    @staticmethod
    def delete(model_id: str) -> bool:
        """모델 삭제"""
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM MODEL WHERE model_id = :1", [model_id])
            return cursor.rowcount > 0

