# COMP322 데이터베이스 텀프로젝트 - 이상재 담당 부분

## 프로젝트 개요
- **과목**: COMP322 데이터베이스
- **프로젝트명**: LLM 운영 대시보드 (LLM-Ops Dashboard)
- **팀**: Team 8
- **마감일**: 2025년 12월 10일

### 팀 구성 및 역할 분담
| 이름 | 이니셜 | Phase 4 담당 |
|------|--------|--------------|
| 김형래 | khk | Mainmenu 2 + Web Dashboard |
| 이상재 | lsj | Mainmenu 1, 5 + FastAPI 기본 세팅 |
| 신영진 | syj | Mainmenu 3, 4 |

---

## 이상재 담당 작업 완료 현황

### ✅ 완료된 작업

#### 1. FastAPI 기본 세팅
- [x] 프로젝트 구조 설계 (routers, schemas, services, db)
- [x] Oracle DB Connection Pool 설정 (oracledb)
- [x] Pydantic 스키마 정의
- [x] GitHub Actions CI/CD 설정
- [x] GCloud Cloud Run 배포 설정
- [x] Dockerfile 작성

#### 2. Mainmenu 1 - 사용자 및 조직 관리 (12개 기능)
| # | 기능 | API 엔드포인트 | 상태 |
|---|------|----------------|------|
| 1 | 부서 조회 | `GET /api/v1/departments/` | ✅ |
| 2 | 부서 추가 | `POST /api/v1/departments/` | ✅ |
| 3 | 부서 수정 | `PUT /api/v1/departments/{id}` | ✅ |
| 4 | 부서 삭제 | `DELETE /api/v1/departments/{id}` | ✅ |
| 5 | 사용자 조회 | `GET /api/v1/users/` | ✅ |
| 6 | 사용자 추가 | `POST /api/v1/users/` | ✅ |
| 7 | 사용자 수정 | `PUT /api/v1/users/{id}` | ✅ |
| 8 | 사용자 삭제 | `DELETE /api/v1/users/{id}` | ✅ |
| 9 | 부서별 사용자 | `GET /api/v1/users/department/{id}` | ✅ |
| 10 | [Q11] 역할별 사용자 | `GET /api/v1/users/stats/by-role` | ✅ |
| 11 | [Q14] 부서명으로 유저 | `GET /api/v1/users/stats/by-department-name` | ✅ |
| 12 | [Q20] 역할+관리자 UNION | `GET /api/v1/users/stats/role-and-managers` | ✅ |

#### 3. Mainmenu 5 - 세션 및 로그 조회 (10개 기능)
| # | 기능 | API 엔드포인트 | 상태 |
|---|------|----------------|------|
| 1 | 세션 조회 | `GET /api/v1/sessions/` | ✅ |
| 2 | 사용자별 세션 | `GET /api/v1/sessions/user/{id}` | ✅ |
| 3 | 프로젝트별 세션 | `GET /api/v1/sessions/project/{id}` | ✅ |
| 4 | 세션 로그 조회 | `GET /api/v1/sessions/{id}/logs` | ✅ |
| 5 | 세션 삭제 | `DELETE /api/v1/sessions/{id}` | ✅ |
| 6 | 세션 로그 삭제 | `DELETE /api/v1/sessions/{id}/logs` | ✅ |
| 7 | [Q15] 상태별 세션 유저 | `GET /api/v1/users/stats/with-sessions` | ✅ |
| 8 | [Q17] 최소 N개 세션 유저 | `GET /api/v1/users/stats/min-sessions` | ✅ |
| 9 | [Q18] 토큰 사용량 순 로그 | `GET /api/v1/sessions/stats/logs-by-token` | ✅ |
| 10 | [Q19] 유저별 세션 수 | `GET /api/v1/sessions/stats/user-session-count` | ✅ |

---

## 배포 현황

### 개인 레포 (테스트용)
| 항목 | 값 |
|------|-----|
| GitHub | https://github.com/softkleenex/llm-dashboard-api |
| 배포 URL | https://llm-dashboard-api-xo73prplpa-du.a.run.app |
| API 문서 | https://llm-dashboard-api-xo73prplpa-du.a.run.app/docs |
| 상태 | ✅ 정상 작동 |

