import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, tools

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Створити FastAPI додаток
app = FastAPI(
    title="AI Service",
    description="FastAPI middleware для роботи з LLM провайдерами",
    version="1.0.0",
)

# Додати CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключити роутери
app.include_router(chat.router)
app.include_router(tools.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "default_provider": settings.default_provider,
        "default_model": settings.default_model,
    }


@app.get("/api/providers")
async def get_providers():
    """Отримати список доступних провайдерів"""
    return {
        "providers": [
            {
                "name": "deepinfra",
                "description": "DeepInfra API",
                "available": settings.deepinfra_api_key is not None,
            },
            {
                "name": "openai",
                "description": "OpenAI API",
                "available": settings.openai_api_key is not None,
            },
            {
                "name": "ollama",
                "description": "Ollama Local",
                "available": True,
            },
        ]
    }
