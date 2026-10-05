from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slack_sdk.errors import SlackApiError

from app.routes.routes import api_router

app = FastAPI(title="Slack Connector RAG")
app.include_router(api_router)


@app.exception_handler(SlackApiError)
def handle_slack_error(request: Request, exc: SlackApiError) -> JSONResponse:
    error = exc.response.get("error", "unknown_error")
    status_code = 404 if error == "channel_not_found" else 502
    return JSONResponse(status_code=status_code, content={"detail": f"Slack error: {error}"})


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", reload=True)
