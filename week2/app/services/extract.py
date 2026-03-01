from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import List

from dotenv import load_dotenv
from ollama import chat

load_dotenv()


def _ensure_genai_configured() -> None:
    """Ensure GOOGLE_API_KEY is set so we can call the Gemini HTTP API."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is not set. "
            "Set it to your Google AI API key to use extract_action_items_llm."
        )

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract actionable tasks from input text using Gemini 1.5 Pro (Google Generative AI).
    Returns a clean Python list of strings containing only the tasks.
    Requires GOOGLE_API_KEY environment variable to be set.
    """
    if not text or not text.strip():
        return []

    _ensure_genai_configured()

    prompt = """Extract all actionable tasks, to-dos, and action items from the following text.
Return ONLY a JSON array of strings. Each string should be a single task, with no bullet points or numbering.
Do not include any explanation or markdown—only the raw JSON array.

Example output format: ["Task one", "Task two", "Task three"]

Text to analyze:
"""
    prompt += text.strip()

    api_key = os.environ["GOOGLE_API_KEY"]
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-1.5-flash:generateContent"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ],
        "generation_config": {
            "response_mime_type": "application/json",
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError):
        # If the LLM call fails for any reason, fall back to no extracted items
        return []

    try:
        response_data = json.loads(resp_body)
    except json.JSONDecodeError:
        return []

    candidates = response_data.get("candidates") or []
    llm_text: str | None = None
    for candidate in candidates:
        content = candidate.get("content") or {}
        parts = content.get("parts") or []
        for part in parts:
            text_part = part.get("text")
            if text_part:
                llm_text = text_part
                break
        if llm_text:
            break

    if not llm_text:
        return []

    # Parse JSON from LLM response (handle potential markdown code blocks)
    raw = llm_text.strip()
    if raw.startswith("```"):
        # Strip markdown code block if present
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        parsed: List[str] = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        return []

    # Return only string items, stripped of whitespace
    return [str(item).strip() for item in parsed if isinstance(item, str) and str(item).strip()]


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
