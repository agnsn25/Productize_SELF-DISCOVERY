import json
import re

from .gemini_client import gemini
from .reasoning_modules import get_modules_text
from .prompts import SELECT_PROMPT, ADAPT_PROMPT, IMPLEMENT_PROMPT
from .config import settings
from .cost import sum_usage


async def run_discovery(task_description: str) -> dict:
    """Run the full SELECT -> ADAPT -> IMPLEMENT pipeline."""
    modules_text = get_modules_text()
    thinking_budget = settings.discovery_thinking_budget

    # Step 1: SELECT
    select_prompt = SELECT_PROMPT.format(task=task_description, modules=modules_text)
    select_result = await gemini.generate(select_prompt, thinking_budget=thinking_budget)
    selected_modules = select_result["text"]

    # Step 2: ADAPT
    adapt_prompt = ADAPT_PROMPT.format(task=task_description, selected_modules=selected_modules)
    adapt_result = await gemini.generate(adapt_prompt, thinking_budget=thinking_budget)
    adapted_modules = adapt_result["text"]

    # Step 3: IMPLEMENT — request JSON output
    implement_prompt = IMPLEMENT_PROMPT.format(task=task_description, adapted_modules=adapted_modules)
    implement_result = await gemini.generate(
        implement_prompt,
        thinking_budget=thinking_budget,
        json_schema=None,  # Parse JSON from text; response_mime_type can be too rigid
    )

    # Parse the JSON structure from response
    raw_structure = implement_result["text"]
    try:
        reasoning_structure = json.loads(raw_structure)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_structure)
        if json_match:
            reasoning_structure = json.loads(json_match.group(1))
        else:
            reasoning_structure = {"raw": raw_structure}

    step_usages = [
        select_result.get("usage", {}),
        adapt_result.get("usage", {}),
        implement_result.get("usage", {}),
    ]
    discovery_usage = {
        "select": select_result.get("usage", {}),
        "adapt": adapt_result.get("usage", {}),
        "implement": implement_result.get("usage", {}),
        "total": sum_usage(step_usages),
    }

    return {
        "task_description": task_description,
        "selected_modules": selected_modules.strip().split("\n"),
        "adapted_modules": adapted_modules.strip().split("\n"),
        "reasoning_structure": reasoning_structure,
        "thinking_traces": {
            "select": select_result.get("thoughts"),
            "adapt": adapt_result.get("thoughts"),
            "implement": implement_result.get("thoughts"),
        },
        "discovery_usage": discovery_usage,
    }
