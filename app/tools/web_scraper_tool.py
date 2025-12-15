from typing import Any
import logging

from app.schemas.tools import ToolParameter
from app.tools.base import BaseTool
from app.services.web_intelligence import WebIntelligenceService

logger = logging.getLogger(__name__)


class WebScraper(BaseTool):
    """Інструмент для скрапінгу конкретних веб-сторінок"""

    def __init__(self):
        self.web_intelligence = WebIntelligenceService()

    @property
    def name(self) -> str:
        return "web_scraper"

    @property
    def description(self) -> str:
        return "Витягує повний контент з конкретної веб-сторінки за URL. Використовуй коли маєш точний URL і потрібно отримати весь текст сторінки."

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="url",
                type="string",
                description="URL веб-сторінки для скрапінгу (повний URL з https://)",
                required=True,
            ),
            ToolParameter(
                name="extract_links",
                type="boolean",
                description="Чи витягувати посилання зі сторінки (за замовчуванням false)",
                required=False,
            )
        ]

    async def execute(self, **kwargs) -> Any:
        """Виконує скрапінг конкретної веб-сторінки"""
        try:
            url = kwargs.get("url", "").strip()
            extract_links = kwargs.get("extract_links", False)

            if not url:
                return {"error": "URL не може бути пустим"}

            # Базова валідація URL
            if not (url.startswith("http://") or url.startswith("https://")):
                return {"error": "URL повинен починатися з http:// або https://"}

            logger.info(f"Scraping URL: {url}")

            # Аналізуємо безпеку URL
            reputation = await self.web_intelligence.analyze_url_reputation(url)

            if reputation.get("risk_level") == "high":
                return {
                    "url": url,
                    "error": "URL може бути небезпечним",
                    "risk_analysis": reputation,
                    "content": ""
                }

            # Виконуємо скрапінг
            result = await self.web_intelligence.get_url_content(url)

            if result.get("error"):
                return {
                    "url": url,
                    "error": result["error"],
                    "content": ""
                }

            # Форматуємо результат
            formatted_result = {
                "url": url,
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "meta_description": result.get("meta_description", ""),
                "status_code": result.get("status_code"),
                "content_length": len(result.get("content", "")),
                "risk_analysis": reputation
            }

            # Додаємо посилання, якщо потрібно
            if extract_links:
                links = result.get("links", [])[:20]  # Обмежуємо кількість
                formatted_result["links"] = links
                formatted_result["links_count"] = len(result.get("links", []))

            # Додаємо інформацію про зображення
            images = result.get("images", [])[:10]  # Перші 10 зображень
            formatted_result["images"] = images
            formatted_result["images_count"] = len(result.get("images", []))

            return formatted_result

        except Exception as e:
            url = kwargs.get("url", "")
            logger.error(f"Error scraping URL '{url}': {str(e)}")
            return {
                "url": url,
                "error": f"Помилка скрапінгу: {str(e)}",
                "content": ""
            }


class WebSummarizer(BaseTool):
    """Інструмент для пошуку та створення резюме інформації"""

    def __init__(self):
        self.web_intelligence = WebIntelligenceService()

    @property
    def name(self) -> str:
        return "web_summarizer"

    @property
    def description(self) -> str:
        return "Шукає інформацію в інтернеті та створює стисле резюме з кількох джерел. Ідеально для отримання повного огляду теми."

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Тема або запит для пошуку та резюмування",
                required=True,
            ),
            ToolParameter(
                name="max_sources",
                type="integer",
                description="Максимальна кількість джерел для резюме (1-5, за замовчуванням 3)",
                required=False,
            )
        ]

    async def execute(self, **kwargs) -> Any:
        """Виконує пошук та створює резюме"""
        try:
            query = kwargs.get("query", "").strip()
            max_sources = kwargs.get("max_sources", 3)

            if not query:
                return {"error": "Запит для резюмування не може бути пустим"}

            # Валідація параметрів
            max_sources = max(1, min(int(max_sources), 5))

            logger.info(f"Creating summary for: {query}")

            # Виконуємо пошук з резюме
            result = await self.web_intelligence.search_with_summary(
                query=query,
                max_results=max_sources
            )

            if result.get("error"):
                return {
                    "query": query,
                    "error": result["error"],
                    "summary": "",
                    "sources": []
                }

            # Підготовка інформації про джерела
            sources_info = []
            scraped_content = result.get("scraped_content", [])

            for i, content in enumerate(scraped_content):
                if not content.get("error"):
                    sources_info.append({
                        "title": content.get("title", ""),
                        "url": content.get("url", ""),
                        "snippet": content.get("meta_description", "")[:200]
                    })

            return {
                "query": query,
                "summary": result.get("summary", ""),
                "sources": sources_info,
                "sources_count": result.get("summary_sources", 0),
                "timestamp": result.get("timestamp"),
                "search_results_total": len(result.get("search_results", []))
            }

        except Exception as e:
            query = kwargs.get("query", "")
            logger.error(f"Error creating summary for '{query}': {str(e)}")
            return {
                "query": query,
                "error": f"Помилка створення резюме: {str(e)}",
                "summary": "",
                "sources": []
            }
