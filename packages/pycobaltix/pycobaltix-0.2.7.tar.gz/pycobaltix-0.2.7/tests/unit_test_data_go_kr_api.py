"""
DATA.GO.KR API 단위 테스트
모킹을 사용한 테스트
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx

from pycobaltix.public.data.endpoints import DataGOKRAPI, AsyncDataGOKRAPI
from pycobaltix.public.data.getBrTitleInfo import GetBrTitleInfo
from pycobaltix.public.data.getBrExposPubuseAreaInfo import GetBrExposPubuseAreaInfo
from pycobaltix.schemas.responses import PaginatedAPIResponse


@pytest.mark.unit
class TestDataGOKRAPIUnit:
    """DATA.GO.KR API 단위 테스트"""

    @pytest.fixture
    def data_go_kr_api(self):
        """테스트용 API 클라이언트"""
        return DataGOKRAPI(api_key="test_api_key")

    @pytest.fixture
    def sample_br_title_info_response(self):
        """건축물대장 표제부 API 응답 샘플"""
        return {
            "response": {
                "body": {
                    "items": {
                        "item": [
                            {
                                "rnum": "1",
                                "platPlc": "서울특별시 노원구 상계동 923번지",
                                "sigunguCd": "11350",
                                "bjdongCd": "10200",
                                "platGbCd": "0",
                                "bun": "0923",
                                "ji": "0000",
                                "mgmBldrgstPk": "11350-10200-0923-0000-001",
                                "regstrGbCd": "1",
                                "regstrGbCdNm": "집합건축물",
                                "regstrKindCd": "1",
                                "regstrKindCdNm": "일반건축물",
                                "bldNm": "테스트 아파트",
                                "newPlatPlc": "서울특별시 노원구 한글비석로 100",
                                "splotNm": "",
                                "block": "",
                                "lot": "",
                                "bylotCnt": "0",
                                "naRoadCd": "113504158013",
                                "naBjdongCd": "10200",
                                "naUgrndCd": "0",
                                "naMainBun": "100",
                                "naSubBun": "0",
                                "dongNm": "101동",
                                "mainAtchGbCd": "1",
                                "mainAtchGbCdNm": "주건축물",
                                "platArea": "1234.56",
                                "archArea": "567.89",
                                "bcRat": "45.50",
                                "totArea": "12345.67",
                                "vlRatEstmTotArea": "10000.00",
                                "vlRat": "250.00",
                                "strctCd": "21",
                                "strctCdNm": "철근콘크리트구조",
                                "etcStrct": "",
                                "mainPurpsCd": "02000",
                                "mainPurpsCdNm": "공동주택",
                                "etcPurps": "",
                                "roofCd": "10",
                                "roofCdNm": "평지붕",
                                "etcRoof": "",
                                "hhldCnt": "150",
                                "fmlyCnt": "150",
                                "hoCnt": "150",
                                "heit": "45.5",
                                "grndFlrCnt": "15",
                                "ugrndFlrCnt": "2",
                                "rideUseElvtCnt": "2",
                                "emgenUseElvtCnt": "1",
                                "atchBldCnt": "1",
                                "atchBldArea": "100.00",
                                "totDongTotArea": "12445.67",
                                "indrMechUtcnt": "50",
                                "indrMechArea": "1000.00",
                                "oudrMechUtcnt": "0",
                                "oudrMechArea": "0.00",
                                "indrAutoUtcnt": "100",
                                "indrAutoArea": "2000.00",
                                "oudrAutoUtcnt": "20",
                                "oudrAutoArea": "500.00",
                                "pmsDay": "20200101",
                                "stcnsDay": "20200201",
                                "useAprDay": "20201201",
                                "pmsnoYear": "2020",
                                "pmsnoKikCd": "11350",
                                "pmsnoKikCdNm": "노원구",
                                "pmsnoGbCd": "1",
                                "pmsnoGbCdNm": "신축허가",
                                "engrGrade": "1",
                                "engrRat": "15.5",
                                "engrEpi": "65.0",
                                "gnBldGrade": "우수",
                                "gnBldCert": "85.0",
                                "itgBldGrade": "일반",
                                "itgBldCert": "75.0",
                                "rserthqkDsgnApplyYn": "Y",
                                "rserthqkAblty": "VII",
                                "crtnDay": "20201215"
                            }
                        ]
                    },
                    "totalCount": "1",
                    "pageNo": "1",
                    "numOfRows": "10"
                }
            }
        }

    @pytest.fixture
    def sample_empty_response(self):
        """빈 응답 샘플"""
        return {
            "response": {
                "body": {
                    "items": {"item": []},
                    "totalCount": "0",
                    "pageNo": "1",
                    "numOfRows": "10"
                }
            }
        }

    @patch('httpx.get')
    def test_get_br_title_info_success(
        self, mock_get, data_go_kr_api, sample_br_title_info_response
    ):
        """getBrTitleInfo 성공 테스트 (모킹)"""
        # Mock 설정
        mock_response = Mock()
        mock_response.json.return_value = sample_br_title_info_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # API 호출
        result = data_go_kr_api.getBrTitleInfo(
            sigunguCd="11350",
            bjdongCd="10200",
            bun="0923",
            ji="0000",
            numOfRows=10,
            pageNo=1,
        )

        # 결과 검증
        assert result is not None
        assert isinstance(result, PaginatedAPIResponse)
        assert len(result.data) == 1

        # 데이터 검증
        building = result.data[0]
        assert isinstance(building, GetBrTitleInfo)
        assert building.sigunguCd == "11350"
        assert building.bjdongCd == "10200"
        assert building.bun == "0923"
        assert building.ji == "0000"
        assert building.bldNm == "테스트 아파트"
        assert building.platPlc == "서울특별시 노원구 상계동 923번지"

        # 페이지네이션 검증
        assert result.pagination.totalCount == 1
        assert result.pagination.currentPage == 1
        assert result.pagination.count == 10
        assert result.pagination.totalPages == 1
        assert result.pagination.hasNext is False
        assert result.pagination.hasPrevious is False

    @patch('httpx.get')
    def test_get_br_title_info_empty_result(
        self, mock_get, data_go_kr_api, sample_empty_response
    ):
        """getBrTitleInfo 빈 결과 테스트"""
        # Mock 설정
        mock_response = Mock()
        mock_response.json.return_value = sample_empty_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # API 호출
        result = data_go_kr_api.getBrTitleInfo(
            sigunguCd="99999",
            bjdongCd="99999",
            numOfRows=10,
            pageNo=1,
        )

        # 결과 검증
        assert result is not None
        assert isinstance(result, PaginatedAPIResponse)
        assert len(result.data) == 0
        assert result.pagination.totalCount == 0

    @patch('httpx.get')
    def test_get_br_title_info_http_error(self, mock_get, data_go_kr_api):
        """getBrTitleInfo HTTP 에러 테스트"""
        # Mock 설정 - HTTP 에러 발생
        mock_get.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=Mock()
        )

        # API 호출 시 예외 발생 확인
        with pytest.raises(httpx.HTTPStatusError):
            data_go_kr_api.getBrTitleInfo(
                sigunguCd="11350",
                bjdongCd="10200",
                numOfRows=10,
                pageNo=1,
            )

    @patch('httpx.get')
    def test_get_br_title_info_retry_logic(self, mock_get, data_go_kr_api):
        """getBrTitleInfo 재시도 로직 테스트"""
        # Mock 설정 - 처음 2번은 실패, 3번째는 성공
        side_effects = [
            httpx.TimeoutException("Timeout"),
            httpx.RequestError("Request failed", request=Mock()),
        ]
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "body": {
                    "items": {"item": []},
                    "totalCount": "0",
                    "pageNo": "1",
                    "numOfRows": "10"
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        side_effects.append(mock_response)
        
        mock_get.side_effect = side_effects

        # API 호출
        with patch('time.sleep'):  # 실제 sleep 방지
            result = data_go_kr_api.getBrTitleInfo(
                sigunguCd="11350",
                bjdongCd="10200",
            )

        # 결과 검증 - 재시도 후 성공
        assert result is not None
        assert mock_get.call_count == 3

    def test_prepare_params(self, data_go_kr_api):
        """_prepare_params 메서드 테스트"""
        params = data_go_kr_api._prepare_params(
            sigunguCd="11350",
            bjdongCd="10200",
            bun=None,
            ji="",
            numOfRows=10
        )

        # 결과 검증
        assert "serviceKey" in params
        assert params["serviceKey"] == "test_api_key"
        assert params["_type"] == "json"
        assert params["sigunguCd"] == "11350"
        assert params["bjdongCd"] == "10200"
        assert params["numOfRows"] == 10
        
        # None과 빈 문자열은 제거되어야 함
        assert "bun" not in params
        assert "ji" not in params

    def test_api_key_validation(self):
        """API 키 검증 테스트"""
        # 환경 변수도 없고 직접 제공도 안 한 경우
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="DATA_GO_KR_API_KEY 환경 변수가 설정되지 않았습니다"):
                DataGOKRAPI()

        # 정상적인 API 키 제공
        api = DataGOKRAPI(api_key="valid_key")
        assert api.serviceKey == "valid_key"


@pytest.mark.unit
class TestAsyncDataGOKRAPIUnit:
    """비동기 DATA.GO.KR API 단위 테스트"""

    @pytest.fixture
    def async_data_go_kr_api(self):
        """테스트용 비동기 API 클라이언트"""
        return AsyncDataGOKRAPI(api_key="test_api_key")

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_async_get_br_expos_pubuse_area_info_success(
        self, mock_client_class, async_data_go_kr_api
    ):
        """비동기 getBrExposPubuseAreaInfo 성공 테스트"""
        # Mock 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "body": {
                    "items": {"item": []},
                    "totalCount": "0",
                    "pageNo": "1",
                    "numOfRows": "10"
                }
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # API 호출
        result = await async_data_go_kr_api.getBrExposPubuseAreaInfo(
            sigunguCd="11350",
            bjdongCd="10200",
            bun="0923",
            ji="0000",
            dongNm="103동",
            hoNm="103호",
        )

        # 결과 검증
        assert result is not None
        assert isinstance(result, PaginatedAPIResponse)

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_async_http_error(self, mock_client_class, async_data_go_kr_api):
        """비동기 HTTP 에러 테스트"""
        # Mock 설정 - HTTP 에러 발생
        mock_client = MagicMock()
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=Mock()
        )
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # API 호출 시 예외 발생 확인
        with pytest.raises(httpx.HTTPStatusError):
            await async_data_go_kr_api.getBrExposPubuseAreaInfo(
                sigunguCd="11350",
                bjdongCd="10200",
                bun="0923",
                ji="0000",
                dongNm="103동",
                hoNm="103호",
            )

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    @patch('asyncio.sleep')
    async def test_async_retry_logic(
        self, mock_sleep, mock_client_class, async_data_go_kr_api
    ):
        """비동기 재시도 로직 테스트"""
        # Mock 설정
        side_effects = [
            httpx.TimeoutException("Timeout"),
            httpx.RequestError("Request failed", request=Mock()),
        ]
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "body": {
                    "items": {"item": []},
                    "totalCount": "0",
                    "pageNo": "1",
                    "numOfRows": "10"
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        side_effects.append(mock_response)
        
        mock_client = MagicMock()
        mock_client.get.side_effect = side_effects
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # API 호출
        result = await async_data_go_kr_api.getBrExposPubuseAreaInfo(
            sigunguCd="11350",
            bjdongCd="10200",
            bun="0923",
            ji="0000",
            dongNm="103동",
            hoNm="103호",
        )

        # 결과 검증
        assert result is not None
        assert mock_client.get.call_count == 3
        assert mock_sleep.call_count == 2  # 2번 재시도 