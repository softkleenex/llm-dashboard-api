# 프로젝트 기여 내역

이 문서는 LLM Dashboard API 프로젝트에서의 개발 기여 내역을 정리한 문서입니다.

## 담당 개발 영역

### 1. FastAPI 백엔드 아키텍처 설계 및 구현

- 프로젝트 구조 설계 (routers, schemas, services, db 레이어 분리)
- Oracle DB Connection Pool 설정 (python-oracledb)
- Pydantic 스키마 정의
- GitHub Actions CI/CD 파이프라인 구축
- GCP Cloud Run 배포 설정
- Dockerfile 작성

### 2. 사용자 및 조직 관리 API (12개 엔드포인트)

| 기능 | API 엔드포인트 |
|------|----------------|
| 부서 조회 | `GET /api/v1/departments/` |
| 부서 추가 | `POST /api/v1/departments/` |
| 부서 수정 | `PUT /api/v1/departments/{id}` |
| 부서 삭제 | `DELETE /api/v1/departments/{id}` |
| 사용자 조회 | `GET /api/v1/users/` |
| 사용자 추가 | `POST /api/v1/users/` |
| 사용자 수정 | `PUT /api/v1/users/{id}` |
| 사용자 삭제 | `DELETE /api/v1/users/{id}` |
| 부서별 사용자 | `GET /api/v1/users/department/{id}` |
| 역할별 사용자 통계 | `GET /api/v1/users/stats/by-role` |
| 부서명 검색 | `GET /api/v1/users/stats/by-department-name` |
| 역할+관리자 통계 | `GET /api/v1/users/stats/role-and-managers` |

### 3. 세션 및 로그 관리 API (10개 엔드포인트)

| 기능 | API 엔드포인트 |
|------|----------------|
| 세션 조회 | `GET /api/v1/sessions/` |
| 사용자별 세션 | `GET /api/v1/sessions/user/{id}` |
| 프로젝트별 세션 | `GET /api/v1/sessions/project/{id}` |
| 세션 로그 조회 | `GET /api/v1/sessions/{id}/logs` |
| 세션 삭제 | `DELETE /api/v1/sessions/{id}` |
| 세션 로그 삭제 | `DELETE /api/v1/sessions/{id}/logs` |
| 상태별 세션 통계 | `GET /api/v1/users/stats/with-sessions` |
| 최소 N개 세션 사용자 | `GET /api/v1/users/stats/min-sessions` |
| 토큰 사용량 순 로그 | `GET /api/v1/sessions/stats/logs-by-token` |
| 유저별 세션 수 | `GET /api/v1/sessions/stats/user-session-count` |

---

## 프로젝트 구조

```
app/
├── main.py                 # FastAPI 앱 진입점
├── config.py               # 환경 설정 (Pydantic Settings)
├── db/
│   └── connection.py       # Oracle DB 연결 풀, 트랜잭션 관리
├── routers/
│   ├── department.py       # 부서 API
│   ├── user.py             # 사용자 API
│   └── session.py          # 세션/로그 API
├── schemas/
│   ├── department.py       # 부서 스키마
│   ├── user.py             # 사용자 스키마
│   └── session.py          # 세션/로그 스키마
└── services/
    ├── department_service.py
    ├── user_service.py
    └── session_service.py
```

---

## 데이터베이스 설계 기여

### ERD 설계 담당 엔티티 (5개)
- MODEL
- MODEL_CONFIG
- DEPLOYMENTS
- DATASET
- PROMPT_TEMPLATE

### ER to Relational 매핑
- `phase2-etr-mapping.txt` - 5개 엔티티의 ER→Relational 매핑 문서
- `phase2-queries.sql` - 10개 SQL 쿼리 (다양한 JOIN, 서브쿼리, 집계 함수 활용)

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| Framework | FastAPI |
| Database | Oracle Database |
| Driver | python-oracledb |
| Validation | Pydantic |
| Deployment | GCP Cloud Run |
| CI/CD | GitHub Actions |
| Container | Docker |

---

## 테스트 데이터 규모

| 테이블 | 건수 |
|--------|------|
| DEPARTMENT | 10 |
| USER | 300 |
| PROJECT | 100 |
| MODEL | 22 |
| MODEL_CONFIG | 132 |
| DATASET | 30 |
| DEPLOYMENTS | 44 |
| PROMPT_TEMPLATE | 120 |
| SESSIONS | 650 |
| SESSION_LOGS | 4,860 |
