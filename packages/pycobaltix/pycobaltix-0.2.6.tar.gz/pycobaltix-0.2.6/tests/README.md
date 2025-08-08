# 테스트 가이드

이 문서는 DATA.GO.KR API의 `getBrTitleInfo` 함수와 관련된 테스트 코드들의 사용법을 안내합니다.

## 🧪 테스트 파일 구성

### 1. 통합 테스트 (Integration Tests)
- **파일**: `integration_test_data_go_kr_api.py`
- **설명**: 실제 API를 호출하는 테스트
- **요구사항**: `DATA_GO_KR_API_KEY` 환경 변수 필요

### 2. 단위 테스트 (Unit Tests)
- **파일**: `unit_test_data_go_kr_api.py`
- **설명**: 모킹을 사용한 API 로직 테스트
- **요구사항**: API 키 불필요

### 3. 실행 예제 (Example Runner)
- **파일**: `test_runner_example.py`
- **설명**: 간단한 API 실행 예제
- **요구사항**: `DATA_GO_KR_API_KEY` 환경 변수 필요

## 🚀 테스트 실행 방법

### 환경 변수 설정 (통합 테스트용)
```bash
export DATA_GO_KR_API_KEY="your_actual_api_key_here"
```

### 1. 모든 테스트 실행
```bash
# 프로젝트 루트에서 실행
pytest tests/

# 커버리지 포함 실행
pytest tests/ --cov=pycobaltix
```

### 2. 단위 테스트만 실행
```bash
pytest tests/unit_test_data_go_kr_api.py -v
```

### 3. 통합 테스트만 실행 (API 키 필요)
```bash
pytest tests/integration_test_data_go_kr_api.py -v
```

### 4. 특정 테스트 함수만 실행
```bash
# getBrTitleInfo 성공 테스트만
pytest tests/integration_test_data_go_kr_api.py::TestDataGOKRAPIIntegration::test_get_br_title_info_success -v

# 단위 테스트의 모킹 테스트만
pytest tests/unit_test_data_go_kr_api.py::TestDataGOKRAPIUnit::test_get_br_title_info_success -v
```

### 5. 마커별 테스트 실행
```bash
# 단위 테스트만
pytest -m unit

# 통합 테스트만
pytest -m integration

# 느린 테스트 제외
pytest -m "not slow"
```

## 📝 간단 실행 예제

실제 API를 테스트해보려면:

```bash
# 환경 변수 설정 후
export DATA_GO_KR_API_KEY="your_api_key"

# 예제 스크립트 실행
python tests/test_runner_example.py
```

## 🧾 테스트 내용

### getBrTitleInfo API 테스트 시나리오

#### 통합 테스트
1. **정상 조회 테스트**: 올바른 파라미터로 API 호출
2. **선택적 파라미터 테스트**: bun, ji 없이 조회
3. **페이지네이션 테스트**: 여러 페이지 조회
4. **잘못된 파라미터 테스트**: 존재하지 않는 지역코드
5. **상세 정보 검증**: 응답 데이터의 필드별 검증
6. **기존 기능 호환성**: getBrExposPubuseAreaInfo 정상 동작 확인

#### 단위 테스트
1. **성공 응답 모킹**: 정상적인 API 응답 시뮬레이션
2. **빈 결과 모킹**: 조회 결과가 없는 경우
3. **HTTP 에러 처리**: 네트워크 오류 상황
4. **재시도 로직**: API 호출 실패 시 재시도 동작
5. **파라미터 전처리**: API 파라미터 준비 로직
6. **API 키 검증**: 환경 변수 및 직접 설정

## 📊 테스트 결과 예시

### 성공적인 테스트 실행
```bash
$ pytest tests/unit_test_data_go_kr_api.py -v

tests/unit_test_data_go_kr_api.py::TestDataGOKRAPIUnit::test_get_br_title_info_success PASSED
tests/unit_test_data_go_kr_api.py::TestDataGOKRAPIUnit::test_get_br_title_info_empty_result PASSED
tests/unit_test_data_go_kr_api.py::TestDataGOKRAPIUnit::test_get_br_title_info_http_error PASSED
tests/unit_test_data_go_kr_api.py::TestDataGOKRAPIUnit::test_get_br_title_info_retry_logic PASSED
tests/unit_test_data_go_kr_api.py::TestDataGOKRAPIUnit::test_prepare_params PASSED
tests/unit_test_data_go_kr_api.py::TestDataGOKRAPIUnit::test_api_key_validation PASSED

6 passed
```

### 실행 예제 결과
```bash
$ python tests/test_runner_example.py

✅ DATA.GO.KR API 클라이언트가 생성되었습니다.

🔍 건축물대장 표제부 조회 테스트 시작...
   - 시군구코드: 11350
   - 법정동코드: 10200
   - 번지: 0923-0000

✅ API 호출 성공!
   - 총 1건의 데이터가 조회되었습니다.
   - 현재 페이지: 1/1
   - 다음 페이지 존재 여부: False

📋 조회된 건축물 정보:
   1. 건물 정보:
      - 순번: 1
      - 대지위치: 서울특별시 노원구 상계동 923번지
      - 건물명: 상계주공아파트
      - 도로명주소: 서울특별시 노원구 한글비석로 100
      ...
```

## ⚠️ 주의사항

1. **API 키 보안**: 실제 API 키는 환경 변수로 관리하고 코드에 하드코딩하지 마세요
2. **API 호출 제한**: 실제 API는 호출 한도가 있을 수 있으니 과도한 테스트는 피하세요
3. **테스트 데이터**: 테스트에 사용된 지역코드는 실제 존재하는 지역이므로 실제 데이터가 조회될 수 있습니다
4. **환경별 차이**: 개발/운영 환경에 따라 API 응답이 다를 수 있습니다

## 🔧 문제 해결

### 자주 발생하는 문제들

#### 1. API 키 오류
```
ValueError: DATA_GO_KR_API_KEY 환경 변수가 설정되지 않았습니다
```
**해결방법**: 환경 변수를 올바르게 설정하세요

#### 2. 네트워크 오류
```
httpx.ConnectError: connection failed
```
**해결방법**: 인터넷 연결과 API 서버 상태를 확인하세요

#### 3. API 응답 오류
```
httpx.HTTPStatusError: 500 Internal Server Error
```
**해결방법**: API 파라미터가 올바른지 확인하고, API 서버 상태를 점검하세요 