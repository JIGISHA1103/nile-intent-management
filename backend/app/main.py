from fastapi import FastAPI

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