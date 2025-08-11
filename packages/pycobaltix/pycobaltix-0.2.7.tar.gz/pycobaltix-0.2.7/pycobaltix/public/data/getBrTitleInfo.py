from dataclasses import dataclass

from pydantic import Field


@dataclass
class GetBrTitleInfo:
    """건축물대장 표제부 정보"""

    # 기본 정보
    rnum: str = Field(..., description="순번")
    platPlc: str = Field(..., description="대지위치", examples=["서울특별시 강남구 개포동 12번지"])
    sigunguCd: str = Field(..., description="시군구코드", examples=["11350"])
    bjdongCd: str = Field(..., description="법정동코드", examples=["10200"])
    platGbCd: str = Field(..., description="지번구분코드", examples=["0", "1", "2"])
    bun: str = Field(..., description="번", examples=["0923"])
    ji: str = Field(..., description="지", examples=["0000"])
    mgmBldrgstPk: str = Field(..., description="관리건축물대장 PK")

    # 등록 정보
    regstrGbCd: str = Field(..., description="대장구분코드")
    regstrGbCdNm: str = Field(..., description="대장구분코드명")
    regstrKindCd: str = Field(..., description="대장종류코드")
    regstrKindCdNm: str = Field(..., description="대장종류코드명")

    # 건물 기본 정보
    bldNm: str = Field(..., description="건물명")
    newPlatPlc: str = Field(..., description="도로명 대지위치")
    splotNm: str = Field(..., description="특수지명")
    block: str = Field(..., description="블록")
    lot: str = Field(..., description="로트")
    bylotCnt: str = Field(..., description="외필지수")

    # 도로명주소
    naRoadCd: str = Field(..., description="새주소도로코드")
    naBjdongCd: str = Field(..., description="새주소법정동코드")
    naUgrndCd: str = Field(..., description="새주소지상지하코드")
    naMainBun: str = Field(..., description="새주소본번")
    naSubBun: str = Field(..., description="새주소부번")

    # 동 정보
    dongNm: str = Field(..., description="동명칭")
    mainAtchGbCd: str = Field(..., description="주부속구분코드")
    mainAtchGbCdNm: str = Field(..., description="주부속구분코드명")

    # 면적 정보
    platArea: str = Field(..., description="대지면적(㎡)")
    archArea: str = Field(..., description="건축면적(㎡)")
    bcRat: str = Field(..., description="건폐율(%)")
    totArea: str = Field(..., description="연면적(㎡)")
    vlRatEstmTotArea: str = Field(..., description="용적률산정연면적(㎡)")
    vlRat: str = Field(..., description="용적률(%)")

    # 구조 및 용도
    strctCd: str = Field(..., description="구조코드")
    strctCdNm: str = Field(..., description="구조코드명")
    etcStrct: str = Field(..., description="기타구조")
    mainPurpsCd: str = Field(..., description="주용도코드")
    mainPurpsCdNm: str = Field(..., description="주용도코드명")
    etcPurps: str = Field(..., description="기타용도")

    # 지붕 정보
    roofCd: str = Field(..., description="지붕코드")
    roofCdNm: str = Field(..., description="지붕코드명")
    etcRoof: str = Field(..., description="기타지붕")

    # 세대/가구 정보
    hhldCnt: str = Field(..., description="세대수(세대)")
    fmlyCnt: str = Field(..., description="가구수(가구)")
    hoCnt: str = Field(..., description="호수(호)")

    # 건물 높이/층수
    heit: str = Field(..., description="높이(m)")
    grndFlrCnt: str = Field(..., description="지상층수")
    ugrndFlrCnt: str = Field(..., description="지하층수")

    # 엘리베이터
    rideUseElvtCnt: str = Field(..., description="승용승강기수")
    emgenUseElvtCnt: str = Field(..., description="비상용승강기수")

    # 부속건축물
    atchBldCnt: str = Field(..., description="부속건축물수")
    atchBldArea: str = Field(..., description="부속건축물면적(㎡)")
    totDongTotArea: str = Field(..., description="총동연면적(㎡)")

    # 기계식 주차장
    indrMechUtcnt: str = Field(..., description="옥내기계식대수")
    indrMechArea: str = Field(..., description="옥내기계식면적(㎡)")
    oudrMechUtcnt: str = Field(..., description="옥외기계식대수")
    oudrMechArea: str = Field(..., description="옥외기계식면적(㎡)")

    # 자주식 주차장
    indrAutoUtcnt: str = Field(..., description="옥내자주식대수")
    indrAutoArea: str = Field(..., description="옥내자주식면적(㎡)")
    oudrAutoUtcnt: str = Field(..., description="옥외자주식대수")
    oudrAutoArea: str = Field(..., description="옥외자주식면적(㎡)")

    # 허가/승인/사용승인 일자
    pmsDay: str = Field(..., description="허가일")
    stcnsDay: str = Field(..., description="착공일")
    useAprDay: str = Field(..., description="사용승인일")

    # 허가번호 정보
    pmsnoYear: str = Field(..., description="허가번호년")
    pmsnoKikCd: str = Field(..., description="허가번호기관코드")
    pmsnoKikCdNm: str = Field(..., description="허가번호기관코드명")
    pmsnoGbCd: str = Field(..., description="허가번호구분코드")
    pmsnoGbCdNm: str = Field(..., description="허가번호구분코드명")

    # 에너지 관련
    engrGrade: str = Field(..., description="에너지효율등급")
    engrRat: str = Field(..., description="에너지절약률")
    engrEpi: str = Field(..., description="EPI점수")
    gnBldGrade: str = Field(..., description="친환경건축물등급")
    gnBldCert: str = Field(..., description="친환경건축물인증점수")
    itgBldGrade: str = Field(..., description="지능형건축물등급")
    itgBldCert: str = Field(..., description="지능형건축물인증점수")

    # 기타
    rserthqkDsgnApplyYn: str = Field(..., description="내진설계적용여부")
    rserthqkAblty: str = Field(..., description="내진능력")
    crtnDay: str = Field(..., description="생성일")
