from fastapi import APIRouter, HTTPException

from ..models import DiscoverRequest, DiscoverResponse
from ..discovery import run_discovery
from ..database import save_structure, get_structure

router = APIRouter()


@router.post("/api/discover", response_model=DiscoverResponse)
async def discover(request: DiscoverRequest):
    try:
        result = await run_discovery(request.task_description)
        structure_id = await save_structure(result)
        saved = await get_structure(structure_id)
        return DiscoverResponse(**saved)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
