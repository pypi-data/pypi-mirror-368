import os

import pytest

from pycobaltix.public.vworld.endpoints import VWorldAPI
from pycobaltix.public.vworld.response.buldSnList import BuildingInfo
from pycobaltix.schemas.responses import PaginatedAPIResponse


@pytest.mark.integration
@pytest.mark.slow
class TestVWorldAPIIntegration:
    """V-World API 통합 테스트"""

    @pytest.fixture(scope="class")
    def vworld_api(self):
        """실제 V-World API 클라이언트 생성"""
        api_key = os.getenv("VWORLD_API_KEY")
        domain = os.getenv("VWORLD_DOMAIN")

        if not api_key or not domain:
            pytest.skip(
                "VWORLD_API_KEY 및 VWORLD_DOMAIN 환경 변수가 설정되지 않았습니다"
            )

        return VWorldAPI(api_key=api_key, domain=domain)

    def test_buld_sn_list_success(self, vworld_api):
        """건물일련번호조회 성공 테스트"""
        # 테스트용 PNU (서울특별시 종로구 청운동)
        test_pnu = "1111010100100010000"

        result = vworld_api.buldSnList(pnu=test_pnu, numOfRows=10, pageNo=1)

        # 결과 검증
        assert result is not None
        assert isinstance(result, PaginatedAPIResponse)
        assert result.success is True
        assert result.status == 200
        assert result.message == "success"

        # 데이터 검증
        assert result.data is not None
        assert isinstance(result.data, list)

        if len(result.data) > 0:
            # 첫 번째 건물 정보 검증
            first_building = result.data[0]
            assert isinstance(first_building, BuildingInfo)
            assert first_building.pnu == test_pnu
            assert first_building.liCodeNm is not None
            assert first_building.buldNm is not None

        # 페이지네이션 검증
        assert result.pagination is not None
        assert result.pagination.currentPage == 1
        assert result.pagination.totalCount >= 0
        assert result.pagination.count == 10

    def test_buld_sn_list_with_agbldg_sn(self, vworld_api):
        """건물일련번호조회 - 농업건물일련번호 조건 포함"""
        test_pnu = "1111010100100010000"
        test_agbldg_sn = "0001"

        result = vworld_api.buldSnList(
            pnu=test_pnu, agbldgSn=test_agbldg_sn, numOfRows=5
        )

        # 결과 검증
        assert result is not None
        assert result.success is True

        # 필터링된 결과 검증
        if len(result.data) > 0:
            for building in result.data:
                assert building.agbldgSn == test_agbldg_sn

    def test_buld_sn_list_pagination(self, vworld_api):
        """건물일련번호조회 - 페이지네이션 테스트"""
        test_pnu = "1111010100100010000"

        # 첫 번째 페이지
        page1 = vworld_api.buldSnList(pnu=test_pnu, numOfRows=5, pageNo=1)

        assert page1.pagination.currentPage == 1
        assert page1.pagination.hasPrevious is False

        # 두 번째 페이지 (데이터가 충분히 있는 경우)
        if page1.pagination.totalPages > 1:
            page2 = vworld_api.buldSnList(pnu=test_pnu, numOfRows=5, pageNo=2)

            assert page2.pagination.currentPage == 2
            assert page2.pagination.hasPrevious is True

    def test_buld_sn_list_invalid_pnu(self, vworld_api):
        """잘못된 PNU로 조회 테스트"""
        invalid_pnu = "0000000000000000000"  # 존재하지 않는 PNU

        result = vworld_api.buldSnList(pnu=invalid_pnu)

        # 빈 결과이지만 성공적으로 응답해야 함
        assert result is not None
        assert result.success is True
        assert len(result.data) == 0
        assert result.pagination.totalCount == 0

# 빠른 테스트용 함수
def quick_test():
    """빠른 테스트 - 환경변수 사용"""
    import os

    api_key = os.getenv("VWORLD_API_KEY")
    domain = os.getenv("VWORLD_DOMAIN")

    if not api_key or not domain:
        print("❌ 환경변수를 설정해주세요:")
        print("export VWORLD_API_KEY='your_key'")
        print("export VWORLD_DOMAIN='your_domain'")
        return

    api = VWorldAPI(api_key=api_key, domain=domain)
    result = api.ladfrlList(pnu="1111010100100010000")

    print(f"🎯 빠른 테스트 결과: {result.success}")
    if result.data:
        print(f"📍 첫 번째 건물: {result.data[0].ldCodeNm}")

    buldHoCoList = api.buldHoCoList(pnu="1111010100100010000", buldDongNm="10", buldHoNm="1032")
    if buldHoCoList.data:
        print(f"📍 첫 번째 건물: {buldHoCoList.data[0].buldNm}")


if __name__ == "__main__":
    print("🚀 V-World API 테스트 선택:")
    print("1. manual_test_buld_sn_list() - 코드에 API 키 직접 입력")
    print("2. quick_test() - 환경변수 사용")
    print()

    # 직접 실행 시 수동 테스트 함수 실행
    quick_test()
