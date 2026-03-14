"""Tests for cost calculation utilities."""

from backend.app.cost import calculate_cost, sum_usage


def test_calculate_cost_basic():
    usage = {
        "input_tokens": 1_000_000,
        "output_tokens": 500_000,
        "thinking_tokens": 500_000,
        "total_tokens": 2_000_000,
    }
    cost = calculate_cost(usage)
    assert abs(cost - 11.25) < 0.001


def test_calculate_cost_empty():
    assert calculate_cost({}) == 0.0


def test_calculate_cost_with_none_values():
    usage = {"input_tokens": None, "output_tokens": None, "thinking_tokens": None}
    assert calculate_cost(usage) == 0.0


def test_calculate_cost_small_values():
    usage = {"input_tokens": 100, "output_tokens": 50, "thinking_tokens": 0}
    cost = calculate_cost(usage)
    expected = (100 / 1_000_000) * 1.25 + (50 / 1_000_000) * 10.0
    assert abs(cost - expected) < 1e-10


def test_sum_usage_basic():
    u1 = {"input_tokens": 100, "output_tokens": 200, "thinking_tokens": 50, "total_tokens": 350}
    u2 = {"input_tokens": 300, "output_tokens": 400, "thinking_tokens": 100, "total_tokens": 800}
    result = sum_usage([u1, u2])
    assert result["input_tokens"] == 400
    assert result["output_tokens"] == 600
    assert result["thinking_tokens"] == 150
    assert result["total_tokens"] == 1150


def test_sum_usage_empty_list():
    result = sum_usage([])
    assert result == {"input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0, "total_tokens": 0}


def test_sum_usage_with_none_entries():
    u1 = {"input_tokens": 50, "output_tokens": 50, "thinking_tokens": 0, "total_tokens": 100}
    result = sum_usage([u1, None, {}, u1])
    assert result["input_tokens"] == 100
    assert result["total_tokens"] == 200


def test_sum_usage_missing_keys():
    u1 = {"input_tokens": 10}
    result = sum_usage([u1])
    assert result["output_tokens"] == 0
    assert result["thinking_tokens"] == 0
    assert result["input_tokens"] == 10
