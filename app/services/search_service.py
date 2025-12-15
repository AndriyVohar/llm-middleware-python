import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    # Спробуємо новий пакет ddgs
    from ddgs import DDGS
except ImportError:
    try:
        # Фоллбек на старий пакет
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

logger = logging.getLogger(__name__)


class SearchService:
    """Сервіс для пошуку інформації в інтернеті"""

    def __init__(self):
        if not DDGS:
            raise ImportError("duckduckgo-search is required for SearchService. Install it with: pip install duckduckgo-search")
        self.ddgs = DDGS()

    async def search_web(
        self,
        query: str,
        max_results: int = 10,
        region: str = "ua-uk",
        safesearch: str = "moderate",
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Пошук веб-сторінок через DuckDuckGo

        Args:
            query: Пошуковий запит
            max_results: Максимальна кількість результатів (1-50)
            region: Регіон пошуку (ua-uk для України)
            safesearch: Рівень безпечного пошуку (strict, moderate, off)
            time_range: Період часу (d, w, m, y для день/тиждень/місяць/рік)

        Returns:
            Dict з результатами пошуку
        """
        try:
            logger.info(f"Searching web for: {query}")

            # Виконуємо пошук в окремому потоці, оскільки duckduckgo-search синхронний
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_web_sync,
                query,
                max_results,
                region,
                safesearch,
                time_range
            )

            return {
                "query": query,
                "results": results,
                "timestamp": datetime.now().isoformat(),
                "source": "duckduckgo",
                "error": None
            }

        except Exception as e:
            logger.error(f"Error searching web for '{query}': {str(e)}")
            return {
                "query": query,
                "results": [],
                "timestamp": datetime.now().isoformat(),
                "source": "duckduckgo",
                "error": str(e)
            }

    def _search_web_sync(
        self,
        query: str,
        max_results: int,
        region: str,
        safesearch: str,
        time_range: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Синхронний пошук через DuckDuckGo"""
        try:
            # Підготовка параметрів
            kwargs = {
                'keywords': query,
                'region': region,
                'safesearch': safesearch,
                'max_results': min(max_results, 50)  # DuckDuckGo обмежує до 50
            }

            if time_range:
                kwargs['timelimit'] = time_range

            # Виконання пошуку
            search_results = list(self.ddgs.text(**kwargs))

            # Форматування результатів
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "published_date": result.get("date", "")
                })

            return formatted_results

        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []

    async def search_news(
        self,
        query: str,
        max_results: int = 10,
        region: str = "ua-uk",
        safesearch: str = "moderate",
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Пошук новин через DuckDuckGo

        Args:
            query: Пошуковий запит
            max_results: Максимальна кількість результатів
            region: Регіон пошуку
            safesearch: Рівень безпечного пошуку
            time_range: Період часу

        Returns:
            Dict з результатами пошуку новин
        """
        try:
            logger.info(f"Searching news for: {query}")

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_news_sync,
                query,
                max_results,
                region,
                safesearch,
                time_range
            )

            return {
                "query": query,
                "results": results,
                "timestamp": datetime.now().isoformat(),
                "source": "duckduckgo_news",
                "error": None
            }

        except Exception as e:
            logger.error(f"Error searching news for '{query}': {str(e)}")
            return {
                "query": query,
                "results": [],
                "timestamp": datetime.now().isoformat(),
                "source": "duckduckgo_news",
                "error": str(e)
            }

    def _search_news_sync(
        self,
        query: str,
        max_results: int,
        region: str,
        safesearch: str,
        time_range: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Синхронний пошук новин через DuckDuckGo"""
        try:
            kwargs = {
                'keywords': query,
                'region': region,
                'safesearch': safesearch,
                'max_results': min(max_results, 50)
            }

            if time_range:
                kwargs['timelimit'] = time_range

            search_results = list(self.ddgs.news(**kwargs))

            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "published_date": result.get("date", ""),
                    "source": result.get("source", "")
                })

            return formatted_results

        except Exception as e:
            logger.error(f"DuckDuckGo news search error: {str(e)}")
            return []

    async def search_images(
        self,
        query: str,
        max_results: int = 10,
        region: str = "ua-uk",
        safesearch: str = "moderate",
        size: Optional[str] = None,
        type_image: Optional[str] = None,
        layout: Optional[str] = None,
        color: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Пошук зображень через DuckDuckGo

        Args:
            query: Пошуковий запит
            max_results: Максимальна кількість результатів
            region: Регіон пошуку
            safesearch: Рівень безпечного пошуку
            size: Розмір зображень (small, medium, large, wallpaper)
            type_image: Тип зображень (photo, clipart, gif, transparent, line)
            layout: Орієнтація (square, tall, wide)
            color: Колір (color, monochrome, red, orange, yellow, green, blue, purple, pink, brown, black, gray, teal, white)

        Returns:
            Dict з результатами пошуку зображень
        """
        try:
            logger.info(f"Searching images for: {query}")

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_images_sync,
                query,
                max_results,
                region,
                safesearch,
                size,
                type_image,
                layout,
                color
            )

            return {
                "query": query,
                "results": results,
                "timestamp": datetime.now().isoformat(),
                "source": "duckduckgo_images",
                "error": None
            }

        except Exception as e:
            logger.error(f"Error searching images for '{query}': {str(e)}")
            return {
                "query": query,
                "results": [],
                "timestamp": datetime.now().isoformat(),
                "source": "duckduckgo_images",
                "error": str(e)
            }

    def _search_images_sync(
        self,
        query: str,
        max_results: int,
        region: str,
        safesearch: str,
        size: Optional[str],
        type_image: Optional[str],
        layout: Optional[str],
        color: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Синхронний пошук зображень через DuckDuckGo"""
        try:
            kwargs = {
                'keywords': query,
                'region': region,
                'safesearch': safesearch,
                'max_results': min(max_results, 50)
            }

            if size:
                kwargs['size'] = size
            if type_image:
                kwargs['type_image'] = type_image
            if layout:
                kwargs['layout'] = layout
            if color:
                kwargs['color'] = color

            search_results = list(self.ddgs.images(**kwargs))

            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "image_url": result.get("image", ""),
                    "thumbnail_url": result.get("thumbnail", ""),
                    "source_url": result.get("url", ""),
                    "width": result.get("width", 0),
                    "height": result.get("height", 0)
                })

            return formatted_results

        except Exception as e:
            logger.error(f"DuckDuckGo images search error: {str(e)}")
            return []

    async def search_videos(
        self,
        query: str,
        max_results: int = 10,
        region: str = "ua-uk",
        safesearch: str = "moderate",
        time_range: Optional[str] = None,
        resolution: Optional[str] = None,
        duration: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Пошук відео через DuckDuckGo

        Args:
            query: Пошуковий запит
            max_results: Максимальна кількість результатів
            region: Регіон пошуку
            safesearch: Рівень безпечного пошуку
            time_range: Період часу
            resolution: Розширення (high, standard)
            duration: Тривалість (short, medium, long)

        Returns:
            Dict з результатами пошуку відео
        """
        try:
            logger.info(f"Searching videos for: {query}")

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_videos_sync,
                query,
                max_results,
                region,
                safesearch,
                time_range,
                resolution,
                duration
            )

            return {
                "query": query,
                "results": results,
                "timestamp": datetime.now().isoformat(),
                "source": "duckduckgo_videos",
                "error": None
            }

        except Exception as e:
            logger.error(f"Error searching videos for '{query}': {str(e)}")
            return {
                "query": query,
                "results": [],
                "timestamp": datetime.now().isoformat(),
                "source": "duckduckgo_videos",
                "error": str(e)
            }

    def _search_videos_sync(
        self,
        query: str,
        max_results: int,
        region: str,
        safesearch: str,
        time_range: Optional[str],
        resolution: Optional[str],
        duration: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Синхронний пошук відео через DuckDuckGo"""
        try:
            kwargs = {
                'keywords': query,
                'region': region,
                'safesearch': safesearch,
                'max_results': min(max_results, 50)
            }

            if time_range:
                kwargs['timelimit'] = time_range
            if resolution:
                kwargs['resolution'] = resolution
            if duration:
                kwargs['duration'] = duration

            search_results = list(self.ddgs.videos(**kwargs))

            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("content", ""),
                    "thumbnail_url": result.get("image", ""),
                    "description": result.get("description", ""),
                    "published_date": result.get("published", ""),
                    "duration": result.get("duration", ""),
                    "publisher": result.get("publisher", "")
                })

            return formatted_results

        except Exception as e:
            logger.error(f"DuckDuckGo videos search error: {str(e)}")
            return []
