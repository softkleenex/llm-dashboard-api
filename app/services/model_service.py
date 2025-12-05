from typing import List, Optional
from app.db.connection import get_cursor
from app.schemas.model import (
    ModelCreate,
    ModelUpdate,
    ModelResponse,
    ModelConfigDeploymentCount,
    ModelAvgTemperatureStats,
    UndeployedModel,
)


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
        """
        모델 수정
        동시성 제어: SELECT FOR UPDATE를 사용하여 Lost Update 문제를 방지합니다.
        """
        with get_cursor() as cursor:
            # 동시성 제어: SELECT FOR UPDATE로 행 레벨 잠금 획득
            # 다른 트랜잭션이 동시에 같은 모델을 수정하는 것을 방지
            cursor.execute(
                """
                SELECT model_name, model_type
                FROM MODEL
                WHERE model_id = :1 FOR UPDATE
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

    # ==========================
    # 통계/분석 쿼리 (for Phase 3 Mapping)
    # ==========================

    @staticmethod
    def query3_model_config_and_deployment_count() -> List[ModelConfigDeploymentCount]:
        """Q3: 모델 설정 및 배포 수"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT M.model_name,
                       M.model_type,
                       COUNT(DISTINCT MC.config_id) AS config_count,
                       COUNT(DISTINCT D.deployment_id) AS deployment_count
                FROM MODEL M, MODEL_CONFIG MC, DEPLOYMENTS D
                WHERE M.model_id = MC.model_id
                  AND M.model_id = D.model_id
                GROUP BY M.model_name, M.model_type
                ORDER BY M.model_name
            """
            )
            rows = cursor.fetchall()
            return [
                ModelConfigDeploymentCount(
                    model_name=row[0],
                    model_type=row[1],
                    config_count=row[2],
                    deployment_count=row[3],
                )
                for row in rows
            ]

    @staticmethod
    def query7_model_avg_temperature_and_deployment_count() -> List[ModelAvgTemperatureStats]:
        """Q7: 모델 평균 Temperature 및 배포 수"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT M.model_name,
                       AVG_CONFIG.avg_temperature,
                       AVG_CONFIG.config_count,
                       DEPLOY_COUNT.deployment_count
                FROM MODEL M,
                     (SELECT model_id,
                             AVG(temperature) AS avg_temperature,
                             COUNT(*) AS config_count
                      FROM MODEL_CONFIG
                      GROUP BY model_id) AVG_CONFIG,
                     (SELECT model_id,
                             COUNT(*) AS deployment_count
                      FROM DEPLOYMENTS
                      GROUP BY model_id) DEPLOY_COUNT
                WHERE M.model_id = AVG_CONFIG.model_id
                  AND M.model_id = DEPLOY_COUNT.model_id
                ORDER BY M.model_name
            """
            )
            rows = cursor.fetchall()
            return [
                ModelAvgTemperatureStats(
                    model_name=row[0],
                    avg_temperature=float(row[1]),
                    config_count=row[2],
                    deployment_count=row[3],
                )
                for row in rows
            ]

    @staticmethod
    def query10_undeployed_models() -> List[UndeployedModel]:
        """Q10: 배포되지 않은 모델"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT model_id, model_name, model_type
                FROM MODEL
                MINUS
                SELECT M.model_id, M.model_name, M.model_type
                FROM MODEL M, DEPLOYMENTS D
                WHERE M.model_id = D.model_id
                ORDER BY model_id
            """
            )
            rows = cursor.fetchall()
            return [
                UndeployedModel(
                    model_id=row[0],
                    model_name=row[1],
                    model_type=row[2],
                )
                for row in rows
            ]

