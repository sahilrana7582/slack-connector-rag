from app.connectors.slack.client import SlackConnector
from app.models.document import Document
from app.models.slack import SlackMessage


class SlackService:
    """Turns Slack content into RAG Documents.

    All Slack access goes through the injected connector, so this class has no
    FastAPI and no slack_sdk in it and can be tested with a fake connector.
    """

    def __init__(self, connector: SlackConnector) -> None:
        self._connector = connector

    def fetch_documents(self, channel_id: str, limit: int = 100) -> list[Document]:
        """Convert Slack messages and threads into RAG Documents."""
        documents = []

        for message in self._connector.get_messages(channel_id, limit):
            if not message.text.strip():
                continue

            if message.reply_count > 0:
                documents.append(self._thread_document(channel_id, message))
            else:
                documents.append(self._message_document(channel_id, message))

        return documents

    def _message_document(self, channel_id: str, message: SlackMessage) -> Document:
        return Document(
            id=f"slack:{channel_id}:{message.ts}",
            content=message.text.strip(),
            metadata={
                "source": "slack",
                "channel_id": channel_id,
                "user_id": message.user,
                "timestamp": message.timestamp,
                "type": "message",
            },
        )

    def _thread_document(self, channel_id: str, message: SlackMessage) -> Document:
        replies = self._connector.get_thread_replies(
            channel_id,
            message.ts or message.thread_ts
        )
        content = "\n\n".join(
            (
                f"user_id={r.user} "
                f"ts={r.ts}] "
                f"timestamp={r.timestamp}] "
                f"{r.text.strip()}"
            )
            for r in replies
            if r.text.strip()
        )

        return Document(
            id=f"slack:{channel_id}:{message.ts}",
            content=content,
            metadata={
                "source": "slack",
                "channel_id": channel_id,
                "user_id": message.user,
                "timestamp": message.timestamp,
                "type": "thread",
                "reply_count": message.reply_count,
            },
        )
