from enum import Enum


class ResponseFormat(str, Enum):
    """Vworld API 응답 포맷 모음"""

    JSON = "json"
    XML = "xml"
