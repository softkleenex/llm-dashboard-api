# COMP322 데이터베이스 텀프로젝트 - 이상재 담당 부분

## 프로젝트 개요
- **과목**: COMP322 데이터베이스
- **프로젝트명**: LLM 운영 대시보드 (LLM-Ops Dashboard)
- **팀**: Team 8

### 팀 구성 및 역할 분담
| 이름 | 이니셜 | Phase 4 담당 |
|------|--------|--------------|
| 김형래 | khk | Mainmenu 2 + Web Dashboard |
| 이상재 | lsj | Mainmenu 1, 5 + FastAPI 기본 세팅 |
| 신영진 | syj | Mainmenu 3, 4 |

---

## 이상재 담당 부분 (Phase별)

### Phase 1: ERD 설계 (팀 공동 작업)
**내 담당 엔티티** (5개):
- MODEL - LLM 모델 정보
- MODEL_CONFIG - 모델 파라미터 설정
- DEPLOYMENTS - 모델 배포 환경
- DATASET - 학습 데이터셋
- PROMPT_TEMPLATE - 프롬프트 템플릿

### Phase 2: ETR Mapping + SQL 쿼리 (팀 공동 작업)
**내 담당 파일**:
- `phase2-etr-mapping.txt` - 5개 엔티티의 ER → Relational Schema 매핑
- `phase2-queries.sql` - 10개 SQL 쿼리 (Query Type 1-10)

**쿼리 목록**:
| Type | 설명 | 사용 기법 |
|------|------|-----------|
| 1 | 활성 프로덕션 배포 환경 조회 | Selection + Projection |
| 2 | 모델-데이터셋-배포 매핑 | Multi-way JOIN (WHERE) |
| 3 | 모델별 설정/배포 개수 집계 | Aggregation + GROUP BY |
| 4 | 평균 GPU 이상 배포 환경 | Subquery |
| 5 | 배포에 사용된 데이터셋 | EXISTS Subquery |
| 6 | 카테고리별 프롬프트 템플릿 | IN predicates |
| 7 | 모델별 평균 temperature | Inline View |
| 8 | 모델-설정-배포 관계 | Multi-way JOIN + ORDER BY |
| 9 | 환경별 GPU/배포 집계 | Aggregation + GROUP BY + ORDER BY |
| 10 | 미배포 모델 | MINUS (SET operation) |

### Phase 3: JDBC Application (팀 공동 작업)
- Phase 2에서 작성한 10개 쿼리를 JDBC로 구현
- PreparedStatement를 이용한 동적 쿼리 지원

### Phase 4: FastAPI Backend (팀 공동 작업)
**내 담당**:
- Mainmenu 1: 사용자 및 조직 관리 (부서/사용자 CRUD)
- Mainmenu 5: 세션 및 로그 조회
- FastAPI 프로젝트 기본 세팅 (구조, DB 연결, 배포)

---

## Phase 4 구현 상세

### 프로젝트 구조 (내가 만든 부분)
```
app/
├── main.py                 # FastAPI 앱 진입점
├── config.py               # 환경 설정 (Pydantic Settings)
├── db/
│   └── connection.py       # Oracle DB 연결 풀
├── routers/
│   ├── department.py       # 부서 API (Mainmenu 1)
│   ├── user.py             # 사용자 API (Mainmenu 1)
│   └── session.py          # 세션/로그 API (Mainmenu 5)
├── schemas/
│   ├── department.py       # 부서 스키마
│   ├── user.py             # 사용자 스키마
│   └── session.py          # 세션/로그 스키마
└── services/
    ├── department_service.py
    ├── user_service.py
    └── session_service.py
```

### API 엔드포인트

#### 부서 관리 (Mainmenu 1)
| Method | Endpoint | 기능 |
|--------|----------|------|
| GET | `/api/v1/departments` | 모든 부서 조회 |
| GET | `/api/v1/departments/{id}` | 부서 상세 조회 |
| POST | `/api/v1/departments` | 부서 추가 |
| PUT | `/api/v1/departments/{id}` | 부서 수정 |
| DELETE | `/api/v1/departments/{id}` | 부서 삭제 |

#### 사용자 관리 (Mainmenu 1)
| Method | Endpoint | 기능 |
|--------|----------|------|
| GET | `/api/v1/users` | 모든 사용자 조회 |
| GET | `/api/v1/users/{id}` | 사용자 상세 조회 |
| GET | `/api/v1/users/department/{dept_id}` | 부서별 사용자 조회 |
| POST | `/api/v1/users` | 사용자 추가 |
| PUT | `/api/v1/users/{id}` | 사용자 수정 |
| DELETE | `/api/v1/users/{id}` | 사용자 삭제 |

#### 세션 및 로그 관리 (Mainmenu 5)
| Method | Endpoint | 기능 |
|--------|----------|------|
| GET | `/api/v1/sessions` | 모든 세션 조회 |
| GET | `/api/v1/sessions/{id}` | 세션 상세 조회 |
| GET | `/api/v1/sessions/user/{user_id}` | 사용자별 세션 조회 |
| GET | `/api/v1/sessions/project/{project_id}` | 프로젝트별 세션 조회 |
| DELETE | `/api/v1/sessions/{id}` | 세션 삭제 |
| GET | `/api/v1/sessions/{id}/logs` | 세션 로그 조회 |
| DELETE | `/api/v1/sessions/{id}/logs` | 세션 로그 전체 삭제 |
| DELETE | `/api/v1/sessions/{id}/logs/{seq}` | 특정 로그 삭제 |

### 배포 설정 (내가 구성)

#### GCloud Cloud Run
- **프로젝트**: `llm-dashboard-knu`
- **리전**: `asia-northeast3` (서울)
- **서비스**: `llm-dashboard-api`
- **URL**: https://llm-dashboard-api-xo73prplpa-du.a.run.app

#### GitHub Actions 자동배포
- main 브랜치 push 시 자동 배포
- Docker 이미지 빌드 → Artifact Registry push → Cloud Run 배포

---

## 기술 스택
- **Framework**: FastAPI
- **Database**: Oracle Database (oracledb)
- **Validation**: Pydantic
- **Deployment**: GCloud Cloud Run
- **CI/CD**: GitHub Actions

---

## 이 폴더의 파일 목록
| 파일명 | 설명 | Phase |
|--------|------|-------|
| README.md | 이상재 담당 부분 문서 | - |
| phase2-etr-mapping.txt | ETR Mapping 문서 | Phase 2 |
| phase2-queries.sql | SQL 쿼리 10개 | Phase 2 |

---

작성일: 2025-11-29
작성자: 이상재 (softkleenex)
