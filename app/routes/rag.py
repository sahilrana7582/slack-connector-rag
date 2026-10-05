from fastapi import APIRouter

from app.dependencies import RagDep, SlackServiceDep
from app.models.document import Document
from app.models.rag import (
    IngestResponse,
    IngestSlackRequest,
    QueryRequest,
    QueryResponse,
)

# The RAG workflow: ingest -> inspect -> query.
# Slack is only reached through SlackService, never through the Slack routes.
router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ingest/slack")
def ingest_slack(
    body: IngestSlackRequest,
    slack: SlackServiceDep,
    rag: RagDep,
) -> IngestResponse:
    documents = slack.fetch_documents(body.channel_id, body.limit)
    return IngestResponse(ingested=rag.ingest(documents))


@router.get("/documents")
def list_documents(rag: RagDep) -> list[Document]:
    return rag.list_documents()


@router.post("/query")
def query(body: QueryRequest, rag: RagDep) -> QueryResponse:
    sources = rag.search(body.question, body.top_k)
    return QueryResponse(question=body.question, sources=sources)
