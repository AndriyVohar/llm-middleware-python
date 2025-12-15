"""Chat API endpoints."""
from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_llm_service
from app.core.exceptions import LLMMiddlewareException
from app.core.logging import get_logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service)
) -> ChatResponse:
    """Process chat request with LLM provider.

    This endpoint:
    - Accepts chat messages and configuration
    - Routes to appropriate LLM provider
    - Handles tool calling if tools are specified
    - Returns assistant response with tool execution details

    Args:
        request: Chat request with messages and configuration
        llm_service: Injected LLM service

    Returns:
        ChatResponse with assistant message and metadata

    Raises:
        HTTPException: If processing fails
    """
    try:
        logger.info(
            f"Chat request received - provider: {request.provider}, "
            f"model: {request.model}, tools: {request.tools}"
        )

        response = await llm_service.chat(request)

        # Log token usage summary
        if response.usage:
            logger.info(
                f"Chat request completed - success: {response.success}, "
                f"tool_calls: {len(response.tool_calls_made)}, "
                f"tokens: {response.usage.get('total_tokens', 0)} "
                f"(prompt: {response.usage.get('prompt_tokens', 0)}, "
                f"completion: {response.usage.get('completion_tokens', 0)})"
            )
        else:
            logger.info(
                f"Chat request completed - success: {response.success}, "
                f"tool_calls: {len(response.tool_calls_made)}"
            )

        return response

    except LLMMiddlewareException as e:
        logger.error(f"LLM middleware error: {e.message}", extra={"details": e.details})
        raise HTTPException(status_code=400, detail=e.message)

    except Exception as e:
        logger.exception("Unexpected error in chat endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



