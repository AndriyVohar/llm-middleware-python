import logging

from fastapi import APIRouter

from app.schemas.tools import ToolSchema
from app.tools import get_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tools"])


@router.get("/tools", response_model=list[ToolSchema])
async def get_tools() -> list[ToolSchema]:
    """
    Отримати список доступних інструментів
    """
    registry = get_registry()
    tools = registry.get_all()
    return [tool.get_schema() for tool in tools]

