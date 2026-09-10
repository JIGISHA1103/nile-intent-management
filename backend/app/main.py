from fastapi import FastAPI

from backend.app.api.intent import router as intent_router


app = FastAPI(
    title="NILE Customer Intent API",
    description="Customer intent and travel requirement management service",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "NILE Customer Intent API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(intent_router)