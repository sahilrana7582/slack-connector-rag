from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.config import get_settings
from app.connectors.slack.client import SlackConnector
from app.services.rag import RagService
from app.services.slack import SlackService


@lru_cache
def get_slack_connector() -> SlackConnector:
    return SlackConnector(get_settings().slack_bot_token)


SlackConnectorDep = Annotated[SlackConnector, Depends(get_slack_connector)]


def get_slack_service(connector: SlackConnectorDep) -> SlackService:
    return SlackService(connector)


@lru_cache
def get_rag_service() -> RagService:
    return RagService()


SlackServiceDep = Annotated[SlackService, Depends(get_slack_service)]
RagDep = Annotated[RagService, Depends(get_rag_service)]
