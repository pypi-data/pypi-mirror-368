import os

import pytest

from pycobaltix.address.naver_api import NaverAPI

NCP_APIGW_API_KEY = os.getenv("NCP_APIGW_API_KEY", "")
NCP_APIGW_API_KEY_ID = os.getenv("NCP_APIGW_API_KEY_ID", "")


def test_convert_address():
    api = NaverAPI(api_key_id=NCP_APIGW_API_KEY_ID, api_key=NCP_APIGW_API_KEY)
    result = api.convert_address("서울특별시 종로구 사직로 161")
    print(result)


@pytest.mark.skipif(
    not NCP_APIGW_API_KEY or not NCP_APIGW_API_KEY_ID,
    reason="Naver API credentials not set",
)
def test_generate_static_map_image():
    x = 126.8068628
    y = 37.3694862
    api = NaverAPI(api_key_id=NCP_APIGW_API_KEY_ID, api_key=NCP_APIGW_API_KEY)
    result = api.generate_static_map_image(x, y)
    print(result)


if __name__ == "__main__":
    # test_convert_address()
    test_generate_static_map_image()
