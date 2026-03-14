import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Look for .env in both project root and backend/
_backend_dir = Path(__file__).resolve().parent.parent
_root_dir = _backend_dir.parent
_env_file = str(_backend_dir / ".env") if (_backend_dir / ".env").exists() else str(_root_dir / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file)

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-pro"
    database_path: str = "self_discover.db"
    discovery_thinking_budget: int = 8192
    inference_thinking_budget: int = -1  # dynamic

    # Pricing (Gemini 2.5 Pro, USD per 1M tokens)
    price_per_1m_input_tokens: float = 1.25
    price_per_1m_output_tokens: float = 10.0  # includes thinking tokens
    cot_sc_passes: int = 20  # CoT-Self-Consistency pass count for projections


settings = Settings()
