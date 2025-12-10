# LLM Dashboard API

LLM(Large Language Model) 운영 대시보드를 위한 FastAPI 백엔드 API 서버입니다.

## 프로젝트 소개

오픈소스 LLM 서비스 사용 현황을 관리하는 대시보드 백엔드로, 다음 기능을 제공합니다:

- **사용자/부서 관리**: 조직 구조 및 권한 관리
- **프로젝트 관리**: LLM 활용 프로젝트 추적
- **모델 관리**: LLM 모델 및 설정 관리
- **세션/로그 관리**: 사용 이력 및 통계

### 주요 특징

- **동시성 제어**: Oracle READ COMMITTED + SELECT FOR UPDATE를 활용한 트랜잭션 관리
- **비즈니스 규칙 무결성**: TEAM_LEADER role과 manager_user_id 자동 동기화
- **RESTful API**: FastAPI 기반 OpenAPI 문서 자동 생성

## 기술 스택

| 분류 | 기술 |
|------|------|
| Framework | FastAPI, Uvicorn |
| Database | Oracle Database |
| Driver | python-oracledb |
| Config | Pydantic Settings |
| CI/CD | GitHub Actions, Docker |
| Cloud | GCP Cloud Run |

## 프로젝트 구조

```
llm-dashboard-api/
├── app/
│   ├── main.py                # FastAPI 엔트리포인트
│   ├── config.py              # 환경 변수 설정
│   ├── db/connection.py       # Oracle 커넥션 풀/트랜잭션
│   ├── routers/               # API 라우터
│   │   ├── department.py      # 부서 CRUD
│   │   ├── user.py            # 사용자 CRUD
│   │   ├── session.py         # 세션/로그 CRUD
│   │   ├── project.py         # 프로젝트 CRUD
│   │   ├── model.py           # 모델 CRUD
│   │   ├── model_config.py    # 모델 설정 CRUD
│   │   ├── dataset.py         # 데이터셋 CRUD
│   │   ├── deployment.py      # 배포 환경 CRUD
│   │   └── prompt_template.py # 프롬프트 템플릿 CRUD
│   ├── schemas/               # Pydantic 스키마
│   └── services/              # 비즈니스 로직
├── docs/                      # 프로젝트 문서
├── requirements.txt
├── Dockerfile
└── .github/workflows/         # CI/CD
```

## 로컬 실행

### 1. 환경 설정

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
cp .env.example .env
# .env 파일에서 DB 연결 정보 수정
```

### 3. 서버 실행

```bash
uvicorn app.main:app --reload
```

### 4. API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 부서 관리

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/departments` | 부서 목록 조회 |
| GET | `/api/v1/departments/{id}` | 부서 상세 조회 |
| POST | `/api/v1/departments` | 부서 생성 |
| PUT | `/api/v1/departments/{id}` | 부서 수정 |
| DELETE | `/api/v1/departments/{id}` | 부서 삭제 |

### 사용자 관리

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/users` | 사용자 목록 조회 |
| GET | `/api/v1/users/{id}` | 사용자 상세 조회 |
| POST | `/api/v1/users` | 사용자 생성 |
| PUT | `/api/v1/users/{id}` | 사용자 수정 |
| DELETE | `/api/v1/users/{id}` | 사용자 삭제 |

### 세션/로그 관리

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/sessions` | 세션 목록 조회 |
| GET | `/api/v1/sessions/{id}/logs` | 세션 로그 조회 |
| DELETE | `/api/v1/sessions/{id}` | 세션 삭제 |

### 기타 API

- `/api/v1/projects` - 프로젝트 관리
- `/api/v1/models` - 모델 관리
- `/api/v1/model-configs` - 모델 설정
- `/api/v1/datasets` - 데이터셋 관리
- `/api/v1/deployments` - 배포 환경
- `/api/v1/prompt-templates` - 프롬프트 템플릿

## 환경변수

| 변수명 | 설명 |
|--------|------|
| DB_DSN | Oracle DB DSN |
| DB_USER | DB 사용자 |
| DB_PASSWORD | DB 비밀번호 |
| DB_WALLET_PASSWORD | Wallet 비밀번호 (Cloud) |
| APP_HOST | 서버 호스트 |
| APP_PORT | 서버 포트 |

## 배포

GitHub Actions를 통해 main 브랜치 push 시 자동 배포됩니다.

1. Docker 이미지 빌드
2. GCP Artifact Registry 푸시
3. Cloud Run 배포

## License

MIT License
