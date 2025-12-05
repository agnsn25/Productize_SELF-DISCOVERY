# Productizing SELF-DISCOVER Reasoning

URL: https://deepmind.google/research/publications/large-language-models-self-discover-reasoning-structures/
Status: Done

My take on productizing the SELF-DISCOVER paper published by Google Deepmind (link: [https://arxiv.org/pdf/2402.03620](https://arxiv.org/pdf/2402.03620)).

The SELF-DISCOVERY paper from Google DeepMind posits the following:

- Similar to humans who reason differently for different types of tasks, AI systems should too. This will lead to far better and more accurate responses with the use of right tools, right techniques, and asking right questions to generate the right responses.
- Through SELF-DISCOVERY, the model will first analyze the problem and generate a step-by-step, auditable reasoning steps to solve a type of problem.
    - Once self-discovery is done per type of problem, it is reused for other problems under the same type.
    - This makes the model compute efficient.
- Benefits
    - Auditable reasoning - unique reasoning structures based on problem types
    - Compute efficient - executed once per problem type
    - Better accuracy in problem solving through problem-specific reasoning steps

## **Product Requirements Document (PRD)**

### I. Executive Summary

- **The Vision:** Delivering compute-efficient, highly accurate LLM responses through a highly problem-specific reasoning that is auditable.
- **Problem:** Fixed prompting methods do not always provide accurate answers. Different types of problems require different methods of solving.
    - From a first principles standpoint, humans tackle different problems differently. Creating art requires an inherently different solution skillset compared to fixing a car.
- **Solution:** - So it must be obvious that LLMs should also use different approaches (reasoning) to distinct problem types to be effective. Using a task-intrinsic strategy through SELF-DISCOVERY to create responses proves to be more accurate. This gets the LLM from being the jack of all trades to a master of the specific task at hand.

### II. Goals & Success Metrics (KPIs)

- **Primary Goal (Accuracy):** Target improvement percentage on complex reasoning benchmarks.

| **Metric** | **Target** | **Rationale** |
| --- | --- | --- |
| **Improvement over CoT Baseline** | **30%** **Average Accuracy Improvement** on challenging benchmarks (e.g., BigBench-Hard, grounded agent reasoning, MATH). | The paper demonstrated improvements **up to 32%** compared to CoT and outperforms CoT on 21 out of 25 tasks. |
| **Competitive Performance** | **20%** **Improvement** over inference-heavy ensemble methods (like CoT-Self-Consistency). | This establishes the product as the new SOTA (State-of-the-Art) for high-performance reasoning. |
- **Secondary Goal (Efficiency):** Target reduction in inference cost (e.g., <1.5x the cost of a direct prompt).

| **Metric** | **Target** | **Rationale** |
| --- | --- | --- |
| **Inference Compute Reduction** | **90%** **Reduction in Inference Compute** (10x fewer resources) compared to inference-heavy competitors (like CoT-Self-Consistency). | The paper showed a **10-40x reduction** in compute, making a 10x reduction (90% savings) a conservative and achievable target that highlights the core value of efficiency. |
| **Inference Steps** | Execute the **Execution Stage (Step 2)** using the discovered structure in **1st inference pass**(the low-cost transaction). | This confirms the model is filling in values in the structured plan efficiently, not re-running the discovery process. |

- **Adoption Metric:** Number of active enterprise/developer projects or API keys in the first 6-12 months.

| **Metric** | **Target** | **Rationale** |
| --- | --- | --- |
| **Active Structure IDs** | **1,000 unique, active** `Problem Type IDs` stored by enterprise/advanced developer users in the first 6 months. | Focuses on the adoption of the core value proposition: generating and reusing the expensive, unique reasoning structure. |

### III. Target Users & Use Cases

- **Primary Persona:** The ML Engineer / Advanced Agent Developer.
- **Key Use Cases:** Uses include any scenario requiring cost-effective compute and high levels of accuracy.
    - Algorithmic Code Generation
    - Fact-checking agents
    - Complex multi-step planning
    - Robotics

### IV. Functional & Technical Requirements

The SELF-DISCOVER API will operate in 2 steps:

1. DISCOVERY: Consume user prompt as the request and generate problem-type specific “reasoning steps” & Problem Type ID as the response. 
    1. A library of “atomic modules” is available to the API and the API chooses the right atomic module sequence to determine the solution approach to a problem.
2. INFERENCE: The user provides the **`Problem Type ID`** (retrieved from the DISCOVERY step) and a new problem instance. The API uses this ID to retrieve the corresponding atomic module sequence for efficient, guided inference.

![image.png](image.png)

### V. Pricing

- **Cost Structure:** I propose a differentiated, two-tiered pricing model.
    - **Tier 1: Discovery (Step 1):** A **premium, one-time setup charge** per new `Problem Type ID` generation, reflecting the high compute cost of self-discovery.
    - **Tier 2: Inference (Step 2):** A **low-cost, high-volume transactional charge** per API call, reflecting the compute efficiency of reusing the generated reasoning steps.
- **Value Alignment:** This pricing strategy ties to the novelty of the SELF-DISCOVERY model.
    - The innovation resides in the DISCOVER step which is compute intensive. As a result, we charge the user a one-time premium per unique problem-type for this.
    - We charge a lower than market price for the INFERENCE step to be competitive with other LLMs.
    - The API returns the “atomic module sequence” along with problem type ID so the user can reuse the reasoning steps in future by passing that to the API, in which case the API skips the DISCOVERY step.

The goal is to make this model compelling with scaled usage on similar problem-types. In this case, 

$$
CostRecurring\_SD≪CostRecurring\_SOTA
$$

$$
Where:
$$

$$
CSD\_Inf≪(N×CCoT\_Inf)
$$

### Variable Definitions

| Variable | Definition | Rationale |
| --- | --- | --- |
| CSD_Inf | Cost of SELF-DISCOVER Inference (Step 2): The low-cost, single pass execution using the saved Reasoning Steps. | This is the low-volume transactional charge in your pricing model. |
| CCoT_Inf | Cost of a Single CoT Inference Pass. | The standard unit cost for a basic prompt completion. |
| N | Number of CoT passes required by SOTA methods (like CoT-Self-Consistency) to achieve comparable high accuracy. | Based on research, N is typically between **10 and 40**. |

The left-hand side represents SELF-DISCOVER API, the right-hand side represents any Reasoning/CoT SoTA API.

### VI. Developer Portal

- **Discovery Playground (UI/UX):** A web interface allowing developers to submit sample tasks and visually inspect the generated `Reasoning Steps` (the sequence of atomic modules) for debugging and auditability before committing to a final ID.

![Developer Playground Mockup](image%201.png)

Developer Playground Mockup

- API Documentation:
    - Detailed API Request structure, in both JSON and XML
    - Sample API Requests and Responses
- **SDK/Client Libraries:** Provision for Python and Java SDKs for easy integration.
- **Documentation:** Clear documentation for the available **Atomic Modules** and best practices for writing high-quality task descriptions to maximize the self-discovery process.

### VII. Ethical AI & Guardrails

- **Transparency:** All outputs must include the explicit, auditable reasoning path for debugging safety issues.
- **Mitigation:** Every reasoning structure response must be governed by pre-established Ethical AI standards to prevent the formation of malicious or harmful reasoning structures.
    - This can be done by passing every reasoning structure generated through a harmful-content detector AI to ensure any harmful atomic module sequence is caught before responding to the user.

### VIII. Future - expand to robotics

Expand to Robotics: The problem-specific reasoning structures are highly applicable to complex, multi-step **Robotics Task Planning**. The system could discover optimal action sequences (atomic modules = robot actions) once for a task, and rapidly execute them in various environments.