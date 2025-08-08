#!/usr/bin/env python3
"""
DATA.GO.KR API getBrTitleInfo 함수 간단 실행 예제
실제 API 키가 있을 때만 동작합니다.
"""

import os
from pycobaltix.public.data.endpoints import DataGOKRAPI


def main():
    """getBrTitleInfo API 실행 예제"""
    # 환경 변수에서 API 키 가져오기
    api_key = os.getenv("DATA_GO_KR_API_KEY")
    
    if not api_key:
        print("❌ DATA_GO_KR_API_KEY 환경 변수를 설정해주세요.")
        print("   export DATA_GO_KR_API_KEY=your_api_key_here")
        return
    
    # API 클라이언트 생성
    try:
        api = DataGOKRAPI(api_key=api_key)
        print("✅ DATA.GO.KR API 클라이언트가 생성되었습니다.")
    except Exception as e:
        print(f"❌ API 클라이언트 생성 실패: {e}")
        return
    
    # 테스트 파라미터
    test_params = {
        "sigunguCd": "11350",  # 서울특별시 노원구
        "bjdongCd": "10200",   # 상계동
        "bun": "0923",         # 번지
        "ji": "0000",          # 지번
        "numOfRows": 5,        # 결과 개수
        "pageNo": 1            # 페이지 번호
    }
    
    print(f"\n🔍 건축물대장 표제부 조회 테스트 시작...")
    print(f"   - 시군구코드: {test_params['sigunguCd']}")
    print(f"   - 법정동코드: {test_params['bjdongCd']}")
    print(f"   - 번지: {test_params['bun']}-{test_params['ji']}")
    
    try:
        # getBrTitleInfo API 호출
        result = api.getBrTitleInfo(**test_params)
        
        print(f"✅ API 호출 성공!")
        print(f"   - 총 {result.pagination.totalCount}건의 데이터가 조회되었습니다.")
        print(f"   - 현재 페이지: {result.pagination.currentPage}/{result.pagination.totalPages}")
        print(f"   - 다음 페이지 존재 여부: {result.pagination.hasNext}")
        
        # 조회된 데이터 출력
        if result.data:
            print(f"\n📋 조회된 건축물 정보:")
            for idx, building in enumerate(result.data, 1):
                print(f"\n   {idx}. 건물 정보:")
                print(f"      - 순번: {building.rnum}")
                print(f"      - 대지위치: {building.platPlc}")
                print(f"      - 건물명: {building.bldNm}")
                print(f"      - 도로명주소: {building.newPlatPlc}")
                print(f"      - 관리건축물대장PK: {building.mgmBldrgstPk}")
                print(f"      - 대장구분: {building.regstrGbCdNm}")
                print(f"      - 대장종류: {building.regstrKindCdNm}")
                
                # 면적 정보
                if building.platArea and building.archArea:
                    print(f"      - 대지면적: {building.platArea}㎡")
                    print(f"      - 건축면적: {building.archArea}㎡")
                
                # 구조 및 용도 정보
                if building.strctCdNm:
                    print(f"      - 구조: {building.strctCdNm}")
                if building.mainPurpsCdNm:
                    print(f"      - 주용도: {building.mainPurpsCdNm}")
                    
                # 층수 정보
                if building.grndFlrCnt and building.ugrndFlrCnt:
                    print(f"      - 층수: 지상{building.grndFlrCnt}층, 지하{building.ugrndFlrCnt}층")
        else:
            print("   ❌ 조회된 데이터가 없습니다.")
            
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        print(f"   에러 타입: {type(e).__name__}")
        return
    
    print(f"\n🔍 선택적 파라미터 없이 조회 테스트...")
    try:
        # bun, ji 없이 조회
        result2 = api.getBrTitleInfo(
            sigunguCd="11350",
            bjdongCd="10200",
            numOfRows=3,
            pageNo=1
        )
        
        print(f"✅ 선택적 파라미터 없이 API 호출 성공!")
        print(f"   - 총 {result2.pagination.totalCount}건의 데이터가 조회되었습니다.")
        
    except Exception as e:
        print(f"❌ 선택적 파라미터 없이 API 호출 실패: {e}")


if __name__ == "__main__":
    main() 