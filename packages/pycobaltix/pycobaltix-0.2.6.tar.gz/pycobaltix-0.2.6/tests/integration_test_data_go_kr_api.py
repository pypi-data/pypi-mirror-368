"""
DATA.GO.KR API 통합 테스트
실제 API 호출을 포함한 테스트
"""

import os

import pytest

from pycobaltix.public.data.endpoints import DataGOKRAPI, AsyncDataGOKRAPI
from pycobaltix.public.data.getBrTitleInfo import GetBrTitleInfo
from pycobaltix.public.data.getBrExposPubuseAreaInfo import GetBrExposPubuseAreaInfo
from pycobaltix.schemas.responses import PaginatedAPIResponse


@pytest.mark.integration
@pytest.mark.slow
class TestDataGOKRAPIIntegration:
    """DATA.GO.KR API 통합 테스트"""

    @pytest.fixture(scope="class")
    def data_go_kr_api(self):
        """실제 DATA.GO.KR API 클라이언트 생성"""
        api_key = os.getenv("DATA_GO_KR_API_KEY")

        if not api_key:
            pytest.skip("DATA_GO_KR_API_KEY 환경 변수가 설정되지 않았습니다")

        return DataGOKRAPI(api_key=api_key)

    @pytest.fixture(scope="class")
    def async_data_go_kr_api(self):
        """실제 DATA.GO.KR 비동기 API 클라이언트 생성"""
        api_key = os.getenv("DATA_GO_KR_API_KEY")

        if not api_key:
            pytest.skip("DATA_GO_KR_API_KEY 환경 변수가 설정되지 않았습니다")

        return AsyncDataGOKRAPI(api_key=api_key)

    def test_get_br_title_info_success(self, data_go_kr_api):
        """건축물대장 표제부 조회 성공 테스트"""
        # 테스트용 파라미터 (서울특별시 노원구 상계동)
        test_sigungu_cd = "11350"  # 노원구
        test_bjdong_cd = "10200"   # 상계동
        test_bun = "0923"
        test_ji = "0000"

        result = data_go_kr_api.getBrTitleInfo(
            sigunguCd=test_sigungu_cd,
            bjdongCd=test_bjdong_cd,
            bun=test_bun,
            ji=test_ji,
            numOfRows=10,
            pageNo=1,
        )

        # 결과 검증
        assert result is not None
        assert isinstance(result, PaginatedAPIResponse)

        # 데이터 검증
        assert result.data is not None
        assert isinstance(result.data, list)

        if len(result.data) > 0:
            # 첫 번째 건물 표제부 정보 검증
            first_building = result.data[0]
            assert isinstance(first_building, GetBrTitleInfo)
            assert first_building.sigunguCd == test_sigungu_cd
            assert first_building.bjdongCd == test_bjdong_cd
            assert first_building.bun == test_bun
            assert first_building.ji == test_ji
            assert first_building.platPlc is not None  # 대지위치
            assert first_building.bldNm is not None    # 건물명

        # 페이지네이션 검증
        assert result.pagination is not None
        assert result.pagination.currentPage == 1
        assert result.pagination.totalCount >= 0
        assert result.pagination.count == 10

    def test_get_br_title_info_with_optional_params(self, data_go_kr_api):
        """선택적 파라미터 없이 건축물대장 표제부 조회 테스트"""
        test_sigungu_cd = "11350"  # 노원구
        test_bjdong_cd = "10200"   # 상계동

        result = data_go_kr_api.getBrTitleInfo(
            sigunguCd=test_sigungu_cd,
            bjdongCd=test_bjdong_cd,
            numOfRows=5,
            pageNo=1,
        )

        # 결과 검증
        assert result is not None
        assert isinstance(result, PaginatedAPIResponse)
        assert result.data is not None

        # 페이지네이션 검증
        assert result.pagination.count == 5

    def test_get_br_title_info_pagination(self, data_go_kr_api):
        """건축물대장 표제부 조회 - 페이지네이션 테스트"""
        test_sigungu_cd = "11350"
        test_bjdong_cd = "10200"

        # 첫 번째 페이지
        page1 = data_go_kr_api.getBrTitleInfo(
            sigunguCd=test_sigungu_cd,
            bjdongCd=test_bjdong_cd,
            numOfRows=3,
            pageNo=1,
        )

        assert page1.pagination.currentPage == 1
        assert page1.pagination.hasPrevious is False

        # 두 번째 페이지 (데이터가 충분히 있는 경우)
        if page1.pagination.totalPages > 1:
            page2 = data_go_kr_api.getBrTitleInfo(
                sigunguCd=test_sigungu_cd,
                bjdongCd=test_bjdong_cd,
                numOfRows=3,
                pageNo=2,
            )

            assert page2.pagination.currentPage == 2
            assert page2.pagination.hasPrevious is True

    def test_get_br_title_info_invalid_params(self, data_go_kr_api):
        """잘못된 파라미터로 건축물대장 표제부 조회 테스트"""
        # 존재하지 않는 시군구코드
        invalid_sigungu_cd = "99999"
        invalid_bjdong_cd = "99999"

        result = data_go_kr_api.getBrTitleInfo(
            sigunguCd=invalid_sigungu_cd,
            bjdongCd=invalid_bjdong_cd,
            numOfRows=10,
            pageNo=1,
        )

        # 잘못된 파라미터에 대해서는 빈 결과 또는 에러 응답이 올 수 있음
        assert result is not None
        assert isinstance(result, PaginatedAPIResponse)

    def test_get_br_title_info_building_details(self, data_go_kr_api):
        """건축물대장 표제부 조회 - 상세 정보 검증"""
        test_sigungu_cd = "11350"
        test_bjdong_cd = "10200"
        test_bun = "0923"
        test_ji = "0000"

        result = data_go_kr_api.getBrTitleInfo(
            sigunguCd=test_sigungu_cd,
            bjdongCd=test_bjdong_cd,
            bun=test_bun,
            ji=test_ji,
            numOfRows=1,
            pageNo=1,
        )

        if len(result.data) > 0:
            building = result.data[0]
            
            # 필수 필드 검증
            assert building.rnum is not None           # 순번
            assert building.platPlc is not None       # 대지위치
            assert building.mgmBldrgstPk is not None  # 관리건축물대장PK
            assert building.regstrGbCd is not None    # 대장구분코드
            assert building.regstrKindCd is not None  # 대장종류코드
            
            # 선택적 필드들이 존재하는지 확인
            if building.bldNm:
                assert isinstance(building.bldNm, str)  # 건물명
            if building.platArea:
                assert isinstance(building.platArea, str)  # 대지면적
            if building.archArea:
                assert isinstance(building.archArea, str)  # 건축면적

    def test_get_br_expos_pubuse_area_info_success(self, data_go_kr_api):
        """건물일련번호조회 성공 테스트 (기존 기능 확인)"""
        result = data_go_kr_api.getBrExposPubuseAreaInfo(
            sigunguCd="11350",
            bjdongCd="10200",
            bun="0923",
            ji="0000",
            dongNm="103동",
            hoNm="103호",
            numOfRows=10,
            pageNo=1,
        )

        # 결과 검증
        assert result is not None
        assert isinstance(result, PaginatedAPIResponse)
        assert result.data is not None
        assert isinstance(result.data, list)

        if len(result.data) > 0:
            first_item = result.data[0]
            assert isinstance(first_item, GetBrExposPubuseAreaInfo)


