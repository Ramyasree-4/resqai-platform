"""
ResQAI – JSON Parser
Robustly parses AI model output into structured dicts.
Handles markdown fences, trailing commas, and partial JSON.
"""
import json
import re
from typing import Any, Dict, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)


def _strip_markdown(text: str) -> str:
    """Remove markdown code fences from LLM output."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` blocks
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def _extract_json_block(text: str) -> Optional[str]:
    """Extract the outermost JSON object from text."""
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i, ch in enumerate(text[start:], start=start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def _fix_trailing_commas(text: str) -> str:
    """Remove trailing commas before } or ] — common LLM mistake."""
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text


def parse_llm_json(raw_text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Parse JSON from LLM raw output.
    Returns (result_dict, error_message).
    
    Attempts in order:
    1. Direct parse
    2. Strip markdown + parse
    3. Extract JSON block + parse
    4. Fix trailing commas + parse
    """
    if not raw_text or not raw_text.strip():
        return None, "Empty response from AI model"

    attempts = [
        ("direct", raw_text),
        ("strip_markdown", _strip_markdown(raw_text)),
    ]

    stripped = _strip_markdown(raw_text)
    extracted = _extract_json_block(stripped)
    if extracted:
        attempts.append(("extracted_block", extracted))
        attempts.append(("fixed_commas", _fix_trailing_commas(extracted)))

    last_error = None
    for strategy, text in attempts:
        try:
            result = json.loads(text)
            if isinstance(result, dict):
                if strategy != "direct":
                    logger.debug("JSON parsed with strategy", strategy=strategy)
                return result, None
        except json.JSONDecodeError as e:
            last_error = f"{strategy}: {str(e)}"
            continue

    return None, f"All JSON parse strategies failed. Last error: {last_error}. Raw preview: {raw_text[:200]}"


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert a value to stripped string."""
    if value is None:
        return default
    return str(value).strip()


def safe_list(value: Any, default: list = None) -> list:
    """Safely convert a value to list."""
    if default is None:
        default = []
    if isinstance(value, list):
        return value
    if value is None:
        return default
    return [value]
