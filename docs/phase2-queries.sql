-- ============================================
-- Phase 2 SQL Queries - 상재 담당
-- ============================================
-- 담당 엔티티: MODEL, MODEL_CONFIG, DEPLOYMENTS, DATASET, PROMPT_TEMPLATE
-- 총 10개 Query Type 작성
-- ============================================

-- ============================================
-- Type 1: Single-table query (Selection + Projection)
-- ============================================
-- 설명: 활성 상태인 프로덕션 배포 환경의 서버명과 GPU 개수 조회
-- 목적: 현재 운영중인 프로덕션 서버 리소스 파악

SELECT server_name, gpu_count, environment, status
FROM DEPLOYMENTS
WHERE environment = 'production'
  AND status = 'active';

-- ============================================
-- Type 2: Multi-way join with join predicates in WHERE
-- ============================================
-- 설명: 각 모델이 어떤 데이터셋으로 어느 환경에 배포되었는지 조회
-- 목적: 모델-데이터셋-배포 환경의 전체 매핑 관계 파악

SELECT
    M.model_name AS model_name,
    M.model_type AS model_type,
    D.server_name AS server_name,
    D.environment AS environment,
    DS.learning_type AS dataset_learning_type,
    DS.s3_path AS dataset_path
FROM MODEL M, DEPLOYMENTS D, DATASET DS
WHERE M.model_id = D.model_id
  AND D.dataset_id = DS.dataset_id;

-- ============================================
-- Type 3: Aggregation + multi-way join + GROUP BY
-- ============================================
-- 설명: 각 모델별로 설정 개수, 배포 개수를 집계
-- 목적: 모델별 활용도 및 설정 다양성 분석

SELECT
    M.model_name,
    M.model_type,
    COUNT(DISTINCT MC.config_id) AS config_count,
    COUNT(DISTINCT D.deployment_id) AS deployment_count
FROM MODEL M, MODEL_CONFIG MC, DEPLOYMENTS D
WHERE M.model_id = MC.model_id
  AND M.model_id = D.model_id
GROUP BY M.model_name, M.model_type;

-- ============================================
-- Type 4: Subquery
-- ============================================
-- 설명: 평균보다 많은 GPU를 사용하는 배포 환경 조회
-- 목적: 고사양 배포 환경 식별 및 리소스 최적화

SELECT
    deployment_id,
    server_name,
    gpu_count,
    environment
FROM DEPLOYMENTS
WHERE gpu_count > (
    SELECT AVG(gpu_count)
    FROM DEPLOYMENTS
);

-- ============================================
-- Type 5: EXISTS를 포함하는 Subquery
-- ============================================
-- 설명: 실제로 배포에 사용된 적이 있는 데이터셋만 조회
-- 목적: 활용되고 있는 데이터셋 파악 (사용되지 않는 데이터셋 제외)

SELECT
    dataset_id,
    learning_type,
    description,
    created_at
FROM DATASET DS
WHERE EXISTS (
    SELECT 1
    FROM DEPLOYMENTS D
    WHERE D.dataset_id = DS.dataset_id
);

-- ============================================
-- Type 6: Selection + Projection + IN predicates
-- ============================================
-- 설명: 특정 작업 카테고리(요약, 번역, 코딩)에 해당하는 프롬프트 템플릿 조회
-- 목적: 주요 작업 유형별 템플릿 목록 확인

SELECT
    template_name,
    task_category,
    version,
    usage_count
FROM PROMPT_TEMPLATE
WHERE task_category IN ('요약', '번역', '코딩')
ORDER BY usage_count DESC;

-- ============================================
-- Type 7: In-line view를 활용한 Query
-- ============================================
-- 설명: 모델별 평균 temperature 설정값과 해당 모델의 배포 개수 조회
-- 목적: 모델별 설정 경향과 활용도 동시 분석

SELECT
    M.model_name,
    AVG_CONFIG.avg_temperature,
    AVG_CONFIG.config_count,
    DEPLOY_COUNT.deployment_count
FROM MODEL M,
    (SELECT
        model_id,
        AVG(temperature) AS avg_temperature,
        COUNT(*) AS config_count
     FROM MODEL_CONFIG
     GROUP BY model_id) AVG_CONFIG,
    (SELECT
        model_id,
        COUNT(*) AS deployment_count
     FROM DEPLOYMENTS
     GROUP BY model_id) DEPLOY_COUNT
WHERE M.model_id = AVG_CONFIG.model_id
  AND M.model_id = DEPLOY_COUNT.model_id;

-- ============================================
-- Type 8: Multi-way join + ORDER BY
-- ============================================
-- 설명: 모델-설정-배포 관계를 조회하고 GPU 수 기준 내림차순 정렬
-- 목적: 고사양 배포부터 순서대로 모델 설정 정보 파악

SELECT
    M.model_name,
    MC.config_name,
    MC.max_tokens,
    MC.temperature,
    D.server_name,
    D.gpu_count,
    D.environment
FROM MODEL M, MODEL_CONFIG MC, DEPLOYMENTS D
WHERE M.model_id = MC.model_id
  AND M.model_id = D.model_id
ORDER BY D.gpu_count DESC, M.model_name ASC;

-- ============================================
-- Type 9: Aggregation + multi-way join + GROUP BY + ORDER BY
-- ============================================
-- 설명: 환경별(개발/테스트/프로덕션) 평균 GPU 수와 배포 개수 집계 후 정렬
-- 목적: 환경별 리소스 사용량 분석 및 비교

SELECT
    D.environment,
    COUNT(DISTINCT D.deployment_id) AS deployment_count,
    AVG(D.gpu_count) AS avg_gpu_count,
    COUNT(DISTINCT M.model_id) AS unique_models
FROM DEPLOYMENTS D, MODEL M
WHERE D.model_id = M.model_id
GROUP BY D.environment
ORDER BY avg_gpu_count DESC;

-- ============================================
-- Type 10: SET operation (MINUS)
-- ============================================
-- 설명: 전체 모델 중 아직 배포되지 않은 모델 조회
-- 목적: 등록은 되었지만 실제 사용되지 않는 모델 식별

SELECT
    model_id,
    model_name,
    model_type
FROM MODEL
MINUS
SELECT
    M.model_id,
    M.model_name,
    M.model_type
FROM MODEL M, DEPLOYMENTS D
WHERE M.model_id = D.model_id;

-- ============================================
-- 추가 Query 예시 (필요시 사용)
-- ============================================

-- [추가 1] 사용 횟수가 가장 많은 상위 5개 프롬프트 템플릿
SELECT
    template_name,
    task_category,
    usage_count,
    version
FROM PROMPT_TEMPLATE
WHERE ROWNUM <= 5
ORDER BY usage_count DESC;

-- [추가 2] 각 데이터셋이 몇 개의 배포에 사용되었는지 집계
SELECT
    DS.dataset_id,
    DS.learning_type,
    COUNT(D.deployment_id) AS used_in_deployments
FROM DATASET DS
LEFT JOIN DEPLOYMENTS D ON DS.dataset_id = D.dataset_id
GROUP BY DS.dataset_id, DS.learning_type
HAVING COUNT(D.deployment_id) > 0;

-- [추가 3] 모델별 최고/최저 temperature 설정값
SELECT
    M.model_name,
    MAX(MC.temperature) AS max_temp,
    MIN(MC.temperature) AS min_temp,
    AVG(MC.temperature) AS avg_temp
FROM MODEL M, MODEL_CONFIG MC
WHERE M.model_id = MC.model_id
GROUP BY M.model_name;

-- ============================================
-- 작성일: 2025-10-13
-- 작성자: 이상재
-- ============================================