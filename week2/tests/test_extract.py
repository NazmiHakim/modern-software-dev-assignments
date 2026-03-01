import os
import pytest
from unittest.mock import MagicMock, patch

from ..app.services.extract import extract_action_items, extract_action_items_llm

# Patch target: where genai.GenerativeModel is used (in the extract module)
_EXTRACT_MODULE = extract_action_items_llm.__module__


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# --- Tests for extract_action_items_llm (mocked, no network calls) ---


@patch(f"{_EXTRACT_MODULE}.genai.GenerativeModel")
def test_extract_action_items_llm_bullet_list(mock_gen_model):
    """Extract action items from text with standard bullet list."""
    os.environ["GOOGLE_API_KEY"] = "test-key"

    mock_model = MagicMock()
    mock_gen_model.return_value = mock_model
    mock_response = MagicMock()
    mock_response.text = '["Set up database", "Implement API extract endpoint", "Write tests"]'
    mock_model.generate_content.return_value = mock_response

    text = """
    Notes from meeting:
    - Set up database
    * Implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """
    result = extract_action_items_llm(text)

    assert result == ["Set up database", "Implement API extract endpoint", "Write tests"]
    mock_model.generate_content.assert_called_once()


@patch(f"{_EXTRACT_MODULE}.genai.GenerativeModel")
def test_extract_action_items_llm_keyword_prefixed(mock_gen_model):
    """Extract action items from text with todo:, action:, next: prefixes."""
    os.environ["GOOGLE_API_KEY"] = "test-key"

    mock_model = MagicMock()
    mock_gen_model.return_value = mock_model
    mock_response = MagicMock()
    mock_response.text = '["Review pull request", "Deploy to staging", "Schedule follow-up"]'
    mock_model.generate_content.return_value = mock_response

    text = """
    todo: Review pull request
    action: Deploy to staging
    next: Schedule follow-up
    """
    result = extract_action_items_llm(text)

    assert result == ["Review pull request", "Deploy to staging", "Schedule follow-up"]
    mock_model.generate_content.assert_called_once()


def test_extract_action_items_llm_empty_input():
    """Return empty list for empty or whitespace-only input (no API call)."""
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   ") == []
    assert extract_action_items_llm("\n\t\n") == []


@patch(f"{_EXTRACT_MODULE}.genai.GenerativeModel")
def test_extract_action_items_llm_response_with_markdown_code_block(mock_gen_model):
    """Handle LLM response wrapped in markdown code block."""
    os.environ["GOOGLE_API_KEY"] = "test-key"

    mock_model = MagicMock()
    mock_gen_model.return_value = mock_model
    mock_response = MagicMock()
    mock_response.text = '```json\n["Task one", "Task two"]\n```'
    mock_model.generate_content.return_value = mock_response

    result = extract_action_items_llm("Meeting: - Task one - Task two")

    assert result == ["Task one", "Task two"]


@patch(f"{_EXTRACT_MODULE}.genai.GenerativeModel")
def test_extract_action_items_llm_empty_response(mock_gen_model):
    """Return empty list when LLM returns no text."""
    os.environ["GOOGLE_API_KEY"] = "test-key"

    mock_model = MagicMock()
    mock_gen_model.return_value = mock_model
    mock_response = MagicMock()
    mock_response.text = None
    mock_model.generate_content.return_value = mock_response

    result = extract_action_items_llm("Some notes with tasks")

    assert result == []


@patch(f"{_EXTRACT_MODULE}.genai.GenerativeModel")
def test_extract_action_items_llm_malformed_json_returns_empty(mock_gen_model):
    """Return empty list when LLM response is not valid JSON."""
    os.environ["GOOGLE_API_KEY"] = "test-key"

    mock_model = MagicMock()
    mock_gen_model.return_value = mock_model
    mock_response = MagicMock()
    mock_response.text = "Here are the tasks: 1. One 2. Two"
    mock_model.generate_content.return_value = mock_response

    result = extract_action_items_llm("Some notes")

    assert result == []


@patch(f"{_EXTRACT_MODULE}.genai.GenerativeModel")
def test_extract_action_items_llm_filters_non_string_items(mock_gen_model):
    """Filter out non-string items from parsed JSON."""
    os.environ["GOOGLE_API_KEY"] = "test-key"

    mock_model = MagicMock()
    mock_gen_model.return_value = mock_model
    mock_response = MagicMock()
    mock_response.text = '["Valid task", 123, null, "", "Another task"]'
    mock_model.generate_content.return_value = mock_response

    result = extract_action_items_llm("Notes with mixed content")

    assert result == ["Valid task", "Another task"]


def test_extract_action_items_llm_missing_api_key_raises():
    """Raise ValueError when GOOGLE_API_KEY is not set."""
    import sys

    extract_module = sys.modules[extract_action_items_llm.__module__]
    original_configured = extract_module._genai_configured
    original_key = os.environ.get("GOOGLE_API_KEY")

    try:
        extract_module._genai_configured = False
        if "GOOGLE_API_KEY" in os.environ:
            del os.environ["GOOGLE_API_KEY"]

        with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
            extract_action_items_llm("Some text")
    finally:
        extract_module._genai_configured = original_configured
        if original_key is not None:
            os.environ["GOOGLE_API_KEY"] = original_key
