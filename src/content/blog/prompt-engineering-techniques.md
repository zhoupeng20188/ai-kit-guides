---
title: "Prompt Engineering: Define Inputs, Constraints, and Checks"
description: "Write prompts that preserve facts and expose missing context. Use examples, output contracts, and verification instead of unsupported performance promises."
pubDate: 2026-06-24
category: "ai-models-basics"
tags: ["prompt-engineering", "chatgpt", "claude", "techniques"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
updatedDate: 2026-10-23
---

Prompt engineering is useful when it reduces ambiguity about a task. It cannot turn missing evidence into a fact or guarantee that a plausible answer is correct.

This guide uses synthetic examples. Earlier claims that a prompt formula doubled quality, changed “temperature” through wording, or reliably revealed internal reasoning have been removed.

## Start with an input and an acceptance condition

For a documentation update, specify the source facts and what must remain unchanged. For code, specify the behavior, runtime, and verification. A role label can set tone; it does not give the model real professional experience.

```text
Input: the supplied build instructions and error log.
Task: propose the next diagnostic step.
Constraints: do not change dependency versions or invent missing output.
Output: observation, possible causes, one check, and the result that would
support or contradict each cause. State missing inputs explicitly.
```

The model still needs review. An answer in the requested format can contain incorrect facts.

## Use examples to clarify a contract

A few examples can show an output shape or a boundary. Include a contrasting case when it distinguishes the rule. For a discount beginning at 100.00, values below, at, and above the threshold matter more than three similar happy-path inputs.

The [JUnit guide](/blog/ai-junit-tests/) and [Java verification project](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/java-verification) make that boundary executable. Do not describe invented examples as production measurements.

## Separate source material from instructions

A document can contain quoted requests, code, or text that looks like a command. State which material is data to analyze and which requirements govern the task. For document-only questions, require a supporting passage and an explicit “not established” answer when the source is silent.

For research, ask for primary sources and open them. A generated citation is a lead to inspect, not proof.

## Ask for a useful explanation

Request a concise rationale, assumptions, alternatives when relevant, and verification steps. Do not demand hidden internal reasoning or assume a longer explanation is more accurate.

OpenAI's [prompting documentation](https://developers.openai.com/api/docs/guides/prompt-engineering) describes task and context design. The effective method depends on the model and task; measure changes on representative inputs rather than repeating a universal technique ranking.

## Make output constraints concrete

For extraction, define fields, types, units, and how missing values are represented. For a draft, define audience, facts, length, and prohibited invention. For an agent task, define allowed scope and the artifact needed for review.

“Be factual” is less testable than “use only these three facts; do not invent a cause or a date.” Likewise, telling a model to be creative is not equivalent to changing an API temperature parameter, which may be unavailable or behave differently by model.

## Iterate against the same checks

Change one important instruction at a time and compare outcomes on the same inputs. Record factual errors, missing cases, correction effort, and usability. A self-rating out of ten is not an accuracy measurement.

A second assistant can suggest a critique, but agreement is not independent verification. The [hallucination guide](/blog/ai-hallucination-tips/) covers primary-source and runtime checks; the [comparison worksheet](/blog/claude-vs-chatgpt-2026/) supplies a simple rubric.

## Move mandatory controls outside the prompt

If a task can change files, call services, or spend money, instructions need an execution environment that enforces scope and records outcomes. Use permissions, validators, budgets, and recovery behavior appropriate to the workflow.

The [harness guide](/blog/harness-engineering/) covers those controls, while the [loop guide](/blog/loop-engineering/) covers repetition and stopping. A well-designed prompt gives an assistant the right job; independent evidence establishes whether it completed that job.
