"""
pycobaltix - API 응답 형식을 정의하는 유틸리티 패키지
"""

__version__ = "0.1.0"

from pycobaltix.public import AsyncVWorldAPI, BuildingInfo, ResponseFormat, VWorldAPI
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
]
