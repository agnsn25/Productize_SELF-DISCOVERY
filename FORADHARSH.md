# FORADHARSH: The SELF-DISCOVER Project Explained

Welcome to the deep-dive on everything this project is, why it exists, and how the pieces fit together. This isn't a dry reference doc -- it's written to make the ideas stick.

---

## What is SELF-DISCOVER and Why Should You Care?

Imagine you're a chef. When someone asks you to cook a meal, you don't just start throwing ingredients in a pan. You first think about *what kind of dish* this is -- is it a stew? A stir-fry? Baking? -- and then you pick your techniques accordingly. You wouldn't whisk eggs the same way you'd deglaze a pan.

Now imagine a chef who uses the exact same technique for every dish. Whisking. Always whisking. Soup? Whisk it. Steak? Whisk it. That chef would produce some okay meals, but a lot of disasters.

**That's what most LLM prompting does today.** Chain-of-Thought (CoT) says "think step by step" for *every* problem. It's one technique applied universally. Sometimes it works great. Sometimes it's like whisking a steak.

SELF-DISCOVER, from a 2024 Google DeepMind paper, says: **let the LLM design its own recipe first, then follow it.** The LLM looks at the type of problem, picks the right reasoning strategies from a library of 39 options, customizes them, and builds a step-by-step JSON blueprint. Then, for every new problem of that type, it just follows the blueprint.

The results? Up to 32% better accuracy than Chain-of-Thought. 10-40x less compute than ensemble methods. And the blueprint is reusable -- discover once, solve forever.

**That's why it's productizable.** You pay for the recipe development once. Every meal after that is cheap.

---

## The Architecture: Why These Specific Technologies?

Here's the stack and the reasoning behind each choice:

### FastAPI (Python Backend)

FastAPI was chosen because it's async-native (important when you're waiting on LLM API calls that take seconds), automatically generates API docs, and has excellent Pydantic integration for request/response validation. For an MVP that's basically an orchestration layer between a frontend, a database, and an LLM API, FastAPI is arguably the best Python option.

### SQLite (Database)

"Wait, SQLite? For production?" -- Yes, for an MVP. SQLite has zero operational overhead. No database server to install, configure, or maintain. It's a single file. The data model is simple: one table (`structures`) storing the discovered reasoning blueprints. At MVP scale (hundreds to low thousands of structures), SQLite handles this easily. If this scales to enterprise, swapping to PostgreSQL is straightforward because the DB helper functions abstract the connection.

### Google Gemini 2.5 Pro (LLM)

The paper used PaLM 2 (also Google). Gemini 2.5 Pro is Google's latest, with a killer feature for this project: **thinking tokens** (more on that below). The `google-genai` SDK (not the older deprecated `google-generativeai`) provides the API access.

### Plain HTML/CSS/JS (Frontend)

No React. No Vue. No build step. The frontend is a developer playground with three tabs -- it doesn't need component state management or a virtual DOM. Plain HTML served directly by FastAPI. This was a deliberate decision: the frontend exists to demo the API, not to be a SaaS product. Simpler tech = faster development = fewer things to break.

---

## How Discovery Works: SELECT, ADAPT, IMPLEMENT

This is the heart of the project. Let's walk through it with a concrete example.

**Say the task is:** "Solve multi-step math word problems involving rates, percentages, and unit conversions."

### Step 1: SELECT

The system sends all 39 reasoning modules to Gemini along with the task description: "Which of these modules are relevant for this task?"

Gemini might select:
- "How can I break down this problem into smaller, more manageable parts?"
- "Does the problem involve quantitative reasoning or data analysis?"
- "I need to find any relevant formulas, equations, or mathematical models"
- "Let's make a step by step plan and implement it with good notation and target"

It ignores modules like "Seek input and collaboration from others" because that's not relevant for math.

**Code path:** `discovery.py` -> formats `SELECT_PROMPT` with the task + all 39 modules -> sends to `gemini_client.py` -> gets back selected modules.

### Step 2: ADAPT

Now the system says: "Take these selected modules and rewrite them specifically for math word problems."

Generic "break into parts" becomes something like: "Identify the quantities given (prices, percentages, rates) and the quantity asked for. Set up the problem in stages."

**Code path:** `discovery.py` -> formats `ADAPT_PROMPT` with task + selected modules -> Gemini call -> adapted modules.

### Step 3: IMPLEMENT

Finally: "Convert these adapted modules into a JSON reasoning structure -- a step-by-step template."