@pytest.mark.integration
@pytest.mark.slow
class TestAsyncDataGOKRAPIIntegration:
    """DATA.GO.KR 비동기 API 통합 테스트"""

    @pytest.fixture(scope="class")
    def async_data_go_kr_api(self):
        """실제 DATA.GO.KR 비동기 API 클라이언트 생성"""
        api_key = os.getenv("DATA_GO_KR_API_KEY")

        if not api_key:
            pytest.skip("DATA_GO_KR_API_KEY 환경 변수가 설정되지 않았습니다")

        return AsyncDataGOKRAPI(api_key=api_key)

    @pytest.mark.asyncio
    async def test_async_get_br_expos_pubuse_area_info_success(self, async_data_go_kr_api):
        """비동기 건물일련번호조회 성공 테스트"""
        result = await async_data_go_kr_api.getBrExposPubuseAreaInfo(
            sigunguCd="11350",
            bjdongCd="10200",
            bun="0923",
            ji="0000",
            dongNm="103동",
            hoNm="103호",
            numOfRows=10,
            pageNo=1,
        )

        # 결과 검증
        assert result is not None
        assert isinstance(result, PaginatedAPIResponse)
        assert result.data is not None
        assert isinstance(result.data, list)

        if len(result.data) > 0:
            first_item = result.data[0]
            assert isinstance(first_item, GetBrExposPubuseAreaInfo) 