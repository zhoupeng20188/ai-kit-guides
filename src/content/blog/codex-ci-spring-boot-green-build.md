---
title: "Codex in CI: Verify the Build and Preserve the Business Rule"
description: "Separate an agent process result from application acceptance. Preserve build exit codes, inspect fresh test reports, and resolve tests-versus-spec conflicts."
pubDate: 2026-09-21
category: "java-testing-ci"
tags: ["openai codex", "spring boot 4", "ci cd", "github actions", "maven", "ai coding agents", "java testing", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["codex in ci", "codex exec exit code", "codex github actions spring boot", "ai agent changed business rule", "codex tests pass but wrong", "codex ci spring boot", "agents md ci rules", "maven green build zero tests"]
updatedDate: 2026-10-23
---

A successful Codex process is not an application acceptance result. A CI job needs an independent build check and an explicit behavioral contract. Do not interpret a completed agent turn as proof that the patch compiles or preserves the requirement.

Earlier versions presented a seven-run score as a general property of the CLI. The original transcripts were not retained. This revision uses a concrete boundary example and a verification procedure rather than claiming the agent always exits zero; tools can fail for many reasons.

## Put the requirement beside the change

Suppose a discount begins at 100.00 **inclusive**. The implementation uses `>=`, while a failing test incorrectly expects no discount at exactly 100.00. Changing the implementation to `>` can produce a green test and a wrong product.

The [downloadable Java sample](/examples/java-verification.zip) includes the inclusive rule and boundary assertions. Its purpose is to make the contract inspectable, not to reproduce a historical model response.

When tests and prose disagree, identify the authoritative requirement before editing either. Require the completion summary to name whether production behavior, a test, or a documented contract changed. Do not write conflicting instructions such as “the test is always truth” and “never change code to match a wrong test.”

## Preserve the build exit status

A pipeline that pipes a build into `tee` or `grep` can accidentally use the last command's status. In Bash, preserve pipeline failure:

```bash
set -euo pipefail
./mvnw -B clean verify 2>&1 | tee verify.log
```

Use this only when `clean verify` is appropriate for the project. The command is a build step, not an agent instruction. Configure the shell explicitly in CI, because `pipefail` is not available in every shell.

Run the check after the patch is prepared. Keep the agent's exit status, build status, and acceptance result as separate observations. A correct refusal to modify code can leave an intentionally failing requirement-conflict test; report that state rather than manufacturing success.

## Inspect fresh reports

Read the expected Surefire and Failsafe suites from the current run. Confirm execution counts, failures, errors, and authorized skips. A zero-skip grep cannot detect a class that was never discovered, and a nonzero total cannot establish that every required suite ran.

Use the [Maven discovery guide](/blog/ai-junit-tests-not-running-spring-boot-4/) or [Gradle reuse guide](/blog/gradle-build-successful-zero-tests-spring-boot-4/) for the relevant runner. The [JUnit guide](/blog/ai-junit-tests/) explains how a running test can still fail to observe the intended behavior.

## Review the diff against the starting revision

Inspect changes to production code, tests, build configuration, instructions, and generated files. `git diff` of the working tree alone misses a change the agent already committed. Compare the intended base revision with the final commit and inspect any remaining staged or unstaged changes.

A “fail if src/main changed” rule is useful only for a task that should not modify production code. It is not a universal CI gate for feature work. Define allowed paths from the task and require human review where the acceptance process needs it.

## Treat environment failures as environment failures

If a dependency mirror, JDK, Docker daemon, or credential is missing, capture that blocker. Do not disable the test or rewrite business logic to compensate. The [Maven sandbox guide](/blog/codex-sandbox-maven-spring-boot/) and [Docker socket guide](/blog/codex-testcontainers-docker-socket-spring-boot/) give narrower diagnostic sequences.

Keep privileges appropriate to trusted code and the runner. Consult the [current Codex security documentation](https://learn.chatgpt.com/docs/agent-approvals-security); do not copy retired approval names or assume one local sandbox failure applies to every installation.

## Define a completion artifact

Keep the starting revision, requirement, patch, tool version, selected model, verification command, fresh report totals, and remaining blockers. That record lets another reviewer distinguish “agent stopped,” “build passed,” and “behavior accepted.”

Put the recurring expectations in the [Boot 4 instruction template](/blog/spring-boot-4-agents-md-guide/). The [Java hub](/blog/ai-for-java-developers/) connects the broader workflow. A short reviewable record is more useful than an unsupported success ratio.
