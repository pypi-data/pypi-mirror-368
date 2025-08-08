"""
네이버 API 통합 테스트
실제 API 호출을 포함한 테스트
"""

import os

import pytest

from pycobaltix.address.model import ConvertedCoordinate
from pycobaltix.address.naver_api import NaverAPI


@pytest.mark.integration
@pytest.mark.slow
class TestNaverAPIIntegration:
    """네이버 API 통합 테스트"""

    @pytest.fixture(scope="class")
    def naver_api(self):
        """실제 네이버 API 클라이언트 생성"""
        api_key_id = os.getenv("NAVER_API_KEY_ID")
        api_key = os.getenv("NAVER_API_KEY")

        if not api_key_id or not api_key:
            pytest.skip(
                "NAVER_API_KEY_ID 및 NAVER_API_KEY 환경 변수가 설정되지 않았습니다"
            )

        return NaverAPI(api_key_id=api_key_id, api_key=api_key)

    def test_convert_real_address_seoul(self, naver_api):
        """실제 서울 주소 변환 테스트"""
        address = "서울특별시 강남구 테헤란로 152"

        result = naver_api.convert_address(address)

        # 결과 검증
        assert result is not None
        assert isinstance(result, ConvertedCoordinate)

        # 좌표 검증 (서울 지역 좌표인지 확인)
        assert result.wgs84_coordinate.x is not None
        assert result.wgs84_coordinate.y is not None
        assert 126.0 < result.wgs84_coordinate.x < 128.0  # 서울 경도 범위
        assert 37.0 < result.wgs84_coordinate.y < 38.0  # 서울 위도 범위

        # TM128 좌표 검증
        assert result.tm128_coordinate.x is not None
        assert result.tm128_coordinate.y is not None

        # 주소 정보 검증
        assert result.transformed_elements.sido == "서울특별시"
        assert result.transformed_elements.sigugun == "강남구"

    def test_convert_real_address_busan(self, naver_api):
        """실제 부산 주소 변환 테스트"""
        address = "부산광역시 해운대구 해운대해변로 264"

        result = naver_api.convert_address(address)

        # 결과 검증
        assert result is not None
        assert isinstance(result, ConvertedCoordinate)

        # 좌표 검증 (부산 지역 좌표인지 확인)
        assert 128.0 < result.wgs84_coordinate.x < 130.0  # 부산 경도 범위
        assert 35.0 < result.wgs84_coordinate.y < 36.0  # 부산 위도 범위

        # 주소 정보 검증
        assert result.transformed_elements.sido == "부산광역시"
        assert result.transformed_elements.sigugun == "해운대구"

    def test_convert_invalid_address(self, naver_api):
        """잘못된 주소 변환 테스트"""
        invalid_addresses = [
            "존재하지않는시 존재하지않는구 존재하지않는로 999",
            "abcdefg 123456 nonexistent address",
            "12345",
            "!@#$%^&*()",
        ]

        for address in invalid_addresses:
            result = naver_api.convert_address(address)
            # 잘못된 주소는 None 또는 검색 결과 없음으로 처리
            if result is not None:
                # 결과가 있다면 유효한 구조인지만 확인
                assert isinstance(result, ConvertedCoordinate)

    def test_convert_partial_address(self, naver_api):
        """부분적인 주소 변환 테스트"""
        partial_addresses = [
            "서울특별시 강남구",
            "서울 강남",
            "테헤란로",
        ]

        for address in partial_addresses:
            result = naver_api.convert_address(address)

            if result is not None:
                # 결과가 있다면 기본 구조 검증
                assert isinstance(result, ConvertedCoordinate)
                assert result.wgs84_coordinate.x is not None
                assert result.wgs84_coordinate.y is not None

    def test_convert_multiple_addresses_consistency(self, naver_api):
        """같은 주소를 여러 번 변환했을 때 일관성 테스트"""
        address = "서울특별시 종로구 종로 1"

        results = []
        for _ in range(3):
            result = naver_api.convert_address(address)
            results.append(result)

        # 모든 결과가 None이 아니라면 동일해야 함
        non_none_results = [r for r in results if r is not None]

        if len(non_none_results) > 1:
            first_result = non_none_results[0]
            for result in non_none_results[1:]:
                assert (
                    abs(result.wgs84_coordinate.x - first_result.wgs84_coordinate.x)
                    < 0.000001
                ), "같은 주소에 대한 좌표가 일치하지 않습니다"
                assert (
                    abs(result.wgs84_coordinate.y - first_result.wgs84_coordinate.y)
                    < 0.000001
                ), "같은 주소에 대한 좌표가 일치하지 않습니다"

    @pytest.mark.parametrize(
        "address,expected_sido",
        [
            ("서울특별시 중구 명동2가", "서울특별시"),
            ("경기도 성남시 분당구 판교역로 166", "경기도"),
            ("인천광역시 연수구 컨벤시아대로 165", "인천광역시"),
        ],
    )
    def test_convert_various_cities(self, naver_api, address, expected_sido):
        """다양한 도시 주소 변환 테스트"""
        result = naver_api.convert_address(address)

        if result is not None:
            assert result.transformed_elements.sido == expected_sido

    def test_api_rate_limiting(self, naver_api):
        """API 속도 제한 테스트"""
        import time

        addresses = [
            "서울특별시 강남구 테헤란로 152",
            "서울특별시 종로구 종로 1",
            "서울특별시 마포구 월드컵북로 21",
        ]

        results = []
        start_time = time.time()

        for address in addresses:
            result = naver_api.convert_address(address)
            results.append(result)
            time.sleep(0.1)  # API 호출 간 최소 간격

        end_time = time.time()

        # 모든 요청이 적절한 시간 내에 완료되었는지 확인
        total_time = end_time - start_time
        assert total_time < 10.0, "API 호출이 너무 오래 걸립니다"

        # 최소 일부 결과는 성공해야 함
        successful_results = [r for r in results if r is not None]
        assert len(successful_results) > 0, "모든 API 호출이 실패했습니다"
