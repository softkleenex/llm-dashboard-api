from typing import List, Optional
from app.db.connection import get_cursor
from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentResponse,
    DeploymentEnvironment,
    DeploymentStatus,
)


class DeploymentService:
    @staticmethod
    def get_all() -> List[DeploymentResponse]:
        """모든 배포 환경 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT deployment_id, server_name, gpu_count, environment, status, model_id, dataset_id
                FROM DEPLOYMENTS
                ORDER BY deployment_id
            """
            )
            rows = cursor.fetchall()
            return [
                DeploymentResponse(
                    deployment_id=row[0],
                    server_name=row[1],
                    gpu_count=row[2],
                    environment=DeploymentEnvironment(row[3]),
                    status=DeploymentStatus(row[4]),
                    model_id=row[5],
                    dataset_id=row[6],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(deployment_id: str) -> Optional[DeploymentResponse]:
        """배포 ID로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT deployment_id, server_name, gpu_count, environment, status, model_id, dataset_id
                FROM DEPLOYMENTS
                WHERE deployment_id = :1
            """,
                [deployment_id],
            )
            row = cursor.fetchone()
            if row:
                return DeploymentResponse(
                    deployment_id=row[0],
                    server_name=row[1],
                    gpu_count=row[2],
                    environment=DeploymentEnvironment(row[3]),
                    status=DeploymentStatus(row[4]),
                    model_id=row[5],
                    dataset_id=row[6],
                )
            return None

    @staticmethod
    def get_by_model(model_id: str) -> List[DeploymentResponse]:
        """모델별 배포 환경 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT deployment_id, server_name, gpu_count, environment, status, model_id, dataset_id
                FROM DEPLOYMENTS
                WHERE model_id = :1
                ORDER BY deployment_id
            """,
                [model_id],
            )
            rows = cursor.fetchall()
            return [
                DeploymentResponse(
                    deployment_id=row[0],
                    server_name=row[1],
                    gpu_count=row[2],
                    environment=DeploymentEnvironment(row[3]),
                    status=DeploymentStatus(row[4]),
                    model_id=row[5],
                    dataset_id=row[6],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_environment(environment: DeploymentEnvironment) -> List[DeploymentResponse]:
        """환경별 배포 환경 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT deployment_id, server_name, gpu_count, environment, status, model_id, dataset_id
                FROM DEPLOYMENTS
                WHERE environment = :1
                ORDER BY deployment_id
            """,
                [environment.value],
            )
            rows = cursor.fetchall()
            return [
                DeploymentResponse(
                    deployment_id=row[0],
                    server_name=row[1],
                    gpu_count=row[2],
                    environment=DeploymentEnvironment(row[3]),
                    status=DeploymentStatus(row[4]),
                    model_id=row[5],
                    dataset_id=row[6],
                )
                for row in rows
            ]

    @staticmethod
    def create(deployment: DeploymentCreate) -> DeploymentResponse:
        """배포 환경 추가"""
        import uuid
        deployment_id = str(uuid.uuid4())
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO DEPLOYMENTS (
                    deployment_id, server_name, gpu_count, environment, status, model_id, dataset_id
                )
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """,
                [
                    deployment_id,
                    deployment.server_name,
                    deployment.gpu_count,
                    deployment.environment.value,
                    deployment.status.value,
                    deployment.model_id,
                    deployment.dataset_id,
                ],
            )
            return DeploymentResponse(
                deployment_id=deployment_id,
                server_name=deployment.server_name,
                gpu_count=deployment.gpu_count,
                environment=deployment.environment,
                status=deployment.status,
                model_id=deployment.model_id,
                dataset_id=deployment.dataset_id,
            )

    @staticmethod
    def update(
        deployment_id: str, deployment: DeploymentUpdate
    ) -> Optional[DeploymentResponse]:
        """배포 환경 수정"""
        with get_cursor() as cursor:
            # 현재 데이터 조회
            cursor.execute(
                """
                SELECT server_name, gpu_count, environment, status, model_id, dataset_id
                FROM DEPLOYMENTS
                WHERE deployment_id = :1
            """,
                [deployment_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            (
                current_server_name,
                current_gpu_count,
                current_environment,
                current_status,
                model_id,
                current_dataset_id,
            ) = row

            new_server_name = deployment.server_name or current_server_name
            new_gpu_count = deployment.gpu_count if deployment.gpu_count is not None else current_gpu_count
            new_environment = (
                deployment.environment.value if deployment.environment else current_environment
            )
            new_status = deployment.status.value if deployment.status else current_status
            new_dataset_id = deployment.dataset_id if deployment.dataset_id is not None else current_dataset_id

            cursor.execute(
                """
                UPDATE DEPLOYMENTS
                SET server_name = :1, gpu_count = :2, environment = :3, status = :4, dataset_id = :5
                WHERE deployment_id = :6
            """,
                [
                    new_server_name,
                    new_gpu_count,
                    new_environment,
                    new_status,
                    new_dataset_id,
                    deployment_id,
                ],
            )

            return DeploymentResponse(
                deployment_id=deployment_id,
                server_name=new_server_name,
                gpu_count=new_gpu_count,
                environment=DeploymentEnvironment(new_environment),
                status=DeploymentStatus(new_status),
                model_id=model_id,
                dataset_id=new_dataset_id,
            )

    @staticmethod
    def delete(deployment_id: str) -> bool:
        """배포 환경 삭제"""
        with get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM DEPLOYMENTS WHERE deployment_id = :1", [deployment_id]
            )
            return cursor.rowcount > 0

