# PyCobaltix

API 응답 형식을 정의하는 유틸리티 패키지입니다.

## 설치 방법

uv를 사용하여 설치:

```bash
uv pip install pycobaltix
```

또는 pip를 사용하여 설치:

```bash
pip install pycobaltix
```

## 사용 방법

### 기본 API 응답 사용하기

```python
from pycobaltix import APIResponse

# 일반 데이터 반환
response = APIResponse(data={"name": "홍길동", "age": 30})

# 성공 응답이 아닌 경우
response = APIResponse(success=False, message="사용자를 찾을 수 없습니다", status=404)
```

### 페이지네이션 API 응답 사용하기

```python
from pycobaltix import PaginatedAPIResponse, PaginationInfo

# 페이지네이션 정보 생성
pagination = PaginationInfo(
    currentPage=1,
    totalPages=5,
    totalCount=50,
    count=10,
    hasNext=True,
    hasPrevious=False
)

# 페이지네이션된 API 응답 생성
response = PaginatedAPIResponse(
    data=[{"name": "홍길동"}, {"name": "김철수"}],
    pagination=pagination
)
```

### 에러 응답 사용하기

```python
from pycobaltix import ErrorResponse

# 에러 응답 생성
error_response = ErrorResponse(
    message="입력 데이터가 유효하지 않습니다",
    status=400,
    error="ValidationError"
)
```

## 개발 환경 설정

개발을 위한 환경 설정은 다음과 같이 합니다:

```bash
# 저장소 클론
git clone https://github.com/username/pycobaltix.git
cd pycobaltix

# 개발 환경 설정 (uv 사용)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## 라이선스

MIT 라이선스
