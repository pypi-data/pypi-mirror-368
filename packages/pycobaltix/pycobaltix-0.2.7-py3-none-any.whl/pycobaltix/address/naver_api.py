import os
from typing import Any, Dict

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from pycobaltix.address.convert_coordinate import (
    wgs84_to_tm128,
)
from pycobaltix.address.endpoint import NaverEndpoint
from pycobaltix.address.model import ConvertedCoordinate, Coordinate, NaverAddress


class NaverAPI:
    def __init__(self, api_key_id: str | None = None, api_key: str | None = None):
        self.api_key_id = api_key_id or os.getenv("NCP_APIGW_API_KEY_ID", "")
        self.api_key = api_key or os.getenv("NCP_APIGW_API_KEY", "")

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5))
    def generate_static_map_image(self, x: float, y: float, zoom: int = 15) -> bytes:
        # 19가 가깝고, 16이 포괄적
        static_map_url = f"{NaverEndpoint.static_map.value}?w=1024&h=1024&markers=type:d|size:mid|pos:{x}%20{y}|color:red&scale=2&level={zoom}&center={x}%20{y}"
        response = httpx.get(
            static_map_url,
            headers={
                "X-NCP-APIGW-API-KEY-ID": self.api_key_id,
                "X-NCP-APIGW-API-KEY": self.api_key,
                "Content-Type": "image/jpeg",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        return response.content

    def _generate_pnu(
        self, legal_district_code: str, land_number: str | None
    ) -> str | None:
        """
        PNU (부동산고유번호) 생성

        Args:
            legal_district_code: 법정동 코드 (10자리)
            land_number: 지번 (예: "123-4", "산74", "산92-1")

        Returns:
            PNU 코드 (19자리) 또는 None
        """
        try:
            if not legal_district_code or len(legal_district_code) != 10:
                print(f"유효하지 않은 법정동 코드: {legal_district_code}")
                return None

            if not land_number:
                print("지번 정보 없음")
                return None

            # 지목 타입 결정: "산"으로 시작하면 2(임야), 아니면 1(대지)
            land_type = "2" if land_number.startswith("산") else "1"

            # "산" 문자 제거하고 숫자 부분만 추출
            clean_jibun = (
                land_number.replace("산", "")
                if land_number.startswith("산")
                else land_number
            )

            # 지번 파싱 (예: "123-4" -> 본번: 123, 부번: 4)
            if "-" in clean_jibun:
                bonbun, bubun = clean_jibun.split("-", 1)
            else:
                bonbun, bubun = clean_jibun, "0"

            # 숫자 변환 및 유효성 검사
            try:
                main_num = int(bonbun.strip())
                sub_num = int(bubun.strip())
            except ValueError:
                print(f"유효하지 않은 지번 형식: {land_number}")
                return None

            # 본번과 부번을 4자리로 포맷 (0 패딩)
            bonbun_padded = f"{main_num:04d}"
            bubun_padded = f"{sub_num:04d}"

            # 범위 체크
            if main_num > 9999 or sub_num > 9999:
                print(f"지번이 범위를 초과함: {land_number}")
                return None

            # PNU 구성: 법정동코드(10) + 지목(1) + 본번(4) + 부번(4)
            pnu = f"{legal_district_code}{land_type}{bonbun_padded}{bubun_padded}"

            if len(pnu) != 19:
                print(f"PNU 길이 오류: {pnu} (길이: {len(pnu)})")
                return None

            return pnu

        except Exception as e:
            print(f"PNU 생성 중 오류: {e}")
            return None

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5))
    def _reverse_geocoding(self, x: float, y: float) -> Dict[str, Any] | None:
        """역 지오코딩을 통해 좌표에서 지역 정보를 가져옵니다."""
        url = f"{NaverEndpoint.reverse_geocoding.value}?coords={x},{y}&output=json"
        response = httpx.get(
            url,
            headers={
                "X-NCP-APIGW-API-KEY-ID": self.api_key_id,
                "X-NCP-APIGW-API-KEY": self.api_key,
            },
            timeout=10.0,
        )
        response.raise_for_status()

        json_data = response.json()

        # 응답 상태 확인
        if json_data.get("status", {}).get("code") != 0:
            return None

        # results 배열에서 첫 번째 항목 추출
        results = json_data.get("results", [])
        if not results:
            return None

        first_result = results[0]

        # 필요한 정보 추출
        return {
            "legal_district": first_result.get("code", {}).get("id"),
            "area1": first_result.get("region", {})
            .get("area1", {})
            .get("name"),  # 시/도
            "area2": first_result.get("region", {})
            .get("area2", {})
            .get("name"),  # 시/군/구
            "area3": first_result.get("region", {})
            .get("area3", {})
            .get("name"),  # 읍/면/동
            "area4": first_result.get("region", {}).get("area4", {}).get("name"),  # 리
        }

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5))
    def _geocoding(self, address: str) -> Dict[str, Any]:
        """지오코딩 API 호출"""
        url = f"{NaverEndpoint.geocoding.value}?query={address}"
        response = httpx.get(
            url,
            headers={
                "X-NCP-APIGW-API-KEY-ID": self.api_key_id,
                "X-NCP-APIGW-API-KEY": self.api_key,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

    def convert_address(self, address: str) -> ConvertedCoordinate | None:
        try:
            if len(address.replace(" ", "")) == 0:
                return None

            json_data = self._geocoding(address)

            # transformed_elements를 딕셔너리로 변경
            addresses = json_data.get("addresses", [])
            if len(addresses) == 0:
                print(address)
                return None

            first_address = addresses[0]
            transformed_elements_dict = {
                element["types"][0]: {  # 첫 번째 타입을 키로 사용
                    "longName": element["longName"],
                    "shortName": element["shortName"],
                }
                for element in first_address["addressElements"]
            }
            wgs84_x = first_address.get("x")
            wgs84_y = first_address.get("y")
            reverse_geocoding_data = self._reverse_geocoding(wgs84_x, wgs84_y)
            coordinates = wgs84_to_tm128(wgs84_x, wgs84_y)
            naver_address = NaverAddress(transformed_elements_dict)
            naver_address.road_address = first_address.get("roadAddress")
            naver_address.jibun_address = first_address.get("jibunAddress")
            naver_address.english_address = first_address.get("englishAddress")
            if reverse_geocoding_data:
                naver_address.pnu = self._generate_pnu(
                    reverse_geocoding_data.get("legal_district", ""),
                    naver_address.land_number,
                )
                naver_address.legal_district = (
                    reverse_geocoding_data.get("legal_district", "")
                    if reverse_geocoding_data
                    else None
                )
            return ConvertedCoordinate(
                tm128_coordinate=coordinates,
                wgs84_coordinate=Coordinate(
                    x=wgs84_x,
                    y=wgs84_y,
                ),
                transformed_elements=naver_address,
            )
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as e:
            print(f"HTTP 오류: {e}")
            return None
        except Exception as e:
            print(f"일반 오류: {e}")
            return None
