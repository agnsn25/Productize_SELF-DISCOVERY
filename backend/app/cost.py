"""Cost calculation utilities for token usage tracking."""

from .config import settings


def calculate_cost(usage: dict) -> float:
    """Calculate USD cost from a usage dict with input_tokens, output_tokens, thinking_tokens."""
    input_tokens = usage.get("input_tokens", 0) or 0
    output_tokens = usage.get("output_tokens", 0) or 0
    thinking_tokens = usage.get("thinking_tokens", 0) or 0

    input_cost = (input_tokens / 1_000_000) * settings.price_per_1m_input_tokens
    # Output and thinking tokens both billed at the output rate
    output_cost = ((output_tokens + thinking_tokens) / 1_000_000) * settings.price_per_1m_output_tokens

    return input_cost + output_cost


def sum_usage(usages: list[dict]) -> dict:
    """Sum multiple usage dicts into one aggregated dict."""
    total = {"input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0, "total_tokens": 0}
    for u in usages:
        if not u:
            continue
        total["input_tokens"] += u.get("input_tokens", 0) or 0
        total["output_tokens"] += u.get("output_tokens", 0) or 0
        total["thinking_tokens"] += u.get("thinking_tokens", 0) or 0
        total["total_tokens"] += u.get("total_tokens", 0) or 0
    return total
