from dataclasses import dataclass


@dataclass
class LandInfo:
    pnu: str
    ldCodeNm: str
    ldCode: str
    mnnmSlno: str
    regstrSeCode: str
    regstrSeCodeNm: str
    lndcgrCode: str
    lndcgrCodeNm: str
    lndpclAr: str
    posesnSeCode: str
    posesnSeCodeNm: str
    cnrsPsnCo: str
    ladFrtlSc: str
    ladFrtlScNm: str
    lastUpdtDt: str

    def to_dict(self):
        return {
            "pnu": self.pnu,
            "ldCodeNm": self.ldCodeNm,
            "ldCode": self.ldCode,
            "mnnmSlno": self.mnnmSlno,
            "regstrSeCode": self.regstrSeCode,
            "regstrSeCodeNm": self.regstrSeCodeNm,
            "lndcgrCode": self.lndcgrCode,
            "lndcgrCodeNm": self.lndcgrCodeNm,
            "lndpclAr": self.lndpclAr,
            "posesnSeCode": self.posesnSeCode,
            "posesnSeCodeNm": self.posesnSeCodeNm,
            "cnrsPsnCo": self.cnrsPsnCo,
            "ladFrtlSc": self.ladFrtlSc,
            "ladFrtlScNm": self.ladFrtlScNm,
            "lastUpdtDt": self.lastUpdtDt,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LandInfo":
        return cls(
            pnu=data["pnu"],
            ldCodeNm=data["ldCodeNm"],
            ldCode=data["ldCode"],
            mnnmSlno=data["mnnmSlno"],
            regstrSeCode=data["regstrSeCode"],
            regstrSeCodeNm=data["regstrSeCodeNm"],
            lndcgrCode=data["lndcgrCode"],
            lndcgrCodeNm=data["lndcgrCodeNm"],
            lndpclAr=data["lndpclAr"],
            posesnSeCode=data["posesnSeCode"],
            posesnSeCodeNm=data["posesnSeCodeNm"],
            cnrsPsnCo=data["cnrsPsnCo"],
            ladFrtlSc=data["ladFrtlSc"],
            ladFrtlScNm=data["ladFrtlScNm"],
            lastUpdtDt=data["lastUpdtDt"],
        )
