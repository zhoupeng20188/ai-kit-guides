---
title: "AI Hallucinations in Code: Check APIs, Versions, and Evidence"
description: "Catch invented APIs and unsupported claims with version-specific documentation, compilation, runtime checks, and explicit uncertainty."
pubDate: 2026-07-08
category: "ai-models-basics"
tags: ["ai hallucination", "reduce ai hallucinations", "chatgpt make things up", "ai code hallucination", "prompt engineering"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["ai hallucination", "why does ai make things up", "how to reduce ai hallucinations", "stop ai hallucinations", "ai makes things up"]
updatedDate: 2026-10-23
---

An AI hallucination in code can be a nonexistent API, a wrong version claim, or an explanation that the supplied evidence does not support. The most useful response is to identify a claim and choose a check that can disprove it.

This guide uses synthetic examples. The previous billing-system production incident was not supported by retained evidence and has been removed.

## Check the API against the intended release

The earlier article incorrectly said `Files.readString(Path)` arrived in Java 12 and would fail on Java 11. The [Java API reference](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/file/Files.html#readString(java.nio.file.Path)) identifies it as available since Java 11.

Compile against the intended release, not merely the JDK installed on your laptop. A method can compile with a newer API and fail on a deployment using an older library. A runtime `NoSuchMethodError` is a linkage symptom; it is not by itself proof that a model invented the method.

## Supply the actual context

If a query depends on an entity or schema, provide the relevant fields and mapping. If an answer depends on a dependency version, provide the resolved version. Redact credentials and customer content before sharing snippets.

A prompt saying “a user table” leaves names and constraints unspecified. A model can fill those gaps plausibly. Ask it to state missing inputs instead of inventing columns, constraints, or business rules.

## Use checks with different strengths

Compilation can reject an unavailable method or incompatible type. It cannot establish object-level authorization, transaction intent, or the correctness of a value read from a document.

Tests can observe behavior only when they execute and assert the relevant contract. The [JUnit guide](/blog/ai-junit-tests/) and [discovery guide](/blog/ai-junit-tests-not-running-spring-boot-4/) cover those limits. A passing test with no meaningful assertion is weak evidence, not a stronger kind of confidence.

## Ask for sources you can inspect

For a factual API claim, ask for the version-specific reference and relevant symbol. Open the source and confirm it supports the statement. A generated URL or a quote that looks official may itself be wrong.

For a document summary, require a section and supporting passage. Include a question the source does not answer. A good response should preserve that absence rather than supply a convenient default.

## Use another model to find disagreements

A second assistant can suggest checks or surface a contradiction. Agreement does not establish truth: both can share incomplete context or the same plausible error. Use a compiler, primary source, database, or actual observation where the claim permits it.

The [Claude/ChatGPT worksheet](/blog/claude-vs-chatgpt-2026/) supplies comparable tasks. It does not treat a model's self-score as a measured accuracy result.

## Constrain the deliverable

State input, expected output, allowed dependencies, version, and failure behavior. Ask for a concise rationale, assumptions, and verification commands. Do not assume that requesting a long explanation reveals the model's internal process or improves every task.

An instruction saying “do not hallucinate” is not an execution check. Use the [prompt guide](/blog/prompt-engineering-techniques/) for concrete task contracts and the [harness guide](/blog/harness-engineering/) for validation outside the prompt.

## Record uncertainty honestly

Distinguish a documented feature, a synthetic example, an AI-produced lab note, and a result you actually reran. Retain the source and output before publishing numerical results. If evidence is missing, narrow the claim.

The purpose is to make errors cheap to detect. A confident tone is neither a reason to accept nor automatically reject an answer; the checkable evidence decides.
