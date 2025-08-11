"""
응답 모델 테스트
"""

from pycobaltix import (
    APIResponse,
    ErrorResponse,
    PaginatedAPIResponse,
    PaginationInfo,
)


def test_pagination_info():
    """PaginationInfo 모델 테스트"""
    # 기본값으로 생성
    pagination = PaginationInfo()
    assert pagination.currentPage == 1
    assert pagination.totalPages == 1
    assert pagination.totalCount == 0
    assert pagination.count == 10
    assert pagination.hasNext is False
    assert pagination.hasPrevious is False

    # 값을 지정하여 생성
    pagination = PaginationInfo(
        currentPage=2,
        totalPages=5,
        totalCount=100,
        count=20,
        hasNext=True,
        hasPrevious=True,
    )
    assert pagination.currentPage == 2
    assert pagination.totalPages == 5
    assert pagination.totalCount == 100
    assert pagination.count == 20
    assert pagination.hasNext is True
    assert pagination.hasPrevious is True


def test_api_response():
    """APIResponse 모델 테스트"""
    # 기본값으로 생성
    response = APIResponse()
    assert response.success is True
    assert response.message == "success"
    assert response.status == 200
    assert response.data is None

    # 데이터 추가
    response = APIResponse(data={"name": "홍길동", "age": 30})
    assert response.data == {"name": "홍길동", "age": 30}

    # 실패 응답
    response = APIResponse(
        success=False,
        message="사용자를 찾을 수 없습니다",
        status=404,
    )
    assert response.success is False
    assert response.message == "사용자를 찾을 수 없습니다"
    assert response.status == 404


def test_paginated_api_response():
    """PaginatedAPIResponse 모델 테스트"""
    # 페이지네이션 정보 생성
    pagination = PaginationInfo(
        currentPage=1,
        totalPages=5,
        totalCount=50,
        count=10,
        hasNext=True,
        hasPrevious=False,
    )

    # 페이지네이션된 API 응답 생성
    response = PaginatedAPIResponse(
        data=[{"name": "홍길동"}, {"name": "김철수"}],
        pagination=pagination,
    )

    assert response.success is True
    assert response.message == "success"
    assert response.status == 200
    assert len(response.data) == 2
    assert response.data[0] == {"name": "홍길동"}
    assert response.data[1] == {"name": "김철수"}
    assert response.pagination.currentPage == 1
    assert response.pagination.totalPages == 5
    assert response.pagination.totalCount == 50
    assert response.pagination.hasNext is True


def test_error_response():
    """ErrorResponse 모델 테스트"""
    # 기본값으로 생성
    error = ErrorResponse()
    assert error.success is False
    assert error.message == "error"
    assert error.status == 400
    assert error.error is None

    # 에러 정보 추가
    error = ErrorResponse(
        message="입력 데이터가 유효하지 않습니다",
        status=422,
        error="ValidationError",
    )
    assert error.success is False
    assert error.message == "입력 데이터가 유효하지 않습니다"
    assert error.status == 422
    assert error.error == "ValidationError"
