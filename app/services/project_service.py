import uuid
from typing import List, Optional

from app.db.connection import get_cursor
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithCreatorAndDepartment,
    ProjectsByDepartment,
    ProjectIdName,
)


class ProjectService:
    @staticmethod
    def _read_lob(value):
        """Oracle LOB 타입을 문자열로 변환 (아닐 경우 그대로 반환)"""
        if value is None:
            return None
        # oracledb.LOB 객체는 read() 메서드로 내용을 가져올 수 있음
        read_method = getattr(value, "read", None)
        if callable(read_method):
            return read_method()
        return value

    @staticmethod
    def get_all() -> List[ProjectResponse]:
        """모든 프로젝트 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT project_id, project_name, description,
                       created_at, creator_user_id, department_id
                FROM PROJECT
                ORDER BY project_id
            """
            )
            rows = cursor.fetchall()
            return [
                ProjectResponse(
                    project_id=row[0],
                    project_name=row[1],
                    description=ProjectService._read_lob(row[2]),
                    created_at=row[3],
                    creator_user_id=row[4],
                    department_id=row[5],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(project_id: str) -> Optional[ProjectResponse]:
        """프로젝트 ID로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT project_id, project_name, description,
                       created_at, creator_user_id, department_id
                FROM PROJECT
                WHERE project_id = :1
            """,
                [project_id],
            )
            row = cursor.fetchone()
            if row:
                return ProjectResponse(
                    project_id=row[0],
                    project_name=row[1],
                    description=ProjectService._read_lob(row[2]),
                    created_at=row[3],
                    creator_user_id=row[4],
                    department_id=row[5],
                )
            return None

    @staticmethod
    def get_by_department(department_id: str) -> List[ProjectResponse]:
        """부서별 프로젝트 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT project_id, project_name, description,
                       created_at, creator_user_id, department_id
                FROM PROJECT
                WHERE department_id = :1
                ORDER BY project_id
            """,
                [department_id],
            )
            rows = cursor.fetchall()
            return [
                ProjectResponse(
                    project_id=row[0],
                    project_name=row[1],
                    description=ProjectService._read_lob(row[2]),
                    created_at=row[3],
                    creator_user_id=row[4],
                    department_id=row[5],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_creator(user_id: str) -> List[ProjectResponse]:
        """사용자별 생성 프로젝트 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT project_id, project_name, description,
                       created_at, creator_user_id, department_id
                FROM PROJECT
                WHERE creator_user_id = :1
                ORDER BY project_id
            """,
                [user_id],
            )
            rows = cursor.fetchall()
            return [
                ProjectResponse(
                    project_id=row[0],
                    project_name=row[1],
                    description=ProjectService._read_lob(row[2]),
                    created_at=row[3],
                    creator_user_id=row[4],
                    department_id=row[5],
                )
                for row in rows
            ]

    @staticmethod
    def search(
        department_name: Optional[str] = None,
        project_name: Optional[str] = None,
        creator_user_name: Optional[str] = None,
    ) -> List[ProjectResponse]:
        """부서명, 프로젝트명, 생성자명으로 프로젝트 검색 (자연어 검색)"""
        with get_cursor() as cursor:
            sql = """
                SELECT P.project_id, P.project_name, P.description,
                       P.created_at, P.creator_user_id, P.department_id
                FROM PROJECT P
                LEFT JOIN DEPARTMENT D ON P.department_id = D.department_id
                LEFT JOIN "USER" U ON P.creator_user_id = U.user_id
                WHERE 1=1
            """
            params: list = []
            param_idx = 1

            if department_name:
                sql += f" AND LOWER(D.department_name) LIKE :{param_idx}"
                params.append(f"%{department_name.lower()}%")
                param_idx += 1

            if project_name:
                sql += f" AND LOWER(P.project_name) LIKE :{param_idx}"
                params.append(f"%{project_name.lower()}%")
                param_idx += 1

            if creator_user_name:
                sql += f" AND LOWER(U.user_name) LIKE :{param_idx}"
                params.append(f"%{creator_user_name.lower()}%")
                param_idx += 1

            sql += " ORDER BY P.project_id"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                ProjectResponse(
                    project_id=row[0],
                    project_name=row[1],
                    description=ProjectService._read_lob(row[2]),
                    created_at=row[3],
                    creator_user_id=row[4],
                    department_id=row[5],
                )
                for row in rows
            ]

    @staticmethod
    def create(project: ProjectCreate) -> ProjectResponse:
        """프로젝트 추가"""
        project_id = str(uuid.uuid4())
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO PROJECT (
                    project_id, project_name, description,
                    creator_user_id, department_id
                )
                VALUES (:1, :2, :3, :4, :5)
            """,
                [
                    project_id,
                    project.project_name,
                    project.description,
                    project.creator_user_id,
                    project.department_id,
                ],
            )
            # created_at은 DB 기본값 사용
            return ProjectResponse(
                project_id=project_id,
                project_name=project.project_name,
                description=project.description,
                created_at=None,
                creator_user_id=project.creator_user_id,
                department_id=project.department_id,
            )

    @staticmethod
    def update(project_id: str, project: ProjectUpdate) -> Optional[ProjectResponse]:
        """
        프로젝트 수정
        동시성 제어: SELECT FOR UPDATE를 사용하여 Lost Update 문제를 방지합니다.
        """
        with get_cursor() as cursor:
            # 동시성 제어: SELECT FOR UPDATE로 행 레벨 잠금 획득
            # 다른 트랜잭션이 동시에 같은 프로젝트를 수정하는 것을 방지
            cursor.execute(
                """
                SELECT project_name, description,
                       created_at, creator_user_id, department_id
                FROM PROJECT
                WHERE project_id = :1 FOR UPDATE
            """,
                [project_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            current_name, current_description, created_at, creator_id, department_id = row
            current_description = ProjectService._read_lob(current_description)

            new_name = project.project_name if project.project_name else current_name
            # description은 빈 문자열이면 NULL 처리
            if project.description is None:
                new_description = current_description
            elif project.description == "":
                new_description = None
            else:
                new_description = project.description

            cursor.execute(
                """
                UPDATE PROJECT
                SET project_name = :1,
                    description = :2
                WHERE project_id = :3
            """,
                [new_name, new_description, project_id],
            )

            return ProjectResponse(
                project_id=project_id,
                project_name=new_name,
                description=new_description,
                created_at=created_at,
                creator_user_id=creator_id,
                department_id=department_id,
            )

    @staticmethod
    def delete(project_id: str) -> bool:
        """프로젝트 삭제"""
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM PROJECT WHERE project_id = :1", [project_id])
            return cursor.rowcount > 0

    # ==========================
    # 통계/분석 쿼리 (from StatisticsDAO)
    # ==========================

    @staticmethod
    def get_project_creator_and_department(
        department_name: Optional[str] = None,
        creator_user_name: Optional[str] = None,
    ) -> List[ProjectWithCreatorAndDepartment]:
        """Q12: 프로젝트 생성자와 소속 부서 정보 (동적 필터)"""
        with get_cursor() as cursor:
            sql = """
                SELECT U.user_name, D.department_name, P.project_name
                FROM "USER" U, DEPARTMENT D, PROJECT P
                WHERE U.department_id = D.department_id
                  AND P.creator_user_id = U.user_id
            """
            params: list = []
            param_idx = 1

            if department_name:
                sql += f" AND D.department_name = :{param_idx}"
                params.append(department_name)
                param_idx += 1

            if creator_user_name:
                sql += f" AND U.user_name = :{param_idx}"
                params.append(creator_user_name)
                param_idx += 1

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                ProjectWithCreatorAndDepartment(
                    user_name=row[0],
                    department_name=row[1],
                    project_name=row[2],
                )
                for row in rows
            ]

    @staticmethod
    def get_projects_by_department_stats(
        department_name: Optional[str] = None, min_count: Optional[int] = None
    ) -> List[ProjectsByDepartment]:
        """Q13: 부서별 프로젝트 수 (동적 필터)"""
        with get_cursor() as cursor:
            sql = """
                SELECT D.department_name, COUNT(P.project_id) AS project_count
                FROM DEPARTMENT D, PROJECT P
                WHERE D.department_id = P.department_id
            """
            params: list = []
            param_idx = 1

            if department_name:
                sql += f" AND D.department_name = :{param_idx}"
                params.append(department_name)
                param_idx += 1

            sql += " GROUP BY D.department_name"

            if min_count and min_count > 0:
                sql += f" HAVING COUNT(P.project_id) >= :{param_idx}"
                params.append(min_count)

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                ProjectsByDepartment(department_name=row[0], project_count=row[1])
                for row in rows
            ]

    @staticmethod
    def get_projects_with_managers() -> List[ProjectIdName]:
        """Q16: 관리자가 지정된 부서의 프로젝트"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT project_id, project_name
                FROM PROJECT
                WHERE department_id IN (
                    SELECT department_id
                    FROM DEPARTMENT
                    WHERE manager_user_id IS NOT NULL
                )
            """
            )
            rows = cursor.fetchall()
            return [
                ProjectIdName(project_id=row[0], project_name=row[1]) for row in rows
            ]