The output is a JSON object like:
```json
{
  "step_1": {
    "instruction": "Extract all numerical values and their units from the problem",
    "reasoning_module": "Identify the quantities given..."
  },
  "step_2": {
    "instruction": "Determine the sequence of operations needed",
    "reasoning_module": "Let's make a step by step plan..."
  },
  "step_3": {
    "instruction": "Execute each operation, tracking units carefully",
    "reasoning_module": "Find relevant formulas..."
  },
  "step_4": {
    "instruction": "Verify the answer by checking units and reasonableness",
    "reasoning_module": "Break into parts..."
  }
}
```

This structure gets saved to SQLite with a unique ID. **That ID is the product.** It's the "recipe" that can be reused infinitely.

**Code path:** `discovery.py` -> formats `IMPLEMENT_PROMPT` -> Gemini call -> JSON parsing (with fallback for markdown code blocks) -> saved via `database.py`.

---

## How Inference Works: Load and SOLVE

Once you have a structure ID, solving a new problem is dead simple:

1. Load the structure from SQLite
2. Format the SOLVE prompt: "Here's the structure, here's the problem, follow the steps"
3. One Gemini call
4. Parse the answer

That's it. One API call. No re-discovery. No ensemble of 10-40 passes. Just one call with a good blueprint.

**The economics:** If CoT-Self-Consistency runs 20 passes to get a reliable answer, SELF-DISCOVER runs 1. For 1000 problems of the same type, that's 1000 calls vs 20,000. The discovery cost (3 calls) amortizes to nothing.

---

## The Compare Feature: Proving the Thesis

The `/api/infer/compare` endpoint is the demo-closer. It runs the same problem through *both* approaches in parallel:

1. **Naive path:** Direct prompt, no structure -- "solve this step by step"
2. **Structured path:** Load the discovered structure, follow the blueprint

The results appear side-by-side in the Compare tab. You can see the naive answer meander and sometimes get lost, while the structured answer follows a clear, methodical path. This is what makes the thesis tangible -- not a chart in a paper, but a live demo you can try with your own problems.

---

## The Codebase: How Files Connect

```
backend/app/
  config.py              <- Settings (API key, model, DB path, thinking budgets)
  gemini_client.py       <- Thin wrapper around google-genai SDK
  reasoning_modules.py   <- The 39 atomic modules (a Python list)
  prompts.py             <- All prompt templates (SELECT, ADAPT, IMPLEMENT, SOLVE, NAIVE)
  models.py              <- Pydantic schemas for API requests/responses
  database.py            <- SQLite CRUD (init, save, get, list)
  discovery.py           <- SELECT->ADAPT->IMPLEMENT orchestrator
  inference.py           <- SOLVE executor + NAIVE executor + answer parsing
  main.py                <- FastAPI app setup, CORS, static files, lifespan
  routes/
    discover.py          <- POST /api/discover endpoint
    infer.py             <- POST /api/infer, POST /api/infer/compare endpoints
    structures.py        <- GET /api/structures, GET /api/structures/{id}

frontend/
  index.html             <- Single-page playground (3 tabs)

tests/
  test_discovery.py      <- Tests for the discovery pipeline
  test_inference.py      <- Tests for inference and answer parsing
  test_database.py       <- Tests for SQLite operations

demo/
  examples.json          <- Pre-built task descriptions and sample problems

specs/
  prd.md                 <- Product requirements
  thesis.md              <- Why SELF-DISCOVER matters (the research background)
  phasedImplementation.md <- Development roadmap
  architectureDiagram.md  <- ASCII architecture diagrams
  decisions.md           <- Decision log (why we chose X over Y)
```

**The data flow:** Frontend -> Routes -> Services (discovery.py / inference.py) -> Gemini Client -> Google Gemini API. Database sits to the side for storage/retrieval.

---

## The 39 Reasoning Modules: Where They Come From

The modules aren't arbitrary. They come from research on human problem-solving strategies. The paper's authors curated them from cognitive science and AI literature. They include things like:

- **Metacognitive strategies:** "Let's think step by step", "Let me take a deep breath and think about this carefully"
- **Analytical frameworks:** Critical thinking, systems thinking, risk analysis
- **Problem decomposition:** Breaking into sub-problems, identifying constraints
- **Domain detection:** "Does this involve quantitative reasoning?", "Does this involve abstract thinking?"
- **Verification:** "How can I measure progress?", "What are the potential risks?"

The magic isn't in any single module -- it's in the SELECT step choosing the *right combination* for a specific task. A math problem gets different modules than an ethical dilemma. That's the whole point.

They live in `reasoning_modules.py` as a simple Python list. No database, no config file -- they're constants from the paper.

---

## Thinking Tokens in Gemini 2.5 Pro

