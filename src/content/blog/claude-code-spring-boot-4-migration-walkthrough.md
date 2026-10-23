---
title: "Spring Boot 4 Upgrade Walkthrough: A Verification Sequence"
description: "Work through baseline capture, test annotation changes, dependency activation, security filters, and persisted-state checks in a Boot 4 upgrade."
pubDate: 2026-10-10
category: "spring-boot-4"
tags: ["spring boot 4", "spring boot migration", "claude code", "ai coding agents", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["spring boot 4 migration lab", "spring boot 3 to 4 upgrade", "spring boot 4 silent failures", "ai agent spring boot 4", "boot 4 migration checklist"]
updatedDate: 2026-10-23
---

A Spring Boot 4 upgrade walkthrough should leave a reader with an ordered set of checks and clear stopping points. The useful question is which application contract a change preserves, not how confidently an agent describes completion.

The earlier page reported an AI-built lab as a personal migration and called it fully reproducible without publishing the complete project. This revision is a reconstruction procedure; historical console excerpts and model scores are not presented as new measurements.

## Capture the old application's contract

Pin a starting revision. Record the JDK, wrapper, resolved dependency versions, active profile, and required services. Run the expected suite and save its reports. Capture a small set of synthetic API payloads, security outcomes, and persistence cases that must survive the upgrade.

If the baseline fails, establish why before changing versions. Keep existing failures visible so an agent cannot silently “fix” them by changing requirements.

## Apply a bounded version change

Read the [official migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide). Upgrade the intended Boot line using the project's management approach. A BOM import manages dependency versions; it does not automatically provide every parent-POM plugin configuration.

Run compilation and keep its errors. Fix documented imports, removed APIs, and module changes in small groups. Avoid concurrent DTO, package-layout, or business-logic cleanup.

## Repair the test configuration deliberately

Boot 4 changes test APIs and modularization. For the relevant release, verify replacement of Boot's removed `@MockBean` with Spring Framework's `@MockitoBean`, and check the correct web test annotation packages and dependencies.

Do not interpret a compiling test source as a discovered test. Use the [Surefire audit](/blog/ai-junit-tests-not-running-spring-boot-4/) and inspect fresh reports. The [downloadable Java fixture](/examples/java-verification.zip) demonstrates how a deliberately failing `*Should` class can be absent from a normal run yet fail under explicit selection; it is not a Boot migration project.

## Confirm the security harness

For MockMvc, use the supported Spring test setup and confirm Spring Security integration. A manually created MockMvc can omit filters. A test that receives 200 in that state does not establish that the protected application endpoint behaves correctly.

Exercise an allowed request and a rejected request. For CSRF, identify the failing filter rather than attributing every POST rejection to the version upgrade. For method authorization, invoke a secured Spring-managed bean with both permitted and denied identities.

The [CSRF guide](/blog/claude-code-spring-boot-4-403/) and [method-security guide](/blog/claude-code-spring-boot-4-preauthorize/) provide the narrower checks.

## Verify activation and binding

For each changed integration, identify the expected bean or behavior. Use an appropriate condition report and a focused check. Do not infer runtime activation solely from dependency resolution or configuration metadata.

For each important property, check the active profile, property-source precedence, target configuration object, and resulting behavior. A local diagnostic endpoint can help, but it must be restricted; it is not the only source of truth. See the [dependency guide](/blog/codex-spring-boot-4-dependencies-silent-failures/) and [YAML guide](/blog/codex-spring-boot-4-yml-properties/).

## Test the upgrade path, not only a fresh database

Run against representative existing schema and migrations. Compare JSON payloads and persisted values with the baseline. A new H2 schema can hide a naming mismatch in a production database, while schema validation cannot establish every native-query or time-value contract.

Use the [Hibernate guide](/blog/spring-boot-4-hibernate-7-silent-failures/) for mapping and query checks. Record the exact environment for any performance comparison rather than reusing an anecdotal multiplier.

Finish with the full configured verification task, independent diff review, and a list of remaining blocked checks. The [migration map](/blog/spring-boot-4-migration-ai-agents/) explains why these layers differ, and the [Java hub](/blog/ai-for-java-developers/) links the related agent workflows.
