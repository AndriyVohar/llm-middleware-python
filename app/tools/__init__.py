
from app.tools.base import BaseTool


class ToolRegistry:
    """Реєстр для управління інструментами"""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Зареєструвати інструмент"""
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        """Отримати інструмент за назвою"""
        return self._tools.get(name)

    def get_all(self) -> list[BaseTool]:
        """Отримати всі інструменти"""
        return list(self._tools.values())

    def get_by_names(self, names: list[str]) -> list[BaseTool]:
        """Отримати інструменти за списком назв"""
        return [tool for name in names if (tool := self.get(name)) is not None]


# Глобальний реєстр
_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Отримати глобальний реєстр"""
    return _registry


# Імпорт інструментів для реєстрації
from app.tools.calculator import Calculator
from app.tools.web_search import WebSearch
from app.tools.news_search import NewsSearch
from app.tools.web_scraper_tool import WebScraper, WebSummarizer

# Реєстрація інструментів
_registry.register(Calculator())
_registry.register(WebSearch())
_registry.register(NewsSearch())
_registry.register(WebScraper())
_registry.register(WebSummarizer())

