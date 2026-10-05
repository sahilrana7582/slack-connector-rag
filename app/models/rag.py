from pydantic import BaseModel, Field

from app.models.document import Document


class IngestSlackRequest(BaseModel):
    channel_id: str
    limit: int = Field(100, ge=1, le=200)


class IngestResponse(BaseModel):
    ingested: int


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(3, ge=1, le=20)


class QueryResponse(BaseModel):
    question: str
    sources: list[Document]
