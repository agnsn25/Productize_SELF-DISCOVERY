"""Tests for the inference flow (SOLVE and NAIVE)."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from backend.app.prompts import SOLVE_PROMPT, NAIVE_PROMPT
from backend.app.inference import _split_answer, run_inference, run_naive


# ── Prompt formatting ────────────────────────────────────────

def test_solve_prompt_formatting():
    """SOLVE_PROMPT should accept structure and problem placeholders."""
    structure = {"step_1": {"instruction": "analyze", "reasoning_module": "mod"}}
    result = SOLVE_PROMPT.format(
        structure=json.dumps(structure, indent=2),
        problem="What is 2+2?",
    )
    assert "What is 2+2?" in result
    assert '"step_1"' in result
    assert "Follow the structure carefully" in result


def test_naive_prompt_formatting():
    """NAIVE_PROMPT should accept a problem placeholder."""
    result = NAIVE_PROMPT.format(problem="Explain gravity")
    assert "Explain gravity" in result
    assert "Solve the following problem step by step" in result


# ── Answer extraction ────────────────────────────────────────

def test_split_answer_with_bold_final_answer():
    text = "Some reasoning here.\n\n**Final Answer:** 42"
    reasoning, answer = _split_answer(text)
    assert reasoning == "Some reasoning here."
    assert answer == "42"


def test_split_answer_with_plain_final_answer():
    text = "Step 1: think\nStep 2: compute\nFinal Answer: The result is 7."
    reasoning, answer = _split_answer(text)
    assert "Step 1: think" in reasoning
    assert answer == "The result is 7."


def test_split_answer_with_answer_colon():
    text = "Worked through it.\n\nANSWER: yes"
    reasoning, answer = _split_answer(text)
    assert reasoning == "Worked through it."
    assert answer == "yes"


def test_split_answer_with_bold_answer():
    text = "Lots of reasoning.\n\n**Answer:** no"
    reasoning, answer = _split_answer(text)
    assert reasoning == "Lots of reasoning."
    assert answer == "no"


def test_split_answer_no_marker_returns_full_text():
    """When no marker is found, both reasoning and answer should be the full text."""
    text = "Just some text with no markers"
    reasoning, answer = _split_answer(text)
    assert reasoning == text
    assert answer == text


def test_split_answer_uses_first_marker_occurrence():
    """If a marker appears multiple times, split on the first occurrence."""
    text = "Part A\n**Final Answer:** first\n**Final Answer:** second"
    reasoning, answer = _split_answer(text)
    assert reasoning == "Part A"
    assert "first" in answer


# ── run_inference ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_inference_returns_structured_result():
    """run_inference should format the prompt, call gemini, and parse the answer."""
    structure = {"step_1": {"instruction": "analyze", "reasoning_module": "mod"}}
    gemini_response = {
        "text": "Step 1: analyzed the problem.\n\n**Final Answer:** 42",
        "thoughts": "I thought about it deeply",
        "usage": {"input_tokens": 100, "output_tokens": 50, "thinking_tokens": 20, "total_tokens": 170},
    }

    mock_gemini = AsyncMock()
    mock_gemini.generate = AsyncMock(return_value=gemini_response)

    with patch("backend.app.inference.gemini", mock_gemini):
        result = await run_inference(structure, "What is 6*7?")

    assert result["answer"] == "42"
    assert "analyzed the problem" in result["reasoning_trace"]
    assert result["thinking_trace"] == "I thought about it deeply"
    assert result["usage"]["input_tokens"] == 100

    # Verify the prompt was formatted with the structure
    call_prompt = mock_gemini.generate.call_args[0][0]
    assert "What is 6*7?" in call_prompt
    assert "step_1" in call_prompt


@pytest.mark.asyncio
async def test_run_inference_handles_no_thinking():
    """run_inference should handle None thinking traces gracefully."""
    structure = {"step_1": {"instruction": "go", "reasoning_module": "m"}}

    mock_gemini = AsyncMock()
    mock_gemini.generate = AsyncMock(return_value={
        "text": "Done.\n\n**Final Answer:** result",
        "thoughts": None,
        "usage": {"input_tokens": 50, "output_tokens": 30, "thinking_tokens": 0, "total_tokens": 80},
    })

    with patch("backend.app.inference.gemini", mock_gemini):
        result = await run_inference(structure, "test")

    assert result["thinking_trace"] is None
    assert result["answer"] == "result"


# ── run_naive ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_naive_returns_reasoning_and_answer():
    """run_naive should call gemini with the naive prompt and split the answer."""
    mock_gemini = AsyncMock()
    mock_gemini.generate = AsyncMock(return_value={
        "text": "I reasoned about it.\n\nFinal Answer: 100",
        "thoughts": None,
        "usage": {"input_tokens": 80, "output_tokens": 40, "thinking_tokens": 0, "total_tokens": 120},
    })

    with patch("backend.app.inference.gemini", mock_gemini):
        result = await run_naive("What is 10*10?")

    assert result["answer"] == "100"
    assert "I reasoned about it" in result["reasoning"]
    assert result["usage"]["input_tokens"] == 80

    # Verify naive prompt was used
    call_prompt = mock_gemini.generate.call_args[0][0]
    assert "Solve the following problem step by step" in call_prompt
    assert "What is 10*10?" in call_prompt


@pytest.mark.asyncio
async def test_run_naive_no_marker():
    """When gemini returns text without an answer marker, full text is returned as both."""
    mock_gemini = AsyncMock()
    mock_gemini.generate = AsyncMock(return_value={
        "text": "The answer is probably 5 but I am not sure",
        "thoughts": None,
        "usage": {"input_tokens": 60, "output_tokens": 30, "thinking_tokens": 0, "total_tokens": 90},
    })

    with patch("backend.app.inference.gemini", mock_gemini):
        result = await run_naive("What is 2+3?")

    # With no marker, both reasoning and answer are the full text
    assert result["reasoning"] == result["answer"]
