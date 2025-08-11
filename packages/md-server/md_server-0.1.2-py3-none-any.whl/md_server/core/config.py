from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_prefix="MD_SERVER_")

    host: str = "127.0.0.1"
    port: int = 8080
    api_key: Optional[str] = None
    max_file_size: int = 50 * 1024 * 1024
    timeout_seconds: int = 30
    url_fetch_timeout: int = 30
    conversion_timeout: int = 120
    debug: bool = False

    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None

    openai_api_key: Optional[str] = None
    azure_doc_intel_endpoint: Optional[str] = None
    azure_doc_intel_key: Optional[str] = None

    crawl4ai_js_rendering: bool = Field(
        default=False, description="Enable JavaScript rendering (requires playwright)"
    )
    crawl4ai_timeout: int = Field(
        default=30, description="Page load timeout in seconds"
    )
    crawl4ai_user_agent: Optional[str] = Field(
        default=None, description="User agent string (uses Crawl4AI default if None)"
    )

    llm_provider_url: Optional[str] = Field(
        default=None,
        description="LLM provider endpoint (e.g., https://openrouter.ai/api/v1)",
    )
    llm_api_key: Optional[str] = Field(default=None, description="LLM API key")
    llm_model: str = Field(
        default="google/gemini-2.5-flash", description="LLM model identifier"
    )

    allowed_file_types: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/html",
        "text/markdown",
        "application/json",
    ]


def get_settings() -> Settings:
    return Settings()
