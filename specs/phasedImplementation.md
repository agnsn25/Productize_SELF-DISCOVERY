# Phased Implementation Plan

---

## Phase 1: Foundation
*Goal: Project scaffolding, specs, core infrastructure*

### Epic 1.1: Project Setup
- [x] Initialize Python project with FastAPI (requirements.txt)
- [x] Create project directory structure (`backend/app/`, `backend/app/routes/`, `frontend/`, `specs/`, `tests/`, `demo/`)
- [x] Set up FastAPI app entry point with CORS and static file serving
- [x] Create `.env.example` config for Gemini API key and model settings

### Epic 1.2: Specifications
- [x] Create `specs/prd.md`
- [x] Create `specs/thesis.md`
- [x] Create `specs/phasedImplementation.md`
- [x] Create `specs/architectureDiagram.md`
- [x] Create `specs/decisions.md`
- [x] Create `specs/future-work.md`

### Epic 1.3: Database
- [x] Set up SQLite database with aiosqlite connection helper
- [x] Create `structures` table schema (id, task_description, selected_modules, adapted_modules, reasoning_structure JSON, thinking_traces JSON, created_at)
- [x] Write DB helper functions: save_structure, get_structure, list_structures

### Epic 1.4: Gemini Client
- [x] Install `google-genai` SDK
- [x] Create Gemini client wrapper with configurable model and generation params
- [x] Lazy initialization to support testing without API key
- [x] Thinking token capture via `include_thoughts=True`

### Epic 1.5: Reasoning Modules & Prompts
- [x] Define all 39 atomic reasoning modules from the paper as a Python list
- [x] Write SELECT prompt template (given task + modules, select relevant ones)
- [x] Write ADAPT prompt template (given task + selected modules, adapt to task)
- [x] Write IMPLEMENT prompt template (given task + adapted modules, produce JSON structure)
- [x] Write SOLVE prompt template (given problem + structure, solve step-by-step)
- [x] Write NAIVE prompt template (direct prompt for baseline comparison)

---

## Phase 2: Discovery Pipeline
*Goal: Working SELECT -> ADAPT -> IMPLEMENT pipeline with persistence*

### Epic 2.1: Discovery Orchestrator
- [x] Build discovery orchestrator service that chains SELECT -> ADAPT -> IMPLEMENT
- [x] Implement SELECT step: call Gemini with task + 39 modules, parse selected modules
- [x] Implement ADAPT step: call Gemini with task + selected modules, parse adapted modules
- [x] Implement IMPLEMENT step: call Gemini with task + adapted modules, parse JSON structure
- [x] Capture thinking traces from all 3 steps for auditability

### Epic 2.2: JSON Structure Output
- [x] Ensure IMPLEMENT step produces valid, parseable JSON
- [x] Add JSON extraction fallback (markdown code blocks, raw text wrapper)
- [x] Define structure schema (step_N keys with instruction + reasoning_module fields)

### Epic 2.3: Discovery API Endpoints
- [x] `POST /api/discover` -- accepts task description, returns discovered structure + structure_id
- [x] `GET /api/structures` -- list all saved structures
- [x] `GET /api/structures/{id}` -- retrieve a specific structure
- [x] Add request/response Pydantic models
- [x] Add error handling (invalid input, Gemini failures, DB errors)

---

## Phase 3: Inference Pipeline
*Goal: Use discovered structures to solve new problem instances*

### Epic 3.1: Inference Executor
- [x] Build inference executor service that loads a structure and solves a problem
- [x] Implement SOLVE step: call Gemini with problem instance + JSON structure
- [x] Parse and return structured solution with reasoning trace
- [x] Answer extraction with multiple marker formats

### Epic 3.2: Inference API Endpoints
- [x] `POST /api/infer` -- accepts structure_id + problem instance, returns solution
- [x] Add request/response Pydantic models
- [x] Add error handling and validation

### Epic 3.3: Compare Endpoint
- [x] `POST /api/infer/compare` -- accepts structure_id + problem instance
- [x] Run naive (direct prompt, no structure) and structured inference in parallel
- [x] Return side-by-side results (naive answer, structured answer, reasoning traces)

---

## Phase 4: Developer Playground UI
*Goal: Web interface for interactive discovery, solving, and comparison*

### Epic 4.1: UI Scaffolding
- [x] Create `frontend/index.html` with tab layout (Discover, Solve, Compare)
- [x] Create `frontend/style.css` with dark theme, responsive design
- [x] Create `frontend/app.js` with tab switching logic and API call helpers
- [x] Serve static files from FastAPI

### Epic 4.2: Discover Tab
- [x] Task description input textarea
- [x] Quick-fill buttons (Math, Logic, Code, Multi-hop QA)
- [x] "Run Discovery" button that calls `POST /api/discover`
- [x] Display pipeline steps: selected modules, adapted modules, JSON structure (collapsible)
- [x] Show structure ID with copy-to-clipboard
- [x] Thinking traces display (collapsible)
- [x] Loading state and error display

### Epic 4.3: Solve Tab
- [x] Dropdown for saved structures (populated from `GET /api/structures`)
- [x] Refresh button for structure list
- [x] Problem instance input textarea with quick-fill buttons
- [x] "Solve" button that calls `POST /api/infer`
- [x] Display reasoning trace and highlighted answer
- [x] Thinking trace (collapsible)
- [x] Loading state and error display

### Epic 4.4: Compare Tab
- [x] Structure selector + problem instance input
- [x] "Compare" button that calls `POST /api/infer/compare`
- [x] Side-by-side display: naive answer vs SELF-DISCOVER answer
- [x] Visual badges (Baseline vs Structured)
- [x] Thinking traces (collapsible)

---

## Phase 5: Polish & Documentation
*Goal: Demo-ready, well-documented project*

### Epic 5.1: Demo Examples
- [x] Add 4 pre-built demo task types with example problems (math, logic, code, multi-hop QA)
- [x] Quick-fill buttons in all tabs
- [ ] Pre-seed database with discovered structures for demos (requires API key)

### Epic 5.2: Error Handling & Resilience
- [x] Error handling across all endpoints
- [x] JSON extraction fallback in discovery
- [x] Input validation via Pydantic models
- [x] Error toast in UI with auto-dismiss

### Epic 5.3: Documentation
- [x] Write `FORADHARSH.md` -- detailed project explanation in plain language
- [ ] Update `README.md` with setup instructions, architecture overview, usage guide

### Epic 5.4: Testing & Verification
- [x] 27 unit tests (database, discovery, inference) -- all passing
- [x] FastAPI app loads with all routes registered
- [ ] End-to-end test with live Gemini API (requires API key)
