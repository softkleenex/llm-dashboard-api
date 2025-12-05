package com.llm.dashboard.dao;

import com.llm.dashboard.db.DatabaseConnection;

import java.sql.*;

/**
 * 통계/분석 쿼리를 담당하는 DAO 클래스
 * Phase2 쿼리들을 구현
 */
public class StatisticsDAO {
    
    // PART 2: 모델 및 배포 관련 통계
    
    // Query 1: 배포 환경 조회 (동적 필터)
    public void query1_ActiveProductionDeployments(String environment, String status) {
        StringBuilder sql = new StringBuilder(
            "SELECT server_name, gpu_count, environment, status " +
            "FROM DEPLOYMENTS WHERE 1=1");
        
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        if (environment != null && !environment.isEmpty()) {
            sql.append(" AND environment = ?");
            params.add(environment);
        }
        
        if (status != null && !status.isEmpty()) {
            sql.append(" AND status = ?");
            params.add(status);
        }
        
        executeAndPrintQueryWithParams(sql.toString(), new String[]{"서버명", "GPU수", "환경", "상태"}, params.toArray());
    }
    
    public void query2_ModelDatasetDeploymentMapping() {
        String sql = "SELECT M.model_name AS model_name, M.model_type AS model_type, " +
                     "D.server_name AS server_name, D.environment AS environment, " +
                     "DS.learning_type AS dataset_learning_type, DS.s3_path AS dataset_path " +
                     "FROM MODEL M, DEPLOYMENTS D, DATASET DS " +
                     "WHERE M.model_id = D.model_id AND D.dataset_id = DS.dataset_id";
        
        executeAndPrintQuery(sql, "모델명", "모델유형", "서버명", "환경", "학습유형", "데이터셋경로");
    }
    
    public void query3_ModelConfigAndDeploymentCount() {
        String sql = "SELECT M.model_name, M.model_type, " +
                     "COUNT(DISTINCT MC.config_id) AS config_count, " +
                     "COUNT(DISTINCT D.deployment_id) AS deployment_count " +
                     "FROM MODEL M, MODEL_CONFIG MC, DEPLOYMENTS D " +
                     "WHERE M.model_id = MC.model_id AND M.model_id = D.model_id " +
                     "GROUP BY M.model_name, M.model_type";
        
        executeAndPrintQuery(sql, "모델명", "모델유형", "설정개수", "배포개수");
    }
    
    // Query 4: GPU 수 기준 배포 조회 (동적 필터)
    public void query4_DeploymentsAboveAvgGPU(Integer minGpuCount, Boolean useAverage) {
        StringBuilder sql = new StringBuilder(
            "SELECT deployment_id, server_name, gpu_count, environment " +
            "FROM DEPLOYMENTS WHERE 1=1");
        
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        if (useAverage != null && useAverage) {
            // 평균보다 많은 경우
            sql.append(" AND gpu_count > (SELECT AVG(gpu_count) FROM DEPLOYMENTS)");
        } else if (minGpuCount != null && minGpuCount > 0) {
            // 최소 GPU 수 지정
            sql.append(" AND gpu_count >= ?");
            params.add(minGpuCount);
        }
        
        executeAndPrintQueryWithParams(sql.toString(), new String[]{"배포ID", "서버명", "GPU수", "환경"}, params.toArray());
    }
    
    public void query5_DatasetsUsedInDeployments() {
        String sql = "SELECT dataset_id, learning_type, description, created_at " +
                     "FROM DATASET DS " +
                     "WHERE EXISTS (SELECT 1 FROM DEPLOYMENTS D WHERE D.dataset_id = DS.dataset_id)";
        
        executeAndPrintQuery(sql, "데이터셋ID", "학습유형", "설명", "생성일시");
    }
    
