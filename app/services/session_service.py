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
                    session_type=row[3],
                    status=row[4],
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
                    session_type=row[3],
                    status=row[4],
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
                    session_type=row[3],
                    status=row[4],
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
                    session_type=row[3],
                    status=row[4],
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
        """세션 ID로 로그 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT sl.session_id, sl.log_sequence, sl.request_time,
                       sl.request_prompt_s3_path, sl.response_s3_path,
                       sl.token_used, sl.response_time, sl.config_id,
                       sl.deployment_id, mc.config_name, d.server_name
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
                    config_name=row[9],
                    deployment_server=row[10],
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
