import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError

from app.config import Settings
from app.routes import router as api_router
from app.middlewares.auth_middleware import AuthMiddleware
from app.utils.logger import logger
from app.services.document_processor import DocumentProcessor
from app.services.summarizer import Summarizer

settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description="FastAPI pipeline for LangChain doc ingestion & summarization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware, secret_key=settings.auth_secret)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

document_processor = DocumentProcessor()
summarizer = Summarizer()

app.include_router(api_router)

@app.on_event("startup")
async def startup():
    await document_processor.initialize()
    await summarizer.initialize()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown():
    await document_processor.shutdown()
    await summarizer.shutdown()
    logger.info("Application shutdown complete")