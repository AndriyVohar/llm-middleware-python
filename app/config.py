from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepinfra_api_key: str | None = None
    openai_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"  # Використовуємо IP замість localhost
    default_provider: str = "deepinfra"
    default_model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    # Web scraping settings
    web_scraping_enabled: bool = True
    web_scraping_timeout: int = 30
    web_scraping_max_concurrent: int = 5
    web_scraping_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    # Search settings
    default_search_region: str = "ua-uk"
    default_search_results: int = 5
    max_search_results: int = 15

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

