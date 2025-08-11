from dataclasses import dataclass


@dataclass
class BuildingInfo:
    """건물 정보 데이터 클래스"""

    # 건물 기본 정보
    agbldgSn: str  # 농업건물일련번호
    buldNm: str  # 건물명
    pnu: str  # 필지고유번호

    # 주소 정보
    liCodeNm: str  # 리코드명 (주소)
    liCode: str  # 리코드
    relateLdEmdLiCode: str  # 관련토지읍면동리코드
    mnnmSlno: str  # 본번슬번호

    # 건물 상세 정보
    buldFloorNm: str  # 건물층명
    buldDongNm: str  # 건물동명
    buldHoNm: str  # 건물호명
    buldRoomNm: str  # 건물실명

    # 분류 및 등록 정보
    clsSeCode: str  # 분류구분코드
    clsSeCodeNm: str  # 분류구분코드명
    regstrSeCode: str  # 등록구분코드
    regstrSeCodeNm: str  # 등록구분코드명

    # 기타 정보
    lastUpdtDt: str  # 최종수정일 (YYYY-MM-DD)
    ldaQotaRate: str  # 토지할당율 (빈 값일 수 있음)

    @classmethod
    def from_dict(cls, data: dict) -> "BuildingInfo":
        """딕셔너리에서 BuildingInfo 인스턴스 생성"""
        return cls(
            agbldgSn=data["agbldgSn"],
            buldFloorNm=data["buldFloorNm"],
            liCodeNm=data["liCodeNm"],
            buldDongNm=data["buldDongNm"],
            ldaQotaRate=data["ldaQotaRate"],
            clsSeCodeNm=data["clsSeCodeNm"],
            buldHoNm=data["buldHoNm"],
            buldRoomNm=data["buldRoomNm"],
            mnnmSlno=data["mnnmSlno"],
            buldNm=data["buldNm"],
            pnu=data["pnu"],
            lastUpdtDt=data["lastUpdtDt"],
            liCode=data["liCode"],
            regstrSeCodeNm=data["regstrSeCodeNm"],
            relateLdEmdLiCode=data["relateLdEmdLiCode"],
            regstrSeCode=data["regstrSeCode"],
            clsSeCode=data["clsSeCode"],
        )

    def to_dict(self) -> dict:
        """인스턴스를 딕셔너리로 변환"""
        return {
            "agbldgSn": self.agbldgSn,
            "buldFloorNm": self.buldFloorNm,
            "liCodeNm": self.liCodeNm,
            "buldDongNm": self.buldDongNm,
            "ldaQotaRate": self.ldaQotaRate,
            "clsSeCodeNm": self.clsSeCodeNm,
            "buldHoNm": self.buldHoNm,
            "buldRoomNm": self.buldRoomNm,
            "mnnmSlno": self.mnnmSlno,
            "buldNm": self.buldNm,
            "pnu": self.pnu,
            "lastUpdtDt": self.lastUpdtDt,
            "liCode": self.liCode,
            "regstrSeCodeNm": self.regstrSeCodeNm,
            "relateLdEmdLiCode": self.relateLdEmdLiCode,
            "regstrSeCode": self.regstrSeCode,
            "clsSeCode": self.clsSeCode,
        }
