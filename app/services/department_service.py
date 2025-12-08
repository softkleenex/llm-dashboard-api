from typing import List, Optional
import uuid
from app.db.connection import get_cursor
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentWithManager,
)
from app.schemas.user import UserRole


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
        department_id = str(uuid.uuid4())
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO DEPARTMENT (department_id, department_name)
                VALUES (:1, :2)
            """,
                [department_id, department.department_name],
            )
            return DepartmentResponse(
                department_id=department_id,
                department_name=department.department_name,
                manager_user_id=None,
            )

    @staticmethod
    def update(department_id: str, department: DepartmentUpdate) -> Optional[DepartmentResponse]:
        """
        부서 수정
        동시성 제어: SELECT FOR UPDATE를 사용하여 Lost Update 문제를 방지합니다.
        관리자 설정 시 검증: 해당 user_id가 이미 다른 부서의 관리자로 설정되어 있는지 확인합니다.
        """
        with get_cursor() as cursor:
            # 동시성 제어: SELECT FOR UPDATE로 행 레벨 잠금 획득
            # 다른 트랜잭션이 동시에 같은 부서를 수정하는 것을 방지
            cursor.execute(
                "SELECT department_name, manager_user_id FROM DEPARTMENT WHERE department_id = :1 FOR UPDATE",
                [department_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            new_name = department.department_name if department.department_name else row[0]
            current_manager = row[1]

            # manager_user_id가 요청에 없거나 빈 문자열이면 기존 값 유지
            if department.manager_user_id in (None, ""):
                new_manager = current_manager
            else:
                new_manager = department.manager_user_id

                # 동시성 제어: 관리자 설정 시 USER 행을 잠금하여 검증 및 업데이트를 원자적으로 수행
                cursor.execute(
                    """
                    SELECT user_id, role, department_id FROM "USER" WHERE user_id = :1 FOR UPDATE
                    """,
                    [new_manager],
                )
                user_row = cursor.fetchone()
                if not user_row:
                    raise ValueError(f"User with id '{new_manager}' not found")

                # 해당 user_id가 이미 다른 부서의 manager_user_id로 설정되어 있는지 확인
                cursor.execute(
                    """
                    SELECT department_id FROM DEPARTMENT 
                    WHERE manager_user_id = :1 AND department_id != :2
                    """,
                    [new_manager, department_id],
                )
                existing_dept = cursor.fetchone()
                if existing_dept:
                    raise ValueError(
                        f"User '{new_manager}' is already a manager of another department (department_id: {existing_dept[0]})"
                    )

                # 관리자로 설정할 때 해당 user의 부서 소속을 현재 부서로 변경하고 역할을 TEAM_LEADER로 변경
                cursor.execute(
                    """
                    UPDATE "USER"
                    SET department_id = :1, role = :2
                    WHERE user_id = :3
                    """,
                    [department_id, UserRole.TEAM_LEADER.value, new_manager],
                )

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
