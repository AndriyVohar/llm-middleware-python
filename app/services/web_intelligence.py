import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.services.search_service import SearchService
from app.services.web_scraper import WebScraperService

logger = logging.getLogger(__name__)


class WebIntelligenceService:
    """Інтегрований сервіс для отримання інформації з інтернету"""

    def __init__(self):
        self.search_service = SearchService()
        self.web_scraper = WebScraperService()

    async def search_and_scrape(
        self,
        query: str,
        max_search_results: int = 5,
        max_scrape_results: int = 3,
        include_content: bool = True,
        search_type: str = "web",  # web, news, images, videos
        region: str = "ua-uk",
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Виконує пошук та скрапінг найкращих результатів

        Args:
            query: Пошуковий запит
            max_search_results: Максимальна кількість результатів пошуку
            max_scrape_results: Скільки з них скрапити (витягнути повний контент)
            include_content: Чи включати повний контент сторінок
            search_type: Тип пошуку (web, news, images, videos)
            region: Регіон пошуку
            time_range: Період часу для пошуку

        Returns:
            Dict з результатами пошуку та скрапінгу
        """
        try:
            logger.info(f"Starting search and scrape for: {query}")

            # Виконуємо пошук
            if search_type == "web":
                search_results = await self.search_service.search_web(
                    query=query,
                    max_results=max_search_results,
                    region=region,
                    time_range=time_range
                )
            elif search_type == "news":
                search_results = await self.search_service.search_news(
                    query=query,
                    max_results=max_search_results,
                    region=region,
                    time_range=time_range
                )
            elif search_type == "images":
                search_results = await self.search_service.search_images(
                    query=query,
                    max_results=max_search_results,
                    region=region
                )
            elif search_type == "videos":
                search_results = await self.search_service.search_videos(
                    query=query,
                    max_results=max_search_results,
                    region=region,
                    time_range=time_range
                )
            else:
                raise ValueError(f"Unsupported search type: {search_type}")

            if search_results.get("error"):
                return search_results

            results = search_results.get("results", [])

            # Якщо не потрібен контент або це не веб/новини, повертаємо результати пошуку
            if not include_content or search_type in ["images", "videos"]:
                return {
                    "query": query,
                    "search_type": search_type,
                    "search_results": results,
                    "scraped_content": [],
                    "timestamp": datetime.now().isoformat(),
                    "error": None
                }

            # Витягуємо URL для скрапінгу
            urls_to_scrape = []
            for result in results[:max_scrape_results]:
                url = result.get("url", "")
                if url and self._is_scrapable_url(url):
                    urls_to_scrape.append(url)

            if not urls_to_scrape:
                return {
                    "query": query,
                    "search_type": search_type,
                    "search_results": results,
                    "scraped_content": [],
                    "timestamp": datetime.now().isoformat(),
                    "error": "No scrapable URLs found"
                }

            # Виконуємо скрапінг
            async with self.web_scraper as scraper:
                scraped_results = await scraper.scrape_multiple_urls(urls_to_scrape)

            return {
                "query": query,
                "search_type": search_type,
                "search_results": results,
                "scraped_content": scraped_results,
                "timestamp": datetime.now().isoformat(),
                "error": None
            }

        except Exception as e:
            logger.error(f"Error in search and scrape for '{query}': {str(e)}")
            return {
                "query": query,
                "search_type": search_type,
                "search_results": [],
                "scraped_content": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    async def get_url_content(self, url: str) -> Dict[str, Any]:
        """
        Отримує повний контент конкретної URL

        Args:
            url: URL для скрапінгу

        Returns:
            Dict з контентом сторінки
        """
        try:
            async with self.web_scraper as scraper:
                result = await scraper.scrape_url(url, extract_content=True)
            return result

        except Exception as e:
            logger.error(f"Error getting content for {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "title": "",
                "content": "",
                "meta_description": "",
                "links": [],
                "images": []
            }

    async def search_recent_news(
        self,
        query: str,
        max_results: int = 10,
        region: str = "ua-uk"
    ) -> Dict[str, Any]:
        """
        Пошук свіжих новин за запитом

        Args:
            query: Пошуковий запит
            max_results: Максимальна кількість результатів
            region: Регіон пошуку

        Returns:
            Dict з новинами
        """
        return await self.search_service.search_news(
            query=query,
            max_results=max_results,
            region=region,
            time_range="w"  # За останній тиждень
        )

    async def search_with_summary(
        self,
        query: str,
        max_results: int = 3,
        region: str = "ua-uk"
    ) -> Dict[str, Any]:
        """
        Пошук з автоматичним створенням стислого резюме

        Args:
            query: Пошуковий запит
            max_results: Максимальна кількість результатів для обробки
            region: Регіон пошуку

        Returns:
            Dict з результатами та резюме
        """
        try:
            # Виконуємо пошук та скрапінг
            results = await self.search_and_scrape(
                query=query,
                max_search_results=max_results,
                max_scrape_results=max_results,
                include_content=True,
                region=region
            )

            if results.get("error"):
                return results

            # Створюємо резюме з зібраної інформації
            summary_parts = []
            scraped_content = results.get("scraped_content", [])

            for i, content in enumerate(scraped_content[:3], 1):
                if content.get("content") and not content.get("error"):
                    title = content.get("title", "")
                    text = content.get("content", "")
                    url = content.get("url", "")

                    # Обрізаємо контент до розумного розміру
                    if len(text) > 500:
                        text = text[:497] + "..."

                    summary_parts.append(f"Джерело {i}: {title}\n{text}\nURL: {url}\n")

            summary = "\n".join(summary_parts) if summary_parts else "Не вдалося отримати контент сторінок."

            results["summary"] = summary
            results["summary_sources"] = len(summary_parts)

            return results

        except Exception as e:
            logger.error(f"Error in search with summary for '{query}': {str(e)}")
            return {
                "query": query,
                "error": str(e),
                "search_results": [],
                "scraped_content": [],
                "summary": "",
                "summary_sources": 0,
                "timestamp": datetime.now().isoformat()
            }

    def _is_scrapable_url(self, url: str) -> bool:
        """
        Перевіряє чи можна скрапити URL
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)

            # Виключаємо деякі типи файлів та сервісів
            excluded_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar']
            excluded_domains = ['youtube.com', 'youtu.be', 'twitter.com', 'facebook.com', 'instagram.com']

            if any(url.lower().endswith(ext) for ext in excluded_extensions):
                return False

            if any(domain in parsed.netloc.lower() for domain in excluded_domains):
                return False

            return parsed.scheme in ['http', 'https'] and parsed.netloc

        except:
            return False

    async def analyze_url_reputation(self, url: str) -> Dict[str, Any]:
        """
        Аналізує репутацію та безпеку URL

        Args:
            url: URL для аналізу

        Returns:
            Dict з інформацією про безпеку URL
        """
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Базовий аналіз домену
            is_https = parsed.scheme == 'https'

            # Список надійних доменів (можна розширити)
            trusted_domains = [
                'wikipedia.org', 'github.com', 'stackoverflow.com', 'medium.com',
                'arxiv.org', 'nature.com', 'sciencedirect.com', 'ieee.org',
                'bbc.com', 'cnn.com', 'reuters.com', 'ap.org',
                'gov.ua', 'gov.uk', 'gov.ca', 'europa.eu'
            ]

            is_trusted = any(trusted in domain for trusted in trusted_domains)

            # Підозрілі ознаки
            suspicious_patterns = [
                len(domain) > 50,  # Дуже довгий домен
                domain.count('-') > 3,  # Багато дефісів
                domain.count('.') > 3,  # Багато крапок
                any(char in domain for char in ['_', '=', '?', '&']),  # Підозрілі символи
            ]

            risk_score = sum(suspicious_patterns)

            return {
                "url": url,
                "domain": domain,
                "is_https": is_https,
                "is_trusted_domain": is_trusted,
                "risk_score": risk_score,
                "risk_level": "low" if risk_score == 0 else "medium" if risk_score <= 2 else "high",
                "recommendations": self._get_url_recommendations(is_https, is_trusted, risk_score)
            }

        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "risk_level": "unknown"
            }

    def _get_url_recommendations(self, is_https: bool, is_trusted: bool, risk_score: int) -> List[str]:
        """Генерує рекомендації щодо URL"""
        recommendations = []

        if not is_https:
            recommendations.append("URL використовує небезпечний HTTP протокол")

        if not is_trusted and risk_score > 2:
            recommendations.append("Домен може бути підозрілим, будьте обережні")

        if risk_score == 0 and is_https:
            recommendations.append("URL виглядає безпечно")

        return recommendations
