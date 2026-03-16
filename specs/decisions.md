# Decision Log

Records the "why" behind key technical and product decisions. Each entry captures the decision, alternatives considered, and rationale.

---

## D001: Gemini 2.5 Pro for Both Stages
**Date:** 2026-03-11
**Decision:** Use Google Gemini 2.5 Pro for both discovery (Stage 1) and inference (Stage 2).

**Alternatives considered:**
- Use a cheaper/smaller model for inference (Stage 2) since the structure guides reasoning
- Use different models for different stages

**Rationale:** The paper uses the same model for both stages. Cost savings in SELF-DISCOVER come from fewer API calls (1 vs 10-40), not from downgrading the model. Using the same model keeps the implementation simple and faithful to the paper. The structure already reduces compute -- no need to also sacrifice model quality.

---

## D002: All 39 Modules from the Paper
**Date:** 2026-03-11
**Decision:** Include all 39 atomic reasoning modules from the paper in the module library.

**Alternatives considered:**
- Curate a smaller subset of "most useful" modules
- Let users define custom modules

**Rationale:** The SELECT step already handles filtering -- it picks only the relevant modules for a given task. Including all 39 gives the system maximum flexibility. Removing modules would be premature optimization. Custom modules are deferred to future work.

---

## D003: SQLite over PostgreSQL
**Date:** 2026-03-11
**Decision:** Use SQLite as the database for storing reasoning structures.

**Alternatives considered:**
- PostgreSQL (more scalable, better for production)
- JSON files on disk

**Rationale:** Zero operational overhead for an MVP. No separate database server to run. SQLite handles the expected load (hundreds to low thousands of structures) perfectly. The data model is simple (one main table). Easy to swap to Postgres later if needed -- the DB helper functions abstract the connection.

---

## D004: Plain HTML/CSS/JS over React
**Date:** 2026-03-11
**Decision:** Build the developer playground with plain HTML, CSS, and vanilla JavaScript. No framework.

**Alternatives considered:**
- React (component model, state management)
- Vue.js (lighter than React)
- Svelte

**Rationale:** No build step needed. The playground is 3 tabs with forms and result displays -- this does not justify a framework's complexity. FastAPI serves static files directly. Faster to develop, easier to understand, zero toolchain to maintain. The UI is a demo/playground, not a production SaaS frontend.

---

## D005: Compare Endpoint
**Date:** 2026-03-11
**Decision:** Build a dedicated `POST /api/infer/compare` endpoint that runs CoT and structured inference side-by-side.

**Alternatives considered:**
- Let users manually run two separate calls and compare themselves
- Only show structured results

**Rationale:** The compare endpoint is the single most persuasive feature for proving the thesis. Seeing a CoT answer next to a structured answer, with reasoning traces, makes the value proposition tangible and visual. It's the demo-closer. Worth the extra implementation effort.

---

## D006: google-genai SDK (not google-generativeai)
**Date:** 2026-03-11
**Decision:** Use the `google-genai` Python SDK for Gemini API access.

**Alternatives considered:**
- `google-generativeai` (the older SDK)
- Direct HTTP calls to the Gemini REST API

**Rationale:** The older `google-generativeai` package hit EOL in November 2025. `google-genai` is the official replacement with active maintenance, better async support, and Gemini 2.x model support. Direct HTTP calls would work but add unnecessary boilerplate for auth, retries, and response parsing that the SDK handles.

---

## D007: Rename "Naive" Baseline to "CoT" (Chain-of-Thought)
**Date:** 2026-03-15
**Decision:** Rename all references from "naive" to "CoT" across the codebase — code, UI, tests, docs, and specs.

**Alternatives considered:**
- Keep "naive" label but add a tooltip explaining it's actually CoT
- Add a truly naive (zero-shot, no reasoning) baseline as a third comparison

**Rationale:** The baseline prompt says "solve step by step" and asks the model to show reasoning — that's textbook Chain-of-Thought prompting, not naive/direct prompting. Calling it "naive" was misleading and undersold the baseline, making SELF-DISCOVER look like it was beating a weaker opponent than it actually is. The original paper compares against CoT, so this rename aligns us with the paper's terminology and is more honest to users.

---

## Critical Change Log

*This section records codebase-wide changes, breaking changes, and major refactors.*

| Date | Change | Rationale | Impact |
|------|--------|-----------|--------|
| 2026-03-11 | Project initialized with specs | Starting from PRD, establishing foundations before code | All future development follows these specs |
| 2026-03-15 | Renamed "naive" → "CoT" across entire codebase | Baseline prompt was CoT, not naive — mislabeling was misleading | API response keys changed: `naive` → `cot`. CSS classes: `naive-*` → `cot-*`. Python: `NAIVE_PROMPT` → `COT_PROMPT`, `run_naive` → `run_cot`. Frontend element IDs updated. |
