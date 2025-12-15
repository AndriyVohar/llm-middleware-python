from typing import Any
import logging

from app.schemas.tools import ToolParameter
from app.tools.base import BaseTool
from app.services.web_intelligence import WebIntelligenceService

logger = logging.getLogger(__name__)


class NewsSearch(BaseTool):
    """Інструмент для пошуку новин"""

    def __init__(self):
        self.web_intelligence = WebIntelligenceService()

    @property
    def name(self) -> str:
        return "news_search"

    @property
    def description(self) -> str:
        return "Шукає свіжі новини та актуальні події. Використовуй для пошуку останніх новин, поточних подій, політичних новин, спортивних результатів тощо."

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Пошуковий запит для новин",
                required=True,
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Максимальна кількість новин (1-15, за замовчуванням 8)",
                required=False,
            ),
            ToolParameter(
                name="time_range",
                type="string",
                description="Період пошуку: 'd' (день), 'w' (тиждень), 'm' (місяць), 'y' (рік). За замовчуванням 'w'",
                required=False,
            )
        ]

    async def execute(self, **kwargs) -> Any:
        """Виконує пошук новин"""
        try:
            query = kwargs.get("query", "").strip()
            max_results = kwargs.get("max_results", 8)
            time_range = kwargs.get("time_range", "w")

            if not query:
                return {"error": "Пошуковий запит не може бути пустим"}

            # Валідація параметрів
            max_results = max(1, min(int(max_results), 15))
            if time_range not in ["d", "w", "m", "y"]:
                time_range = "w"

            logger.info(f"Executing news search for: {query}")

            # Виконуємо пошук новин
            result = await self.web_intelligence.search_and_scrape(
                query=query,
                max_search_results=max_results,
                max_scrape_results=min(max_results, 3),
                include_content=True,
                search_type="news",
                time_range=time_range
            )

            if result.get("error"):
                return {
                    "query": query,
                    "error": result["error"],
                    "news": []
                }

            # Форматуємо новини для LLM
            search_results = result.get("search_results", [])
            scraped_content = result.get("scraped_content", [])

            formatted_news = []

            for i, news_item in enumerate(search_results):
                formatted_item = {
                    "title": news_item.get("title", ""),
                    "url": news_item.get("url", ""),
                    "snippet": news_item.get("snippet", ""),
                    "published_date": news_item.get("published_date", ""),
                    "source": news_item.get("source", "")
                }

                # Додаємо повний контент для перших кількох новин
                if i < len(scraped_content):
                    scraped = scraped_content[i]
                    if scraped.get("content") and not scraped.get("error"):
                        formatted_item["full_content"] = scraped["content"][:1500]

                formatted_news.append(formatted_item)

            return {
                "query": query,
                "news": formatted_news,
                "total_found": len(formatted_news),
                "time_range": time_range,
                "timestamp": result.get("timestamp"),
                "source": "duckduckgo_news"
            }

        except Exception as e:
            query = kwargs.get("query", "")
            logger.error(f"Error in news search for '{query}': {str(e)}")
            return {
                "query": query,
                "error": f"Помилка пошуку новин: {str(e)}",
                "news": []
            }
