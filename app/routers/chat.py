import logging

from fastapi import APIRouter

from app.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])
llm_service = LLMService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Основний endpoint для чату

    Прийміває ChatRequest з повідомленнями, провайдером, інструментами
    Повертає ChatResponse з відповіддю та інформацією про tool calls
    """
    logger.info(f"Chat request: provider={request.provider}, tools={request.tools}")

    response = await llm_service.chat(request)
    return response

