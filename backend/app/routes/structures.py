from fastapi import APIRouter, HTTPException

from ..models import StructureListItem, StructureDetail
from ..database import get_structure, list_structures

router = APIRouter()


@router.get("/api/structures", response_model=list[StructureListItem])
async def get_structures():
    structures = await list_structures()
    return [
        StructureListItem(
            id=s["id"],
            task_description=s["task_description"],
            created_at=s["created_at"],
        )
        for s in structures
    ]


@router.get("/api/structures/{structure_id}", response_model=StructureDetail)
async def get_structure_detail(structure_id: str):
    structure = await get_structure(structure_id)
    if not structure:
        raise HTTPException(status_code=404, detail="Structure not found")
    return StructureDetail(**structure)