    // Query 6: 프롬프트 템플릿 카테고리 조회 (동적 필터)
    public void query6_PromptTemplatesByCategory(java.util.List<String> categories) {
        StringBuilder sql = new StringBuilder(
            "SELECT template_name, task_category, version, usage_count " +
            "FROM PROMPT_TEMPLATE WHERE 1=1");
        
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        if (categories != null && !categories.isEmpty()) {
            sql.append(" AND task_category IN (");
            for (int i = 0; i < categories.size(); i++) {
                if (i > 0) sql.append(", ");
                sql.append("?");
                params.add(categories.get(i));
            }
            sql.append(")");
        }
        
        sql.append(" ORDER BY usage_count DESC");
        
        executeAndPrintQueryWithParams(sql.toString(), new String[]{"템플릿명", "작업카테고리", "버전", "사용횟수"}, params.toArray());
    }
    
    public void query7_ModelAvgTemperatureAndDeploymentCount() {
        String sql = "SELECT M.model_name, AVG_CONFIG.avg_temperature, " +
                     "AVG_CONFIG.config_count, DEPLOY_COUNT.deployment_count " +
                     "FROM MODEL M, " +
                     "(SELECT model_id, AVG(temperature) AS avg_temperature, COUNT(*) AS config_count " +
                     " FROM MODEL_CONFIG GROUP BY model_id) AVG_CONFIG, " +
                     "(SELECT model_id, COUNT(*) AS deployment_count " +
                     " FROM DEPLOYMENTS GROUP BY model_id) DEPLOY_COUNT " +
                     "WHERE M.model_id = AVG_CONFIG.model_id AND M.model_id = DEPLOY_COUNT.model_id";
        
        executeAndPrintQuery(sql, "모델명", "평균Temperature", "설정개수", "배포개수");
    }
    
    // Query 8 (2-Type8): 모델-설정-배포 관계 (동적 정렬)
    // 주의: ORDER BY 절의 컬럼명은 PreparedStatement의 ? 바인딩을 사용할 수 없음
    // (컬럼명은 SQL 구문의 일부이므로 문자열 연결 필요)
    // 따라서 화이트리스트 검증을 통해 안전하게 처리
    public void query8_ModelConfigDeploymentByGPU(String orderBy, String orderDir) {
        // 화이트리스트로 안전한 컬럼만 허용
        String[] allowedColumns = {"gpu_count", "temperature", "max_tokens", "model_name"};
        String safeOrderBy = "gpu_count"; // 기본값
        
        if (orderBy != null && !orderBy.isEmpty()) {
            for (String col : allowedColumns) {
                if (col.equalsIgnoreCase(orderBy)) {
                    safeOrderBy = col;
                    break;
                }
            }
        }
        
        String safeOrderDir = "DESC";
        if (orderDir != null && orderDir.equalsIgnoreCase("ASC")) {
            safeOrderDir = "ASC";
        }
        
        String sql = "SELECT M.model_name, MC.config_name, MC.max_tokens, MC.temperature, " +
                     "D.server_name, D.gpu_count, D.environment " +
                     "FROM MODEL M, MODEL_CONFIG MC, DEPLOYMENTS D " +
                     "WHERE M.model_id = MC.model_id AND M.model_id = D.model_id " +
                     "ORDER BY D." + safeOrderBy + " " + safeOrderDir + ", M.model_name ASC";
        
        executeAndPrintQuery(sql, "모델명", "설정명", "최대토큰", "Temperature", "서버명", "GPU수", "환경");
    }
    
    // Query 9 (2-Type9): 환경별 평균 GPU/배포 수 (동적 필터)
    public void query9_EnvironmentAvgGPUAndDeploymentCount(String environment, Double minAvgGpu) {
        StringBuilder sql = new StringBuilder(
            "SELECT D.environment, COUNT(DISTINCT D.deployment_id) AS deployment_count, " +
            "AVG(D.gpu_count) AS avg_gpu_count, COUNT(DISTINCT M.model_id) AS unique_models " +
            "FROM DEPLOYMENTS D, MODEL M " +
            "WHERE D.model_id = M.model_id");
        
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        if (environment != null && !environment.isEmpty()) {
            sql.append(" AND D.environment = ?");
            params.add(environment);
        }
        
        sql.append(" GROUP BY D.environment");
        
        if (minAvgGpu != null && minAvgGpu > 0) {
            sql.append(" HAVING AVG(D.gpu_count) >= ?");
            params.add(minAvgGpu);
        }
        
        sql.append(" ORDER BY avg_gpu_count DESC");
        
        executeAndPrintQueryWithParams(sql.toString(), new String[]{"환경", "배포개수", "평균GPU수", "고유모델수"}, params.toArray());
    }
    
