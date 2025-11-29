from typing import List, Optional
from app.db.connection import get_cursor
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithDepartment,
    UserByRole,
    UserBasic,
    UserWithSessionCount,
    UserIdOnly,
)


class UserService:
    @staticmethod
    def get_all() -> List[UserWithDepartment]:
        """모든 사용자 조회 (부서 정보 포함)"""
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT u.user_id, u.user_name, u.user_email, u.role,
                       u.is_active, u.last_login, u.department_id, d.department_name
                FROM "USER" u
                LEFT JOIN DEPARTMENT d ON u.department_id = d.department_id
                ORDER BY u.user_id
            """)
            rows = cursor.fetchall()
            return [
                UserWithDepartment(
                    user_id=row[0],
                    user_name=row[1],
                    user_email=row[2],
                    role=row[3],
                    is_active=row[4],
                    last_login=row[5],
                    department_id=row[6],
                    department_name=row[7],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(user_id: str) -> Optional[UserWithDepartment]:
        """사용자 ID로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT u.user_id, u.user_name, u.user_email, u.role,
                       u.is_active, u.last_login, u.department_id, d.department_name
                FROM "USER" u
                LEFT JOIN DEPARTMENT d ON u.department_id = d.department_id
                WHERE u.user_id = :1
            """,
                [user_id],
            )
            row = cursor.fetchone()
            if row:
                return UserWithDepartment(
                    user_id=row[0],
                    user_name=row[1],
                    user_email=row[2],
                    role=row[3],
                    is_active=row[4],
                    last_login=row[5],
                    department_id=row[6],
                    department_name=row[7],
                )
            return None

    @staticmethod
    def get_by_department(department_id: str) -> List[UserWithDepartment]:
        """부서별 사용자 목록 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT u.user_id, u.user_name, u.user_email, u.role,
                       u.is_active, u.last_login, u.department_id, d.department_name
                FROM "USER" u
                LEFT JOIN DEPARTMENT d ON u.department_id = d.department_id
                WHERE u.department_id = :1
                ORDER BY u.user_id
            """,
                [department_id],
            )
            rows = cursor.fetchall()
            return [
                UserWithDepartment(
                    user_id=row[0],
                    user_name=row[1],
                    user_email=row[2],
                    role=row[3],
                    is_active=row[4],
                    last_login=row[5],
                    department_id=row[6],
                    department_name=row[7],
                )
                for row in rows
            ]

    @staticmethod
    def create(user: UserCreate) -> UserResponse:
        """사용자 추가"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO "USER" (user_id, user_name, user_email, password, role, is_active, department_id)
                VALUES (:1, :2, :3, :4, :5, 'Y', :6)
            """,
                [
                    user.user_id,
                    user.user_name,
                    user.user_email,
                    user.password,
                    user.role.value,
                    user.department_id,
                ],
            )
            return UserResponse(
                user_id=user.user_id,
                user_name=user.user_name,
                user_email=user.user_email,
                role=user.role,
                is_active="Y",
                last_login=None,
                department_id=user.department_id,
            )

    @staticmethod
    def update(user_id: str, user: UserUpdate) -> Optional[UserResponse]:
        """사용자 수정"""
        with get_cursor() as cursor:
            # 현재 데이터 조회
            cursor.execute(
                """
                SELECT user_name, user_email, password, role, is_active, last_login, department_id
                FROM "USER" WHERE user_id = :1
            """,
                [user_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            new_name = user.user_name if user.user_name else row[0]
            new_email = user.user_email if user.user_email else row[1]
            new_password = user.password if user.password else row[2]
            new_role = user.role.value if user.role else row[3]
            new_active = user.is_active if user.is_active else row[4]
            new_dept = user.department_id if user.department_id else row[6]

            cursor.execute(
                """
                UPDATE "USER"
                SET user_name = :1, user_email = :2, password = :3,
                    role = :4, is_active = :5, department_id = :6
                WHERE user_id = :7
            """,
                [new_name, new_email, new_password, new_role, new_active, new_dept, user_id],
            )
            return UserResponse(
                user_id=user_id,
                user_name=new_name,
                user_email=new_email,
                role=new_role,
                is_active=new_active,
                last_login=row[5],
                department_id=new_dept,
            )

    @staticmethod
    def delete(user_id: str) -> bool:
        """사용자 삭제"""
        with get_cursor() as cursor:
            cursor.execute('DELETE FROM "USER" WHERE user_id = :1', [user_id])
            return cursor.rowcount > 0

    # ========================================
    # 통계/분석 쿼리 (Phase 3 Mainmenu 1)
    # ========================================

    @staticmethod
    def get_by_role(role: str) -> List[UserByRole]:
        """Q11: 특정 역할 사용자 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, user_name, user_email
                FROM "USER"
                WHERE role = :1
                ORDER BY user_id
            """,
                [role],
            )
            rows = cursor.fetchall()
            return [
                UserByRole(user_id=row[0], user_name=row[1], user_email=row[2])
                for row in rows
            ]

    @staticmethod
    def get_by_department_name(department_name: str) -> List[UserBasic]:
        """Q14: 특정 부서명으로 유저 조회 (서브쿼리 사용)"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, user_name
                FROM "USER"
                WHERE department_id = (
                    SELECT department_id FROM DEPARTMENT WHERE department_name = :1
                )
                ORDER BY user_id
            """,
                [department_name],
            )
            rows = cursor.fetchall()
            return [UserBasic(user_id=row[0], user_name=row[1]) for row in rows]

    @staticmethod
    def get_users_with_active_sessions(session_status: Optional[str] = None) -> List[UserBasic]:
        """Q15: 특정 상태 세션을 보유한 유저 조회 (EXISTS 서브쿼리)"""
        with get_cursor() as cursor:
            if session_status:
                cursor.execute(
                    """
                    SELECT U.user_id, U.user_name
                    FROM "USER" U
                    WHERE EXISTS (
                        SELECT 1 FROM SESSIONS S
                        WHERE S.user_id = U.user_id
                        AND S.status = :1
                    )
                    ORDER BY U.user_id
                """,
                    [session_status],
                )
            else:
                cursor.execute(
                    """
                    SELECT U.user_id, U.user_name
                    FROM "USER" U
                    WHERE EXISTS (
                        SELECT 1 FROM SESSIONS S
                        WHERE S.user_id = U.user_id
                    )
                    ORDER BY U.user_id
                """
                )
            rows = cursor.fetchall()
            return [UserBasic(user_id=row[0], user_name=row[1]) for row in rows]

    @staticmethod
    def get_users_with_min_sessions(min_count: int = 5) -> List[UserWithSessionCount]:
        """Q17: 최소 세션 수 이상 보유 유저 조회 (인라인 뷰)"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT U.user_id, U.user_name, S.session_count
                FROM (
                    SELECT user_id, COUNT(*) AS session_count
                    FROM SESSIONS
                    GROUP BY user_id
                ) S, "USER" U
                WHERE S.user_id = U.user_id
                AND S.session_count >= :1
                ORDER BY S.session_count DESC
            """,
                [min_count],
            )
            rows = cursor.fetchall()
            return [
                UserWithSessionCount(user_id=row[0], user_name=row[1], session_count=row[2])
                for row in rows
            ]

    @staticmethod
    def get_role_users_and_managers(role: Optional[str] = None) -> List[UserIdOnly]:
        """Q20: 특정 역할 유저와 부서 관리자 통합 조회 (UNION)"""
        with get_cursor() as cursor:
            if role:
                cursor.execute(
                    """
                    SELECT user_id FROM "USER" WHERE role = :1
                    UNION
                    SELECT manager_user_id FROM DEPARTMENT WHERE manager_user_id IS NOT NULL
                """,
                    [role],
                )
            else:
                cursor.execute(
                    """
                    SELECT user_id FROM "USER"
                    UNION
                    SELECT manager_user_id FROM DEPARTMENT WHERE manager_user_id IS NOT NULL
                """
                )
            rows = cursor.fetchall()
            return [UserIdOnly(user_id=row[0]) for row in rows]
