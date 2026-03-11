SELECT_PROMPT = """\
Given the task: {task}

Here are the available reasoning modules:
{modules}

Select the reasoning modules that are most relevant to solving the given task.
Choose only the modules that would genuinely help — do not select all of them.

Return your answer as a JSON array of strings, where each string is the exact
text of a selected reasoning module. Example:

["Module text 1", "Module text 2", "Module text 3"]

Return ONLY the JSON array, no extra commentary.
"""

ADAPT_PROMPT = """\
Given the task: {task}

The following reasoning modules have been identified as relevant:
{selected_modules}

Rephrase and adapt each selected module so that it is specifically tailored to
the given task. Make each module actionable and concrete in the context of the
task while preserving the core intent of the original module.

Return your answer as a JSON array of strings, where each string is the adapted
version of one module. Keep the same order as the input. Example:

["Adapted module 1 text", "Adapted module 2 text"]

Return ONLY the JSON array, no extra commentary.
"""

IMPLEMENT_PROMPT = """\
Given the task: {task}

The following adapted reasoning modules should be used:
{adapted_modules}

Create a structured JSON reasoning plan that operationalizes these modules into
an ordered sequence of steps. The JSON object should have keys "step_1",
"step_2", etc. Each step should be an object with two fields:

- "instruction": A clear, specific instruction for what to do in this step.
- "reasoning_module": The adapted reasoning module this step is based on.

Make sure the steps flow logically — later steps can build on earlier ones.
The final step should synthesize everything into a conclusion or answer.

Example format:
{{
  "step_1": {{
    "instruction": "Identify the core variables ...",
    "reasoning_module": "Adapted module text ..."
  }},
  "step_2": {{
    "instruction": "Break the problem into ...",
    "reasoning_module": "Adapted module text ..."
  }}
}}

Return ONLY the JSON object, no extra commentary.
"""

SOLVE_PROMPT = """\
You are given a reasoning structure (a step-by-step plan) and a specific
problem to solve. Follow the structure carefully, filling in each step with
your reasoning applied to the problem.

Reasoning structure:
{structure}

Problem to solve:
{problem}

For each step in the structure, write out your reasoning under that step.
After completing all steps, provide your final answer.

Format your response as a JSON object with two keys:
- "reasoning_trace": A string containing your full step-by-step reasoning
  (include the step labels so it's easy to follow).
- "answer": A string containing your final, concise answer.

Return ONLY the JSON object, no extra commentary.
"""

NAIVE_PROMPT = """\
Solve the following problem step by step:

{problem}

Think through the problem carefully, show your reasoning, and then provide
your final answer.

Format your response as a JSON object with two keys:
- "reasoning": A string containing your step-by-step reasoning.
- "answer": A string containing your final, concise answer.

Return ONLY the JSON object, no extra commentary.
"""
