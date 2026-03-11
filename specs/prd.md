# Product Requirements Document (PRD)
# Productizing SELF-DISCOVER Reasoning

**Paper:** [SELF-DISCOVER: Large Language Models Self-Compose Reasoning Structures](https://arxiv.org/pdf/2402.03620)
**Status:** Active Development
**Last Updated:** 2026-03-11

---

## I. Executive Summary

**Vision:** Deliver compute-efficient, highly accurate LLM responses through problem-specific reasoning that is auditable and reusable.

**Problem:** Fixed prompting methods (CoT, zero-shot, few-shot) treat every problem the same way. Different problem types require fundamentally different reasoning approaches. Humans tackle art differently than they fix cars -- LLMs should do the same.

**Solution:** Productize Google DeepMind's SELF-DISCOVER framework as an API service. The system discovers task-specific reasoning structures once (expensive), then reuses them for all future instances of that problem type (cheap). This gets the LLM from jack-of-all-trades to master of the specific task at hand.

**Core Insight:** The discovered reasoning structure is reusable. You pay for discovery once and get cheap inference forever. This is what makes it productizable.

---

## II. Goals & Success Metrics (KPIs)

### Primary Goal: Accuracy

| Metric | Target | Rationale |
|--------|--------|-----------|
| Improvement over CoT Baseline | **30% average accuracy improvement** on challenging benchmarks (BigBench-Hard, MATH, grounded agent reasoning) | Paper demonstrated improvements up to 32% vs CoT, outperforms CoT on 21/25 tasks |
| Competitive Performance | **20% improvement** over inference-heavy ensemble methods (CoT-Self-Consistency) | Establishes the product as new SOTA for high-performance reasoning |

### Secondary Goal: Efficiency

| Metric | Target | Rationale |
|--------|--------|-----------|
| Inference Compute Reduction | **90% reduction** (10x fewer resources) vs CoT-Self-Consistency | Paper showed 10-40x reduction; 10x is conservative and achievable |
| Inference Steps | Execute Stage 2 using discovered structure in **1 inference pass** | Confirms model fills in the structured plan, not re-running discovery |

### Adoption Metric

| Metric | Target | Rationale |
|--------|--------|-----------|
| Active Structure IDs | **1,000 unique, active** Problem Type IDs stored by users in first 6 months | Measures adoption of the core value prop: generating and reusing reasoning structures |

---

## III. Target Users & Use Cases

**Primary Persona:** ML Engineers and Advanced Agent Developers who need reliable, cost-effective reasoning for complex tasks.

**Key Use Cases:**
- Algorithmic code generation
- Fact-checking agents
- Complex multi-step planning
- Mathematical problem solving
- Any scenario requiring cost-effective compute with high accuracy

---

## IV. Functional & Technical Requirements

### Tech Stack
- **Backend:** Python / FastAPI
- **Database:** SQLite (zero-ops for MVP)
- **Frontend:** Plain HTML/CSS/JS (no build step)
- **LLM:** Google Gemini 2.5 Pro via `google-genai` SDK

### API Endpoints

#### 1. Discovery API: `POST /api/discover`
- **Input:** Task description + example instances
- **Process:** SELECT relevant reasoning modules -> ADAPT to task -> IMPLEMENT as JSON structure
- **Output:** Discovered reasoning structure + structure ID
- **Cost tier:** Premium, one-time per problem type

#### 2. Inference API: `POST /api/infer`
- **Input:** Structure ID + new problem instance
- **Process:** Load saved structure -> SOLVE by following the structure
- **Output:** Solution with reasoning trace
- **Cost tier:** Low-cost, high-volume transactional

#### 3. Structure Retrieval: `GET /api/structures`
- **Input:** Optional structure ID
- **Output:** Saved reasoning structure(s)

#### 4. Compare API: `POST /api/infer/compare`
- **Input:** Problem instance + structure ID
- **Process:** Run naive (direct prompt) and structured inference in parallel
- **Output:** Side-by-side results showing accuracy and reasoning differences
- **Purpose:** Proves the thesis visually

### Atomic Reasoning Modules
The system uses all 39 atomic reasoning modules from the paper. The SELECT action chooses which are relevant for a given task. Modules include things like:
- "How could I break down this problem into smaller steps?"
- "What are the constraints or conditions I need to consider?"
- "How can I verify my answer?"

---

## V. Pricing Model

**Two-tiered, value-aligned pricing:**

| Tier | Description | Rationale |
|------|-------------|-----------|
| **Tier 1: Discovery** | Premium, one-time setup charge per new structure generation | Reflects the high compute cost of self-discovery |
| **Tier 2: Inference** | Low-cost, high-volume transactional charge per API call | Reflects compute efficiency of reusing discovered structures |

**Economics:**
```
Cost_Recurring_SD << Cost_Recurring_SOTA

Where:
CSD_Inf << (N x CCoT_Inf)

N = number of CoT passes for comparable accuracy (typically 10-40)
```

The pricing makes scaled usage on similar problem types compelling. Users pay once to discover, then get cheaper-than-market inference forever.

---

## VI. Developer Playground

A web interface with 3 tabs:

1. **Discover Tab:** Submit task descriptions, see the SELECT -> ADAPT -> IMPLEMENT pipeline in action, inspect generated reasoning structures
2. **Solve Tab:** Pick a saved structure, submit a new problem instance, see the structured solution with reasoning trace
3. **Compare Tab:** Submit a problem, see side-by-side naive vs structured results to prove the thesis

**Additional Portal Features:**
- API documentation with JSON request/response examples
- Documentation for available atomic modules
- Best practices for writing high-quality task descriptions

---

## VII. Ethical AI & Guardrails

- **Transparency:** All outputs include the explicit, auditable reasoning path for debugging
- **Mitigation:** Reasoning structures should be governed by ethical AI standards to prevent malicious or harmful reasoning structures
- **Implementation (deferred):** Harmful-content detector AI to screen every reasoning structure before responding

---

## VIII. Out of Scope (MVP)

- Authentication / API keys
- Actual billing / pricing tiers
- Python/Java SDKs
- XML support
- Enterprise metrics dashboard
- Robotics expansion
- Benchmarking harness
