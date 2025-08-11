from dataclasses import dataclass

from pydantic import Field


@dataclass
class GetBrExposPubuseAreaInfo:
    rnum: int = Field(..., description="순번")
    platPlc: str = Field(
        ..., description="대지위치", examples=["서울특별시  강남구 개포동 12번지"]
    )
    sigunguCd: str = Field(..., description="시군구코드", examples=["11350"])
    bjdongCd: str = Field(..., description="법정동코드", examples=["10200"])
    platGbCd: str = Field(..., description="지번구분코드", examples=["0", "1", "2"])
    bun: str = Field(..., description="번", examples=["0923"])
    ji: str = Field(..., description="지", examples=["0000"])
    mgmBldrgstPk: int = Field(..., description="관리건축물대장 PK")
    regstrGbCd: str = Field(..., description="등록구분코드", examples=["0", "1", "2"])
    regstrGbCdNm: str = Field(..., description="등록구분코드명")
    regstrKindCd: str = Field(..., description="등록종류코드")
    regstrKindCdNm: str = Field(..., description="등록종류코드명")
    newPlatPlc: str = Field(
        ..., description="도로명대지위치", examples=["서울특별시  강남구 개포동 12번지"]
    )
    bldNm: str = Field(..., description="건물명", examples=["초안아파트"])
    splotNm: str = Field(..., description="특수지명")
    block: str = Field(..., description="블록")
    lot: str = Field(..., description="로트")
    naRoadCd: str = Field(..., description="새주소도로코드", examples=["116804166040"])
    naBjdongCd: str = Field(
        ..., description="새주소법정동코드", examples=["11680416604010301"]
    )
    naUgrndCd: str = Field(..., description="새주소지번구분코드", examples=["0"])
    naMainBun: str = Field(..., description="새주소본번", examples=["0923"])
    naSubBun: str = Field(..., description="새주소부번", examples=["0000"])
    dongNm: str = Field(..., description="동명", examples=["개포동"])
    hoNm: str = Field(..., description="호명", examples=["12호"])
    flrGbCd: str = Field(..., description="층구분코드")
    flrGbCdNm: str = Field(..., description="층구분코드명")
    flrNo: int = Field(..., description="층")
    flrNoNm: str = Field(..., description="층번호명")
    exposPubuseGbCd: str = Field(
        ..., description="전유구분코드", examples=["0", "1", "2"]
    )
    exposPubuseGbCdNm: str = Field(
        ..., description="전유구분코드명", examples=["전유부"]
    )
    mainAtchGbCd: str = Field(..., description="주부속구분코드")
    mainAtchGbCdNm: str = Field(..., description="주부속구분코드명")
    strctCd: str = Field(..., description="구조코드")
    strctCdNm: str = Field(..., description="구조코드명")
    etcStrct: str = Field(..., description="기타구조")
    mainPurpsCd: str = Field(..., description="주용도코드")
    mainPurpsCdNm: str = Field(..., description="주용도코드명")
    etcPurps: str = Field(..., description="기타용도")
    area: float = Field(..., description="면적", examples=[100.0])
    crtnDay: str = Field(..., description="생성일")
