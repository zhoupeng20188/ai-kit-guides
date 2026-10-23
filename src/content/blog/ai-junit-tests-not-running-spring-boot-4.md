---
title: "Spring Boot 4 Tests Not Running: Audit Surefire Discovery"
description: "Check Surefire naming, explicit selection, Failsafe binding, and fresh reports. Avoid confusing test-source counts with executed test cases."
pubDate: 2026-09-09
category: "java-testing-ci"
tags: ["junit 6", "spring boot 4", "surefire", "ai generated tests", "claude code", "java testing", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["junit 6 tests not running", "spring boot 4 surefire no tests", "ai generated tests silently skipped", "maven surefire test not executed", "spring boot 4 mockbean removed"]
updatedDate: 2026-10-23
---

Spring Boot 4 tests can compile without being selected by the Maven test runner. Diagnose discovery separately from compilation, skips, and failed assertions. The build's final success line does not enumerate everything that was eligible to run.

This article uses documented runner behavior and a [Java verification sample](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/java-verification). Earlier model-run totals and claims that source-file count must equal execution count have been removed.

## Check the selected runner and engine

Record the Java version, effective plugin configuration, test engine, and command. A dependency BOM and a parent POM provide different kinds of management; inspect the effective build rather than assuming an imported BOM configures plugins.

```bash
java -version
./mvnw -version
./mvnw help:effective-pom
./mvnw dependency:tree
```

JUnit 6 requires Java 17 or later. A JUnit 4 import can be a compilation failure when that API is absent, or a discovery problem when the API is present but the required engine is missing. The classpath decides which case applies.

## Use the discovery patterns as a starting point

Surefire documents default class-name includes such as `Test*`, `*Test`, `*Tests`, and `*TestCase` in its [inclusion reference](https://maven.apache.org/surefire/maven-surefire-plugin/examples/inclusion-exclusion.html). Check custom includes and excludes in the effective build.

The sample deliberately contains `UndiscoveredShould.java` with a failing assertion. Its name is outside those defaults. A normal sample test run omits that class. Selecting it explicitly should expose the assertion:

```bash
mvn -B test -Dtest=UndiscoveredShould
```

Run that command in the extracted sample directory. It is intended to fail. A failure during dependency download or compilation is not the same result; inspect which test ran and why it failed.

Do not generalize this to “Maven silently ignores an explicitly requested nonexistent test.” Surefire has a separate `failIfNoSpecifiedTests` setting, and explicit-selection failures depend on that configuration.

## Repeat the discovery check inside a Boot application

The [complete Boot lab](/examples/boot4-verification-lab/) runs the same source against Boot 3.5.7 with JUnit 5.12.2 and Boot 4.0.0 with JUnit 6.0.1. Each normal run executes eleven cases with no failures, errors or skips. Both omit the intentionally failing `UndiscoveredShould` class.

Selecting that class in the Boot 4 profile executes one test and fails with `DISCOVERY_SENTINEL`. The [failure log](/examples/boot4-verification/discovery.log) and named XML in the source package establish which assertion ran. `verify.py` requires that identity and failure, so a broken download or compiler error cannot count as reproduction.

The shared naming behavior is evidence about this Surefire configuration, not a new rule introduced by Boot 4. The [walkthrough](/blog/claude-code-spring-boot-4-migration-walkthrough/) explains the eleven selected checks and the actual HTTP/database checks that make this more than a test-count comparison.

## Wire integration tests deliberately

If the project uses Failsafe for integration tests, bind its `integration-test` and `verify` goals. Running `mvn verify` alone does not add a plugin execution. Follow the [Failsafe usage guide](https://maven.apache.org/surefire/maven-failsafe-plugin/usage.html) and inspect the resulting reports.

Renaming every `*IT` into a unit-test pattern is not always the right fix. It changes which phase runs the test and may bypass lifecycle setup or teardown.

## Inspect fresh reports instead of counting Java files

A file can hold helpers, an abstract base class, nested cases, parameterized tests, or generated tests. One source file is not one executed case. Comparing all Java files with console class summaries produces false alarms and missed cases.

Create a fresh verification run and inspect the expected suites in `target/surefire-reports` and, when configured, `target/failsafe-reports`. Compare executed cases, failures, errors, and skips with the intended suite. Avoid double-counting nested report structures or accepting reports left over from an earlier run.

`failIfNoTests` can reject a wholly empty suite; it does not prove every intended class was selected. Coverage is also supplementary evidence, not an inventory of all required tests.

## Check Boot-specific test wiring

When moving from Boot 3 to Boot 4, verify changed test annotations, packages, and modules against the [migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide). Use Spring Framework's `@MockitoBean` where the removed Boot `@MockBean` API must be replaced.

For MockMvc security checks, ensure the security chain is applied. A manually constructed MockMvc can answer a request without the filters that would reject it in the application. The [CSRF guide](/blog/claude-code-spring-boot-4-403/) covers that false-success case.

After discovery is correct, review the [assertions](/blog/ai-junit-tests/) and [CI acceptance contract](/blog/codex-ci-spring-boot-green-build/). Gradle's reuse behavior is a different mechanism, covered in the [Gradle guide](/blog/gradle-build-successful-zero-tests-spring-boot-4/). The [Java hub](/blog/ai-for-java-developers/) connects the related checks.
