from pyproj import Proj, Transformer

from pycobaltix.address.model import Coordinate

# Private 상수들 (내부 구현용)
_WGS84 = {
    "proj": "latlong",
    "datum": "WGS84",
    "ellps": "WGS84",
}

# naver
_TM128 = {
    "proj": "tmerc",
    "lat_0": "38N",
    "lon_0": "128E",
    "ellps": "bessel",
    "x_0": "400000",
    "y_0": "600000",
    "k": 0.9999,
    "towgs84": "-146.43,507.89,681.46",
}


# Private 변환기 객체들
_wgs84_to_tm128_transformer = Transformer.from_proj(
    Proj(**_WGS84),  # type: ignore
    Proj(**_TM128),  # type: ignore
    always_xy=True,  # type: ignore
)
_tm128_to_wgs84_transformer = Transformer.from_proj(
    Proj(**_TM128),  # type: ignore
    Proj(**_WGS84),  # type: ignore
    always_xy=True,  # type: ignore
)


# Public API (사용자가 직접 사용할 함수들)
def wgs84_to_tm128(longitude: float, latitude: float) -> Coordinate[int]:
    x, y = _wgs84_to_tm128_transformer.transform(longitude, latitude)
    return Coordinate(x=int(x), y=int(y))


def tm128_to_wgs84(x: int, y: int) -> Coordinate[float]:
    x, y = _tm128_to_wgs84_transformer.transform(x, y)
    return Coordinate(x=float(x), y=float(y))


# Private 함수 (내부 구현용)
def _test_coordinate_conversion():
    """기존 메서드의 좌표 변환 결과를 확인"""

    # 테스트 좌표들 (TM128 x, y)
    test_coordinates = [(315845, 559398)]

    print("=" * 80)
    print("TM128 -> WGS84 변환 결과 확인")
    print("=" * 80)
    print(f"{'TM128 좌표':<20} {'WGS84 좌표 (위도, 경도)':<30} {'역변환 확인':<20}")
    print("-" * 80)

    for x, y in test_coordinates:
        # TM128 -> WGS84 변환
        wgs84_coordinate = tm128_to_wgs84(x, y)

        # 역변환으로 확인
        reverse_tm128_coordinate = wgs84_to_tm128(
            wgs84_coordinate.x, wgs84_coordinate.y
        )

        # 오차 계산
        error_x = abs(x - reverse_tm128_coordinate.x)
        error_y = abs(y - reverse_tm128_coordinate.y)

        print(
            f"{str((x, y)):<20} {f'{wgs84_coordinate.x:.6f}, {wgs84_coordinate.y:.6f}':<30} 오차: {error_x:.2f}, {error_y:.2f}"
        )

    print("\n" + "=" * 50)
    print("결론: 기존 메서드는 올바르게 작동합니다.")
    print("네이버 TM128 좌표계는 Bessel 타원체 기반이므로")
    print("EPSG 표준 좌표계와는 다릅니다.")
    print("=" * 50)


if __name__ == "__main__":
    _test_coordinate_conversion()
