# LLM Dashboard API

COMP322 데이터베이스 Term Project Phase 4 - FastAPI 백엔드

## 팀원

- 김형래
- 이상재
- 신영진

## 기술 스택

- **Framework**: FastAPI, Uvicorn
- **DB**: Oracle Database
- **Driver**: python-oracledb
- **Config**: Pydantic Settings (.env)
- **CI/CD**: GitHub Actions, Docker

## 프로젝트 구조

```
team8-db-proj-backend/
├── app/
│   ├── main.py                # FastAPI 엔트리포인트, 라우터 등록, CORS, health
│   ├── config.py              # 환경 변수 로딩 (DB/앱 설정)
│   ├── db/connection.py       # Oracle 커넥션 풀/트랜잭션 헬퍼
│   ├── routers/               # API 라우터 (prefix=/api/v1)
│   │   ├── department.py      # 부서 CRUD
│   │   ├── user.py            # 사용자 CRUD/검색
│   │   ├── session.py         # 세션·로그 CRUD/통계
│   │   ├── project.py         # 프로젝트 CRUD/통계
│   │   ├── prompt_template.py # 프롬프트 템플릿 CRUD/통계
│   │   ├── model.py           # 모델 CRUD/통계
│   │   ├── model_config.py    # 모델 설정 CRUD
│   │   ├── dataset.py         # 데이터셋 CRUD/통계
│   │   └── deployment.py      # 배포 환경 CRUD/통계
│   ├── schemas/               # 요청/응답 Pydantic 모델
│   └── services/              # 비즈니스 로직, DB 질의
├── requirements.txt           # 의존성
├── Dockerfile                 # 컨테이너 빌드 정의
├── Procfile                   # 프로세스 정의 (예: Railway)
└── .github/workflows/deploy.yml# CI/CD 파이프라인
```

## 로컬 실행 방법

### 1. 가상환경 설정

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp .env.example .env
# .env 파일에서 DB 연결 정보 수정
```

### 4. 서버 실행

```bash
uvicorn app.main:app --reload
```

### 5. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 부서 관리 (Mainmenu 1)

| Method | Endpoint                   | 설명           |
| ------ | -------------------------- | -------------- |
| GET    | `/api/v1/departments`      | 모든 부서 조회 |
| GET    | `/api/v1/departments/{id}` | 부서 상세 조회 |
| POST   | `/api/v1/departments`      | 부서 추가      |
| PUT    | `/api/v1/departments/{id}` | 부서 수정      |
| DELETE | `/api/v1/departments/{id}` | 부서 삭제      |

### 사용자 관리 (Mainmenu 1)

| Method | Endpoint                             | 설명               |
| ------ | ------------------------------------ | ------------------ |
| GET    | `/api/v1/users`                      | 모든 사용자 조회   |
| GET    | `/api/v1/users/{id}`                 | 사용자 상세 조회   |
| GET    | `/api/v1/users/department/{dept_id}` | 부서별 사용자 조회 |
| POST   | `/api/v1/users`                      | 사용자 추가        |
| PUT    | `/api/v1/users/{id}`                 | 사용자 수정        |
| DELETE | `/api/v1/users/{id}`                 | 사용자 삭제        |

### 세션 및 로그 관리 (Mainmenu 5)

| Method | Endpoint                                | 설명                 |
| ------ | --------------------------------------- | -------------------- |
| GET    | `/api/v1/sessions`                      | 모든 세션 조회       |
| GET    | `/api/v1/sessions/{id}`                 | 세션 상세 조회       |
| GET    | `/api/v1/sessions/user/{user_id}`       | 사용자별 세션 조회   |
| GET    | `/api/v1/sessions/project/{project_id}` | 프로젝트별 세션 조회 |
| DELETE | `/api/v1/sessions/{id}`                 | 세션 삭제            |
| GET    | `/api/v1/sessions/{id}/logs`            | 세션 로그 조회       |
| DELETE | `/api/v1/sessions/{id}/logs`            | 세션 로그 전체 삭제  |
| DELETE | `/api/v1/sessions/{id}/logs/{seq}`      | 특정 로그 삭제       |

## 배포 (GitHub Actions + Docker)

### 자동배포 흐름

1. `main` 브랜치에 push
2. GitHub Actions가 자동 실행
3. Docker 이미지 빌드 → Docker Hub에 push
4. SSH로 서버 접속 → 컨테이너 배포

### GitHub Repository Secrets 설정

Repository → Settings → Secrets and variables → Actions에서 설정:

| Secret                | 설명                |
| --------------------- | ------------------- |
| `DOCKER_HUB_USERNAME` | Docker Hub 사용자명 |
| `DOCKER_HUB_PASSWORD` | Docker Hub 비밀번호 |
| `SERVER_HOST`         | 배포 서버 IP/호스트 |
| `SERVER_USERNAME`     | 서버 SSH 사용자명   |
| `SERVER_KEY`          | 서버 SSH 개인키     |
| `DB_HOST`             | Oracle DB 호스트    |
| `DB_PORT`             | Oracle DB 포트      |
| `DB_SERVICE`          | Oracle 서비스명     |
| `DB_USER`             | DB 사용자           |
| `DB_PASSWORD`         | DB 비밀번호         |

### 수동 배포 트리거

GitHub Actions 탭 → Deploy → Run workflow

## 환경변수

| 변수명      | 설명             | 기본값    |
| ----------- | ---------------- | --------- |
| DB_HOST     | Oracle DB 호스트 | localhost |
| DB_PORT     | Oracle DB 포트   | 55554     |
| DB_SERVICE  | Oracle 서비스명  | orclpdb1  |
| DB_USER     | DB 사용자        | llm_admin |
| DB_PASSWORD | DB 비밀번호      | comp322   |
| APP_HOST    | 서버 호스트      | 0.0.0.0   |
| APP_PORT    | 서버 포트        | 8000      |
