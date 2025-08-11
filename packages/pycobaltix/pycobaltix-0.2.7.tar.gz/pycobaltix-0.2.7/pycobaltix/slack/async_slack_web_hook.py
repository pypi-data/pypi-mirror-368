import json
from typing import Any

import aiohttp
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient


class AsyncSlackWebHook:
    """비동기 웹훅 생성자

    Args:
        webhook_url (str): 웹훅 URL
    """

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def send_slack_message(self, title: str, content: str = "", detail: str = ""):
        """
        슬랙 메시지 전송 함수 (비동기)
        Function to send Slack message (async)

        웹훅 사용시 timestamp 반환 *안함*
        Does *not* return timestamp when using webhook

        Args:
            title (str, optional): 제목 / Title. Defaults to "".
            content (str, optional): 내용 / Content. Defaults to None.
            detail (str, optional): 상세내용 / Detailed content. Defaults to None.

        Raises:
            ValueError: 웹훅 URL 을 제공해야 합니다. / You must provide either webhook URL.
            ValueError: 웹훅 요청 중 오류 발생: {response.status}, 응답: {response_text} / Error occurred during webhook request: {response.status}, response: {response_text}

        Returns:
            None
        """

        # 텍스트 버전 메시지 생성 / Create text version of message
        text = f"{title}\n{content}\n{detail}".strip()

        blocks: list[dict[str, Any]] = [
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
            data = {"blocks": blocks, "text": text}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url, headers=headers, data=json.dumps(data)
                ) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        raise ValueError(
                            f"웹훅 요청 중 오류 발생: {response.status}, 응답: {response_text} / "
                            f"Error occurred during webhook request: {response.status}, response: {response_text}"
                        )
        else:
            raise ValueError(
                "웹훅 URL 을 제공해야 합니다. / You must provide either webhook URL."
            )


class AsyncSlackBot:
    """
    비동기 Slack 메시지를 보내고 업데이트하는 봇\n
    Async bot for sending and updating Slack messages
    """

    def __init__(self, channel: str, bot_token: str) -> None:
        """
        AsyncSlackBot 클래스의 생성자입니다.
        Constructor for the AsyncSlackBot class.

        :param channel: Slack 채널 ID / Slack channel ID
        :param bot_token: Slack 봇 토큰 / Slack bot token
        """
        self.channel = channel
        self.bot_token = bot_token
        self.client = AsyncWebClient(token=bot_token)

    async def update_slack_message(self, timestamp: str, title: str):
        """
        슬랙메시지 갱신 메서드 (비동기)
        Method to update Slack message (async)

        Args:
            timestamp (str): send_slack_message 메서드에서 반환된 타임스탬프 / Timestamp returned from send_slack_message method
            title (str): 메시지 제목 / Message title

        Raises:
            ValueError: 업데이트 요청 중 오류 발생 / Error occurred during update request
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bot_token}",
        }
        message = f"*{title}*"
        data = {"channel": self.channel, "ts": timestamp, "text": message}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://slack.com/api/chat.update", headers=headers, json=data
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise ValueError(
                        f"Request to slack returned an error {response.status}, "
                        f"the response is:\n{response_text}"
                    )

    async def send_slack_message(self, title: str, content: str = "", detail: str = ""):
        """
        슬랙 메시지 전송 함수 (비동기)
        Function to send Slack message (async)

        봇 토큰과 채널명 사용시에만 timestamp *반환*
        *Returns* timestamp only when using bot token and channel name

        Args:
            title (str, optional): 제목 / Title. Defaults to "".
            content (str, optional): 내용 / Content. Defaults to None.
            detail (str, optional): 상세내용 / Detailed content. Defaults to None.

        Raises:
            ValueError: Slack API 오류 발생: {e} / Slack API error occurred: {e}

        Returns:
            str: timestamp optional
        """

        # 텍스트 버전 메시지 생성 / Create text version of message
        text = f"{title}\n{content}\n{detail}".strip()

        blocks: list[dict[str, Any]] = [
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
            response = await self.client.chat_postMessage(
                channel=self.channel, blocks=blocks, text=text
            )
            return response["ts"]
        except SlackApiError as e:
            print(f"Slack API 오류 발생: {e} / Slack API error occurred: {e}")
            return None
