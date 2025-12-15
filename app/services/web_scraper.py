import asyncio
import logging
from typing import Any, Dict, List
from urllib.parse import urljoin, urlparse
import re

try:
    import httpx
except ImportError:
    httpx = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from newspaper import Article
except ImportError:
    Article = None

try:
    from readability import Document
except ImportError:
    Document = None

logger = logging.getLogger(__name__)


class WebScraperService:
    """Сервіс для скрапінгу веб-сторінок"""

    def __init__(self):
        if not httpx:
            raise ImportError("httpx is required for WebScraperService. Install it with: pip install httpx")
        if not BeautifulSoup:
            raise ImportError("BeautifulSoup is required for WebScraperService. Install it with: pip install beautifulsoup4")

        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
            follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def scrape_url(self, url: str, extract_content: bool = True) -> Dict[str, Any]:
        """
        Скрапить одну веб-сторінку

        Args:
            url: URL для скрапінгу
            extract_content: Чи витягувати основний контент статті

        Returns:
            Dict з інформацією про сторінку
        """
        try:
            logger.info(f"Scraping URL: {url}")

            if not self.session:
                raise RuntimeError("WebScraperService not initialized properly")

            response = await self.session.get(url)
            response.raise_for_status()

            # Базова інформація
            result = {
                "url": url,
                "status_code": response.status_code,
                "title": "",
                "content": "",
                "meta_description": "",
                "links": [],
                "images": [],
                "error": None
            }

            # Парсинг HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Отримання title
            title_tag = soup.find('title')
            if title_tag:
                result["title"] = title_tag.get_text().strip()

            # Отримання meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                result["meta_description"] = meta_desc.get('content', '').strip()

            # Витягування основного контенту
            if extract_content:
                content = await self._extract_main_content(response.text, url)
                result["content"] = content

            # Витягування посилань
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Конвертуємо відносні посилання в абсолютні
                absolute_url = urljoin(url, href)
                link_text = link.get_text().strip()
                if link_text and self._is_valid_url(absolute_url):
                    links.append({
                        "url": absolute_url,
                        "text": link_text
                    })

            result["links"] = links[:20]  # Обмежуємо кількість посилань

            # Витягування зображень
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                absolute_url = urljoin(url, src)
                alt_text = img.get('alt', '').strip()
                if self._is_valid_url(absolute_url):
                    images.append({
                        "url": absolute_url,
                        "alt": alt_text
                    })

            result["images"] = images[:10]  # Обмежуємо кількість зображень

            return result

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "title": "",
                "content": "",
                "meta_description": "",
                "links": [],
                "images": []
            }

    async def _extract_main_content(self, html: str, url: str) -> str:
        """Витягує основний контент статті"""
        if Article:
            try:
                # Спробуємо newspaper3k для витягування статей
                article = Article(url)
                article.set_html(html)
                article.parse()

                if article.text and len(article.text.strip()) > 100:
                    return article.text.strip()

            except Exception as e:
                logger.debug(f"Newspaper3k failed for {url}: {str(e)}")

        if Document:
            try:
                # Спробуємо readability як fallback
                doc = Document(html)
                content = doc.summary()

                # Видаляємо HTML теги
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text()

                # Очищуємо текст
                text = re.sub(r'\s+', ' ', text).strip()

                if len(text) > 100:
                    return text

            except Exception as e:
                logger.debug(f"Readability failed for {url}: {str(e)}")

        # Якщо все не вдалося, просто витягуємо текст з HTML
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Видаляємо скрипти та стилі
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            text = re.sub(r'\s+', ' ', text).strip()

            return text[:5000]  # Обмежуємо розмір

        except Exception as e:
            logger.error(f"All content extraction methods failed for {url}: {str(e)}")
            return ""

    def _is_valid_url(self, url: str) -> bool:
        """Перевіряє чи є URL валідним"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    async def scrape_multiple_urls(self, urls: List[str], max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """
        Скрапить кілька URL одночасно

        Args:
            urls: Список URL для скрапінгу
            max_concurrent: Максимальна кількість одночасних запитів

        Returns:
            Список результатів скрапінгу
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_semaphore(url: str):
            async with semaphore:
                return await self.scrape_url(url)

        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обробляємо винятки
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "url": urls[i],
                    "error": str(result),
                    "title": "",
                    "content": "",
                    "meta_description": "",
                    "links": [],
                    "images": []
                })
            else:
                processed_results.append(result)

        return processed_results
