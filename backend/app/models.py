from pydantic import BaseModel


# ── Discover ──────────────────────────────────────────────

class DiscoverRequest(BaseModel):
    task_description: str


class DiscoverResponse(BaseModel):
    id: str
    task_description: str
    selected_modules: list[str]
    adapted_modules: list[str]
    reasoning_structure: dict
    thinking_traces: dict  # keys: select, adapt, implement
    created_at: str


# ── Infer ─────────────────────────────────────────────────

class InferRequest(BaseModel):
    structure_id: str
    problem: str


class InferResponse(BaseModel):
    structure_id: str
    problem: str
    reasoning_trace: str
    answer: str
    thinking_trace: str | None


# ── Compare ───────────────────────────────────────────────

class CompareRequest(BaseModel):
    structure_id: str
    problem: str


class CompareResponse(BaseModel):
    structure_id: str
    problem: str
    naive: dict  # keys: reasoning, answer
    self_discover: dict  # keys: reasoning_trace, answer
    thinking_traces: dict | None


# ── Structures ────────────────────────────────────────────

class StructureListItem(BaseModel):
    id: str
    task_description: str
    created_at: str


class StructureDetail(BaseModel):
    id: str
    task_description: str
    selected_modules: list[str]
    adapted_modules: list[str]
    reasoning_structure: dict
    thinking_traces: dict
    created_at: str
