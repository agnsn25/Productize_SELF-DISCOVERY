"""Tests for the discovery flow (SELECT -> ADAPT -> IMPLEMENT)."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from backend.app.reasoning_modules import REASONING_MODULES, get_modules_text
from backend.app.prompts import SELECT_PROMPT, ADAPT_PROMPT, IMPLEMENT_PROMPT
from backend.app.discovery import run_discovery


# ── Reasoning modules ────────────────────────────────────────

def test_reasoning_modules_count():
    """The module library should contain exactly 39 atomic reasoning modules."""
    assert len(REASONING_MODULES) == 39


def test_get_modules_text_returns_numbered_list():
    """get_modules_text should return a numbered multi-line string."""
    text = get_modules_text()
    lines = text.strip().split("\n")

    assert len(lines) == 39
    assert lines[0].startswith("1. ")
    assert lines[-1].startswith("39. ")

    # Each line should contain the corresponding module text
    for i, module in enumerate(REASONING_MODULES):
        assert module in lines[i]


# ── Prompt formatting ────────────────────────────────────────

def test_select_prompt_formatting():
    """SELECT_PROMPT should accept task and modules placeholders."""
    result = SELECT_PROMPT.format(task="test task", modules="mod1\nmod2")
    assert "test task" in result
    assert "mod1\nmod2" in result
    assert "Select the reasoning modules" in result


def test_adapt_prompt_formatting():
    """ADAPT_PROMPT should accept task and selected_modules placeholders."""
    result = ADAPT_PROMPT.format(task="test task", selected_modules="selected")
    assert "test task" in result
    assert "selected" in result
    assert "Rephrase and adapt" in result


def test_implement_prompt_formatting():
    """IMPLEMENT_PROMPT should accept task and adapted_modules placeholders."""
    result = IMPLEMENT_PROMPT.format(task="test task", adapted_modules="adapted")
    assert "test task" in result
    assert "adapted" in result
    assert "structured JSON reasoning plan" in result


# ── JSON parsing from implement step ─────────────────────────

@pytest.mark.asyncio
async def test_run_discovery_parses_json_from_code_block():
    """Discovery should extract JSON even if wrapped in markdown code blocks."""
    structure = {"step_1": {"instruction": "do thing", "reasoning_module": "mod"}}
    json_in_code_block = f"```json\n{json.dumps(structure)}\n```"

    mock_gemini = AsyncMock()
    mock_gemini.generate = AsyncMock(
        side_effect=[
            {"text": "Module A\nModule B", "thoughts": "thinking select"},
            {"text": "Adapted A\nAdapted B", "thoughts": "thinking adapt"},
            {"text": json_in_code_block, "thoughts": "thinking implement"},
        ]
    )

    with patch("backend.app.discovery.gemini", mock_gemini):
        result = await run_discovery("solve math problems")

    assert result["reasoning_structure"] == structure
    assert result["task_description"] == "solve math problems"


@pytest.mark.asyncio
async def test_run_discovery_parses_raw_json():
    """Discovery should parse JSON directly when not in a code block."""
    structure = {"step_1": {"instruction": "analyze", "reasoning_module": "critical"}}

    mock_gemini = AsyncMock()
    mock_gemini.generate = AsyncMock(
        side_effect=[
            {"text": "Module X", "thoughts": None},
            {"text": "Adapted X", "thoughts": None},
            {"text": json.dumps(structure), "thoughts": None},
        ]
    )

    with patch("backend.app.discovery.gemini", mock_gemini):
        result = await run_discovery("debug code")

    assert result["reasoning_structure"] == structure


@pytest.mark.asyncio
async def test_run_discovery_falls_back_on_invalid_json():
    """If JSON parsing fails entirely, discovery wraps raw text in a dict."""
    mock_gemini = AsyncMock()
    mock_gemini.generate = AsyncMock(
        side_effect=[
            {"text": "Module A", "thoughts": None},
            {"text": "Adapted A", "thoughts": None},
            {"text": "This is not valid JSON at all", "thoughts": None},
        ]
    )

    with patch("backend.app.discovery.gemini", mock_gemini):
        result = await run_discovery("some task")

    assert "raw" in result["reasoning_structure"]


# ── Orchestration ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_discovery_calls_gemini_three_times_in_order():
    """Discovery must call gemini.generate exactly 3 times: SELECT, ADAPT, IMPLEMENT."""
    structure = {"step_1": {"instruction": "x", "reasoning_module": "y"}}

    mock_gemini = AsyncMock()
    mock_gemini.generate = AsyncMock(
        side_effect=[
            {"text": "Module A\nModule B", "thoughts": "t1"},
            {"text": "Adapted A\nAdapted B", "thoughts": "t2"},
            {"text": json.dumps(structure), "thoughts": "t3"},
        ]
    )

    with patch("backend.app.discovery.gemini", mock_gemini):
        result = await run_discovery("test task")

    assert mock_gemini.generate.call_count == 3

    # Verify call order: first call should contain SELECT prompt content
    first_call_prompt = mock_gemini.generate.call_args_list[0][0][0]
    assert "Select the reasoning modules" in first_call_prompt

    # Second call should contain ADAPT prompt content
    second_call_prompt = mock_gemini.generate.call_args_list[1][0][0]
    assert "Rephrase and adapt" in second_call_prompt

    # Third call should contain IMPLEMENT prompt content
    third_call_prompt = mock_gemini.generate.call_args_list[2][0][0]
    assert "structured JSON reasoning plan" in third_call_prompt

    # Verify thinking traces are captured
    assert result["thinking_traces"]["select"] == "t1"
    assert result["thinking_traces"]["adapt"] == "t2"
    assert result["thinking_traces"]["implement"] == "t3"

    # Verify modules are split into lists
    assert result["selected_modules"] == ["Module A", "Module B"]
    assert result["adapted_modules"] == ["Adapted A", "Adapted B"]
