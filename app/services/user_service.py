from typing import List, Optional
from oracledb import IntegrityError
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
    UserRole,
    UserRoleDistribution,
)
from app.schemas.session import SessionStatus


class UserService:
    @staticmethod
    def get_all(
        user_name: Optional[str] = None,
        role: Optional[str] = None,
    ) -> List[UserWithDepartment]:
        """모든 사용자 조회 (부서 정보 포함, 유저 이름 및 역할 필터링 가능)"""
        with get_cursor() as cursor:
            sql = """
                SELECT u.user_id, u.user_name, u.user_email, u.role,
                       u.is_active, u.last_login, u.department_id, d.department_name
                FROM "USER" u
                LEFT JOIN DEPARTMENT d ON u.department_id = d.department_id
                WHERE 1=1
            """
            params = []
            param_idx = 1

            if user_name:
                sql += f" AND u.user_name = :{param_idx}"
                params.append(user_name)
                param_idx += 1

            if role:
                sql += f" AND u.role = :{param_idx}"
                params.append(role)
                param_idx += 1

            sql += " ORDER BY u.user_id"

            cursor.execute(sql, params)
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
    def get_by_department(
        department_id: str,
        user_name: Optional[str] = None,
        role: Optional[str] = None,
    ) -> List[UserWithDepartment]:
        """부서별 사용자 목록 조회 (유저 이름 및 역할 필터링 가능)"""
        with get_cursor() as cursor:
            sql = """
                SELECT u.user_id, u.user_name, u.user_email, u.role,
                       u.is_active, u.last_login, u.department_id, d.department_name
                FROM "USER" u
                LEFT JOIN DEPARTMENT d ON u.department_id = d.department_id
                WHERE u.department_id = :1
            """
            params = [department_id]
            param_idx = 2

            if user_name:
                sql += f" AND u.user_name = :{param_idx}"
                params.append(user_name)
                param_idx += 1

            if role:
                sql += f" AND u.role = :{param_idx}"
                params.append(role)
                param_idx += 1

            sql += " ORDER BY u.user_id"

            cursor.execute(sql, params)
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
        import uuid
        user_id = str(uuid.uuid4())
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO "USER" (user_id, user_name, user_email, role, is_active, department_id)
                VALUES (:1, :2, :3, :4, 'Y', :5)
            """,
                [
                    user_id,
                    user.user_name,
                    user.user_email,
                    user.role.value,
                    user.department_id,
                ],
            )
            # TeamLeader → 부서장 단일성 보장
            if user.role == UserRole.TEAM_LEADER and user.department_id:
                cursor.execute(
                    "SELECT manager_user_id FROM DEPARTMENT WHERE department_id = :1 FOR UPDATE",
                    [user.department_id],
                )
                dept_row = cursor.fetchone()
                if dept_row and dept_row[0] not in (None, user_id):
                    raise ValueError("이미 다른 관리자가 지정된 부서입니다. 먼저 해제하세요.")
                cursor.execute(
                    """
                    UPDATE DEPARTMENT
                    SET manager_user_id = :1
                    WHERE department_id = :2
                    """,
                    [user_id, user.department_id],
                )
            return UserResponse(
                user_id=user_id,
                user_name=user.user_name,
                user_email=user.user_email,
                role=user.role,
                is_active="Y",
                last_login=None,
                department_id=user.department_id,
            )

    @staticmethod
    def update(user_id: str, user: UserUpdate) -> Optional[UserResponse]:
        """
        사용자 수정
        동시성 제어: SELECT FOR UPDATE를 사용하여 Lost Update 문제를 방지합니다.
        """
        with get_cursor() as cursor:
            # 동시성 제어: SELECT FOR UPDATE로 행 레벨 잠금 획득
            # 다른 트랜잭션이 동시에 같은 사용자를 수정하는 것을 방지
            cursor.execute(
                """
                SELECT user_name, user_email, role, is_active, last_login, department_id
                FROM "USER" WHERE user_id = :1 FOR UPDATE
            """,
                [user_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            new_name = user.user_name if user.user_name else row[0]
            new_email = user.user_email if user.user_email else row[1]
            new_role = user.role.value if user.role else row[2]
            new_active = user.is_active if user.is_active else row[3]
            new_dept = user.department_id if user.department_id else row[5]
            old_role = row[2]
            old_dept = row[5]

            # TeamLeader 로직: 단일성 및 부서장 연동
            if new_role == UserRole.TEAM_LEADER.value and new_dept:
                # 새 부서의 매니저 잠금 및 단일성 검증
                cursor.execute(
                    "SELECT manager_user_id FROM DEPARTMENT WHERE department_id = :1 FOR UPDATE",
                    [new_dept],
                )
                dept_row = cursor.fetchone()
                if dept_row and dept_row[0] not in (None, user_id):
                    raise ValueError("이미 다른 관리자가 있는 부서입니다. 먼저 해제해야 합니다.")
                # 이전 부서에서 매니저였다면 해제
                if old_dept and old_dept != new_dept:
                    cursor.execute(
                        """
                        UPDATE DEPARTMENT
                        SET manager_user_id = NULL
                        WHERE department_id = :1 AND manager_user_id = :2
                        """,
                        [old_dept, user_id],
                    )
                # 새 부서 매니저로 설정
                cursor.execute(
                    """
                    UPDATE DEPARTMENT
                    SET manager_user_id = :1
                    WHERE department_id = :2
                    """,
                    [user_id, new_dept],
                )
            else:
                # TeamLeader 해제 혹은 부서 이동 시 매니저 해제
                if old_role == UserRole.TEAM_LEADER.value:
                    cursor.execute(
                        """
                        UPDATE DEPARTMENT
                        SET manager_user_id = NULL
                        WHERE manager_user_id = :1
                        """,
                        [user_id],
                    )

            cursor.execute(
                """
                UPDATE "USER"
                SET user_name = :1, user_email = :2,
                    role = :3, is_active = :4, department_id = :5
                WHERE user_id = :6
            """,
                [new_name, new_email, new_role, new_active, new_dept, user_id],
            )
            return UserResponse(
                user_id=user_id,
                user_name=new_name,
                user_email=new_email,
                role=new_role,
                is_active=new_active,
                last_login=row[4],
                department_id=new_dept,
            )

    @staticmethod
    def delete(user_id: str) -> bool:
        """사용자 삭제"""
        with get_cursor() as cursor:
            try:
                # 동시성 제어: 삭제 대상 USER 잠금으로 삭제 중 참조 생성 방지
                cursor.execute(
                    'SELECT user_id FROM "USER" WHERE user_id = :1 FOR UPDATE', [user_id]
                )
                if not cursor.fetchone():
                    return False

                cursor.execute('DELETE FROM "USER" WHERE user_id = :1', [user_id])
                return cursor.rowcount > 0
            except IntegrityError as exc:
                # 부서 매니저인 경우 등 FK 제약 위반
                raise ValueError("해당 사용자는 부서 관리자로 지정되어 있어 삭제할 수 없습니다.") from exc

    # ========================================
    # 통계/분석 쿼리 (for Phase 3 Mapping)
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
    def get_user_role_distribution() -> List[UserRoleDistribution]:
        """
        Q11: 모든 역할별 사용자 분포 (웹 대시보드용)
        Phase 4 수정: 웹 대시보드에서 Pie Chart를 위해 모든 역할별 사용자 분포가 필요함.
        기존 get_by_role은 특정 역할만 조회하지만, 이 메서드는 모든 역할별 집계를 한 번에 반환하여
        API 호출 횟수를 줄이고 네트워크 오버헤드를 감소시킴.
        """
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT role, COUNT(*) AS count
                FROM "USER"
                GROUP BY role
                ORDER BY count DESC
            """
            )
            rows = cursor.fetchall()
            return [
                UserRoleDistribution(role=row[0], count=row[1])
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
    def get_users_with_active_sessions(
        session_status: Optional[SessionStatus] = None,
    ) -> List[UserBasic]:
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
                    [session_status.value],
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
    def get_users_with_min_sessions(
        min_count: int = 5, limit: Optional[int] = None
    ) -> List[UserWithSessionCount]:
        """
        Q17: 최소 세션 수 이상 보유 유저 조회 (인라인 뷰)
        Phase 4 수정: 웹 대시보드에서 Ranking List를 위해 상위 5명 사용자만 필요함.
        limit 파라미터를 추가하여 서버에서 결과를 제한함으로써 네트워크 트래픽을 줄이고
        클라이언트에서 추가 정렬/필터링 연산을 불필요하게 만듦.
        """
        with get_cursor() as cursor:
            sql = """
                SELECT U.user_id, U.user_name, S.session_count
                FROM (
                    SELECT user_id, COUNT(*) AS session_count
                    FROM SESSIONS
                    GROUP BY user_id
                ) S, "USER" U
                WHERE S.user_id = U.user_id
                AND S.session_count >= :1
                ORDER BY S.session_count DESC
            """
            params = [min_count]

            if limit is not None and limit > 0:
                sql += f" FETCH FIRST {int(limit)} ROWS ONLY"

            cursor.execute(sql, params)
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