    public void query10_UndeployedModels() {
        String sql = "SELECT model_id, model_name, model_type " +
                     "FROM MODEL " +
                     "MINUS " +
                     "SELECT M.model_id, M.model_name, M.model_type " +
                     "FROM MODEL M, DEPLOYMENTS D " +
                     "WHERE M.model_id = D.model_id";
        
        executeAndPrintQuery(sql, "모델ID", "모델명", "모델유형");
    }
    
    // PART 3: 사용자 및 세션 관련 통계
    
    // Query 11 (3-Type1): 역할별 사용자 조회 (동적 프레디킷)
    public void query11_UsersByRole(String role) {
        String sql = "SELECT user_id, user_name, user_email " +
                     "FROM \"USER\" " +
                     "WHERE role = ?";
        
        executeAndPrintQueryWithParams(sql, new String[]{"사용자ID", "이름", "이메일"}, role);
    }
    
    // Query 12 (3-Type2): 프로젝트 생성자/부서 (동적 필터)
    public void query12_ProjectCreatorAndDepartment(String departmentName, String creatorUserName) {
        StringBuilder sql = new StringBuilder(
            "SELECT U.user_name, D.department_name, P.project_name " +
            "FROM \"USER\" U, DEPARTMENT D, PROJECT P " +
            "WHERE U.department_id = D.department_id AND P.creator_user_id = U.user_id");
        
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        if (departmentName != null && !departmentName.isEmpty()) {
            sql.append(" AND D.department_name = ?");
            params.add(departmentName);
        }
        if (creatorUserName != null && !creatorUserName.isEmpty()) {
            sql.append(" AND U.user_name = ?");
            params.add(creatorUserName);
        }
        
        executeAndPrintQueryWithParams(sql.toString(), new String[]{"사용자명", "부서명", "프로젝트명"}, params.toArray());
    }
    
    // Query 13 (3-Type3): 부서별 프로젝트 수 (동적 필터)
    public void query13_ProjectsByDepartment(String departmentName, Integer minCount) {
        StringBuilder sql = new StringBuilder(
            "SELECT D.department_name, COUNT(P.project_id) AS project_count " +
            "FROM DEPARTMENT D, PROJECT P " +
            "WHERE D.department_id = P.department_id");
        
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        if (departmentName != null && !departmentName.isEmpty()) {
            sql.append(" AND D.department_name = ?");
            params.add(departmentName);
        }
        
        sql.append(" GROUP BY D.department_name");
        
        if (minCount != null && minCount > 0) {
            sql.append(" HAVING COUNT(P.project_id) >= ?");
            params.add(minCount);
        }
        
        executeAndPrintQueryWithParams(sql.toString(), new String[]{"부서명", "프로젝트수"}, params.toArray());
    }
    
    // Query 14 (3-Type4): 특정 부서 소속 유저 (동적 프레디킷)
    public void query14_UsersByDepartment(String departmentName) {
        String sql = "SELECT user_id, user_name " +
                     "FROM \"USER\" " +
                     "WHERE department_id = (SELECT department_id FROM DEPARTMENT WHERE department_name = ?)";
        
        executeAndPrintQueryWithParams(sql, new String[]{"사용자ID", "이름"}, departmentName);
    }
    
