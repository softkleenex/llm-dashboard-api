from typing import List, Optional
from app.db.connection import get_cursor
from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionWithUser,
    SessionLogCreate,
    SessionLogResponse,
    SessionLogWithDetails,
    SessionLogByToken,
    UserSessionCount,
    SessionType,
    SessionStatus,
)


class SessionService:
    @staticmethod
    def get_all() -> List[SessionWithUser]:
        """모든 세션 조회"""
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT s.session_id, s.start_time, s.end_time, s.session_type,
                       s.status, s.user_id, s.project_id, u.user_name, p.project_name
                FROM SESSIONS s
                LEFT JOIN "USER" u ON s.user_id = u.user_id
                LEFT JOIN PROJECT p ON s.project_id = p.project_id
                ORDER BY s.start_time DESC
            """)
            rows = cursor.fetchall()
            return [
                SessionWithUser(
                    session_id=row[0],
                    start_time=row[1],
                    end_time=row[2],
                    session_type=SessionType(row[3]),
                    status=SessionStatus(row[4]),
                    user_id=row[5],
                    project_id=row[6],
                    user_name=row[7],
                    project_name=row[8],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(session_id: str) -> Optional[SessionWithUser]:
        """세션 ID로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT s.session_id, s.start_time, s.end_time, s.session_type,
                       s.status, s.user_id, s.project_id, u.user_name, p.project_name
                FROM SESSIONS s
                LEFT JOIN "USER" u ON s.user_id = u.user_id
                LEFT JOIN PROJECT p ON s.project_id = p.project_id
                WHERE s.session_id = :1
            """,
                [session_id],
            )
            row = cursor.fetchone()
            if row:
                return SessionWithUser(
                    session_id=row[0],
                    start_time=row[1],
                    end_time=row[2],
                    session_type=SessionType(row[3]),
                    status=SessionStatus(row[4]),
                    user_id=row[5],
                    project_id=row[6],
                    user_name=row[7],
                    project_name=row[8],
                )
            return None

    @staticmethod
    def get_by_user(user_id: str) -> List[SessionWithUser]:
        """사용자별 세션 목록 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT s.session_id, s.start_time, s.end_time, s.session_type,
                       s.status, s.user_id, s.project_id, u.user_name, p.project_name
                FROM SESSIONS s
                LEFT JOIN "USER" u ON s.user_id = u.user_id
                LEFT JOIN PROJECT p ON s.project_id = p.project_id
                WHERE s.user_id = :1
                ORDER BY s.start_time DESC
            """,
                [user_id],
            )
            rows = cursor.fetchall()
            return [
                SessionWithUser(
                    session_id=row[0],
                    start_time=row[1],
                    end_time=row[2],
                    session_type=SessionType(row[3]),
                    status=SessionStatus(row[4]),
                    user_id=row[5],
                    project_id=row[6],
                    user_name=row[7],
                    project_name=row[8],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_project(project_id: str) -> List[SessionWithUser]:
        """프로젝트별 세션 목록 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT s.session_id, s.start_time, s.end_time, s.session_type,
                       s.status, s.user_id, s.project_id, u.user_name, p.project_name
                FROM SESSIONS s
                LEFT JOIN "USER" u ON s.user_id = u.user_id
                LEFT JOIN PROJECT p ON s.project_id = p.project_id
                WHERE s.project_id = :1
                ORDER BY s.start_time DESC
            """,
                [project_id],
            )
            rows = cursor.fetchall()
            return [
                SessionWithUser(
                    session_id=row[0],
                    start_time=row[1],
                    end_time=row[2],
                    session_type=SessionType(row[3]),
                    status=SessionStatus(row[4]),
                    user_id=row[5],
                    project_id=row[6],
                    user_name=row[7],
                    project_name=row[8],
                )
                for row in rows
            ]

    @staticmethod
    def search(
        user_name: Optional[str] = None,
        project_name: Optional[str] = None,
        session_type: Optional[SessionType] = None,
        status: Optional[SessionStatus] = None,
    ) -> List[SessionWithUser]:
        """사용자명, 프로젝트명, 세션 타입, 상태로 세션 검색 (자연어 + Enum 필터)"""
        with get_cursor() as cursor:
            sql = """
                SELECT s.session_id, s.start_time, s.end_time, s.session_type,
                       s.status, s.user_id, s.project_id, u.user_name, p.project_name
                FROM SESSIONS s
                LEFT JOIN "USER" u ON s.user_id = u.user_id
                LEFT JOIN PROJECT p ON s.project_id = p.project_id
                WHERE 1=1
            """
            params: list = []
            param_idx = 1

            if user_name:
                # 부분 일치(자연어) 검색
                sql += f" AND LOWER(u.user_name) LIKE :{param_idx}"
                params.append(f"%{user_name.lower()}%")
                param_idx += 1

            if project_name:
                sql += f" AND LOWER(p.project_name) LIKE :{param_idx}"
                params.append(f"%{project_name.lower()}%")
                param_idx += 1

            if session_type:
                sql += f" AND s.session_type = :{param_idx}"
                params.append(session_type.value)
                param_idx += 1

            if status:
                sql += f" AND s.status = :{param_idx}"
                params.append(status.value)
                param_idx += 1

            sql += " ORDER BY s.start_time DESC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                SessionWithUser(
                    session_id=row[0],
                    start_time=row[1],
                    end_time=row[2],
                    session_type=SessionType(row[3]),
                    status=SessionStatus(row[4]),
                    user_id=row[5],
                    project_id=row[6],
                    user_name=row[7],
                    project_name=row[8],
                )
                for row in rows
            ]

    @staticmethod
    def delete(session_id: str) -> bool:
        """세션 삭제 (CASCADE로 로그도 자동 삭제)"""
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM SESSIONS WHERE session_id = :1", [session_id])
            return cursor.rowcount > 0


class SessionLogService:
    @staticmethod
    def get_by_session(session_id: str) -> List[SessionLogWithDetails]:
        """세션 ID로 로그 조회 (config 정보 포함)"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT sl.session_id, sl.log_sequence, sl.request_time,
                       sl.request_prompt_s3_path, sl.response_s3_path,
                       sl.token_used, sl.response_time, sl.config_id,
                       sl.deployment_id, 
                       mc.max_tokens, mc.temperature, 
                       mc.top_p, mc.top_k,
                       d.server_name
                FROM SESSION_LOGS sl
                LEFT JOIN MODEL_CONFIG mc ON sl.config_id = mc.config_id
                LEFT JOIN DEPLOYMENTS d ON sl.deployment_id = d.deployment_id
                WHERE sl.session_id = :1
                ORDER BY sl.log_sequence
            """,
                [session_id],
            )
            rows = cursor.fetchall()
            return [
                SessionLogWithDetails(
                    session_id=row[0],
                    log_sequence=row[1],
                    request_time=row[2],
                    request_prompt_s3_path=row[3],
                    response_s3_path=row[4],
                    token_used=row[5],
                    response_time=row[6],
                    config_id=row[7],
                    deployment_id=row[8],
                    config_max_tokens=row[9],
                    config_temperature=row[10],
                    config_top_p=row[11],
                    config_top_k=row[12],
                    deployment_server=row[13],
                )
                for row in rows
            ]

    @staticmethod
    def delete_by_session(session_id: str) -> int:
        """세션의 모든 로그 삭제"""
        with get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM SESSION_LOGS WHERE session_id = :1",
                [session_id],
            )
            return cursor.rowcount

    @staticmethod
    def delete_single(session_id: str, log_sequence: int) -> bool:
        """특정 로그 삭제"""
        with get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM SESSION_LOGS WHERE session_id = :1 AND log_sequence = :2",
                [session_id, log_sequence],
            )
            return cursor.rowcount > 0

    # ========================================
    # 통계/분석 쿼리 (for Phase 3 Mapping)
    # ========================================

    @staticmethod
    def get_logs_by_token_usage(
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        user_name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[SessionLogByToken]:
        """Q18: 세션 로그 토큰 사용량 순 조회 (동적 필터)"""
        with get_cursor() as cursor:
            sql = """
                SELECT SL.session_id, SL.log_sequence, U.user_name, SL.token_used
                FROM SESSION_LOGS SL, SESSIONS S, "USER" U
                WHERE SL.session_id = S.session_id AND S.user_id = U.user_id
            """
            params = []
            param_idx = 1

            if date_from:
                sql += f" AND SL.request_time >= TO_DATE(:{param_idx}, 'YYYY-MM-DD')"
                params.append(date_from)
                param_idx += 1

            if date_to:
                sql += f" AND SL.request_time <= TO_DATE(:{param_idx}, 'YYYY-MM-DD')"
                params.append(date_to)
                param_idx += 1

            if user_name:
                sql += f" AND U.user_name = :{param_idx}"
                params.append(user_name)
                param_idx += 1

            sql += " ORDER BY SL.token_used DESC"

            if limit and limit > 0:
                sql += f" FETCH FIRST {int(limit)} ROWS ONLY"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                SessionLogByToken(
                    session_id=row[0],
                    log_sequence=row[1],
                    user_name=row[2],
                    token_used=row[3],
                )
                for row in rows
            ]

    @staticmethod
    def get_user_session_count(limit: Optional[int] = None) -> List[UserSessionCount]:
        """Q19: 유저별 세션 수 집계 및 정렬"""
        with get_cursor() as cursor:
            sql = """
                SELECT U.user_name, COUNT(S.session_id) AS total_sessions
                FROM "USER" U, SESSIONS S
                WHERE U.user_id = S.user_id
                GROUP BY U.user_name
                ORDER BY total_sessions DESC
            """

            if limit and limit > 0:
                sql += f" FETCH FIRST {int(limit)} ROWS ONLY"

            cursor.execute(sql)
            rows = cursor.fetchall()
            return [
                UserSessionCount(user_name=row[0], total_sessions=row[1])
                for row in rows
            ]
