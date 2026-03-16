# Architecture Diagram

---

## System Overview

```
+------------------------------------------------------------------+
|                     WEB PLAYGROUND (Browser)                      |
|                  Plain HTML / CSS / JavaScript                    |
|                                                                   |
|   +----------------+  +----------------+  +------------------+   |
|   |  Discover Tab  |  |   Solve Tab    |  |   Compare Tab    |   |
|   |                |  |                |  |                  |   |
|   | Task input     |  | Structure pick |  | Structure pick   |   |
|   | -> SELECT      |  | Problem input  |  | Problem input    |   |
|   | -> ADAPT       |  | -> Solution    |  | -> Side-by-side  |   |
|   | -> IMPLEMENT   |  |                |  |   CoT vs         |   |
|   | -> Structure   |  |                |  |   structured     |   |
|   +----------------+  +----------------+  +------------------+   |
+------------------------------|------------------------------------+
                               | HTTP (fetch)
                               v
+------------------------------------------------------------------+
|                      FastAPI Backend (Python)                     |
|                                                                   |
|  Routers:                                                        |
|  +------------------------------------------------------------+  |
|  | POST /api/discover     -> Discovery Orchestrator            |  |
|  | GET  /api/structures   -> DB: list structures               |  |
|  | GET  /api/structures/id-> DB: get structure                 |  |
|  | POST /api/infer        -> Inference Executor                |  |
|  | POST /api/infer/compare-> Parallel CoT + structured         |  |
|  +------------------------------------------------------------+  |
|                               |                                   |
|  Services:                    |                                   |
|  +----------------------------+-------------------------------+  |
|  |                            |                               |  |
|  |  Discovery Orchestrator    |    Inference Executor         |  |
|  |  +---------------------+  |    +----------------------+   |  |
|  |  | 1. SELECT           |  |    | 1. Load structure    |   |  |
|  |  | 2. ADAPT            |  |    | 2. SOLVE (fill in    |   |  |
|  |  | 3. IMPLEMENT        |  |    |    JSON structure)    |   |  |
|  |  | 4. Save to DB       |  |    | 3. Return solution   |   |  |
|  |  +---------------------+  |    +----------------------+   |  |
|  |                            |                               |  |
|  +----------------------------+-------------------------------+  |
|               |                              |                    |
+---------------|------------------------------|--------------------+
                |                              |
       +--------+--------+                    |
       v                 v                    v
+------------+    +------------+    +------------------+
|   SQLite   |    | 39 Atomic  |    | Google Gemini    |
|            |    | Reasoning  |    | 2.5 Pro          |
| structures |    | Modules    |    |                  |
| table:     |    | (in-code   |    | via google-genai |
| - id       |    |  constant) |    | SDK              |
| - task_desc|    |            |    |                  |
| - selected |    +------------+    +------------------+
| - adapted  |
| - structure|
| - created  |
+------------+
```

---

## Discovery Flow (Stage 1)

```
User Task Description
        |
        v
+-------------------+      +------------------+
| SELECT            |----->| Gemini 2.5 Pro   |
| "Which of these   |      | Returns: subset  |
|  39 modules are   |<-----| of modules       |
|  relevant?"       |      +------------------+
+-------------------+
        |
        v (selected modules)
+-------------------+      +------------------+
| ADAPT             |----->| Gemini 2.5 Pro   |
| "Rewrite these    |      | Returns: task-   |
|  modules for this |<-----| specific modules |
|  specific task"   |      +------------------+
+-------------------+
        |
        v (adapted modules)
+-------------------+      +------------------+
| IMPLEMENT         |----->| Gemini 2.5 Pro   |
| "Convert to an    |      | Returns: JSON    |
|  actionable JSON  |<-----| reasoning        |
|  structure"       |      | structure        |
+-------------------+
        |
        v
+-------------------+
| Save to SQLite    |
| Return structure  |
| + structure_id    |
+-------------------+
```

---

## Inference Flow (Stage 2)

```
Structure ID + New Problem Instance
        |
        v
+-------------------+
| Load structure    |
| from SQLite       |
+-------------------+
        |
        v
+-------------------+      +------------------+
| SOLVE             |----->| Gemini 2.5 Pro   |
| "Follow this JSON |      | Returns: filled  |
|  structure to     |<-----| structure with   |
|  solve the        |      | solution         |
|  problem"         |      +------------------+
+-------------------+
        |
        v
+-------------------+
| Return solution   |
| with reasoning    |
| trace             |
+-------------------+
```

---

## Compare Flow

```
Structure ID + Problem Instance
        |
        +----------------------------+
        |                            |
        v                            v
+----------------+          +-----------------+
| CoT Path       |          | Structured Path |
| (step-by-step  |          | (load structure |
|  no structure) |          |  -> SOLVE)      |
+----------------+          +-----------------+
        |                            |
        v                            v
+----------------+          +-----------------+
| Gemini call    |          | Gemini call     |
| (single pass)  |          | (single pass)   |
+----------------+          +-----------------+
        |                            |
        +----------------------------+
        |
        v
+-------------------+
| Side-by-side      |
| comparison result |
| + timing data     |
+-------------------+
```

---

## Directory Structure

```
Productizing_SELF-DISCOVER/
|-- app/
|   |-- __init__.py
|   |-- main.py              # FastAPI app entry point
|   |-- config.py             # Settings, env vars
|   |-- database.py           # SQLite connection + helpers
|   |-- routers/
|   |   |-- discover.py       # POST /api/discover, GET /api/structures
|   |   |-- infer.py          # POST /api/infer, POST /api/infer/compare
|   |-- services/
|   |   |-- discovery.py      # Discovery orchestrator (SELECT->ADAPT->IMPLEMENT)
|   |   |-- inference.py      # Inference executor (SOLVE)
|   |   |-- gemini_client.py  # Gemini API wrapper
|   |-- models/
|   |   |-- schemas.py        # Pydantic request/response models
|   |-- prompts/
|   |   |-- modules.py        # 39 atomic reasoning modules
|   |   |-- templates.py      # SELECT, ADAPT, IMPLEMENT, SOLVE prompt templates
|-- static/
|   |-- index.html            # Playground UI
|   |-- style.css
|   |-- app.js
|-- specs/                    # This directory
|-- data/
|   |-- selfdiscover.db       # SQLite database file
|-- requirements.txt
|-- .env
|-- README.md
|-- FORADHARSH.md
```
