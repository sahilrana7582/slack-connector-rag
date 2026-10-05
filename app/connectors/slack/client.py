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

    def fetch_documents(
        self,
        channel_id: str,
        limit: int = 100,
    ) -> list[Document]:
        """Convert Slack messages and threads into RAG Documents."""

        documents = []

        messages = self.get_messages(channel_id, limit)

        for message in messages:

            if not message.text.strip():
                continue

            # This message has replies.
            if message.reply_count > 0:

                print("Inside the Reply Count")

                thread_messages = self.get_thread_replies(
                    channel_id,
                    message.thread_ts or message.ts,
                )

                content_parts = []

                for thread_message in thread_messages:
                    if thread_message.text.strip():
                        content_parts.append(thread_message.text.strip())

                content = "\n\n".join(content_parts)

                document = Document(
                    id=f"slack:{channel_id}:{message.ts}",
                    content=content,
                    metadata={
                        "source": "slack",
                        "channel_id": channel_id,
                        "user_id": message.user,
                        "timestamp": message.ts,
                        "type": "thread",
                        "reply_count": message.reply_count,
                    },
                )

            # Normal Slack message
            else:

                document = Document(
                    id=f"slack:{channel_id}:{message.ts}",
                    content=message.text.strip(),
                    metadata={
                        "source": "slack",
                        "channel_id": channel_id,
                        "user_id": message.user,
                        "timestamp": message.ts,
                        "type": "message",
                    },
                )

            documents.append(document)

        return documents