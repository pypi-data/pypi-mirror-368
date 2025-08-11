"""
address 모듈 단위 테스트
"""

from unittest.mock import Mock, patch

import pytest

from pycobaltix.address.endpoint import NaverEndpoint
from pycobaltix.address.model import ConvertedCoordinate, Coordinate, NaverAddress
from pycobaltix.address.naver_api import NaverAPI


@pytest.mark.unit
class TestNaverAddress:
    """NaverAddress 모델 테스트"""

    def test_naver_address_initialization(self):
        """NaverAddress 초기화 테스트"""
        # 완전한 데이터로 테스트
        data = {
            "SIDO": {"longName": "서울특별시"},
            "SIGUGUN": {"longName": "강남구"},
            "DONGMYUN": {"longName": "역삼동"},
            "ROAD_NAME": {"longName": "테헤란로"},
            "BUILDING_NUMBER": {"longName": "152"},
            "POSTAL_CODE": {"longName": "06236"},
        }

        address = NaverAddress(data)

        assert address.sido == "서울특별시"
        assert address.sigugun == "강남구"
        assert address.dongmyun == "역삼동"
        assert address.road_name == "테헤란로"
        assert address.building_number == "152"
        assert address.postal_code == "06236"

    def test_naver_address_partial_data(self):
        """부분적인 데이터로 NaverAddress 테스트"""
        data = {"SIDO": {"longName": "서울특별시"}, "SIGUGUN": {"longName": "강남구"}}

        address = NaverAddress(data)

        assert address.sido == "서울특별시"
        assert address.sigugun == "강남구"
        assert address.dongmyun is None
        assert address.road_name is None

    def test_make_building_name_with_building_name(self):
        """건물명이 있을 때 make_building_name 테스트"""
        data = {"BUILDING_NAME": {"longName": "코엑스"}}

        address = NaverAddress(data)
        assert address.make_building_name == "코엑스"

    def test_make_building_name_with_ri(self):
        """리가 있을 때 make_building_name 테스트"""
        data = {
            "DONGMYUN": {"longName": "역삼동"},
            "RI": {"longName": "산1-1"},
            "LAND_NUMBER": {"longName": "737"},
        }

        address = NaverAddress(data)
        expected = "역삼동 737"
        assert address.make_building_name == expected

    def test_make_building_name_without_ri(self):
        """리가 없을 때 make_building_name 테스트"""
        data = {"DONGMYUN": {"longName": "역삼동"}, "LAND_NUMBER": {"longName": "737"}}

        address = NaverAddress(data)
        expected = " 737"  # ri가 None이므로 공백 + 번지
        assert address.make_building_name == expected


@pytest.mark.unit
class TestCoordinate:
    """Coordinate 모델 테스트"""

    def test_coordinate_int(self):
        """정수 좌표 테스트"""
        coord = Coordinate[int](x=100, y=200)

        assert coord.x == 100
        assert coord.y == 200
        assert isinstance(coord.x, int)
        assert isinstance(coord.y, int)

    def test_coordinate_float(self):
        """실수 좌표 테스트"""
        coord = Coordinate[float](x=127.0276368, y=37.4979517)

        assert coord.x == 127.0276368
        assert coord.y == 37.4979517
        assert isinstance(coord.x, float)
        assert isinstance(coord.y, float)


@pytest.mark.unit
class TestConvertedCoordinate:
    """ConvertedCoordinate 모델 테스트"""

    def test_converted_coordinate_creation(self):
        """ConvertedCoordinate 생성 테스트"""
        tm128_coord = Coordinate[int](x=200000, y=450000)
        wgs84_coord = Coordinate[float](x=127.0276368, y=37.4979517)

        address_data = {
            "SIDO": {"longName": "서울특별시"},
            "SIGUGUN": {"longName": "강남구"},
        }
        naver_address = NaverAddress(address_data)

        converted = ConvertedCoordinate(
            tm128_coordinate=tm128_coord,
            wgs84_coordinate=wgs84_coord,
            transformed_elements=naver_address,
        )

        assert converted.tm128_coordinate.x == 200000
        assert converted.tm128_coordinate.y == 450000
        assert converted.wgs84_coordinate.x == 127.0276368
        assert converted.wgs84_coordinate.y == 37.4979517
        assert converted.transformed_elements.sido == "서울특별시"


