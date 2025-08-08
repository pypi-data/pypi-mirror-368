import json
import re
from typing import List

import httpx

from pycobaltix.public.registration.registration import (
    PropertyType,
    RealEstateInfo,
    RegistrationStatus,
)
from pycobaltix.schemas.responses import PaginatedAPIResponse, PaginationInfo


def clean_html_tags(text: str) -> str:
    """
    HTML 태그를 제거하고 순수한 텍스트만 반환합니다.

    Args:
        text (str): HTML 태그가 포함된 텍스트

    Returns:
        str: HTML 태그가 제거된 깔끔한 텍스트
    """
    if not text:
        return text

    # HTML 태그 제거 (정규식 사용)
    clean_text = re.sub(r"<[^>]+>", "", text)

    # 연속된 공백을 하나로 정리
    clean_text = re.sub(r"\s+", " ", clean_text)

    # 앞뒤 공백 제거
    return clean_text.strip()


def clean_real_estate_data(data: dict) -> dict:
    """
    부동산 데이터에서 HTML 태그를 제거합니다.

    Args:
        data (dict): 원본 부동산 데이터

    Returns:
        dict: HTML 태그가 제거된 부동산 데이터
    """
    # 주소 및 텍스트 관련 필드들에서 HTML 태그 제거 (원본 API 필드명 사용)
    text_fields = [
        "rd_addr_detail",  # full_address
        "rd_addr",  # road_address
        "buld_name",  # building_name
        "real_indi_cont_detail",  # detailed_land_address
        "real_indi_cont",  # land_address
        "addItem",  # additional_info
    ]

    cleaned_data = data.copy()
    for field in text_fields:
        if field in cleaned_data and cleaned_data[field]:
            cleaned_data[field] = clean_html_tags(cleaned_data[field])

    return cleaned_data


def search_real_estate(
    keyword: str,
    rgs_rec_stat: RegistrationStatus = RegistrationStatus.CURRENT,
    kind_cls: PropertyType = PropertyType.ALL,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedAPIResponse[RealEstateInfo]:
    """
    부동산 등기 정보 검색 API에 요청을 보내고 결과를 PaginatedAPIResponse 객체로 직접 파싱하여 반환합니다.

    Args:
        keyword (str): 검색할 주소 또는 키워드.

    Returns:
        PaginatedAPIResponse[RealEstateInfo]: API 응답을 파싱한 PaginatedAPIResponse 객체.
    """
    request_url = "https://www.iros.go.kr/biz/Pr20ViaRlrgSrchCtrl/retrieveSmplSrchList.do?IS_NMBR_LOGIN__=null"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Content-Type": "application/json; charset=utf-8",
    }

    request_body = {
        "websquare_param": {
            "conn_menu_cls_cd": "01",
            "prgs_mode_cls_cd": "01",
            "inet_srch_cls_cd": "PR01",
            "prgs_stg_cd": "",
            "move_cls": "",
            "swrd": keyword,
            "addr_cls": "3",
            "kind_cls": kind_cls.value,
            "land_bing_yn": "",
            "rgs_rec_stat": rgs_rec_stat.value,
            "admin_regn1": "all",
            "admin_regn2": "",
            "admin_regn3": "",
            "lot_no": "",
            "buld_name": "",
            "buld_no_buld": "",
            "buld_no_room": "",
            "rd_name": "",
            "rd_buld_no": "",
            "rd_buld_no2": "",
            "issue_cls": "5",
            "pageIndex": page,
            "pageUnit": page_size,
            "cmort_flag": "",
            "kap_seq_flag": "",
            "trade_seq_flag": "",
            "etdoc_sel_yn": "",
            "show_cls": "",
            "real_pin_con": "",
            "svc_cls_con": "",
            "item_cls_con": "",
            "judge_enr_cls_con": "",
            "cmort_cls_con": "",
            "trade_cls_con": "",
            "extend_srch": "",
            "usg_cls_con": "",
        }
    }

    encoded_body = json.dumps(
        request_body, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")

    try:
        with httpx.Client() as client:
            response = client.post(request_url, headers=headers, content=encoded_body)
            response.raise_for_status()
            json_response = response.json()

            # API 응답에서 직접 데이터 추출
            pagination_data = json_response.get("paginationInfo", {})
            real_estate_data = json_response.get("dataList", [])

            # RealEstateInfo 객체들 직접 생성 (HTML 태그 제거 후 List Comprehension으로 한 번에 변환)
            real_estate_items: List[RealEstateInfo] = [
                RealEstateInfo.model_validate(clean_real_estate_data(item))
                for item in real_estate_data
            ]

            # PaginationInfo 직접 생성 (중간 모델 없이 바로 변환)
            pagination = PaginationInfo(
                currentPage=pagination_data.get("currentPageNo", 1),
                totalPages=pagination_data.get("totalPageCount", 1),
                totalCount=pagination_data.get("totalRecordCount", 0),
                count=pagination_data.get("recordCountPerPage", 10),
                hasNext=pagination_data.get("lastPageNoOnPageList", 1)
                > pagination_data.get("currentPageNo", 1),
                hasPrevious=pagination_data.get("firstPageNoOnPageList", 1)
                < pagination_data.get("currentPageNo", 1),
            )

            # 최종 응답 객체 반환 (단일 변환)
            return PaginatedAPIResponse(data=real_estate_items, pagination=pagination)
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        return PaginatedAPIResponse(
            data=[],
            pagination=PaginationInfo(
                currentPage=0,
                totalPages=0,
                totalCount=0,
                count=0,
                hasNext=False,
                hasPrevious=False,
            ),
        )


if __name__ == "__main__":
    search_result: PaginatedAPIResponse[RealEstateInfo] = search_real_estate(
        "대전광역시 동구 옥천로 ", page_size=100
    )
    if search_result:
        print("Request successful!")
        # 새로운 직관적인 필드명으로 데이터에 접근
        if search_result.data:
            for item in search_result.data:
                print(item.model_dump_json(indent=4, by_alias=True))
        else:
            print("No real estate data found.")
