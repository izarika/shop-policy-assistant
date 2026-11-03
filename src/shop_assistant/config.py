import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from shop_assistant.entity.models import Regulation, Reply

RESOURCES = Path("resources")


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    api_key: str
    model: str

    @classmethod
    def load(cls) -> "Settings":
        load_dotenv()
        settings = cls(
            os.getenv("TELEGRAM_BOT_TOKEN", ""), os.getenv("OPENAI_API_KEY", ""),
            os.getenv("OPENAI_MODEL", "gpt-6-luna"),
        )
        if not settings.api_key:
            raise ValueError("Set OPENAI_API_KEY in .env")
        return settings


def load_knowledge() -> Regulation:
    data = json.loads((RESOURCES / "knowledge.json").read_text(encoding="utf-8"))
    replies = {Reply(key): text for key, text in data["replies"].items()}
    if set(replies) != set(Reply) or data["return_days"] < 1:
        raise ValueError("Incomplete regulation")
    return Regulation(data["return_days"], tuple(data["source_rules"]), replies)
