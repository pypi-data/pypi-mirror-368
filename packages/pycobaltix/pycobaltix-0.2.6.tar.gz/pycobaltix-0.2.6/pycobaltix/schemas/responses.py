"""
API 응답 형식을 정의하는 모델들
"""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationInfo(BaseModel):
    """페이지네이션 메타 정보를 위한 모델"""

    currentPage: int = Field(default=1, description="현재 페이지 번호")
    totalPages: int = Field(default=1, description="전체 페이지 수")
    totalCount: int = Field(default=0, description="전체 아이템 수")
    count: int = Field(default=10, description="페이지당 아이템 수")
    hasNext: bool = Field(default=False, description="다음 페이지 존재 여부")
    hasPrevious: bool = Field(default=False, description="이전 페이지 존재 여부")


class APIResponse(BaseModel, Generic[T]):
    """기본 API 응답 형식"""

    success: bool = Field(default=True, description="성공 여부")
    message: str = Field(default="success", description="메시지")
    status: int = Field(default=200, description="상태 코드")
    data: Optional[T] = Field(default=None, description="데이터")


class PaginatedAPIResponse(APIResponse, Generic[T]):
    """페이지네이션된 API 응답 형식"""

    data: List[T] = Field(default=[], description="데이터 목록")
    pagination: PaginationInfo = Field(..., description="페이지네이션 정보")


class ErrorResponse(BaseModel):
    """에러 응답 형식"""

    success: bool = Field(default=False, description="성공 여부")
    message: str = Field(default="error", description="메시지")
    status: int = Field(default=400, description="상태 코드")
    error: Optional[str] = Field(default=None, description="에러 코드")
