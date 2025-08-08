import asyncio
import logging
import math
import os
import time
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Dict

import httpx

from pycobaltix.public.data.getBrExposPubuseAreaInfo import GetBrExposPubuseAreaInfo
from pycobaltix.public.data.getBrTitleInfo import GetBrTitleInfo
from pycobaltix.schemas.responses import PaginatedAPIResponse, PaginationInfo

logger = logging.getLogger(__name__)


class BaseDataGOKRAPI(ABC):
    """V-World API의 공통 로직을 담은 베이스 클래스"""

    def __init__(self, api_key: str | None = None):
        self.serviceKey = api_key or os.getenv("DATA_GO_KR_API_KEY")
        if not self.serviceKey:
            raise ValueError("DATA_GO_KR_API_KEY 환경 변수가 설정되지 않았습니다")
        self.base_url = "http://apis.data.go.kr"

    def _prepare_params(self, **params) -> Dict[str, Any]:
        """요청 파라미터 준비 (공통 로직)"""
        # 모든 요청에 serviceKey 자동 추가
        params.update({"serviceKey": self.serviceKey})
        params.update({"_type": "json"})

        # None 값과 빈 문자열 제거
        return {k: v for k, v in params.items() if v is not None and v != ""}

    def _parse_response(
        self, response: Dict[str, Any], numOfRows: int, pageNo: int
    ) -> PaginatedAPIResponse[GetBrExposPubuseAreaInfo]:
        """응답 파싱 (공통 로직)"""
        body = response.get("response", {}).get("body", {})
        items = [
            GetBrExposPubuseAreaInfo(**item)
            for item in body.get("items", {}).get("item", [])
        ]
        total_count = int(body["totalCount"])
        total_pages = math.ceil(total_count / numOfRows)
        current_page = int(body["pageNo"])

        return PaginatedAPIResponse(
            data=items,
            pagination=PaginationInfo(
                totalPages=total_pages,
                currentPage=current_page,
                count=numOfRows,
                totalCount=total_count,
                hasNext=current_page < total_pages,
                hasPrevious=current_page > 1,
            ),
        )
        
    def _parse_getBrTitleInfo_response(
        self,
        response: Dict[str, Any],
        numOfRows: int,
    ) -> PaginatedAPIResponse[GetBrTitleInfo]:
        body = response.get("response", {}).get("body", {})
        items = [
            GetBrTitleInfo(**item)
            for item in body.get("items", {}).get("item", [])
        ]
        total_count = int(body["totalCount"])
        total_pages = math.ceil(total_count / numOfRows)
        current_page = int(body["pageNo"])
        
        return PaginatedAPIResponse(
            data=items,
            pagination=PaginationInfo(
                totalPages=total_pages,
                currentPage=current_page,
                count=numOfRows,
                totalCount=total_count,
                hasNext=current_page < total_pages,
                hasPrevious=current_page > 1,
            ),
        )

    @abstractmethod
    def _make_request(self, endpoint: str, **params) -> Dict[str, Any]:
        """HTTP 요청 실행 (동기/비동기에서 각각 구현)"""
        pass