This is a genuinely cool feature. Gemini 2.5 Pro supports "thinking" -- the model can reason internally before giving its answer, similar to how a person might scratch out notes before writing a final response.

In the API, you set a `thinking_budget` (in tokens). The model's response then contains two types of content:
- **Thought parts** (`part.thought = True`): The model's internal reasoning. You can inspect these but they aren't part of the "official" answer.
- **Text parts** (`part.thought = False`): The actual response.

Our `gemini_client.py` separates these and returns both. The frontend displays thinking traces in collapsible sections so you can peek behind the curtain.

**Why capture thinking tokens?**
1. **Debugging:** If the model gives a wrong answer, you can see *where* its reasoning went off track
2. **Transparency:** Customers can audit the reasoning process
3. **Tuning:** The `thinking_budget` setting (8192 for discovery, dynamic for inference) controls how much "scratch space" the model gets. More budget = deeper reasoning = higher cost. It's a tunable knob.

---

## Lessons Worth Remembering

### 1. Simpler Tech Stacks Win for MVPs

This project uses SQLite, plain HTML, and a single Python backend. No Kubernetes, no Redis, no message queues, no React build pipeline. And it works. The temptation to over-engineer an MVP is real -- resist it. Every piece of infrastructure you add is something you have to maintain, debug, and explain. Start simple. Add complexity only when the simple thing breaks.

### 2. Prove the Thesis Before Building Enterprise Features

The compare endpoint exists before authentication, billing, or SDKs. Why? Because if the core thesis doesn't hold -- if structured reasoning isn't meaningfully better than naive prompting -- then none of the enterprise features matter. The compare feature is the "does this even work?" test. Always build the proof before the product.

### 3. Academic Insights Translate to Product Economics

The paper talks about "compute reduction" and "transferable reasoning structures." Translated to product language: "cheaper API calls" and "reusable assets your customers pay for once." The academic framing and the business framing are the same insight wearing different clothes. Reading papers with a "how would I sell this?" lens is a superpower.

### 4. JSON Parsing from LLMs is Fragile

LLMs don't always return clean JSON. Sometimes they wrap it in markdown code blocks (```json ... ```). Sometimes they add commentary before or after. The discovery code has a fallback chain: try `json.loads()` directly, then try extracting from code blocks, then fall back to wrapping the raw text. This defensive parsing pattern comes up in *every* project that asks LLMs for structured output. Expect it. Plan for it.

### 5. Async Patterns in Python Require Care

The Gemini SDK's `generate_content` is synchronous. But FastAPI is async. Calling a synchronous function in an async context blocks the event loop -- meaning your server can't handle other requests while waiting for Gemini. The fix: `asyncio.to_thread()`, which runs the sync call in a worker thread. This is a common pattern when wrapping sync libraries in async code. Watch for it.

---

## Potential Pitfalls (and How to Avoid Them)

### API Rate Limits
Gemini has rate limits. Discovery makes 3 API calls in sequence. If you're running multiple discoveries concurrently, you can hit limits fast. Solution: add retry logic with exponential backoff, or queue discovery requests.

### Thinking Budget Tuning
Too low a thinking budget and the model gives shallow answers. Too high and you burn tokens (and money) on overthinking. The current defaults (8192 for discovery, dynamic/-1 for inference) are starting points. Tuning these per task type would be a valuable future feature.

### JSON Parsing Failures
Even with fallbacks, LLMs occasionally produce unparseable output. The current fallback (`{"raw": raw_text}`) preserves the output but loses structure. A retry mechanism (ask the model again with "please return valid JSON") would be more robust.

### SQLite Concurrency
SQLite handles concurrent reads fine but concurrent writes can cause "database is locked" errors under heavy load. For an MVP this is fine. At scale, switch to PostgreSQL or add write queuing.

### The SOLVE Prompt Placeholder
There's a subtlety in the codebase: `prompts.py` defines `SOLVE_PROMPT` with `{structure}` as the placeholder, but `inference.py` calls `.format(reasoning_structure=...)`. The keyword argument name must match the placeholder name in the template. If you see a `KeyError` at runtime, this is likely why. Always double-check that `.format()` kwargs match the `{placeholder}` names in your templates.

---

## The Big Picture

This project takes a research paper and turns it into a working product. The insight is simple but powerful: **reasoning strategies are reusable assets, not throwaway computations.** Discover once, solve forever. The whole architecture -- the two-stage pipeline, the database of structures, the compare endpoint -- exists to prove and deliver on that single idea.

The best engineering isn't about using the fanciest tools. It's about picking the right level of complexity for the problem at hand, building the proof before the polish, and making the core value proposition undeniable. That's what this project does.
