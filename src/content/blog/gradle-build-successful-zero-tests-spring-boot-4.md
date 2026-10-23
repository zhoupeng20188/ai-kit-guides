---
title: "Gradle Tests Not Rerun: UP-TO-DATE, Cache, and Missing Inputs"
description: "Distinguish legitimate Gradle test reuse from an undeclared-input bug. Check task outcomes, force execution, and declare the state the test reads."
pubDate: 2026-09-23
category: "java-testing-ci"
tags: ["gradle", "spring boot 4", "claude code", "java testing", "ci cd", "build cache", "ai coding agents", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["gradle build successful zero tests", "gradle test up to date", "gradle test from cache", "gradle build cache stale results", "spring boot 4 gradle", "gradle rerun tests", "gradle test not running", "ai agent gradle false green", "claude code gradle", "claude code tests not running"]
updatedDate: 2026-10-23
---

A Gradle test task marked `UP-TO-DATE` or `FROM-CACHE` reuses a previous outcome. That can be correct and useful. The risk appears when a test reads state absent from its declared inputs, so Gradle has no reason to invalidate the outcome when that state changes.

This guide explains that mechanism with a hypothetical external flag file. It removes the earlier article's unretained timing measurements and model success ratios. The commands are diagnostic procedures to run on your own build, not a new benchmark.

## Read the task outcome

Use a log mode that preserves task labels:

```bash
./gradlew test --console=plain
```

Distinguish a task that executed from `UP-TO-DATE`, `FROM-CACHE`, `NO-SOURCE`, `SKIPPED`, or an explicitly excluded task. The [Gradle testing guide](https://docs.gradle.org/current/userguide/java_testing.html) describes test execution and filtering. Overall success means the selected work did not fail; it does not promise every test was freshly executed.

A fast run is not proof of a problem. It may be legitimate reuse, a small suite, or a different selected task graph. Use the outcome and reports, not a millisecond threshold.

## Construct the missing-input scenario

Suppose a test reads `flags/discount-enabled.txt` directly from the project root. It passes when the file contains `true`. If the build does not declare that file as a task input, changing it may not invalidate the test outcome.

Reproduce the sequence in a disposable project: run with `true`, change only the flag to `false`, inspect the task outcome, then force execution. Keep the source, configuration, and logs if reporting the result. A cache hit is evidence about declared inputs; it is not proof the external flag still has the expected value.

## Force the relevant verification

Check wrapper support for task-level `--rerun`. A broadly available diagnostic is:

```bash
./gradlew test --rerun-tasks --no-build-cache --console=plain
```

This intentionally forgoes reuse for the selected invocation. It can cost more work, so it is a diagnostic choice rather than a reason to disable caching for every build permanently.

Compare actual failures and reports after the forced run. A result-file modification time can reflect copying from a cache. Internal timestamps can provide a clue, but they are not a universal proof of freshness across reporters and configurations.

## Declare what the test reads

For the hypothetical file, the Groovy DSL can include:

```groovy
tasks.named('test') {
    useJUnitPlatform()
    inputs.file('flags/discount-enabled.txt')
        .withPathSensitivity(PathSensitivity.NONE)
}
```

Choose path sensitivity from the test's semantics. `NONE` is appropriate when only content matters; it is wrong if behavior depends on the path. The [Gradle input/output reference](https://docs.gradle.org/current/userguide/incremental_build.html) explains how declared state participates in reuse.

Verify both directions: the bad flag must invalidate a good result, the corrected flag must permit a successful result, and unchanged valid inputs may legitimately reuse it. Account for environment variables, external services, and time-dependent behavior separately; one file declaration cannot describe them all.

## Compare runners accurately

Maven Surefire's default naming patterns can omit a class; Gradle reuse can avoid executing a selected task. Those are different diagnoses. Both runners also have configuration-dependent filtering, discovery, and engine behavior, so “Maven hides files, Gradle discovers everything” is too broad.

An explicitly requested nonexistent Maven test need not silently pass; check Surefire's selection-failure settings. Use the [Maven discovery guide](/blog/ai-junit-tests-not-running-spring-boot-4/) for that investigation.

## Require an honest completion record

When an agent runs the build, ask which task executed and which outcome was reused. If the acceptance requirement calls for fresh external-service verification, request that explicitly and record environmental blockers.

Review the [JUnit assertions](/blog/ai-junit-tests/) once execution is established. The [CI contract guide](/blog/codex-ci-spring-boot-green-build/) covers acceptance beyond exit status, and the [Boot 4 instructions](/blog/spring-boot-4-agents-md-guide/) show how to encode the expectation. The [Java hub](/blog/ai-for-java-developers/) links the related scenarios.
