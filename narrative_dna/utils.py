from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = PROJECT_ROOT / "prompts"
EXAMPLE_FILE = PROJECT_ROOT / "examples" / "examples.json"


def load_environment() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def get_api_key() -> str | None:
    load_environment()
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if key:
        return key

    try:
        import streamlit as st

        value = st.secrets.get("OPENAI_API_KEY", "")
        return str(value).strip() or None
    except Exception:
        return None


def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    return path.read_text(encoding="utf-8").strip()


def load_examples() -> list[dict[str, Any]]:
    with EXAMPLE_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("examples.json must contain a list.")
    return data


def compact_json(value: Any) -> str:
    if isinstance(value, BaseException):
        return json.dumps({"error": str(value)}, ensure_ascii=False)
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, ensure_ascii=False, indent=2)


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))
