"""
pycobaltix - API 응답 형식을 정의하는 유틸리티 패키지
"""

__version__ = "0.1.0"

from pycobaltix.public import AsyncVWorldAPI, BuildingInfo, ResponseFormat, VWorldAPI

# Registration(등기) 관련 공개 API와 데이터 모델을 최상위에서 재노출
from pycobaltix.public.registration import (
    LandRight,
    OwnershipRecord,
    PropertyType,
    RealEstateInfo,
    RegistrationStatus,
    RegistryDocument,
    RegistryParser,
    RegistryProperty,
    RightRecord,
    search_real_estate,
)
from pycobaltix.schemas.responses import (
    APIResponse,
    ErrorResponse,
    PaginatedAPIResponse,
    PaginationInfo,
)
from pycobaltix.slack import SlackBot, SlackWebHook

__all__ = [
    "APIResponse",
    "PaginatedAPIResponse",
    "PaginationInfo",
    "ErrorResponse",
    "SlackWebHook",
    "SlackBot",
    # V-World API
    "VWorldAPI",
    "AsyncVWorldAPI",
    "BuildingInfo",
    "ResponseFormat",
    # Registration API
    "search_real_estate",
    "RealEstateInfo",
    "PropertyType",
    "RegistrationStatus",
    "RegistryParser",
    "RegistryDocument",
    "RegistryProperty",
    "LandRight",
    "OwnershipRecord",
    "RightRecord",
]
