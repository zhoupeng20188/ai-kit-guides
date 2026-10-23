---
title: "AGENTS.md for Spring Boot: Discovery, Scope, and Local Overrides"
description: "Configure Codex project instructions without confusing nested scope, local overrides, permissions, or verification of a Spring Boot change."
pubDate: 2026-08-28
category: "ai-coding-agents"
tags: ["openai codex", "agents.md", "spring boot", "codex spring boot", "java ai tools", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["agents.md spring boot", "codex agents.md", "openai codex spring boot", "agents.md example", "spring boot ai coding"]
updatedDate: 2026-10-23
---

An `AGENTS.md` for Spring Boot should answer three questions: which project is this, which checks establish the requested behavior, and which changes need extra review? It should not become a replacement for the build or a place to store credentials.

This page explains instruction discovery and scoping. The [Boot 4 instruction template](/blog/spring-boot-4-agents-md-guide/) covers migration-specific acceptance checks. Neither is a benchmark of instruction effectiveness.

## Check what the installed tool loads

OpenAI's [instruction-file guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md) describes Codex's discovery order, nested instructions, overrides, and size limits. Inspect the applicable files before editing a module. A deeper file can specialize inherited guidance; it does not mean the root guidance disappears entirely.

`AGENTS.override.md` is an override filename, not automatically a private or ignored file. If you use one for personal settings, explicitly exclude it from version control and check its scope. Do not use it to silently omit required integration tests; describe unavailable checks in the completion record instead.

## Keep the root file useful

The following is an example for a Maven repository. Replace paths and commands with facts from your build:

```markdown
# Repository instructions

## Build and verification
- Read pom.xml, the wrapper, and the relevant module instructions first.
- Use ./mvnw -B verify for the final check.
- Use the documented focused-test command during iteration.
- Report executed, failed, and skipped tests and any environmental blocker.

## Changes
- Preserve unrelated working-tree edits.
- Controllers delegate to services; services enforce business invariants.
- Do not alter applied database migrations.
- Generated files are outputs; update the source generator or template.
- Do not change a business rule just to agree with a failing assertion.

## Evidence
- Identify the acceptance requirement and the test that demonstrates it.
- Review build files, security configuration, and changed tests explicitly.
- A successful agent exit is not the application's verification result.
```

A `package -DskipTests` command may be useful for packaging, but should not be called test verification. Likewise, a passing focused test is narrower evidence than the full verification task.

## Scope module instructions deliberately

In a multi-module repository, root instructions can describe shared tooling while module files describe module-specific commands or data contracts. Check the current working directory and the file being edited; a task launched from a subdirectory may load a different instruction chain from one launched at the root.

Ask the agent to summarize which instructions apply before changing a sensitive module. Verify a concrete behavior, such as its chosen focused-test command, rather than accepting a claim that it read everything.

For instruction files shared across tools, check each tool's current documentation. [Claude Code's memory guide](https://code.claude.com/docs/en/memory) documents its own `CLAUDE.md` and `AGENTS.md` support. A symlink can be a maintenance choice, but it is not proof that both tools interpret scope, overrides, or loading identically.

## Replace vague rules with observable checks

“Use good security” gives a reviewer little to inspect. “An order lookup must be scoped to the authenticated owner; test a second authenticated user” identifies a behavior. “Never break migrations” becomes more useful when it specifies an upgrade test against a database with existing migration history.

Avoid rules that contradict each other. “Never change production code to match a test” and “tests are always the source of truth” cannot resolve a conflict between a wrong test and a documented requirement. Name the rule of record and require a report when evidence disagrees.

The [CI contract guide](/blog/codex-ci-spring-boot-green-build/) covers that conflict. The [Flyway guide](/blog/flyway-checksum-mismatch-ai-agent/) covers existing database history.

## Keep enforcement outside prose

An instruction file is guidance. A model can misunderstand it, context can be incomplete, and an authorized task can change its scope. Use permissions for access restrictions and independent CI for mandatory checks. Do not assume a file saying “do not read secrets” removes access to secrets.

Trial the file on a small change, inspect the diff, and record missing or ambiguous guidance. Revise it from actual failures instead of copying a large template whose commands do not match your repository. Start the agent workflow from the [Codex setup guide](/blog/codex-spring-boot/) and use the [Java hub](/blog/ai-for-java-developers/) for related checks.
