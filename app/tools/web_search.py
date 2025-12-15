from typing import Any
import logging

from app.schemas.tools import ToolParameter
from app.tools.base import BaseTool
from app.services.web_intelligence import WebIntelligenceService

logger = logging.getLogger(__name__)


class WebSearch(BaseTool):
    """Інструмент для пошуку інформації в інтернеті"""

    def __init__(self):
        self.web_intelligence = WebIntelligenceService()

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Шукає актуальну інформацію в інтернеті. Використовуй для пошуку новин, фактів, поточних подій та будь-якої інформації, якої немає в твоїй базі знань."

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Пошуковий запит українською або англійською мовою",
                required=True,
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Максимальна кількість результатів (1-10, за замовчуванням 5)",
                required=False,
            ),
            ToolParameter(
                name="include_content",
                type="boolean",
                description="Чи включати повний контент сторінок (за замовчуванням true)",
                required=False,
            )
        ]

    async def execute(self, **kwargs) -> Any:
        """Виконує пошук інформації в інтернеті"""
        try:
            query = kwargs.get("query", "").strip()
            max_results = kwargs.get("max_results", 5)
            include_content = kwargs.get("include_content", True)

            if not query:
                return {"error": "Пошуковий запит не може бути пустим"}

            # Валідація параметрів
            max_results = max(1, min(int(max_results), 10))

            logger.info(f"Executing web search for: {query}")

            # Виконуємо пошук з отриманням контенту
            result = await self.web_intelligence.search_and_scrape(
                query=query,
                max_search_results=max_results,
                max_scrape_results=min(max_results, 3),  # Обмежуємо скрапінг для швидкості
                include_content=include_content,
                search_type="web"
            )

            if result.get("error"):
                return {
                    "query": query,
                    "error": result["error"],
                    "results": []
                }

            # Форматуємо результати для LLM
            search_results = result.get("search_results", [])
            scraped_content = result.get("scraped_content", [])

            formatted_results = []

            # Додаємо результати пошуку
            for i, search_result in enumerate(search_results):
                formatted_result = {
                    "title": search_result.get("title", ""),
                    "url": search_result.get("url", ""),
                    "snippet": search_result.get("snippet", ""),
                    "published_date": search_result.get("published_date", "")
                }

                # Додаємо повний контент, якщо він є
                if include_content and i < len(scraped_content):
                    scraped = scraped_content[i]
                    if scraped.get("content") and not scraped.get("error"):
                        formatted_result["full_content"] = scraped["content"][:2000]  # Обмежуємо розмір
                        formatted_result["meta_description"] = scraped.get("meta_description", "")

                formatted_results.append(formatted_result)

            return {
                "query": query,
                "results": formatted_results,
                "total_found": len(formatted_results),
                "timestamp": result.get("timestamp"),
                "source": "duckduckgo_search"
            }

        except Exception as e:
            query = kwargs.get("query", "")
            logger.error(f"Error in web search for '{query}': {str(e)}")
            return {
                "query": query,
                "error": f"Помилка пошуку: {str(e)}",
                "results": []
            }

