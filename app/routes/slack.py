from fastapi import APIRouter, Query

from app.dependencies import SlackDep
from app.models.slack import SlackChannel, SlackFile, SlackMessage

# Raw look at what Slack returns. Nothing here touches the RAG side.
# Plain `def` (not `async def`) on purpose: slack_sdk is blocking, so FastAPI
# runs these in a threadpool instead of freezing the event loop.
router = APIRouter(prefix="/slack", tags=["slack"])


@router.get("/channels")
def list_channels(slack: SlackDep) -> list[SlackChannel]:
    return slack.list_channels()


@router.get("/channels/{channel_id}/messages")
def get_messages(
    channel_id: str,
    slack: SlackDep,
    limit: int = Query(20, ge=1, le=200),
) -> list[SlackMessage]:
    return slack.get_messages(channel_id, limit)


@router.get("/channels/{channel_id}/files")
def list_files(
    channel_id: str,
    slack: SlackDep,
    limit: int = Query(20, ge=1, le=200),
) -> list[SlackFile]:
    return slack.list_files(channel_id, limit)
