from pydantic import BaseModel


# ── Shared ───────────────────────────────────────────────

class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0
    total_tokens: int = 0


class ScaleProjection(BaseModel):
    n: int
    naive_cost: float
    cot_sc_cost: float
    sd_full_cost: float | None
    sd_inference_cost: float


# ── Discover ──────────────────────────────────────────────

class DiscoverRequest(BaseModel):
    task_description: str


class DiscoverResponse(BaseModel):
    id: str
    task_description: str
    selected_modules: list[str]
    adapted_modules: list[str]
    reasoning_structure: dict
    thinking_traces: dict
    created_at: str
    discovery_usage: dict | None = None


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
    naive: dict
    self_discover: dict
    thinking_traces: dict | None
    token_usage: dict | None = None
    scale_projections: list[ScaleProjection] | None = None
    cot_sc_passes: int | None = None


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
    discovery_usage: dict | None = None
