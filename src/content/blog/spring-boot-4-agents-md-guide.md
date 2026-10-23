---
title: "Spring Boot 4 AGENTS.md: A Migration Verification Template"
description: "A Boot 4 instruction template that checks dependencies, property binding, test discovery, and security without treating green builds as proof."
pubDate: 2026-10-16
category: "ai-coding-agents"
tags: ["agents.md", "spring boot 4", "ai coding agents", "codex", "java ai tools", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["agents.md spring boot 4", "spring boot 4 agents.md rules", "ai agent silent failure spring boot 4", "agents.md example spring boot", "codex agents.md spring boot 4", "spring boot 4 migration agents.md"]
updatedDate: 2026-10-23
---

A Spring Boot 4 `AGENTS.md` should describe what must remain true after a change. “Make Maven green” leaves room for a resolving dependency that never activates, an undiscovered test, or a changed business rule.

This template is an editorial reconstruction from AI-built lab scenarios and official references. The original agent transcripts were not retained, so earlier model success ratios and exact run totals are not evidence of repeatable performance.

## Adapt the template to your build

```markdown
# Spring Boot migration instructions

## Baseline
- Read the wrapper, build files, active profiles, and module instructions.
- Record the exact Boot, Java, test-engine, and build-plugin versions.
- Preserve unrelated changes and existing database migration history.

## Definition of done
- Run the repository's documented verification task and preserve its exit code.
- Inspect fresh test reports: discovery, execution, failures, and skips.
- Check expected test suites, not equality between source files and test methods.
- State checks blocked by missing services, credentials, or network access.

## Dependencies and configuration
- Check the Boot migration guide for the feature's integration module or starter.
- Prove the relevant bean or behavior is active, not only that Maven resolves.
- Verify important configuration with a binding or behavioral test.
- Keep diagnostic actuator endpoints local and restricted.

## Behavior and security
- Preserve the documented business requirement when tests disagree.
- Do not weaken, disable, or silently exclude tests to obtain success.
- Verify ownership, method security, and CSRF with the security chain active.
- A stateless session policy alone does not justify a CSRF exemption.
- Require explicit justification for dependency, security, and schema changes.

## Completion record
- Report the diff, checks, executed and skipped test totals, and limitations.
- Do not use the agent process exit status as the build result.
```

Use the [AGENTS.md discovery guide](/blog/codex-agents-md-spring-boot/) to place this file correctly. Version and command values come from the repository, not from the example.

## Prove the feature is active

Boot 4 modularization changes where integration and auto-configuration live. A library on the classpath can be useful without being the Boot integration required by a particular task. Consult the [official migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide), then verify the behavior: a migration applies, a client builder exists, or the expected endpoint starts.

The [dependency guide](/blog/codex-spring-boot-4-dependencies-silent-failures/) separates resolution from activation. Do not turn “prefer the appropriate starter for this Boot feature” into “third-party libraries are never valid dependencies.”

## Check binding and exposure separately

Configuration metadata helps tools describe known properties. Its presence does not prove an active bean consumed a value, and its absence does not prove runtime rejection. Use a focused binding or behavior test for the key that matters. The [YAML guide](/blog/codex-spring-boot-4-yml-properties/) explains that distinction.

An actuator `configprops` response may help in a local diagnostic environment, but it is not the only valid check. Do not expose sensitive diagnostic endpoints publicly merely to make an agent's investigation convenient.

## Check the intended suite

One source file can contain helpers, nested tests, parameterized tests, or multiple cases. Source-file count is not an executed-test count. A grep for skipped tests also misses undiscovered tests and can read stale output.

Require the correct suite and inspect fresh reports. Bind Failsafe when the project relies on its integration-test naming convention; `verify` alone does not invent that configuration. Use the [Surefire guide](/blog/ai-junit-tests-not-running-spring-boot-4/) and [Gradle guide](/blog/gradle-build-successful-zero-tests-spring-boot-4/) for runner-specific checks.

## Keep the business requirement visible

If a test says a discount starts above 100 but the specification says at or above 100, the conflict needs a decision based on the authoritative requirement. A prompt cannot infer a rule missing from every available source.

Keep the requirement and its boundary examples in the repository. Require the agent to identify which changed when it fixes a failure. The [CI contract example](/blog/codex-ci-spring-boot-green-build/) shows how code and tests can agree while the intended rule is lost.

## Verify security behavior

A successful response from a MockMvc test proves little about security if the security filters were never applied. Confirm the chain, then test both allowed and rejected requests. Preserve CSRF protection for browser-authenticated flows unless the threat model supports an exemption; HTTP Basic can still involve automatically sent credentials.

The [security migration case](/blog/claude-code-spring-boot-4-403/) and [method-security guide](/blog/claude-code-spring-boot-4-preauthorize/) cover those checks. Keep final review independent of the agent's completion summary. The [Java hub](/blog/ai-for-java-developers/) organizes the related guides.
