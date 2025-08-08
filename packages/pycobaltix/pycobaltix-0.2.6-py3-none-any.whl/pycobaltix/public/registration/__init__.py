"""
Registration(등기) 공개 API 모듈

노출 대상:
- search_real_estate: 등기 검색 함수
- RealEstateInfo, PropertyType, RegistrationStatus: 데이터 모델 및 열거형
- RegistryParser, RegistryDocument, RegistryProperty, LandRight, OwnershipRecord, RightRecord: PDF 파서 및 데이터 구조
"""

from .check import search_real_estate
from .pdf_parsing import (
    LandRight,
    OwnershipRecord,
    RegistryDocument,
    RegistryParser,
    RegistryProperty,
    RightRecord,
)
from .registration import PropertyType, RealEstateInfo, RegistrationStatus

__all__ = [
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
