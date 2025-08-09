import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMConfig:
    provider: str
    base_url: str
    model: str
    api_key: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 1500
    timeout: int = 60

def get_llm_config(args) -> LLMConfig:
    return LLMConfig(
        provider=args.provider or os.getenv("LLM_PROVIDER", "gemini"),
        base_url=args.base_url or os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com"),
        model=args.model or os.getenv("LLM_MODEL", "gemini-2.5-flash"),
        api_key=args.api_key or os.getenv("LLM_API_KEY"),
        temperature=args.temp or float(os.getenv("LLM_TEMPERATURE", "0.3")),
        max_tokens=args.max_tokens or int(os.getenv("LLM_MAX_TOKENS", "1500")),
        timeout=args.timeout or int(os.getenv("LLM_TIMEOUT", "60")),
    )
