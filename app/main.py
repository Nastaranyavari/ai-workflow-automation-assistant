from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AI Workflow Automation Assistant",
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "AI Workflow Automation Assistant"
    }