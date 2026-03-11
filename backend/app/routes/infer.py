import asyncio

from fastapi import APIRouter, HTTPException

from ..models import InferRequest, InferResponse, CompareRequest, CompareResponse
from ..inference import run_inference, run_naive
from ..database import get_structure

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
        # Run both in parallel
        naive_task = run_naive(request.problem)
        sd_task = run_inference(structure["reasoning_structure"], request.problem)
        naive_result, sd_result = await asyncio.gather(naive_task, sd_task)

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
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
