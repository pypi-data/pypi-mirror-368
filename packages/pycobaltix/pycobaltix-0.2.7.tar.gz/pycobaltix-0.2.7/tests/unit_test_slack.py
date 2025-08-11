"""
slack 모듈 단위 테스트
"""

import json
from unittest.mock import Mock, patch

import pytest
from slack_sdk.errors import SlackApiError

from pycobaltix.slack.slack_web_hook import SlackBot, SlackWebHook


@pytest.mark.unit
class TestSlackWebHook:
    """SlackWebHook 클래스 테스트"""

    def test_slack_webhook_initialization(self, mock_slack_webhook_url):
        """SlackWebHook 초기화 테스트"""
        webhook = SlackWebHook(webhook_url=mock_slack_webhook_url)
        assert webhook.webhook_url == mock_slack_webhook_url

    def test_send_slack_message_success(
        self, mock_requests_post, mock_slack_webhook_url
    ):
        """슬랙 웹훅 메시지 전송 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_post.return_value = mock_response

        # 웹훅 생성 및 메시지 전송
        webhook = SlackWebHook(webhook_url=mock_slack_webhook_url)
        webhook.send_slack_message(
            title="테스트 제목", content="테스트 내용", detail="테스트 상세내용"
        )

        # 요청 검증
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args

        # URL 검증
        assert call_args[0][0] == mock_slack_webhook_url

        # 헤더 검증
        assert call_args[1]["headers"]["Content-Type"] == "application/json"

        # 데이터 검증
        sent_data = json.loads(call_args[1]["data"])
        assert "blocks" in sent_data
        assert "text" in sent_data
        assert len(sent_data["blocks"]) == 2  # section + context

    def test_send_slack_message_without_detail(
        self, mock_requests_post, mock_slack_webhook_url
    ):
        """상세내용 없이 슬랙 메시지 전송 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_post.return_value = mock_response

        # 웹훅 생성 및 메시지 전송
        webhook = SlackWebHook(webhook_url=mock_slack_webhook_url)
        webhook.send_slack_message(title="테스트 제목", content="테스트 내용")

        # 요청 검증
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args

        # 데이터 검증 - detail이 없으면 블록이 1개만 있어야 함
        sent_data = json.loads(call_args[1]["data"])
        assert len(sent_data["blocks"]) == 1  # section only

    def test_send_slack_message_minimal(
        self, mock_requests_post, mock_slack_webhook_url
    ):
        """최소한의 정보로 슬랙 메시지 전송 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_post.return_value = mock_response

        # 웹훅 생성 및 메시지 전송
        webhook = SlackWebHook(webhook_url=mock_slack_webhook_url)
        webhook.send_slack_message(title="테스트 제목")

        # 요청 검증
        mock_requests_post.assert_called_once()

    def test_send_slack_message_webhook_error(
        self, mock_requests_post, mock_slack_webhook_url
    ):
        """웹훅 오류 응답 테스트"""
        # Mock 오류 응답 설정
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_requests_post.return_value = mock_response

        # 웹훅 생성
        webhook = SlackWebHook(webhook_url=mock_slack_webhook_url)

        # 오류 발생 확인
        with pytest.raises(ValueError) as exc_info:
            webhook.send_slack_message(title="테스트")

        assert "웹훅 요청 중 오류 발생" in str(exc_info.value)
        assert "400" in str(exc_info.value)

    def test_send_slack_message_no_webhook_url(self):
        """웹훅 URL 없이 메시지 전송 시도 테스트"""
        # 웹훅 URL 없이 생성
        webhook = SlackWebHook(webhook_url="")

        # 오류 발생 확인
        with pytest.raises(ValueError) as exc_info:
            webhook.send_slack_message(title="테스트")

        assert "웹훅 URL 을 제공해야 합니다" in str(exc_info.value)


@pytest.mark.unit
class TestSlackBot:
    """SlackBot 클래스 테스트"""

    def test_slack_bot_initialization(self, mock_slack_bot_config):
        """SlackBot 초기화 테스트"""
        bot = SlackBot(
            channel=mock_slack_bot_config["channel"],
            bot_token=mock_slack_bot_config["bot_token"],
        )

        assert bot.channel == "#test-channel"
        assert bot.bot_token == "xoxb-test-token"

    def test_send_slack_message_success(
        self, mock_slack_webclient, mock_slack_bot_config
    ):
        """슬랙 봇 메시지 전송 성공 테스트"""
        # 봇 생성 및 메시지 전송
        bot = SlackBot(
            channel=mock_slack_bot_config["channel"],
            bot_token=mock_slack_bot_config["bot_token"],
        )

        timestamp = bot.send_slack_message(
            title="테스트 제목", content="테스트 내용", detail="테스트 상세내용"
        )

        # 결과 검증
        assert timestamp == "1234567890.123456"

        # WebClient 호출 검증
        mock_slack_webclient.chat_postMessage.assert_called_once()
        call_args = mock_slack_webclient.chat_postMessage.call_args

        # 파라미터 검증
        assert call_args[1]["channel"] == "#test-channel"
        assert "blocks" in call_args[1]
        assert "text" in call_args[1]

    def test_send_slack_message_without_detail(
        self, mock_slack_webclient, mock_slack_bot_config
    ):
        """상세내용 없이 슬랙 봇 메시지 전송 테스트"""
        bot = SlackBot(
            channel=mock_slack_bot_config["channel"],
            bot_token=mock_slack_bot_config["bot_token"],
        )

        timestamp = bot.send_slack_message(title="테스트 제목", content="테스트 내용")

        # 결과 검증
        assert timestamp == "1234567890.123456"

        # WebClient 호출 검증
        mock_slack_webclient.chat_postMessage.assert_called_once()
        call_args = mock_slack_webclient.chat_postMessage.call_args

        # 블록 수 검증 - detail이 없으면 1개만
        assert len(call_args[1]["blocks"]) == 1

    @patch("slack_sdk.WebClient")
    def test_send_slack_message_api_error(
        self, mock_webclient_class, mock_slack_bot_config
    ):
        """Slack API 오류 테스트"""
        # Mock WebClient에서 예외 발생 설정
        mock_client = Mock()
        mock_client.chat_postMessage.side_effect = SlackApiError(
            "API Error", response={"error": "invalid_auth"}
        )
        mock_webclient_class.return_value = mock_client

        # 봇 생성 및 메시지 전송
        bot = SlackBot(
            channel=mock_slack_bot_config["channel"],
            bot_token=mock_slack_bot_config["bot_token"],
        )

        # API 오류 발생 시 None 반환 확인
        result = bot.send_slack_message(title="테스트")
        assert result is None

    def test_update_slack_message_success(
        self, mock_requests_post, mock_slack_bot_config
    ):
        """슬랙 메시지 업데이트 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_post.return_value = mock_response

        # 봇 생성 및 메시지 업데이트
        bot = SlackBot(
            channel=mock_slack_bot_config["channel"],
            bot_token=mock_slack_bot_config["bot_token"],
        )

        bot.update_slack_message(timestamp="1234567890.123456", title="업데이트된 제목")

        # 요청 검증
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args

        # URL 검증
        assert call_args[0][0] == "https://slack.com/api/chat.update"

        # 헤더 검증
        assert call_args[1]["headers"]["Authorization"] == "Bearer xoxb-test-token"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"

        # 데이터 검증
        sent_data = call_args[1]["json"]
        assert sent_data["channel"] == "#test-channel"
        assert sent_data["ts"] == "1234567890.123456"
        assert "업데이트된 제목" in sent_data["text"]

    def test_update_slack_message_error(
        self, mock_requests_post, mock_slack_bot_config
    ):
        """슬랙 메시지 업데이트 오류 테스트"""
        # Mock 오류 응답 설정
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_requests_post.return_value = mock_response

        # 봇 생성
        bot = SlackBot(
            channel=mock_slack_bot_config["channel"],
            bot_token=mock_slack_bot_config["bot_token"],
        )

        # 오류 발생 확인
        with pytest.raises(ValueError) as exc_info:
            bot.update_slack_message(
                timestamp="1234567890.123456", title="업데이트된 제목"
            )

        assert "Request to slack returned an error 400" in str(exc_info.value)
