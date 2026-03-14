import asyncio

from fastapi import APIRouter, HTTPException

from ..models import InferRequest, InferResponse, CompareRequest, CompareResponse, ScaleProjection
from ..inference import run_inference, run_naive
from ..database import get_structure
from ..cost import calculate_cost
from ..config import settings

router = APIRouter()


@router.post("/api/infer", response_model=InferResponse)
async def infer(request: InferRequest):
    structure = await get_structure(request.structure_id)
    if not structure:
        raise HTTPException(status_code=404, detail="Structure not found")

    try:
        result = await run_inference(structure["reasoning_structure"], request.problem)
        return InferResponse(
            structure_id=request.structure_id,
            problem=request.problem,
            reasoning_trace=result["reasoning_trace"],
            answer=result["answer"],
            thinking_trace=result.get("thinking_trace"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/infer/compare", response_model=CompareResponse)
async def compare(request: CompareRequest):
    structure = await get_structure(request.structure_id)
    if not structure:
        raise HTTPException(status_code=404, detail="Structure not found")

    try:
        naive_task = run_naive(request.problem)
        sd_task = run_inference(structure["reasoning_structure"], request.problem)
        naive_result, sd_result = await asyncio.gather(naive_task, sd_task)

        naive_usage = naive_result.get("usage", {})
        sd_inference_usage = sd_result.get("usage", {})
        discovery_usage = structure.get("discovery_usage")
        discovery_total_usage = discovery_usage.get("total", {}) if discovery_usage else None

        naive_cost = calculate_cost(naive_usage)
        sd_inference_cost = calculate_cost(sd_inference_usage)
        discovery_cost = calculate_cost(discovery_total_usage) if discovery_total_usage else None

        sd_full_cost = (discovery_cost + sd_inference_cost) if discovery_cost is not None else None

        token_usage = {
            "naive": {**naive_usage, "cost_usd": naive_cost},
            "sd_inference_only": {**sd_inference_usage, "cost_usd": sd_inference_cost},
            "sd_full": {
                **(discovery_total_usage or {}),
                "cost_usd": sd_full_cost,
                "discovery_cost_usd": discovery_cost,
                "inference_cost_usd": sd_inference_cost,
            },
        }

        k = settings.cot_sc_passes
        scale_ns = [1, 10, 100, 1000]
        projections = []
        for n in scale_ns:
            projections.append(ScaleProjection(
                n=n,
                naive_cost=round(n * naive_cost, 6),
                cot_sc_cost=round(n * k * naive_cost, 6),
                sd_full_cost=round(discovery_cost + n * sd_inference_cost, 6) if discovery_cost is not None else None,
                sd_inference_cost=round(n * sd_inference_cost, 6),
            ))

        return CompareResponse(
            structure_id=request.structure_id,
            problem=request.problem,
            naive={"reasoning": naive_result["reasoning"], "answer": naive_result["answer"]},
            self_discover={
                "reasoning_trace": sd_result["reasoning_trace"],
                "answer": sd_result["answer"],
            },
            thinking_traces={
                "naive": None,
                "self_discover": sd_result.get("thinking_trace"),
            },
            token_usage=token_usage,
            scale_projections=projections,
            cot_sc_passes=k,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