class DataGOKRAPI(BaseDataGOKRAPI):
    """DataGOKR API 동기 클라이언트"""

    def _make_request(self, endpoint: str, **params) -> Dict[str, Any]:
        """동기 HTTP 요청 (재시도 로직 포함)"""
        filtered_params = self._prepare_params(**params)

        # 서비스키만 URL 인코딩
        service_key = filtered_params.pop("serviceKey")

        # 나머지 파라미터는 인코딩하지 않고 직접 URL에 붙임
        param_string = "&".join([f"{k}={v}" for k, v in filtered_params.items()])
        url = f"{self.base_url}{endpoint}?serviceKey={service_key}&{param_string}"

        max_retries = 5  # 최대 재시도 횟수
        base_delay = 1.0  # 기본 지연 시간 (초)

        for attempt in range(max_retries + 1):
            try:
                # params 인자를 사용하지 않고 직접 URL 사용
                response = httpx.get(url, timeout=5.0)
                response.raise_for_status()
                return response.json()

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

    def getBrExposPubuseAreaInfo(
        self,
        sigunguCd: str,
        bjdongCd: str,
        bun: str,
        ji: str,
        dongNm: str,
        hoNm: str,
        numOfRows: int = 100,
        pageNo: int = 1,
    ) -> PaginatedAPIResponse[GetBrExposPubuseAreaInfo]:
        """건물일련번호조회"""
        response = self._make_request(
            "/1613000/BldRgstHubService/getBrExposPubuseAreaInfo",
            sigunguCd=sigunguCd,
            bjdongCd=bjdongCd,
            bun=bun,
            ji=ji,
            numOfRows=numOfRows,
            pageNo=pageNo,
            dongNm=dongNm,
            hoNm=hoNm,
        )
        return self._parse_response(response, numOfRows, pageNo)
    
    def getBrTitleInfo(
        self,
        sigunguCd: str,
        bjdongCd: str,
        bun: str | None = None,
        ji: str | None = None,
        numOfRows: int = 100,
        pageNo: int = 1,
    ) -> PaginatedAPIResponse[GetBrTitleInfo]:
        """건축물대장 표제부 조회"""
        response = self._make_request(
            "/1613000/BldRgstHubService/getBrTitleInfo",
            sigunguCd=sigunguCd,
            bjdongCd=bjdongCd,
            bun=bun,
            ji=ji,
            numOfRows=numOfRows,
            pageNo=pageNo,
        )
        
        return self._parse_getBrTitleInfo_response(response, numOfRows)


class AsyncDataGOKRAPI(BaseDataGOKRAPI):
    """DataGOKR API 비동기 클라이언트"""

    async def _make_request(self, endpoint: str, **params) -> Dict[str, Any]:
        """비동기 HTTP 요청 (재시도 로직 포함)"""
        filtered_params = self._prepare_params(**params)

        # 서비스키만 URL 인코딩
        service_key = urllib.parse.quote(filtered_params.pop("serviceKey"), safe="")

        # 나머지 파라미터는 인코딩하지 않고 직접 URL에 붙임
        param_string = "&".join([f"{k}={v}" for k, v in filtered_params.items()])
        url = f"{self.base_url}{endpoint}?serviceKey={service_key}&{param_string}"

        max_retries = 5  # 최대 재시도 횟수
        base_delay = 1.0  # 기본 지연 시간 (초)

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # params 인자를 사용하지 않고 직접 URL 사용
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.json()

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
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"예상치 못한 에러 발생: {str(e)}")
                raise

        raise RuntimeError("예상치 못한 코드 경로")

    async def getBrExposPubuseAreaInfo(
        self,
        sigunguCd: str,
        bjdongCd: str,
        bun: str,
        ji: str,
        dongNm: str,
        hoNm: str,
        numOfRows: int = 100,
        pageNo: int = 1,
    ) -> PaginatedAPIResponse[GetBrExposPubuseAreaInfo]:
        """건물일련번호조회 (비동기)"""
        response = await self._make_request(
            "/1613000/BldRgstHubService/getBrExposPubuseAreaInfo",
            sigunguCd=sigunguCd,
            bjdongCd=bjdongCd,
            bun=bun,
            ji=ji,
            numOfRows=numOfRows,
            pageNo=pageNo,
            dongNm=dongNm,
            hoNm=hoNm,
        )
        return self._parse_response(response, numOfRows, pageNo)


if __name__ == "__main__":
    api = DataGOKRAPI()
    response = api.getBrExposPubuseAreaInfo(
        sigunguCd="11350",
        bjdongCd="10200",
        bun="0923",
        ji="0000",
        numOfRows=100,
        pageNo=1,
        dongNm="103동",
        hoNm="103호",
    )
    print(response)
