import logging
import math
import os
import time
import urllib.parse
from typing import Any, Dict

import httpx

from pycobaltix.public.juso.model import JusoInfo
from pycobaltix.schemas.responses import PaginatedAPIResponse, PaginationInfo

logger = logging.getLogger(__name__)


class JusoGOKRAPI:
    """도로명주소 API 클라이언트"""

    def __init__(self, confm_key: str | None = None):
        self.confmKey = confm_key or os.getenv("JUSO_GO_KR_CONFM_KEY")
        if not self.confmKey:
            raise ValueError("JUSO_GO_KR_CONFM_KEY 환경 변수가 설정되지 않았습니다")
        self.base_url = "https://business.juso.go.kr"

    def _prepare_params(self, **params) -> Dict[str, Any]:
        """요청 파라미터 준비"""
        # 모든 요청에 confmKey와 resultType 자동 추가
        params.update({
            "confmKey": self.confmKey,
            "resultType": "json"
        })

        # None 값과 빈 문자열 제거
        return {k: v for k, v in params.items() if v is not None and v != ""}

    def _make_request(self, endpoint: str, **params) -> Dict[str, Any]:
        """HTTP 요청 실행 (재시도 로직 포함)"""
        filtered_params = self._prepare_params(**params)

        # confmKey만 URL 인코딩 (이미 인코딩된 키 사용)
        confm_key = filtered_params.pop("confmKey")

        # 나머지 파라미터는 URL 인코딩
        encoded_params = {}
        for k, v in filtered_params.items():
            if k == "keyword":
                # keyword는 UTF-8 인코딩
                encoded_params[k] = urllib.parse.quote(str(v), safe='')
            else:
                encoded_params[k] = str(v)

        # URL 구성
        param_string = "&".join([f"{k}={v}" for k, v in encoded_params.items()])
        url = f"{self.base_url}{endpoint}?confmKey={confm_key}&{param_string}"

        max_retries = 5  # 최대 재시도 횟수
        base_delay = 1.0  # 기본 지연 시간 (초)

        for attempt in range(max_retries + 1):
            try:
                # POST 요청으로 전송
                response = httpx.post(url, timeout=10.0)
                response.raise_for_status()
                
                # JSONP 응답 처리 - 괄호 제거
                response_text = response.text.strip()
                if response_text.startswith('(') and response_text.endswith(')'):
                    response_text = response_text[1:-1]
                
                import json
                return json.loads(response_text)

            except (
                httpx.HTTPStatusError,
                httpx.RequestError,
                httpx.TimeoutException,
            ) as e:
                if attempt == max_retries:
                    logger.error(
                        f"API 요청 실패 (최대 재시도 {max_retries}회 초과): {url}"
                    )
                    raise

                delay = base_delay
                logger.warning(
                    f"API 요청 실패 (시도 {attempt + 1}/{max_retries + 1}), {delay}초 후 재시도: {str(e)}"
                )
                time.sleep(delay)

            except Exception as e:
                logger.error(f"예상치 못한 에러 발생: {str(e)}")
                raise

        raise RuntimeError("예상치 못한 코드 경로")

    def _parse_juso_response(
        self, response: Dict[str, Any], countPerPage: int, currentPage: int
    ) -> PaginatedAPIResponse[JusoInfo]:
        """도로명주소 API 응답 파싱"""
        results = response.get("results", {})
        common = results.get("common", {})
        
        # 에러 체크
        error_code = common.get("errorCode", "0")
        if error_code != "0":
            error_message = common.get("errorMessage", "알 수 없는 오류")
            raise RuntimeError(f"API 오류 (코드: {error_code}): {error_message}")

        # 데이터 파싱
        juso_list = results.get("juso", [])
        items = [JusoInfo(**juso) for juso in juso_list]
        
        # 페이지네이션 정보 (common에서 가져오기)
        total_count = int(common.get("totalCount", "0"))
        current_page = int(common.get("currentPage", str(currentPage)))
        count_per_page = int(common.get("countPerPage", str(countPerPage)))
        total_pages = math.ceil(total_count / count_per_page) if total_count > 0 else 1

        return PaginatedAPIResponse(
            data=items,
            pagination=PaginationInfo(
                totalPages=total_pages,
                currentPage=current_page,
                count=count_per_page,
                totalCount=total_count,
                hasNext=current_page < total_pages,
                hasPrevious=current_page > 1,
            ),
        )

    def getJuso(
        self,
        keyword: str,
        currentPage: int = 1,
        countPerPage: int = 10,
        addInfoYn: str = "Y",
        hstryYn: str = "Y",
    ) -> PaginatedAPIResponse[JusoInfo]:
        """도로명주소 검색"""
        response = self._make_request(
            "/addrlink/addrLinkApiJsonp.do",
            keyword=keyword,
            currentPage=currentPage,
            countPerPage=countPerPage,
            addInfoYn=addInfoYn,
            hstryYn=hstryYn,
            resultType="json",
        )
        
        return self._parse_juso_response(response, countPerPage, currentPage)

