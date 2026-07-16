from fastapi import FastAPI

from app.routers.upload_router import router as upload_router
from app.routers.chat_router import router as chat_router


app = FastAPI(
    title="DocuMind AI",
    description="Enterprise RAG Assistant for Intelligent Document Question Answering",
    version="1.0.0"
)


app.include_router(upload_router)
app.include_router(chat_router)


@app.get("/")
async def root():

    return {
        "message": "Welcome to DocuMind AI API",
        "version": "1.0.0",
        "status": "running"
    }