"""Tools API endpoints."""
from fastapi import APIRouter, Depends

from app.core.dependencies import get_tool_registry
from app.core.logging import get_logger
from app.schemas.tools import ToolSchema
from app.tools import ToolRegistry

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["tools"])


@router.get("/tools", response_model=list[ToolSchema])
async def list_tools(
    registry: ToolRegistry = Depends(get_tool_registry)
) -> list[ToolSchema]:
    """Get list of all available tools.

    Returns tool schemas with names, descriptions, and parameters
    for all registered tools in the system.

    Args:
        registry: Injected tool registry

    Returns:
        List of tool schemas
    """
    tools = registry.get_all()
    logger.info(f"Returning {len(tools)} available tools")
    return [tool.get_schema() for tool in tools]