    // Query 15: 특정 상태 세션 보유 유저 조회 (동적 필터)
    public void query15_UsersWithActiveSessions(String sessionStatus) {
        StringBuilder sql = new StringBuilder(
            "SELECT U.user_id, U.user_name " +
            "FROM \"USER\" U " +
            "WHERE EXISTS (SELECT 1 FROM SESSIONS S WHERE S.user_id = U.user_id");
        
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        if (sessionStatus != null && !sessionStatus.isEmpty()) {
            sql.append(" AND S.status = ?");
            params.add(sessionStatus);
        }
        
        sql.append(")");
        
        executeAndPrintQueryWithParams(sql.toString(), new String[]{"사용자ID", "이름"}, params.toArray());
    }
    
    public void query16_ProjectsWithManagers() {
        String sql = "SELECT project_id, project_name " +
                     "FROM PROJECT " +
                     "WHERE department_id IN (SELECT department_id FROM DEPARTMENT WHERE manager_user_id IS NOT NULL)";
        
        executeAndPrintQuery(sql, "프로젝트ID", "프로젝트명");
    }
    
    // Query 17: 최소 세션 수 이상 보유 유저 조회 (동적 필터)
    public void query17_UsersWith5OrMoreSessions(Integer minSessionCount) {
        int minCount = (minSessionCount != null && minSessionCount > 0) ? minSessionCount : 5;
        
        String sql = "SELECT U.user_id, U.user_name, S.session_count " +
                     "FROM (SELECT user_id, COUNT(*) AS session_count FROM SESSIONS GROUP BY user_id) S, \"USER\" U " +
                     "WHERE S.user_id = U.user_id AND session_count >= ?";
        
        executeAndPrintQueryWithParams(sql, new String[]{"사용자ID", "이름", "세션수"}, minCount);
    }
    
    // Query 18 (3-Type8): 세션 로그 토큰 사용량 순 (동적 필터)
    public void query18_SessionLogsByTokenUsage(String dateFrom, String dateTo, String userName, Integer topN) {
        StringBuilder sql = new StringBuilder(
            "SELECT SL.session_id, SL.log_sequence, U.user_name, SL.token_used " +
            "FROM SESSION_LOGS SL, SESSIONS S, \"USER\" U " +
            "WHERE SL.session_id = S.session_id AND S.user_id = U.user_id");
        
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        if (dateFrom != null && !dateFrom.isEmpty()) {
            sql.append(" AND SL.request_time >= TO_DATE(?, 'YYYY-MM-DD')");
            params.add(dateFrom);
        }
        if (dateTo != null && !dateTo.isEmpty()) {
            sql.append(" AND SL.request_time <= TO_DATE(?, 'YYYY-MM-DD')");
            params.add(dateTo);
        }
        if (userName != null && !userName.isEmpty()) {
            sql.append(" AND U.user_name = ?");
            params.add(userName);
        }
        
        sql.append(" ORDER BY SL.token_used DESC");
        
        // 주의: FETCH FIRST N ROWS ONLY의 N은 PreparedStatement의 ? 바인딩을 사용할 수 없음
        // (Oracle 제약사항) 따라서 Integer 타입으로 검증 후 문자열 연결 사용
        if (topN != null && topN > 0) {
            sql.append(" FETCH FIRST ").append(topN).append(" ROWS ONLY");
        }
        
        executeAndPrintQueryWithParams(sql.toString(), new String[]{"세션ID", "로그순번", "사용자명", "토큰사용량"}, params.toArray());
    }
    
    // Query 19 (3-Type9): 유저별 세션 수 TopN (동적 제한)
    // 주의: FETCH FIRST N ROWS ONLY의 N은 PreparedStatement의 ? 바인딩을 사용할 수 없음
    // (Oracle 제약사항) 따라서 Integer 타입으로 검증 후 문자열 연결 사용
    public void query19_UserSessionCount(Integer topN) {
        StringBuilder sql = new StringBuilder(
            "SELECT U.user_name, COUNT(S.session_id) AS total_sessions " +
            "FROM \"USER\" U, SESSIONS S " +
            "WHERE U.user_id = S.user_id " +
            "GROUP BY U.user_name " +
            "ORDER BY total_sessions DESC");
        
        if (topN != null && topN > 0) {
            sql.append(" FETCH FIRST ").append(topN).append(" ROWS ONLY");
        }
        
        executeAndPrintQuery(sql.toString(), "사용자명", "총세션수");
    }
    
