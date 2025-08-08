import json
from typing import Optional

import httpx
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackWebHook:
    """웹훅 생성자

    Args:
        webhook_url (str): 웹훅 URL
    """

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send_slack_message(
        self, title="", content: Optional[str] = None, detail: Optional[str] = None
    ):
        """
        슬랙 메시지 전송 함수
        Function to send Slack message

        웹훅 사용시 timestamp 반환 *안함*
        Does *not* return timestamp when using webhook

        Args:
            title (str, optional): 제목 / Title. Defaults to "".
            content (str, optional): 내용 / Content. Defaults to None.
            detail (str, optional): 상세내용 / Detailed content. Defaults to None.

        Raises:
            ValueError: 웹훅 URL 을 제공해야 합니다. / You must provide either webhook URL.
            ValueError: 웹훅 요청 중 오류 발생: {response.status_code}, 응답: {response.text} / Error occurred during webhook request: {response.status_code}, response: {response.text}
            ValueError: Slack API 오류 발생: {e} / Slack API error occurred: {e}

        Returns:
            str: timestamp optional
        """

        content = content or ""
        detail = detail or ""

        # 텍스트 버전 메시지 생성 / Create text version of message
        text = f"{title}\n{content}\n{detail}".strip()

        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{title}*\n{content}"},
            }
        ]

        if detail:
            blocks.append(
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": f"{detail}"}],
                }
            )

        if self.webhook_url:
            headers = {"Content-Type": "application/json"}
            data = {"blocks": blocks, "text": text}  # text 추가 / Add text
            response = httpx.post(
                self.webhook_url,
                headers=headers,
                content=json.dumps(data),
                timeout=10.0,
            )
            if response.status_code != 200:
                raise ValueError(
                    f"웹훅 요청 중 오류 발생: {response.status_code}, 응답: {response.text} / Error occurred during webhook request: {response.status_code}, response: {response.text}"
                )
        else:
            raise ValueError(
                "웹훅 URL 을 제공해야 합니다. / You must provide either webhook URL."
            )


class SlackBot:
    """
    Slack 메시지를 보내고 업데이트하는 봇\n
    Bot for sending and updating Slack messages
    """

    def __init__(self, channel: str, bot_token: str) -> None:
        """
        SlackBot 클래스의 생성자입니다.
        Constructor for the SlackBot class.

        :param channel: Slack 채널 ID (선택적) / Slack channel ID (optional)
        :param bot_token: Slack 봇 토큰 (선택적) / Slack bot token (optional)
        """
        self.channel = channel
        self.bot_token = bot_token

    def update_slack_message(
        self,
        timestamp: str,
        title: str,
    ):
        """
        슬랙메시지 갱신 메서드
        Method to update Slack message

        Args:
            timestamp (str): send_slack_message 메서드에서 반환된 타임스탬프 / Timestamp returned from send_slack_message method
            title (str): 메시지 제목 / Message title

        Raises:
            ValueError: 웹훅 URL 또는 (채널 ID와 봇 토큰)을 제공해야 합니다. / You must provide either webhook URL or (channel ID and bot token).
            ValueError: 웹훅 요청 중 오류 발생: {response.status_code}, 응답: {response.text} / Error occurred during webhook request: {response.status_code}, response: {response.text}
            ValueError: webhook은 메시지 업데이트를 지원하지않습니다. 봇을 생성하여 채널아이디와 봇 토큰을 주입해주세요 / Webhook does not support message updates. Please create a bot and inject channel ID and bot token.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bot_token}",
        }
        message = f"*{title}*"
        data = {"channel": self.channel, "ts": timestamp, "text": message}
        response = httpx.post(
            "https://slack.com/api/chat.update",
            headers=headers,
            json=data,
            timeout=10.0,
        )
        if response.status_code != 200:
            raise ValueError(
                f"Request to slack returned an error {response.status_code}, the response is:\n{response.text}"
            )

    def send_slack_message(
        self, title="", content: Optional[str] = None, detail: Optional[str] = None
    ):
        """
        슬랙 메시지 전송 함수
        Function to send Slack message
        봇 토큰과 채널명 사용시에만 timestamp *반환*
        *Returns* timestamp only when using bot token and channel name

        Args:
            title (str, optional): 제목 / Title. Defaults to "".
            content (str, optional): 내용 / Content. Defaults to None.
            detail (str, optional): 상세내용 / Detailed content. Defaults to None.

        Raises:
            ValueError: 채널 ID와 봇 토큰 을 제공해야 합니다. / You must provide channel ID and bot token.
            ValueError: 웹훅 요청 중 오류 발생: {response.status_code}, 응답: {response.text} / Error occurred during webhook request: {response.status_code}, response: {response.text}
            ValueError: Slack API 오류 발생: {e} / Slack API error occurred: {e}

        Returns:
            str: timestamp optional
        """

        content = content or ""
        detail = detail or ""

        # 텍스트 버전 메시지 생성 / Create text version of message
        text = f"{title}\n{content}\n{detail}".strip()

        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{title}*\n{content}"},
            }
        ]

        if detail:
            blocks.append(
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": f"{detail}"}],
                }
            )

        try:
            client = WebClient(token=self.bot_token)
            response = client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text=text,
                # text 파라미터 추가 / Add text parameter
            )
            return response["ts"]
        except SlackApiError as e:
            print(f"Slack API 오류 발생: {e} / Slack API error occurred: {e}")
            return None
