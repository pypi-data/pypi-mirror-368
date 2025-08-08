from dataclasses import dataclass
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RegistrationStatus(str, Enum):
    """등기 기록 상태"""

    ALL = "all"
    CURRENT = "현행"
    CLOSED = "폐쇄"


class PropertyType(str, Enum):
    """부동산 유형"""

    ALL = "all"
    COMBINED_BUILDING = "집합건물"
    BUILDING = "건물"
    LAND = "토지"


@dataclass
class RealEstateInfo(BaseModel):
    """부동산 등기 정보 모델 - 직관적인 필드명 사용"""

    # 주소 관련 정보
    full_road_address: str = Field(alias="rd_addr_detail", description="전체 주소")
    road_address: str = Field(alias="rd_addr", description="도로명 주소")
    jibun_address: str = Field(alias="real_indi_cont", description="지번 주소")
    detailed_jibun_address: str = Field(
        alias="real_indi_cont_detail", description="상세 지번 주소"
    )
    sido: str = Field(alias="sido", description="시도")

    # 건물 정보
    building_name: str = Field(alias="buld_name", description="건물명")
    dong: str = Field(alias="buld_no_buld", description="동 번호")
    ho: str = Field(alias="buld_no_room", description="호수")
    floor: str = Field(alias="buld_no_floor", description="층수")
    road_main_building_number: str = Field(
        alias="buld_no", description="도로명 건물 번호"
    )
    road_building_inner_number: str = Field(
        alias="buld_no_inner", description="내부 건물 번호"
    )

    # 토지 정보
    jibun: str = Field(alias="lot_no", description="지번")
    additional_info: str = Field(alias="addItem", description="추가 정보")

    # 기술적 정보
    registration_id: str = Field(alias="pin", description="부동산 고유번호")
    land_registration_id: str = Field(
        alias="pin_land", description="토지 고유번호, 건물의 경우 존재"
    )
    work_registration_id: str = Field(alias="wk_pin", description="작업용 부동산 번호")
    jurisdiction_code: str = Field(
        alias="juris_regt_no", description="관할 등기소 코드"
    )
    usage_status: str = Field(alias="use_cls_cd", description="이용 상태")
    property_type: PropertyType = Field(alias="real_cls_cd", description="부동산 유형")
    land_sequence: str = Field(alias="land_seq", description="토지 순번")
    special_lot_flag: str = Field(
        alias="pin_mid_spe_yn", description="중간특수지번 여부"
    )


@dataclass
class DataMap(BaseModel):
    """API 응답 메타데이터 (필요시 사용)"""

    strInitSrch: str
    spcl_lect_yn: str
    swrd_check_rslt: str
    bSrchEngine: Optional[str] = None