### 팀 레포
| 항목 | 값 |
|------|-----|
| GitHub | https://github.com/knu-comp322-team8/team8-db-proj-backend |
| 배포 URL | https://llm-dashboard-api-xo73prplpa-du.a.run.app |
| API 문서 | https://llm-dashboard-api-xo73prplpa-du.a.run.app/docs |
| 상태 | ✅ 정상 작동 (Oracle Cloud 연결 완료) |

### Oracle Cloud Database
| 항목 | 값 |
|------|-----|
| 서비스 | Oracle Cloud Free Tier Autonomous DB |
| 리전 | ap-chuncheon-1 (춘천) |
| 연결 방식 | Wallet 기반 mTLS |
| 상태 | ✅ 연결 성공 |

---

## 프로젝트 구조

```
app/
├── main.py                 # FastAPI 앱 진입점
├── config.py               # 환경 설정 (Pydantic Settings)
├── db/
│   └── connection.py       # Oracle DB 연결 풀
├── routers/
│   ├── department.py       # 부서 API (5개)
│   ├── user.py             # 사용자 API (11개)
│   └── session.py          # 세션/로그 API (10개)
├── schemas/
│   ├── department.py       # 부서 스키마
│   ├── user.py             # 사용자 스키마 (통계용 포함)
│   └── session.py          # 세션/로그 스키마 (통계용 포함)
└── services/
    ├── department_service.py
    ├── user_service.py     # 통계 쿼리 포함
    └── session_service.py  # 통계 쿼리 포함
```

---

## 커밋 로그

```
b67b000 fix: 라우터 순서 수정 (stats 엔드포인트를 /{id} 보다 먼저 정의)
99ab95f feat: Mainmenu 1, 5 통계 쿼리 API 추가 (Q11, Q14, Q15, Q17, Q18, Q19, Q20)
86ce158 feat: 팀원별 작업 폴더 추가 (lsj, khk, syj)
7a3f582 fix: Dockerfile libaio1 패키지명 수정 (libaio1t64)
edee9d8 feat: GCloud Cloud Run 배포 설정
aff4e66 feat: GitHub Actions 배포 방식 변경 (Docker Hub + SSH)
4b8fe98 feat: 배포 설정 추가 (Dockerfile, Railway, GitHub Actions)
7550065 feat: FastAPI 프로젝트 초기 세팅 - Mainmenu 1, 5 API 구현
```

---

## Phase 1-4 전체 기여 요약

### Phase 1: ERD 설계
**담당 엔티티** (5개):
- MODEL, MODEL_CONFIG, DEPLOYMENTS, DATASET, PROMPT_TEMPLATE

### Phase 2: ETR Mapping + SQL 쿼리
**담당 파일**:
- `phase2-etr-mapping.txt` - 5개 엔티티 ER→Relational 매핑
- `phase2-queries.sql` - 10개 SQL 쿼리 (Type 1-10)

### Phase 3: JDBC Application
- Phase 2 쿼리를 JDBC로 구현
- PreparedStatement 동적 쿼리

### Phase 4: FastAPI Backend
- Mainmenu 1, 5 전체 구현 (22개 기능)
- FastAPI 기본 세팅 + 배포

---

## 기술 스택
- **Framework**: FastAPI
- **Database**: Oracle Database (oracledb)
- **Validation**: Pydantic
- **Deployment**: GCloud Cloud Run
- **CI/CD**: GitHub Actions
- **Container**: Docker

---

## 이 폴더의 파일 목록
| 파일명 | 설명 | Phase |
|--------|------|-------|
| README.md | 이상재 담당 부분 문서 | Phase 4 |
| phase2-etr-mapping.txt | ETR Mapping 문서 | Phase 2 |
| phase2-queries.sql | SQL 쿼리 10개 | Phase 2 |

---

작성일: 2025-11-29
최종 수정: 2025-11-29
작성자: 이상재 (softkleenex)

### 데이터 현황
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
