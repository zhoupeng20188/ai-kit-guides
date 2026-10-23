---
title: "Claude Code Memory for Spring Boot: Instructions and Verification"
description: "Keep stable Spring Boot instructions separate from local setup notes and remembered observations. Check what loaded and verify facts before reusing them."
pubDate: 2026-08-19
category: "ai-coding-agents"
tags: ["claude code", "spring boot", "claude code remember", "java ai tools", "claude code setup", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["claude code remember", "claude code spring boot", "claude code CLAUDE.md", "spring boot ai coding", "claude code setup", "claude code project context"]
updatedDate: 2026-10-23
---

Claude Code memory for a Spring Boot repository should reduce repeated setup without turning an old observation into a permanent fact. Build versions, profiles, and permissions can change after a note was written.

This is a maintenance guide, not a report of months of personal production use. It separates instructions you own from observations that need to be checked again.

## Choose the right home for a fact

Claude's [memory documentation](https://code.claude.com/docs/en/memory) distinguishes persistent project instructions from auto memory. The details of loading and scope depend on the installation. Check the files actually loaded when diagnosing a session.

Put stable conventions in a project instruction file: the wrapper command, module boundaries, generated-code paths, and acceptance requirements. Put machine-specific setup in an appropriately excluded local file or environment configuration. Put a reproducible failure report in the issue or a versioned technical note with its date and versions.

A remembered sentence saying “Docker is unavailable” should not silently become “skip integration tests forever.” Recheck availability for the current environment and report a blocked check separately.

## Use a short project entry point

```markdown
## Build context
- Read the checked-in wrapper and build files for exact versions.
- Run the documented verification task from the correct module/root.
- Do not edit generated output or applied migrations.

## Change review
- Preserve ownership and business rules at the service boundary.
- Record the acceptance requirement before changing an assertion.
- Inspect executed and skipped tests, not only the final build message.

## References
- Architecture and module commands: docs/development.md
- Environment setup: README.md
```

The reference paths are examples: create or replace them with real project documentation. An instruction file full of dead links is worse than a concise file that points to the actual build.

Avoid embedding credentials, production URLs with secret parameters, or copied customer payloads. Excluding a file from an index does not necessarily prevent a command-line tool from reading it.

## Review what survived into a new session

Ask for the loaded instruction sources and the proposed build command. Compare the answer with the repository. A correct summary of an instruction is only evidence that it was available; the final diff and checks establish whether it was followed.

When the agent recalls a previous migration conclusion, check the version and reproduction. A property that was inactive without a JDBC module may work after the module is added. The [Boot 4 YAML guide](/blog/codex-spring-boot-4-yml-properties/) explains why classpath and binding belong together.

## Resolve conflicting instructions explicitly

Inspect user, project, module, local, and managed configuration using the current [settings documentation](https://code.claude.com/docs/en/settings). Do not assume that every list replaces a previous list or that all tools use the same precedence rules.

Keep a single canonical statement of a business rule. If a local note disagrees with the requirement and tests, resolve the conflict before editing code. Repeating the same wrong instruction in several files does not make it more authoritative.

For cross-tool instructions, see [AGENTS.md scope](/blog/codex-agents-md-spring-boot/). Verify each tool's support rather than assuming a symlink shares every local override.

## Maintain observations as observations

A useful troubleshooting note records the symptom, environment, command, output, proposed explanation, and verification step. Keep the observed fact separate from the explanation. “Connection to this socket was denied in this profile” is narrower and more reusable than “Testcontainers is broken.”

When later testing disproves an explanation, update the articles and instruction snippets that cite it. Leaving the correction only in private memory preserves the mistake for readers.

Use the [Claude Code workflow](/blog/claude-code-spring-boot/) for task execution, the [Boot 4 instructions](/blog/spring-boot-4-agents-md-guide/) for acceptance checks, and the [Java hub](/blog/ai-for-java-developers/) for related scenarios. Persistent context should make the next investigation easier; executable checks still establish the result.
