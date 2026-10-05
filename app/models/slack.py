from typing import Optional

from pydantic import BaseModel, Field


# Field names match Slack's payload, so raw Slack JSON validates directly
# and any keys we don't list are ignored.


class SlackChannel(BaseModel):
    id: str
    name: str
    is_private: bool = False


class SlackFile(BaseModel):
    id: str
    name: Optional[str] = None
    mimetype: Optional[str] = None
    size: Optional[int] = None
    url_private: Optional[str] = None


class SlackMessage(BaseModel):
    ts: str
    user: Optional[str] = None
    text: str = ""
    thread_ts: Optional[str] = None
    files: list[SlackFile] = Field(default_factory=list)
