from dataclasses import dataclass
from pydantic import Field


@dataclass
class JusoInfo:
    """도로명주소 정보"""
    
    # 기본 주소 정보
    roadAddr: str = Field(..., description="전체 도로명주소")
    roadAddrPart1: str = Field(..., description="도로명주소(참고항목 제외)")
    roadAddrPart2: str = Field(..., description="도로명주소 참고항목")
    jibunAddr: str = Field(..., description="지번주소")
    engAddr: str = Field(..., description="도로명주소(영문)")
    
    # 우편번호
    zipNo: str = Field(..., description="우편번호")
    
    # 행정구역 정보
    admCd: str = Field(..., description="행정구역코드")
    rnMgtSn: str = Field(..., description="도로명코드")
    bdMgtSn: str = Field(..., description="건물관리번호")
    
    # 상세 위치 정보
    detBdNmList: str = Field(..., description="상세건물명")
    bdNm: str = Field(..., description="건물명")
    bdKdcd: str = Field(..., description="공동주택여부(1:공동주택, 0:비공동주택)")
    siNm: str = Field(..., description="시도명")
    sggNm: str = Field(..., description="시군구명")
    emdNm: str = Field(..., description="읍면동명")
    emdNo: str = Field(..., description="읍면동번호")
    liNm: str = Field(..., description="법정리명")
    rn: str = Field(..., description="도로명")
    udrtYn: str = Field(..., description="지하여부(0:지상, 1:지하)")
    buldMnnm: str = Field(..., description="건물본번")
    buldSlno: str = Field(..., description="건물부번")
    mtYn: str = Field(..., description="산여부(0:대지, 1:산)")
    lnbrMnnm: str = Field(..., description="지번본번(번지)")
    lnbrSlno: str = Field(..., description="지번부번(호)")
    
    # 이력 정보 (hstryYn=Y일 때 제공)
    hstryYn: str = Field(..., description="이력여부")
    relJibun: str = Field(..., description="관련지번")
    hemdNm: str = Field(..., description="관할읍면")
    
    # 좌표 정보 (addInfoYn=Y일 때 제공) - 실제로는 응답에 없음
    entX: str = Field(default="", description="X좌표(경도)")
    entY: str = Field(default="", description="Y좌표(위도)") 