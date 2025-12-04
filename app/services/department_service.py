from typing import List, Optional
from app.db.connection import get_cursor
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentWithManager,
)


class DepartmentService:
    @staticmethod
    def get_all() -> List[DepartmentWithManager]:
        """모든 부서 조회 (관리자 정보 포함)"""
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT d.department_id, d.department_name, d.manager_user_id, u.user_name
                FROM DEPARTMENT d
                LEFT JOIN "USER" u ON d.manager_user_id = u.user_id
                ORDER BY d.department_id
            """)
            rows = cursor.fetchall()
            return [
                DepartmentWithManager(
                    department_id=row[0],
                    department_name=row[1],
                    manager_user_id=row[2],
                    manager_name=row[3],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(department_id: str) -> Optional[DepartmentWithManager]:
        """부서 ID로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT d.department_id, d.department_name, d.manager_user_id, u.user_name
                FROM DEPARTMENT d
                LEFT JOIN "USER" u ON d.manager_user_id = u.user_id
                WHERE d.department_id = :1
            """,
                [department_id],
            )
            row = cursor.fetchone()
            if row:
                return DepartmentWithManager(
                    department_id=row[0],
                    department_name=row[1],
                    manager_user_id=row[2],
                    manager_name=row[3],
                )
            return None

    @staticmethod
    def get_by_name(department_name: str) -> Optional[DepartmentWithManager]:
        """부서 이름으로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT d.department_id, d.department_name, d.manager_user_id, u.user_name
                FROM DEPARTMENT d
                LEFT JOIN "USER" u ON d.manager_user_id = u.user_id
                WHERE d.department_name = :1
            """,
                [department_name],
            )
            row = cursor.fetchone()
            if row:
                return DepartmentWithManager(
                    department_id=row[0],
                    department_name=row[1],
                    manager_user_id=row[2],
                    manager_name=row[3],
                )
            return None

    @staticmethod
    def create(department: DepartmentCreate) -> DepartmentResponse:
        """부서 추가"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO DEPARTMENT (department_id, department_name)
                VALUES (:1, :2)
            """,
                [department.department_id, department.department_name],
            )
            return DepartmentResponse(
                department_id=department.department_id,
                department_name=department.department_name,
                manager_user_id=None,
            )

    @staticmethod
    def update(department_id: str, department: DepartmentUpdate) -> Optional[DepartmentResponse]:
        """부서 수정"""
        with get_cursor() as cursor:
            # 현재 데이터 조회
            cursor.execute(
                "SELECT department_name, manager_user_id FROM DEPARTMENT WHERE department_id = :1",
                [department_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            new_name = department.department_name if department.department_name else row[0]
            # manager_user_id가 요청에 없거나 빈 문자열이면 기존 값 유지
            if department.manager_user_id in (None, ""):
                new_manager = row[1]
            else:
                new_manager = department.manager_user_id

            cursor.execute(
                """
                UPDATE DEPARTMENT
                SET department_name = :1, manager_user_id = :2
                WHERE department_id = :3
            """,
                [new_name, new_manager, department_id],
            )
            return DepartmentResponse(
                department_id=department_id,
                department_name=new_name,
                manager_user_id=new_manager,
            )

    @staticmethod
    def delete(department_id: str) -> bool:
        """부서 삭제"""
        with get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM DEPARTMENT WHERE department_id = :1",
                [department_id],
            )
            return cursor.rowcount > 0
