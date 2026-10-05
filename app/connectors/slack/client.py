from slack_sdk import WebClient

from app.models.document import Document
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

    def get_messages(self, channel_id: str, limit: int = 20) -> list[SlackMessage]:
        response = self._client.conversations_history(channel=channel_id, limit=limit)
        return [SlackMessage.model_validate(m) for m in response["messages"]]

    def list_files(self, channel_id: str, limit: int = 20) -> list[SlackFile]:
        response = self._client.files_list(channel=channel_id, count=limit)
        return [SlackFile.model_validate(f) for f in response["files"]]

    def fetch_documents(self, channel_id: str, limit: int = 100) -> list[Document]:
        """Messages normalised into the Document shape the RAG side expects."""
        return [
            Document(
                id=f"slack:{channel_id}:{m.ts}",  # ts is only unique per channel
                content=m.text,
                metadata={
                    "source": "slack",
                    "channel_id": channel_id,
                    "user_id": m.user,
                    "timestamp": m.ts,
                },
            )
            for m in self.get_messages(channel_id, limit)
            if m.text.strip()
        ]
