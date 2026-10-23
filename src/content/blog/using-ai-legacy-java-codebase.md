---
title: "Using AI in a Legacy Java Codebase: Preserve Behavior First"
description: "Map callers, capture current contracts, and make small reviewed Java changes with AI when tests and business documentation are incomplete."
pubDate: 2026-07-22
category: "java-ai-tools"
tags: ["legacy java", "ai coding", "claude code", "legacy code refactoring", "java ai tools", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["ai legacy java code", "using ai on legacy code", "claude code java", "ai refactoring legacy java", "ai change old code"]
updatedDate: 2026-10-23
---

The difficult part of changing legacy Java is often deciding which existing behavior is a requirement. An AI tool can trace callers and suggest tests, but it cannot infer the correct business policy from inconsistent code alone. Start by preserving what is understood and recording what still needs a decision.

This is a workflow with illustrative examples, not a report of a production refactoring. It applies whether the assistant runs in an editor or a terminal; see the [Java and AI guide index](/blog/ai-for-java-developers/) for tool-specific setup.

## Map one execution path

Choose a small change and identify its public entry points, callers, persistence, transaction boundary, and external side effects. Ask the assistant to name source paths and symbols for every claimed relationship. Check those references before accepting the map.

For example, a service might be called by a web controller, a scheduled task, and an import job. Converting every exception to an HTTP response inside that service could satisfy the controller while breaking background callers. That is a hypothetical design conflict worth resolving before editing.

Build a short contract record:

| Question | What to record |
| --- | --- |
| Who calls this method? | Actual callers and adapters, including jobs and message handlers |
| What happens for missing data? | Existing return values or exceptions and caller expectations |
| Which effects occur? | Database writes, messages, emails, files, or remote calls |
| Which context is assumed? | Principal, tenant, locale, time zone, transaction, or thread state |
| What remains unknown? | A decision needed from a maintainer or domain owner |

A comment is evidence of intent, not proof of actual behavior. Inspect code and tests together. When behavior is clearly defective, capture it as a known defect rather than silently promoting it into a permanent requirement.

## Add characterization before general cleanup

Characterization tests record the current behavior of a selected seam. Use them to protect the path you intend to preserve, then write a failing test for the specific change requested. Keep these purposes distinct so a generated test does not merely encode the new implementation.

Useful examples include an exact discount boundary, a missing order, an existing null value, a timestamp around a time-zone transition, and a downstream exception. The right cases come from the contract, not from a demand for a particular test count. The [Java verification project](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/java-verification) contains a small inclusive discount boundary and owner-scoped lookup; it is a teaching project, not a characterization of your application.

Run the selected tests against the original code where feasible, save the result, and then make the targeted change. If a test never fails when the defect is present, examine whether it reaches the real code. [JUnit discovery checks](/blog/ai-junit-tests-not-running-spring-boot-4/) help distinguish an absent test from a passing assertion.

## Refactor through a narrow seam

A useful task for an assistant is extracting a pure calculation while retaining the existing public method and adapters. A much riskier task is simultaneously changing exceptions, persistence, transaction propagation, and return types.

For a small change, require the agent to show:

1. The entry points affected and the intended behavioral difference.
2. Tests protecting callers and covering the new behavior.
3. A diff without unrelated renaming or formatting churn.
4. The exact checks executed and any unavailable service.

Review Spring proxy boundaries separately. Moving a transactional method or invoking it through self-invocation can affect how advice is applied; consult the [Spring transaction reference](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html). Similar care is needed for security advice. See [method authorization](/blog/claude-code-spring-boot-4-preauthorize/).

## Preserve the path to rollback and review

Keep changes small enough that a reviewer can connect each edit to its contract. Separate a behavior change from a framework migration unless they must be coordinated. Record the baseline revision and environment, especially when an old JDK or database version is needed to reproduce behavior.

If integration tests cannot run locally, report that limitation and require the relevant CI result before treating the work as complete. Do not replace a database check with a mock and describe it as equivalent. [Independent CI gates](/blog/ai-code-ci-gates-archunit-spotless/) can preserve that distinction after the assistant leaves the task.
