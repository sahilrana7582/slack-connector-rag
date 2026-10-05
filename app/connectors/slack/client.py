from slack_sdk import WebClient

from app.models.slack import SlackChannel, SlackFile, SlackMessage


class SlackConnector:
    """Talks to Slack and nothing else. No FastAPI, no RAG."""

    def __init__(self, token: str) -> None:
        self._client = WebClient(token=token)

    def list_channels(self, limit: int = 100) -> list[SlackChannel]:
        response = self._client.conversations_list(
            types="public_channel,private_channel",
            limit=limit,
        )
        return [SlackChannel.model_validate(c) for c in response["channels"]]

    def get_messages(self, channel_id: str, limit: int = 100) -> list[SlackMessage]:
        """All messages in the channel. `limit` is the page size per Slack request."""
        return self._get_all_messages(
            self._client.conversations_history,
            channel=channel_id,
            limit=limit,
        )

    def list_files(self, channel_id: str, limit: int = 100) -> list[SlackFile]:
        response = self._client.files_list(channel=channel_id, count=limit)
        return [SlackFile.model_validate(f) for f in response["files"]]

    def get_thread_replies(
        self,
        channel_id: str,
        thread_ts: str,
        limit: int = 100,
    ) -> list[SlackMessage]:
        """The root and every reply in the thread. `limit` is the page size per request."""
        return self._get_all_messages(
            self._client.conversations_replies,
            channel=channel_id,
            ts=thread_ts,
            limit=limit,
        )

    @staticmethod
    def _get_all_messages(api_method, **params) -> list[SlackMessage]:
        """Follow Slack's next_cursor until there are no more pages."""
        messages: list[SlackMessage] = []
        cursor = None

        while True:
            response = api_method(cursor=cursor, **params)
            messages.extend(SlackMessage.model_validate(m) for m in response["messages"])

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                return messages
