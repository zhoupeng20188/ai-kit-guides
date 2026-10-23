---
title: "Harness Engineering: Make Agent Work Verifiable"
description: "Design the environment around an AI coding agent: clear task contracts, constrained tools, independent checks, and a handoff with inspectable evidence."
pubDate: 2026-07-07
category: "ai-coding-agents"
tags: ["harness engineering", "ai agents", "prompt engineering", "claude code", "cursor"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["harness engineering", "what is harness engineering", "harness engineering vs prompt engineering", "ai agent reliability"]
updatedDate: 2026-10-23
---

An AI coding agent needs a working environment that turns a request into changes someone can inspect. In this guide, a **harness** means that surrounding environment: repository context, available tools, permissions, execution limits, checks, and reporting. This is a practical design framework, not a claim that every product uses this terminology identically.

The useful question is concrete: after an agent says it fixed a Java bug, what allows another person to establish that the requested behavior changed without unrelated damage?

## Start with a task contract

Consider a teaching example: orders belonging to another user must not be returned by an order lookup. A useful contract states the entry point, trusted identity source, required behavior, allowed files, and verification commands. It also specifies what must remain private in logs.

```text
Task: scope order lookup to the authenticated owner.
Identity: derive it from the server-side principal, not request JSON.
Acceptance: owner succeeds; another owner and anonymous requests fail.
Scope: lookup path and its tests; report other exposed paths separately.
Evidence: changed files, test cases executed, command status, limitations.
```

This is an illustrative contract. A real endpoint also needs decisions about authorization, error responses, caches, list/search paths, and persistence. The [API security guide](/blog/claude-code-insecure-api-spring-boot/) develops those questions. Ambiguous business policy should remain an explicit question, not an invented assertion in a generated test.

## Separate guidance from enforcement

Repository instructions help an agent choose relevant code and commands. They do not enforce filesystem access or prevent a process from using credentials. Configure those controls in the actual tool environment. OpenAI's [agent approvals and security documentation](https://learn.chatgpt.com/docs/agent-approvals-security) describes its product's controls; other agents require their own configuration.

Build the environment in layers:

| Layer | Concrete decision | Evidence to keep |
| --- | --- | --- |
| Context | Which instructions and source files apply? | Paths and resolved task scope |
| Execution | Which JDK, wrapper and services are available? | Version output and setup failures |
| Authority | What can run, write, or use credentials? | Actual configured permissions |
| Validation | What detects the requested defect? | Test identity and report |
| Recovery | How can the work be inspected or reverted? | Diff and isolated working copy |

Do not put secrets into the context merely because the task needs a network connection. A process can receive narrowly configured access without copying credential values into prompts or reports. The [sandbox diagnosis guide](/blog/codex-sandbox-maven-spring-boot/) distinguishes access problems from application failures.

## Design a check that can fail for the right reason

A command returning zero is useful only if it ran the relevant check. Confirm test discovery and examine the assertions. For the order example, an owner-only success test misses the defect: the meaningful negative case requests the same order as another authenticated user.

The [Java verification project](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/java-verification) contains a small owner-scoped lookup and negative tests. It is an educational fixture, not a Spring Security application. Its README states the versions and observed results. Use it to inspect what a check establishes, then add the appropriate HTTP and persistence tests to your actual service.

Independent CI should obtain the changed revision and run its own checks. Require review for changes to tests and gate configuration, since an agent able to edit a gate can also weaken it. Keep expected behavior outside the agent's success summary; see [test and architecture gates](/blog/ai-code-ci-gates-archunit-spotless/).

## Bound the work and hand it off

Set a time or action budget and stop conditions for missing credentials, repeated identical failures, unclear requirements, and changes outside scope. Do not turn an infrastructure outage into an unlimited edit cycle. [Bounded agent loops](/blog/loop-engineering/) discuss the execution mechanism separately.

A useful final handoff names the revision, changed behavior, checks executed, failures, and unverified assumptions. Save raw reports where possible. If no execution occurred, say so. These artifacts allow the next person to continue the work without treating the agent's narrative as a test result.
