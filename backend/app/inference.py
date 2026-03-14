import json

from .gemini_client import gemini
from .prompts import SOLVE_PROMPT, NAIVE_PROMPT
from .config import settings

ANSWER_MARKERS = ["**Final Answer:**", "Final Answer:", "ANSWER:", "**Answer:**"]


def _split_answer(text: str) -> tuple[str, str]:
    """Split response text into (reasoning_trace, answer) using known markers."""
    for marker in ANSWER_MARKERS:
        if marker in text:
            parts = text.split(marker, 1)
            return parts[0].strip(), parts[1].strip()
    return text, text


async def run_inference(reasoning_structure: dict, problem: str) -> dict:
    """Solve a problem using a discovered reasoning structure."""
    structure_text = json.dumps(reasoning_structure, indent=2)
    prompt = SOLVE_PROMPT.format(structure=structure_text, problem=problem)

    result = await gemini.generate(
        prompt,
        thinking_budget=settings.inference_thinking_budget,
    )

    reasoning_trace, answer = _split_answer(result["text"])

    return {
        "reasoning_trace": reasoning_trace,
        "answer": answer,
        "thinking_trace": result.get("thoughts"),
        "usage": result.get("usage", {}),
    }


async def run_naive(problem: str) -> dict:
    """Solve a problem with a simple direct prompt (no structure)."""
    prompt = NAIVE_PROMPT.format(problem=problem)
    result = await gemini.generate(
        prompt,
        thinking_budget=settings.inference_thinking_budget,
    )

    reasoning, answer = _split_answer(result["text"])

    return {
        "reasoning": reasoning,
        "answer": answer,
        "usage": result.get("usage", {}),
    }
