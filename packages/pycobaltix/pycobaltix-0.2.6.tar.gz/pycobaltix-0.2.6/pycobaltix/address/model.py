from dataclasses import dataclass
from typing import Generic, TypeVar


class NaverAddress:
    road_address: str | None
    jibun_address: str | None
    english_address: str | None
    sido: str | None
    sigugun: str | None
    dongmyun: str | None
    ri: str | None
    road_name: str | None
    building_number: str | None
    building_name: str | None
    land_number: str | None
    postal_code: str | None
    pnu: str | None
    legal_district: str | None

    def __init__(self, data: dict):
        self.sido = data.get("SIDO", {}).get("longName", None)
        self.sigugun = data.get("SIGUGUN", {}).get("longName", None)
        self.dongmyun = data.get("DONGMYUN", {}).get("longName", None)
        self.ri = data.get("RI", {}).get("longName", None)
        self.road_name = data.get("ROAD_NAME", {}).get("longName", None)
        self.building_number = data.get("BUILDING_NUMBER", {}).get("longName", None)
        self.building_name = data.get("BUILDING_NAME", {}).get("longName", None)
        self.land_number = data.get("LAND_NUMBER", {}).get("longName", None)
        self.postal_code = data.get("POSTAL_CODE", {}).get("longName", None)

    @property
    def make_building_name(self):
        building_name = self.building_name or ""
        if building_name != "":
            return building_name
        if self.ri:
            building_name += self.dongmyun or ""
        else:
            building_name += self.ri or ""

        building_name += " " + (self.land_number or "")

        return building_name


T = TypeVar("T", int, float)


@dataclass(frozen=True)
class Coordinate(Generic[T]):
    x: T
    y: T


@dataclass
class ConvertedCoordinate:
    tm128_coordinate: Coordinate[int]
    wgs84_coordinate: Coordinate[float]
    transformed_elements: NaverAddress
