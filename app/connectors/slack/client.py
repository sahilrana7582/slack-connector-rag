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
        response = self._client.conversations_history(channel=channel_id, limit=limit)
        return [SlackMessage.model_validate(m) for m in response["messages"]]

    def list_files(self, channel_id: str, limit: int = 100) -> list[SlackFile]:
        response = self._client.files_list(channel=channel_id, count=limit)
        return [SlackFile.model_validate(f) for f in response["files"]]
    
    def get_thread_replies(
        self,
        channel_id: str,
        thread_ts: str,
    ) -> list[SlackMessage]:
        
        response = self._client.conversations_replies(
            channel=channel_id,
            ts=thread_ts,
            limit=100,
        )

        return [
            SlackMessage.model_validate(message)
            for message in response["messages"]
        ]
