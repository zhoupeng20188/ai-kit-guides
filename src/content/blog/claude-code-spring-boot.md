---
title: "Claude Code with Spring Boot: A Verifiable Repository Workflow"
description: "Set up a Claude Code task around your Spring Boot build, project instructions, scoped changes, and checks that establish what actually ran."
pubDate: 2026-07-31
category: "ai-coding-agents"
tags: ["claude code", "spring boot", "ai coding", "java ai tools", "claude code workflow", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["claude code spring boot", "claude code with spring boot", "claude code spring boot tutorial", "ai coding spring boot", "spring boot ai workflow"]
updatedDate: 2026-10-23
---

Claude Code with Spring Boot is most useful when a repository task ends in a reviewable patch and a verification record. A controller that compiles is only part of that result: wiring, authorization, persistence, and test discovery still need checks.

This article is an operational guide. It replaces unsupported personal time-saving stories and fixed model recommendations with a concrete workflow you can apply to your own project.

## Start with the repository's environment

Follow the [Claude Code setup documentation](https://code.claude.com/docs/en/overview) for your platform and authentication choice. Inspect the installed CLI and establish the Java baseline:

```bash
claude --version
java -version
./mvnw -version
./mvnw -B verify
```

For Gradle, use the repository's Gradle wrapper and verification tasks. Record an existing failure before asking the agent to edit anything. Check whether the required JDK, Maven mirror, database, and container runtime are available in the same environment where the agent runs commands.

Avoid choosing a model solely from a dated tutorial. Record the selected model and account restrictions for a particular run. A subscription, API provider, CLI version, and selected model are separate inputs to a comparison.

## Put stable instructions in CLAUDE.md

Claude documents persistent instructions in its [memory guide](https://code.claude.com/docs/en/memory). Keep a short file covering decisions that cannot be inferred reliably from one source file:

```markdown
## Repository contract
- Read the build and nearby code before changing versions or dependencies.
- Controllers call services; services enforce authorization and business rules.
- Match existing DTO, mapper, and exception conventions.
- Preserve unrelated edits and applied database migrations.

## Acceptance
- Use the repository wrapper and documented verification task.
- Report executed and skipped tests, not only BUILD SUCCESS.
- Do not weaken assertions or change business rules to hide a failure.
- State blocked checks and remaining assumptions explicitly.
```

Adapt this template to the actual project. Boundary validation in a request DTO does not eliminate the need for service-level business invariants: a scheduled job or another service may bypass the controller entirely.

Instruction text is context, not an enforcement mechanism. See [permissions](https://code.claude.com/docs/en/permissions) for the controls your installation supports. A sentence saying “never edit secrets” is not equivalent to preventing access to them.

## Explain the change before requesting edits

Ask the agent to identify the entry point, the service method, callers, data access, and relevant tests. Require paths or symbols you can verify. If it names an absent bean or assumes a profile that is inactive, resolve that misunderstanding before editing.

A bounded example is a paginated orders endpoint:

> Use the existing repository and mapper. Return only the authenticated user's orders. Preserve the response contract and maximum page size. Define deterministic sorting. Cover an owner, another user, an empty result, and pagination boundaries. List any assumptions before modifying security or dependencies.

This is an illustrative task brief, not a report of a timed model trial. The acceptance conditions matter more than whether the first output looks idiomatic.

## Review the tests as part of the patch

A generated test should fail when the intended behavior is broken. Inspect actual assertions, mock boundaries, fixtures, and discovery. An assertion that the response is non-null cannot establish ownership or page order.

Run the focused tests during iteration and the project verification task before review. Read test reports to distinguish executed, skipped, filtered, and undiscovered cases. The [JUnit guide](/blog/ai-junit-tests/) covers assertion quality; the [Surefire guide](/blog/ai-junit-tests-not-running-spring-boot-4/) covers discovery.

For a security test, confirm the Spring Security filter chain is actually installed. A manually assembled MockMvc without security integration can produce a misleading success even though the application would reject the request.

## Keep the final review independent

Inspect build files, security configuration, database migrations, and changed tests separately. Ask what changed in the contract, not only whether the command finished successfully. Record a verification result with its command and environment; if Docker is unavailable, say the integration check was blocked rather than quietly disabling it.

A transaction listener is another place where a plausible patch can conceal a missing guarantee. The [AFTER_COMMIT case](/blog/claude-code-after-commit-email-loss/) explains why a successful database commit does not by itself establish durable notification delivery. The [ownership example](/blog/claude-code-insecure-api-spring-boot/) covers record-level authorization.

For configuration maintenance across sessions, use [project memory](/blog/claude-code-remember-spring-boot/). For the migration-specific acceptance surface, use the [Boot 4 guide](/blog/spring-boot-4-migration-ai-agents/). The [Java hub](/blog/ai-for-java-developers/) connects the full workflow.