    // Query 20: 특정 역할 유저와 부서 관리자 통합 조회 (동적 필터)
    public void query20_DataScientistsAndManagers(String role) {
        StringBuilder sql = new StringBuilder("SELECT user_id FROM \"USER\" WHERE 1=1");
        
        java.util.List<Object> params = new java.util.ArrayList<>();
        
        if (role != null && !role.isEmpty()) {
            sql.append(" AND role = ?");
            params.add(role);
        }
        
        sql.append(" UNION SELECT manager_user_id FROM DEPARTMENT WHERE manager_user_id IS NOT NULL");
        
        executeAndPrintQueryWithParams(sql.toString(), new String[]{"사용자ID"}, params.toArray());
    }
    
    /**
     * 쿼리를 실행하고 결과를 출력하는 헬퍼 메서드 (Statement 사용)
     */
    private void executeAndPrintQuery(String sql, String... columnHeaders) {
        // SQL 출력 (디버깅용)
        System.out.println("\n[실행 SQL]");
        System.out.println(sql);
        
        try (Connection conn = DatabaseConnection.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            printResultSet(rs, columnHeaders);
            
        } catch (SQLException e) {
            System.err.println("쿼리 실행 오류: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * PreparedStatement를 사용하여 쿼리를 실행하고 결과를 출력하는 헬퍼 메서드
     * @param sql SQL 쿼리 (PreparedStatement 형식)
     * @param columnHeaders 컬럼 헤더들
     * @param params SQL 파라미터들 (null이 아닌 값만 설정됨)
     */
    private void executeAndPrintQueryWithParams(String sql, String[] columnHeaders, Object... params) {
        // SQL 출력 (디버깅용)
        System.out.println("\n[실행 SQL]");
        System.out.println(sql);
        
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            // 파라미터 설정 (null이 아닌 값만)
            int paramIndex = 1;
            for (Object param : params) {
                if (param != null) {
                    if (param instanceof String) {
                        pstmt.setString(paramIndex++, (String) param);
                    } else if (param instanceof Integer) {
                        pstmt.setInt(paramIndex++, (Integer) param);
                    } else if (param instanceof Double) {
                        pstmt.setDouble(paramIndex++, (Double) param);
                    }
                }
            }
            
            try (ResultSet rs = pstmt.executeQuery()) {
                printResultSet(rs, columnHeaders);
            }
            
        } catch (SQLException e) {
            System.err.println("쿼리 실행 오류: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * ResultSet의 결과를 출력하는 공통 메서드
     */
    private void printResultSet(ResultSet rs, String... columnHeaders) throws SQLException {
        // 컬럼 헤더 출력
        System.out.println();
        int colCount = columnHeaders.length;
        StringBuilder separator = new StringBuilder();
        for (int i = 0; i < colCount; i++) {
            separator.append("----------------------------------------------------------------");
        }
        System.out.println(separator.toString());
        
        // 헤더 출력
        System.out.printf("%-15s", columnHeaders[0]);
        for (int i = 1; i < colCount; i++) {
            System.out.printf(" %-30s", columnHeaders[i]);
        }
        System.out.println();
        System.out.println(separator.toString());
        
        // 결과 출력
        int rowCount = 0;
        while (rs.next()) {
            rowCount++;
            for (int i = 1; i <= colCount; i++) {
                Object value = rs.getObject(i);
                String strValue = value != null ? value.toString() : "없음";
                if (i == 1) {
                    System.out.printf("%-15s", strValue.length() > 15 ? strValue.substring(0, 12) + "..." : strValue);
                } else {
                    System.out.printf(" %-30s", strValue.length() > 30 ? strValue.substring(0, 27) + "..." : strValue);
                }
            }
            System.out.println();
        }
        
        System.out.println(separator.toString());
        System.out.println("총 " + rowCount + "개의 행이 조회되었습니다.");
    }
}

