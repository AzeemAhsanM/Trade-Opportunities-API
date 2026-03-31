"""
Trade Opportunities API - Main Application
FastAPI service for analyzing Indian market sector trade opportunities
"""

import time
import uuid
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import analyze
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.session import SessionMiddleware
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - startup and shutdown events."""
    logger.info("Trade Opportunities API starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Trade Opportunities API shutting down...")


app = FastAPI(
    title="Trade Opportunities API",
    description=(
        "A FastAPI service that analyzes market data and provides trade opportunity "
        "insights for specific sectors in India. Powered by AI and real-time web data."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware)
app.add_middleware(RateLimitMiddleware)


# Request / response logging

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    logger.info(f"[{request_id}] → {request.method} {request.url.path}")

    response: Response = await call_next(request)

    elapsed = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"[{request_id}] ← {response.status_code} ({elapsed} ms)"
    )
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{elapsed}ms"
    return response


# Routers

app.include_router(analyze.router, tags=["Analysis"])


# Root / health endpoint

@app.get("/", summary="API Root", tags=["Health"])
async def root():
    return {
        "name": "Trade Opportunities API",
        "version": "1.0.0",
        "description": "AI-powered trade opportunity analysis for Indian market sectors",
        "docs": "/docs",
        "health": "/health",
        "analyze": "/analyze/{sector}",
    }


@app.get("/health", summary="Health Check", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "trade-opportunities-api",
    }


# Global exception handler

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "path": str(request.url.path),
        },
    )
