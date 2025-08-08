"""
테스트 설정 및 fixture 정의
"""

import os
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_naver_api_credentials():
    """네이버 API 테스트용 자격 증명"""
    return {"api_key_id": "test_api_key_id", "api_key": "test_api_key"}


@pytest.fixture
def mock_slack_webhook_url():
    """슬랙 웹훅 테스트용 URL"""
    return "https://hooks.slack.com/services/TEST/TEST/TEST"


@pytest.fixture
def mock_slack_bot_config():
    """슬랙 봇 테스트용 설정"""
    return {"channel": "#test-channel", "bot_token": "xoxb-test-token"}


@pytest.fixture
def sample_naver_geocoding_response():
    """네이버 지오코딩 API 응답 샘플"""
    return {
        "status": "OK",
        "meta": {"totalCount": 1, "page": 1, "count": 1},
        "addresses": [
            {
                "roadAddress": "서울특별시 강남구 테헤란로 152",
                "jibunAddress": "서울특별시 강남구 역삼동 737",
                "englishAddress": "152, Teheran-ro, Gangnam-gu, Seoul, Republic of Korea",
                "addressElements": [
                    {
                        "types": ["SIDO"],
                        "longName": "서울특별시",
                        "shortName": "서울특별시",
                        "code": "",
                    },
                    {
                        "types": ["SIGUGUN"],
                        "longName": "강남구",
                        "shortName": "강남구",
                        "code": "",
                    },
                    {
                        "types": ["DONGMYUN"],
                        "longName": "역삼동",
                        "shortName": "역삼동",
                        "code": "",
                    },
                    {
                        "types": ["ROAD_NAME"],
                        "longName": "테헤란로",
                        "shortName": "테헤란로",
                        "code": "",
                    },
                    {
                        "types": ["BUILDING_NUMBER"],
                        "longName": "152",
                        "shortName": "152",
                        "code": "",
                    },
                    {
                        "types": ["POSTAL_CODE"],
                        "longName": "06236",
                        "shortName": "06236",
                        "code": "",
                    },
                ],
                "x": "127.0276368",
                "y": "37.4979517",
                "distance": 0.0,
            }
        ],
        "errorMessage": "",
    }


@pytest.fixture
def sample_coordinates():
    """테스트용 좌표 데이터"""
    return {
        "wgs84": {"x": 127.0276368, "y": 37.4979517},
        "tm128": {"x": 200000, "y": 450000},
    }


@pytest.fixture
def mock_requests_get():
    """requests.get 모킹을 위한 fixture"""
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_requests_post():
    """requests.post 모킹을 위한 fixture"""
    with patch("requests.post") as mock_post:
        yield mock_post


@pytest.fixture
def mock_slack_webclient():
    """Slack WebClient 모킹을 위한 fixture"""
    with patch("slack_sdk.WebClient") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.chat_postMessage.return_value = {"ts": "1234567890.123456"}
        yield mock_instance


@pytest.fixture(autouse=True)
def setup_test_environment():
    """테스트 환경 자동 설정"""
    # 테스트용 환경 변수 설정
    os.environ["TESTING"] = "1"
    yield
    # 테스트 후 환경 변수 정리
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


# 마커 설정
def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line("markers", "unit: 단위 테스트")
    config.addinivalue_line("markers", "integration: 통합 테스트")
    config.addinivalue_line("markers", "e2e: E2E 테스트")
    config.addinivalue_line("markers", "slow: 느린 테스트")


def pytest_collection_modifyitems(config, items):
    """테스트 수집 후 마커 자동 추가"""
    for item in items:
        # 파일명 기반으로 마커 자동 추가
        if "unit" in item.fspath.basename:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        elif "e2e" in item.fspath.basename:
            item.add_marker(pytest.mark.e2e)
