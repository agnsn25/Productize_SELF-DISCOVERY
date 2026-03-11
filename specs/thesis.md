# Core Thesis & Problem Domain Background

**Paper:** [SELF-DISCOVER: Large Language Models Self-Compose Reasoning Structures](https://arxiv.org/pdf/2402.03620)
**Authors:** Zhou et al., Google DeepMind & USC (2024)

---

## The Problem: Why Fixed Prompting Fails

Traditional prompting strategies (zero-shot, few-shot, Chain-of-Thought) apply the same reasoning template to every problem. This is like using a screwdriver for every job -- sometimes you need a hammer.

**Fixed prompting limitations:**
- CoT uses a single reasoning style regardless of problem type
- Ensemble methods (CoT-Self-Consistency) brute-force accuracy by running many passes (10-40x compute)
- No task-specific reasoning adaptation
- No reusability -- every new problem starts from scratch

The core insight: humans reason differently for different tasks. Math problems, ethical dilemmas, spatial reasoning, and creative tasks all use different cognitive strategies. LLMs should too.

---

## How SELF-DISCOVER Works

SELF-DISCOVER operates in two stages:

### Stage 1: Discovery (expensive, one-time per task type)

The LLM composes a task-specific reasoning structure from a library of 39 atomic reasoning modules. Three actions:

1. **SELECT:** Given a task description and the full library of 39 modules, the LLM selects which modules are relevant. Example: for a math word problem, it might select "break into sub-problems," "identify constraints," and "verify the answer."

2. **ADAPT:** The LLM rewrites the selected modules to be task-specific. Generic "break into sub-problems" becomes "identify the quantities given and the quantity asked for, then set up equations."

3. **IMPLEMENT:** The LLM converts the adapted modules into an actionable JSON reasoning structure -- a step-by-step template that any instance of this problem type can follow.

### Stage 2: Inference (cheap, reusable)

Given a new problem instance and the discovered JSON structure:

4. **SOLVE:** The LLM follows the reasoning structure step-by-step, filling in values for the specific problem. No re-discovery needed.

### The 39 Atomic Reasoning Modules

The paper defines 39 seed modules drawn from research on human problem-solving. These include strategies like:
- Critical thinking and questioning assumptions
- Breaking problems into sub-problems
- Working backwards from the goal
- Using analogies and creative thinking
- Verifying and double-checking results
- Considering constraints and edge cases
- Systems thinking and interconnections

The SELECT step ensures only relevant modules are used for a given task -- you don't need all 39 for any single problem.

---

## Key Findings from the Paper

### Performance
- **Outperforms CoT on 21 out of 25 tasks** on BigBench-Hard
- **Up to 32% improvement** over Chain-of-Thought on challenging benchmarks
- **Outperforms CoT-Self-Consistency** (an ensemble method) on most tasks despite using far less compute
- Strong results on **MATH** benchmark and **grounded agent reasoning** tasks

### Efficiency
- **10-40x compute reduction** compared to ensemble methods like CoT-Self-Consistency
- CoT-SC runs 10-40 parallel inference passes and takes a majority vote
- SELF-DISCOVER runs discovery once, then each inference is a single pass
- At scale (many instances of the same problem type), the discovery cost amortizes to nearly zero

### Transferability
- Discovered structures transfer across LLM families (structures found by one model can be used by another)
- Structures are interpretable -- humans can read and understand the reasoning plan
- Structures align with human reasoning patterns on similar tasks

---

## Why SELF-DISCOVER is Productizable

The economics work because of one key property: **reusability**.

**Traditional reasoning (CoT-SC):**
```
Cost per problem = N x single_inference_cost  (N = 10-40)
Cost for 1000 problems = 1000 x N x single_inference_cost
```

**SELF-DISCOVER:**
```
Cost per problem type = 1 x discovery_cost (one-time)
Cost per problem instance = 1 x single_inference_cost
Cost for 1000 problems = discovery_cost + (1000 x single_inference_cost)
```

As usage scales, SELF-DISCOVER's cost per problem approaches a single inference call, while ensemble methods stay at 10-40x forever. This creates a natural two-tier pricing model: charge a premium for discovery, charge below-market for inference.

**Additional productization factors:**
- JSON structures are storable, retrievable, and versioned in a database
- Structures are auditable -- customers can inspect and trust the reasoning
- Structures are transferable -- discovered once, usable across model versions
- The API surface is clean: discover, store, retrieve, solve

---

## The Thesis in One Sentence

SELF-DISCOVER transforms LLM reasoning from a per-query expense into a per-problem-type investment, making high-accuracy reasoning economically viable at scale.