@pytest.mark.unit
class TestNaverEndpoint:
    """NaverEndpoint 열거형 테스트"""

    def test_endpoint_values(self):
        """엔드포인트 값 테스트"""
        assert (
            NaverEndpoint.static_map
            == "https://maps.apigw.ntruss.com/map-static/v2/raster"
        )
        assert (
            NaverEndpoint.directions_5
            == "https://maps.apigw.ntruss.com/map-direction/v1/driving"
        )
        assert (
            NaverEndpoint.directions_15
            == "https://maps.apigw.ntruss.com/map-direction-15/v1/driving"
        )
        assert (
            NaverEndpoint.geocoding
            == "https://maps.apigw.ntruss.com/map-geocode/v2/geocode"
        )
        assert (
            NaverEndpoint.reverse_geocoding
            == "https://maps.apigw.ntruss.com/map-reversegeocode/v2/gc"
        )


@pytest.mark.unit
class TestNaverAPI:
    """NaverAPI 클래스 테스트"""

    def test_naver_api_initialization(self, mock_naver_api_credentials):
        """NaverAPI 초기화 테스트"""
        api = NaverAPI(
            api_key_id=mock_naver_api_credentials["api_key_id"],
            api_key=mock_naver_api_credentials["api_key"],
        )

        assert api.api_key_id == "test_api_key_id"
        assert api.api_key == "test_api_key"

    def test_convert_address_empty_input(self, mock_naver_api_credentials):
        """빈 주소 입력 테스트"""
        api = NaverAPI(
            api_key_id=mock_naver_api_credentials["api_key_id"],
            api_key=mock_naver_api_credentials["api_key"],
        )

        # 빈 문자열
        result = api.convert_address("")
        assert result is None

        # 공백만 있는 문자열
        result = api.convert_address("   ")
        assert result is None

    @patch("pycobaltix.address.convert_coordinate.wgs84_to_tm128")
    @patch("pycobaltix.address.convert_coordinate.tm128_to_wgs84")
    def test_convert_address_success(
        self,
        mock_tm128_to_wgs84,
        mock_wgs84_to_tm128,
        mock_requests_get,
        mock_naver_api_credentials,
        sample_naver_geocoding_response,
    ):
        """주소 변환 성공 테스트"""
        # Mock 설정
        mock_response = Mock()
        mock_response.json.return_value = sample_naver_geocoding_response
        mock_requests_get.return_value = mock_response

        mock_wgs84_to_tm128.return_value = Coordinate[int](x=200000, y=450000)
        mock_tm128_to_wgs84.return_value = Coordinate[float](
            x=127.0276368, y=37.4979517
        )

        # API 호출
        api = NaverAPI(
            api_key_id=mock_naver_api_credentials["api_key_id"],
            api_key=mock_naver_api_credentials["api_key"],
        )

        result = api.convert_address("서울특별시 강남구 테헤란로 152")

        # 결과 검증
        assert result is not None
        assert isinstance(result, ConvertedCoordinate)
        assert result.tm128_coordinate.x == 200000
        assert result.tm128_coordinate.y == 450000
        assert result.wgs84_coordinate.x == 127.0276368
        assert result.wgs84_coordinate.y == 37.4979517
        assert result.transformed_elements.sido == "서울특별시"

        # API 호출 검증
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        assert "query=서울특별시 강남구 테헤란로 152" in call_args[0][0]

    def test_convert_address_no_results(
        self, mock_requests_get, mock_naver_api_credentials
    ):
        """주소 검색 결과 없음 테스트"""
        # Mock 설정 - 빈 결과
        mock_response = Mock()
        mock_response.json.return_value = {"status": "OK", "addresses": []}
        mock_requests_get.return_value = mock_response

        # API 호출
        api = NaverAPI(
            api_key_id=mock_naver_api_credentials["api_key_id"],
            api_key=mock_naver_api_credentials["api_key"],
        )

        result = api.convert_address("존재하지않는주소")

        # 결과 검증
        assert result is None

    def test_convert_address_exception_handling(
        self, mock_requests_get, mock_naver_api_credentials
    ):
        """예외 처리 테스트"""
        # Mock에서 예외 발생
        mock_requests_get.side_effect = Exception("Network error")

        # API 호출
        api = NaverAPI(
            api_key_id=mock_naver_api_credentials["api_key_id"],
            api_key=mock_naver_api_credentials["api_key"],
        )

        result = api.convert_address("서울특별시 강남구 테헤란로 152")

        # 예외가 처리되어 None 반환
        assert result is None
