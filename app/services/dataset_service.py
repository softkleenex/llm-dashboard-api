from typing import List, Optional
from app.db.connection import get_cursor
from app.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    LearningType,
    DatasetUsedInDeployment,
)


class DatasetService:
    @staticmethod
    def _read_lob(value):
        """Oracle LOB 타입을 문자열로 변환 (아닐 경우 그대로 반환)"""
        if value is None:
            return None
        read_method = getattr(value, "read", None)
        if callable(read_method):
            return read_method()
        return value

    @staticmethod
    def get_all() -> List[DatasetResponse]:
        """모든 데이터셋 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT dataset_id, learning_type, description, s3_path, created_at
                FROM DATASET
                ORDER BY dataset_id
            """
            )
            rows = cursor.fetchall()
            return [
                DatasetResponse(
                    dataset_id=row[0],
                    learning_type=LearningType(row[1]),
                    description=DatasetService._read_lob(row[2]),
                    s3_path=row[3],
                    created_at=row[4],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(dataset_id: str) -> Optional[DatasetResponse]:
        """데이터셋 ID로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT dataset_id, learning_type, description, s3_path, created_at
                FROM DATASET
                WHERE dataset_id = :1
            """,
                [dataset_id],
            )
            row = cursor.fetchone()
            if row:
                return DatasetResponse(
                    dataset_id=row[0],
                    learning_type=LearningType(row[1]),
                    description=DatasetService._read_lob(row[2]),
                    s3_path=row[3],
                    created_at=row[4],
                )
            return None

    @staticmethod
    def create(dataset: DatasetCreate) -> DatasetResponse:
        """데이터셋 추가"""
        import uuid
        dataset_id = str(uuid.uuid4())
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO DATASET (dataset_id, learning_type, description, s3_path)
                VALUES (:1, :2, :3, :4)
            """,
                [
                    dataset_id,
                    dataset.learning_type.value,
                    dataset.description,
                    dataset.s3_path,
                ],
            )
            # created_at은 DB 기본값 사용
            return DatasetResponse(
                dataset_id=dataset_id,
                learning_type=dataset.learning_type,
                description=dataset.description,
                s3_path=dataset.s3_path,
                created_at=None,
            )

    @staticmethod
    def update(dataset_id: str, dataset: DatasetUpdate) -> Optional[DatasetResponse]:
        """데이터셋 수정"""
        with get_cursor() as cursor:
            # 현재 데이터 조회
            cursor.execute(
                """
                SELECT learning_type, description, s3_path, created_at
                FROM DATASET
                WHERE dataset_id = :1
            """,
                [dataset_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            current_learning_type, current_description, current_s3_path, created_at = row
            current_description = DatasetService._read_lob(current_description)

            new_learning_type = (
                dataset.learning_type.value if dataset.learning_type else current_learning_type
            )
            if dataset.description is None:
                new_description = current_description
            elif dataset.description == "":
                new_description = None
            else:
                new_description = dataset.description
            new_s3_path = dataset.s3_path or current_s3_path

            cursor.execute(
                """
                UPDATE DATASET
                SET learning_type = :1, description = :2, s3_path = :3
                WHERE dataset_id = :4
            """,
                [new_learning_type, new_description, new_s3_path, dataset_id],
            )

            return DatasetResponse(
                dataset_id=dataset_id,
                learning_type=LearningType(new_learning_type),
                description=new_description,
                s3_path=new_s3_path,
                created_at=created_at,
            )

    @staticmethod
    def delete(dataset_id: str) -> bool:
        """데이터셋 삭제"""
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM DATASET WHERE dataset_id = :1", [dataset_id])
            return cursor.rowcount > 0

    @staticmethod
    def search(
        dataset_name: Optional[str] = None,
        learning_type: Optional[LearningType] = None,
    ) -> List[DatasetResponse]:
        """데이터셋 검색: dataset_id(이름) 및 learning_type으로 필터링"""
        with get_cursor() as cursor:
            sql = """
                SELECT dataset_id, learning_type, description, s3_path, created_at
                FROM DATASET
                WHERE 1=1
            """
            params: list = []
            param_idx = 1

            if dataset_name:
                sql += f" AND LOWER(dataset_id) LIKE :{param_idx}"
                params.append(f"%{dataset_name.lower()}%")
                param_idx += 1

            if learning_type:
                sql += f" AND learning_type = :{param_idx}"
                params.append(learning_type.value)
                param_idx += 1

            sql += " ORDER BY dataset_id"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                DatasetResponse(
                    dataset_id=row[0],
                    learning_type=LearningType(row[1]),
                    description=DatasetService._read_lob(row[2]),
                    s3_path=row[3],
                    created_at=row[4],
                )
                for row in rows
            ]

    # ==========================
    # 통계/분석 쿼리 (for Phase 3 Mapping)
    # ==========================

    @staticmethod
    def query5_datasets_used_in_deployments() -> List[DatasetUsedInDeployment]:
        """Q5: 배포에 사용된 데이터셋"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT dataset_id, learning_type, description, created_at
                FROM DATASET DS
                WHERE EXISTS (
                    SELECT 1 FROM DEPLOYMENTS D
                    WHERE D.dataset_id = DS.dataset_id
                )
                ORDER BY dataset_id
            """
            )
            rows = cursor.fetchall()
            return [
                DatasetUsedInDeployment(
                    dataset_id=row[0],
                    learning_type=LearningType(row[1]),
                    description=DatasetService._read_lob(row[2]),
                    created_at=row[3],
                )
                for row in rows
            ]

