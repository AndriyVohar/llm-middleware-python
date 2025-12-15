"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.exceptions import LLMMiddlewareException
from app.core.logging import get_logger, setup_logging
from app.routers import chat, tools

# Initialize settings and logging
settings = get_settings()
setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    # Startup
    logger.info("Starting LLM Middleware service...")
    logger.info(f"Default provider: {settings.default_provider}")
    logger.info(f"Default model: {settings.default_model}")
    logger.info(f"DeepInfra available: {settings.is_deepinfra_available}")
    logger.info(f"OpenAI available: {settings.is_openai_available}")
    logger.info(f"Ollama available: {settings.is_ollama_available}")

    yield

    # Shutdown
    logger.info("Shutting down LLM Middleware service...")


# Create FastAPI application
app = FastAPI(
    title="LLM Middleware Service",
    description="FastAPI middleware для роботи з LLM провайдерами та tool calling",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(LLMMiddlewareException)
async def llm_middleware_exception_handler(request, exc: LLMMiddlewareException):
    """Handle custom middleware exceptions."""
    logger.error(f"LLM Middleware error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": exc.message,
            "details": exc.details,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.exception("Unexpected error occurred")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc),
        }
    )


# Include routers
app.include_router(chat.router)
app.include_router(tools.router)


# Health check endpoints
@app.get("/", tags=["health"])
async def root():
    """Root endpoint."""
    return {
        "service": "LLM Middleware",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint with system information."""
    return {
        "status": "ok",
        "service": "LLM Middleware",
        "version": "2.0.0",
        "config": {
            "default_provider": settings.default_provider,
            "default_model": settings.default_model,
            "providers_available": {
                "deepinfra": settings.is_deepinfra_available,
                "openai": settings.is_openai_available,
                "ollama": settings.is_ollama_available,
            }
        }
    }


@app.get("/api/providers", tags=["info"])
async def get_providers():
    """Get list of available LLM providers."""
    return {
        "providers": [
            {
                "name": "deepinfra",
                "description": "DeepInfra API - Cloud-based LLM provider",
                "available": settings.is_deepinfra_available,
                "requires_api_key": True,
            },
            {
                "name": "openai",
                "description": "OpenAI API - GPT models",
                "available": settings.is_openai_available,
                "requires_api_key": True,
            },
            {
                "name": "ollama",
                "description": "Ollama Local - Self-hosted models",
                "available": settings.is_ollama_available,
                "requires_api_key": False,
            },
        ]
    }


