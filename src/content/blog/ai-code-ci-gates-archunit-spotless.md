---
title: "Java CI Gates: Prove ArchUnit Rules Fail on Violations"
description: "Use positive and negative fixtures to verify architecture rules, preserve formatting gates, and review agent changes to the checks themselves."
pubDate: 2026-09-04
category: "java-testing-ci"
tags: ["ai code ci gate", "archunit", "spotless", "claude code", "spring boot ci", "java ci", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["archunit ai generated code", "spotless spring boot ci", "claude code ci gate", "archunit rule not failing", "ai code fails ci java"]
updatedDate: 2026-10-23
---

A Java CI gate is useful only if it rejects the violation it was designed to reject. A passing ArchUnit rule can mean that the code follows the rule, the selection missed the relevant code, or the intended check never executed.

This guide reconstructs the useful mechanism from an earlier AI-built lab. It does not retain the original agent transcript or claim that a particular model usually changes or preserves gates.

## Separate mechanical checks from architectural requirements

A formatter checks a mechanical contract. An architecture test checks a defined dependency or annotation constraint. Neither proves the application's business behavior.

Choose a formatting tool and configuration that match the project's JDK and style. Bind its check to the intended verification lifecycle. Running a formatter locally is useful, but the CI check still needs to run independently.

For architecture rules, state the actual requirement: for example, the web package must not depend directly on the repository package. The [ArchUnit guide](https://www.archunit.org/userguide/html/000_Index.html) describes importing classes and defining rules against their bytecode.

## Prefer typed references when the type is available

A typed annotation reference avoids guessing whether a string is a simple name or a fully qualified name. For a project forbidding field injection, an illustrative rule is:

```java
noFields().should().beAnnotatedWith(Autowired.class);
```

This is a fragment: import the rule API and the actual annotation, then apply the rule to the relevant main classes. Do not copy an unrelated dependency solely to make a sample compile.

When using a string-based API, check its documented name semantics. A passing negative rule is not evidence that a particular annotation was matched.

## Use a violating fixture and a clean fixture

The [Java verification sample](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/java-verification) contains an analogous rule against `Deprecated.class`, avoiding a Spring dependency in the small teaching project. One fixture has an annotated field and must trigger an assertion failure. A second has a normal field and must pass.

The test around the violating fixture asserts that the rule throws; the overall suite is supposed to pass because the gate detected the deliberately bad fixture. This is different from weakening the rule to make bad production code acceptable.

Also inspect the imported classes and selection predicates. Empty selection can have its own failure behavior depending on the rule and ArchUnit configuration. Do not assume every empty or unmatched rule silently passes.

## Preserve the checks when an agent edits code

Use a clean baseline or record pre-existing working-tree changes. Require the completion report to identify edits to architecture tests, formatter configuration, exclusions, and assertions. A rule that is wrong may legitimately need repair, but changing it should be a visible decision tied to the requirement.

“Never touch a test file” is too broad when the task is to fix a test. “Never weaken a check merely to make the current patch pass” describes the actual concern.

Review reverts as well as new edits. Restoring a file from Git can destroy a legitimate uncommitted fix. The instruction to preserve unrelated edits belongs in the task boundary.

## Verify the whole chain

Confirm that the test was discovered, that its positive fixture fails as expected, and that the CI job preserves the build exit status. A formatter check that was never bound to the lifecycle and an architecture rule that was never executed offer no acceptance evidence.

Use the [Surefire diagnostic guide](/blog/ai-junit-tests-not-running-spring-boot-4/) for discovery, the [JUnit guide](/blog/ai-junit-tests/) for assertion quality, and the [CI contract guide](/blog/codex-ci-spring-boot-green-build/) for independent acceptance. The [Boot 4 instruction template](/blog/spring-boot-4-agents-md-guide/) shows how to record the expectations, and the [Java hub](/blog/ai-for-java-developers/) organizes related checks.
