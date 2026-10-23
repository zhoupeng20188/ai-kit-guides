---
title: "Claude Code Subagents and Hooks: Scope Java Review Tasks"
description: "Use a small read-oriented subagent and verified hook behavior. Keep instructions, tool permissions, and operating-system boundaries distinct."
pubDate: 2026-08-12
category: "ai-coding-agents"
tags: ["claude code", "claude code subagents", "claude code hooks", "spring boot", "ai coding", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["claude code subagents spring boot", "claude code hooks spring boot", "claude code guardrails", "claude code agents java", "claude code spring boot advanced"]
updatedDate: 2026-10-23
---

Claude Code subagents can separate a focused investigation from the main conversation. Hooks can run checks at documented lifecycle events. Neither should be described as “zero-cost guardrails” or a complete sandbox.

This guide replaces unsupported production anecdotes with a small configuration and acceptance checklist. Follow the [subagent reference](https://code.claude.com/docs/en/sub-agents) and [hook reference](https://code.claude.com/docs/en/hooks) for the installed version.

## Give the subagent one review question

An illustrative `.claude/agents/java-reviewer.md`:

```markdown
---
name: java-reviewer
description: Review a Java change for concrete behavior and missing evidence.
tools: Read, Grep, Glob
---

Read the requested diff and relevant callers.
For each finding, identify the trigger, affected symbol, consequence, and check.
Distinguish observed defects from assumptions requiring more context.
Do not claim a build or test ran when no execution evidence is available.
Return concise findings and remaining questions.
```

The example limits the declared tools to reading and search. Check the product's actual capability and permission behavior; a prompt saying “read only” by itself does not enforce access boundaries.

## Supply the relevant contract

For an orders change, include ownership, response policy, transaction expectations, and the actual test command. Ask the subagent to investigate a narrow concern, such as whether a lookup is scoped to the authenticated user.

Do not treat a second model's agreement as independent proof. Both agents can work from the same incomplete requirement or incorrect retrieved context. Check findings against code and executable behavior.

## Keep shared-workspace edits deliberate

Parallel agents that edit the same files can overwrite or conflict with each other. Define file ownership or isolate work where edits are necessary. A review-only subtask avoids that particular mutation risk but still consumes requests and context.

Report the source paths and limits of the review. A subagent that cannot run the build should say so; the main workflow still owns verification.

## Use hooks for documented events

Choose the lifecycle event corresponding to the check. For a pre-tool check, parse the documented input schema and verify the tool name and arguments. Confirm the exit or structured-result behavior for that event; a nonzero shell status does not have the same meaning at every hook stage.

Avoid advertising a regular expression for `rm -rf` as comprehensive command safety. Shell syntax, indirect execution, scripts, and other tools create additional paths. Use product permissions and OS isolation for stronger restrictions.

## Test the hook itself

In a disposable workspace, test a harmless allowed operation, a harmless operation expected to be denied, malformed input, and a checker failure or timeout. Check what the parent agent sees and whether the intended action executed.

For a post-edit verification hook, ensure its output preserves the build failure and does not misreport a skipped or undiscovered suite as success. The [CI gate guide](/blog/ai-code-ci-gates-archunit-spotless/) describes positive and negative fixtures for checks.

## Retain one acceptance owner

The main task should collect findings, inspect the complete diff, and run the intended verification. Use the [Claude Code workflow](/blog/claude-code-spring-boot/) and [project memory guide](/blog/claude-code-remember-spring-boot/) for the surrounding setup.

The [JUnit guide](/blog/ai-junit-tests/) covers assertion quality; the [Java hub](/blog/ai-for-java-developers/) connects related scenarios. Delegation helps manage work, while explicit evidence establishes completion.
