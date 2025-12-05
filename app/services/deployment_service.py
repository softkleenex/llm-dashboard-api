from typing import List, Optional
from app.db.connection import get_cursor
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
    DeploymentStatusCount,
)
from app.schemas.dataset import LearningType


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
        """
        배포 환경 수정
        동시성 제어: SELECT FOR UPDATE를 사용하여 Lost Update 문제를 방지합니다.
        """
        with get_cursor() as cursor:
            # 동시성 제어: SELECT FOR UPDATE로 행 레벨 잠금 획득
            # 다른 트랜잭션이 동시에 같은 배포 환경을 수정하는 것을 방지
            cursor.execute(
                """
                SELECT server_name, gpu_count, environment, status, model_id, dataset_id
                FROM DEPLOYMENTS
                WHERE deployment_id = :1 FOR UPDATE
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

    # ==========================
    # 통계/분석 쿼리 (for Phase 3 Mapping)
    # ==========================

    @staticmethod
    def query1_active_production_deployments(
        environment: Optional[DeploymentEnvironment] = None,
        status: Optional[DeploymentStatus] = None,
    ) -> List[DeploymentBasic]:
        """Q1: 배포 환경 조회 (동적 필터)"""
        with get_cursor() as cursor:
            sql = """
                SELECT server_name, gpu_count, environment, status
                FROM DEPLOYMENTS
                WHERE 1=1
            """
            params: list = []
            param_idx = 1

            if environment:
                sql += f" AND environment = :{param_idx}"
                params.append(environment.value)
                param_idx += 1

            if status:
                sql += f" AND status = :{param_idx}"
                params.append(status.value)
                param_idx += 1

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                DeploymentBasic(
                    server_name=row[0],
                    gpu_count=row[1],
                    environment=DeploymentEnvironment(row[2]),
                    status=DeploymentStatus(row[3]),
                )
                for row in rows
            ]

    @staticmethod
    def query1_deployment_status_count() -> List[DeploymentStatusCount]:
        """
        Q1: 배포 상태별 집계 (웹 대시보드용)
        Phase 4 수정: 웹 대시보드에서 Donut Chart를 위해 상태별 배포 환경 비율이 필요함.
        기존 Q1은 개별 deployment 목록을 반환하지만, 이 메서드는 상태별 집계(count)를 반환하여
        네트워크 트래픽을 줄이고 클라이언트 연산 부담을 감소시킴.
        """
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM DEPLOYMENTS
                WHERE status IN ('활성', '오류', '유지보수')
                GROUP BY status
                ORDER BY status
            """
            )
            rows = cursor.fetchall()
            return [
                DeploymentStatusCount(
                    status=DeploymentStatus(row[0]),
                    count=row[1],
                )
                for row in rows
            ]

    @staticmethod
    def query2_model_dataset_deployment_mapping() -> List[ModelDatasetDeploymentMapping]:
        """Q2: 모델-데이터셋-배포 매핑"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT M.model_name AS model_name,
                       M.model_type AS model_type,
                       D.server_name AS server_name,
                       D.environment AS environment,
                       DS.learning_type AS dataset_learning_type,
                       DS.s3_path AS dataset_path
                FROM MODEL M, DEPLOYMENTS D, DATASET DS
                WHERE M.model_id = D.model_id
                  AND D.dataset_id = DS.dataset_id
                ORDER BY M.model_name, D.server_name
            """
            )
            rows = cursor.fetchall()
            return [
                ModelDatasetDeploymentMapping(
                    model_name=row[0],
                    model_type=row[1],
                    server_name=row[2],
                    environment=DeploymentEnvironment(row[3]),
                    dataset_learning_type=row[4],
                    dataset_path=row[5],
                )
                for row in rows
            ]

    @staticmethod
    def query4_deployments_above_avg_gpu(
        min_gpu_count: Optional[int] = None,
        use_average: Optional[bool] = None,
    ) -> List[DeploymentByGPU]:
        """Q4: GPU 수 기준 배포 조회 (동적 필터)"""
        with get_cursor() as cursor:
            sql = """
                SELECT deployment_id, server_name, gpu_count, environment
                FROM DEPLOYMENTS
                WHERE 1=1
            """
            params: list = []
            param_idx = 1

            if use_average:
                # 평균보다 많은 경우
                sql += " AND gpu_count > (SELECT AVG(gpu_count) FROM DEPLOYMENTS)"
            elif min_gpu_count is not None and min_gpu_count > 0:
                # 최소 GPU 수 지정
                sql += f" AND gpu_count >= :{param_idx}"
                params.append(min_gpu_count)
                param_idx += 1

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                DeploymentByGPU(
                    deployment_id=row[0],
                    server_name=row[1],
                    gpu_count=row[2],
                    environment=DeploymentEnvironment(row[3]),
                )
                for row in rows
            ]

    @staticmethod
    def query8_model_config_deployment_by_gpu(
        order_by: Optional[str] = None,
        order_dir: Optional[str] = None,
    ) -> List[ModelConfigDeployment]:
        """Q8: 모델-설정-배포 관계 (동적 정렬)"""
        with get_cursor() as cursor:
            # 화이트리스트로 안전한 컬럼만 허용 및 테이블 매핑
            column_mapping = {
                "gpu_count": "D.gpu_count",
                "temperature": "MC.temperature",
                "max_tokens": "MC.max_tokens",
                "model_name": "M.model_name",
            }
            safe_order_by = "D.gpu_count"  # 기본값

            if order_by:
                for col, table_col in column_mapping.items():
                    if col.lower() == order_by.lower():
                        safe_order_by = table_col
                        break

            safe_order_dir = "DESC"
            if order_dir and order_dir.upper() == "ASC":
                safe_order_dir = "ASC"

            # ORDER BY는 파라미터 바인딩 불가능하므로 문자열 연결 사용
            sql = f"""
                SELECT M.model_name,
                       MC.config_name,
                       MC.max_tokens,
                       MC.temperature,
                       D.server_name,
                       D.gpu_count,
                       D.environment
                FROM MODEL M, MODEL_CONFIG MC, DEPLOYMENTS D
                WHERE M.model_id = MC.model_id
                  AND M.model_id = D.model_id
                ORDER BY {safe_order_by} {safe_order_dir}, M.model_name ASC
            """

            cursor.execute(sql)
            rows = cursor.fetchall()
            return [
                ModelConfigDeployment(
                    model_name=row[0],
                    config_name=row[1],
                    max_tokens=row[2],
                    temperature=row[3],
                    server_name=row[4],
                    gpu_count=row[5],
                    environment=DeploymentEnvironment(row[6]),
                )
                for row in rows
            ]

    @staticmethod
    def query9_environment_avg_gpu_and_deployment_count(
        environment: Optional[DeploymentEnvironment] = None,
        min_avg_gpu: Optional[float] = None,
    ) -> List[EnvironmentStats]:
        """
        Q9: 환경별 총 GPU/배포 수 (동적 필터)
        Phase 4 수정: 웹 대시보드에서 Bar Chart를 위해 환경별 할당된 총 GPU 개수 비교가 필요함.
        기존 AVG(D.gpu_count)를 SUM(D.gpu_count)로 변경하여 각 환경에 할당된 총 GPU 리소스를 정확히 집계.
        이를 통해 클라이언트에서 추가 연산 없이 바로 차트 데이터로 활용 가능.
        """
        with get_cursor() as cursor:
            sql = """
                SELECT D.environment,
                       COUNT(DISTINCT D.deployment_id) AS deployment_count,
                       SUM(D.gpu_count) AS total_gpu_count,
                       COUNT(DISTINCT M.model_id) AS unique_models
                FROM DEPLOYMENTS D, MODEL M
                WHERE D.model_id = M.model_id
            """
            params: list = []
            param_idx = 1

            if environment:
                sql += f" AND D.environment = :{param_idx}"
                params.append(environment.value)
                param_idx += 1

            sql += " GROUP BY D.environment"

            # Phase 3: SUM을 사용하므로 HAVING 절도 SUM 기준으로 변경
            if min_avg_gpu is not None and min_avg_gpu > 0:
                sql += f" HAVING SUM(D.gpu_count) >= :{param_idx}"
                params.append(min_avg_gpu)
                param_idx += 1

            sql += " ORDER BY total_gpu_count DESC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                EnvironmentStats(
                    environment=DeploymentEnvironment(row[0]),
                    deployment_count=row[1],
                    total_gpu_count=int(row[2]),  # Phase 3: float에서 int로 변경 (SUM 결과는 정수)
                    unique_models=row[3],
                )
                for row in rows
            ]

