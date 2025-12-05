from typing import List, Optional

from app.db.connection import get_cursor
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse,
    TaskCategory,
    PromptTemplateByCategory,
)


class PromptTemplateService:
    @staticmethod
    def _read_lob(value):
        """Oracle LOB 타입을 문자열로 변환 (아닐 경우 그대로 반환)"""
        if value is None:
            return None
        read_method = getattr(value, "read", None)
        if callable(read_method):
            return read_method()
        return value

    @staticmethod
    def get_all() -> List[PromptTemplateResponse]:
        """모든 프롬프트 템플릿 조회 (생성자 이름 포함)"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT T.template_id,
                       T.template_name,
                       T.prompt_s3_path,
                       T.description,
                       T.task_category,
                       T.variables,
                       T.version,
                       T.usage_count,
                       T.created_at,
                       T.creator_user_id,
                       U.user_name
                FROM PROMPT_TEMPLATE T
                LEFT JOIN "USER" U ON T.creator_user_id = U.user_id
                ORDER BY T.template_id
            """
            )
            rows = cursor.fetchall()
            return [
                PromptTemplateResponse(
                    template_id=row[0],
                    template_name=row[1],
                    prompt_s3_path=row[2],
                    description=PromptTemplateService._read_lob(row[3]),
                    task_category=TaskCategory(row[4]),
                    variables=row[5],
                    version=row[6],
                    usage_count=row[7],
                    created_at=row[8],
                    creator_user_id=row[9],
                    creator_user_name=row[10],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(template_id: str) -> Optional[PromptTemplateResponse]:
        """템플릿 ID로 조회"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT T.template_id,
                       T.template_name,
                       T.prompt_s3_path,
                       T.description,
                       T.task_category,
                       T.variables,
                       T.version,
                       T.usage_count,
                       T.created_at,
                       T.creator_user_id,
                       U.user_name
                FROM PROMPT_TEMPLATE T
                LEFT JOIN "USER" U ON T.creator_user_id = U.user_id
                WHERE T.template_id = :1
            """,
                [template_id],
            )
            row = cursor.fetchone()
            if row:
                return PromptTemplateResponse(
                    template_id=row[0],
                    template_name=row[1],
                    prompt_s3_path=row[2],
                    description=PromptTemplateService._read_lob(row[3]),
                    task_category=TaskCategory(row[4]),
                    variables=row[5],
                    version=row[6],
                    usage_count=row[7],
                    created_at=row[8],
                    creator_user_id=row[9],
                    creator_user_name=row[10],
                )
            return None

    @staticmethod
    def create(template: PromptTemplateCreate) -> PromptTemplateResponse:
        """프롬프트 템플릿 추가"""
        import uuid
        template_id = str(uuid.uuid4())
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO PROMPT_TEMPLATE (
                    template_id,
                    template_name,
                    prompt_s3_path,
                    description,
                    task_category,
                    variables,
                    version,
                    creator_user_id
                )
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
            """,
                [
                    template_id,
                    template.template_name,
                    template.prompt_s3_path,
                    template.description,
                    template.task_category.value,
                    template.variables,
                    template.version,
                    template.creator_user_id,
                ],
            )
            # usage_count, created_at은 DB 기본값 사용
            # 생성자 이름 조회
            cursor.execute(
                'SELECT user_name FROM "USER" WHERE user_id = :1',
                [template.creator_user_id],
            )
            row = cursor.fetchone()
            creator_name = row[0] if row else None

            return PromptTemplateResponse(
                template_id=template_id,
                template_name=template.template_name,
                prompt_s3_path=template.prompt_s3_path,
                description=template.description,
                task_category=template.task_category,
                variables=template.variables,
                version=template.version,
                usage_count=0,
                created_at=None,
                creator_user_id=template.creator_user_id,
                creator_user_name=creator_name,
            )

    @staticmethod
    def update(
        template_id: str, template: PromptTemplateUpdate
    ) -> Optional[PromptTemplateResponse]:
        """프롬프트 템플릿 수정"""
        with get_cursor() as cursor:
            # 현재 데이터 조회
            cursor.execute(
                """
                SELECT template_name,
                       prompt_s3_path,
                       description,
                       task_category,
                       variables,
                       version,
                       usage_count,
                       created_at,
                       creator_user_id
                FROM PROMPT_TEMPLATE
                WHERE template_id = :1
            """,
                [template_id],
            )
            row = cursor.fetchone()
            if not row:
                return None

            (
                current_name,
                current_s3_path,
                current_description,
                current_category,
                current_variables,
                current_version,
                usage_count,
                created_at,
                creator_user_id,
            ) = row
            current_description = PromptTemplateService._read_lob(current_description)

            new_name = template.template_name or current_name
            new_s3_path = template.prompt_s3_path or current_s3_path

            if template.description is None:
                new_description = current_description
            elif template.description == "":
                new_description = None
            else:
                new_description = template.description

            if template.task_category is None:
                new_category = current_category
            else:
                new_category = template.task_category.value

            if template.variables is None:
                new_variables = current_variables
            elif template.variables == "":
                new_variables = None
            else:
                new_variables = template.variables

            new_version = template.version or current_version

            cursor.execute(
                """
                UPDATE PROMPT_TEMPLATE
                SET template_name = :1,
                    prompt_s3_path = :2,
                    description = :3,
                    task_category = :4,
                    variables = :5,
                    version = :6
                WHERE template_id = :7
            """,
                [
                    new_name,
                    new_s3_path,
                    new_description,
                    new_category,
                    new_variables,
                    new_version,
                    template_id,
                ],
            )

            # 생성자 이름 조회
            cursor.execute(
                'SELECT user_name FROM "USER" WHERE user_id = :1', [creator_user_id]
            )
            row = cursor.fetchone()
            creator_name = row[0] if row else None

            return PromptTemplateResponse(
                template_id=template_id,
                template_name=new_name,
                prompt_s3_path=new_s3_path,
                description=new_description,
                task_category=TaskCategory(new_category),
                variables=new_variables,
                version=new_version,
                usage_count=usage_count,
                created_at=created_at,
                creator_user_id=creator_user_id,
                creator_user_name=creator_name,
            )

    @staticmethod
    def delete(template_id: str) -> bool:
        """프롬프트 템플릿 삭제"""
        with get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM PROMPT_TEMPLATE WHERE template_id = :1", [template_id]
            )
            return cursor.rowcount > 0

    @staticmethod
    def search(
        template_name: Optional[str] = None,
        creator_user_name: Optional[str] = None,
    ) -> List[PromptTemplateResponse]:
        """템플릿명, 생성자명으로 프롬프트 템플릿 검색 (자연어 검색)"""
        with get_cursor() as cursor:
            sql = """
                SELECT T.template_id,
                       T.template_name,
                       T.prompt_s3_path,
                       T.description,
                       T.task_category,
                       T.variables,
                       T.version,
                       T.usage_count,
                       T.created_at,
                       T.creator_user_id,
                       U.user_name
                FROM PROMPT_TEMPLATE T
                LEFT JOIN "USER" U ON T.creator_user_id = U.user_id
                WHERE 1=1
            """
            params: list = []
            param_idx = 1

            if template_name:
                sql += f" AND LOWER(T.template_name) LIKE :{param_idx}"
                params.append(f"%{template_name.lower()}%")
                param_idx += 1

            if creator_user_name:
                sql += f" AND LOWER(U.user_name) LIKE :{param_idx}"
                params.append(f"%{creator_user_name.lower()}%")
                param_idx += 1

            sql += " ORDER BY T.template_id"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                PromptTemplateResponse(
                    template_id=row[0],
                    template_name=row[1],
                    prompt_s3_path=row[2],
                    description=PromptTemplateService._read_lob(row[3]),
                    task_category=TaskCategory(row[4]),
                    variables=row[5],
                    version=row[6],
                    usage_count=row[7],
                    created_at=row[8],
                    creator_user_id=row[9],
                    creator_user_name=row[10],
                )
                for row in rows
            ]

    # ==========================
    # 통계/분석 쿼리 (for Phase 3 Mapping)
    # ==========================

    @staticmethod
    def query6_prompt_templates_by_category(
        categories: Optional[List[TaskCategory]] = None,
    ) -> List[PromptTemplateByCategory]:
        """Q6: 프롬프트 템플릿 카테고리 조회 (동적 필터)"""
        with get_cursor() as cursor:
            sql = """
                SELECT template_name, task_category, version, usage_count
                FROM PROMPT_TEMPLATE
                WHERE 1=1
            """
            params: list = []
            param_idx = 1

            if categories and len(categories) > 0:
                placeholders = ", ".join([f":{param_idx + i}" for i in range(len(categories))])
                sql += f" AND task_category IN ({placeholders})"
                params.extend([cat.value for cat in categories])
                param_idx += len(categories)

            sql += " ORDER BY usage_count DESC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                PromptTemplateByCategory(
                    template_name=row[0],
                    task_category=TaskCategory(row[1]),
                    version=row[2],
                    usage_count=row[3],
                )
                for row in rows
            ]


