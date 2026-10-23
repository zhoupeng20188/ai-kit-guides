---
title: "Spring Boot 4 Migration: Choose the Contracts to Verify"
description: "Scope a Boot 4 upgrade around JSON, security, persistence and configuration contracts. Choose the right checks before following the runnable case study."
pubDate: 2026-08-31
category: "spring-boot-4"
tags: ["spring boot 4", "spring boot migration", "claude code", "java ai tools", "spring security 7", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["spring boot 4 migration", "spring boot 4 breaking changes", "jackson 3 spring boot", "spring security 7 csrf 403", "ai agent spring boot migration"]
updatedDate: 2026-10-23
---

Before asking an AI agent to upgrade Spring Boot, decide which observable application contracts must survive. A version change touches a dependency platform; acceptance depends on how your application uses it.

This overview helps scope that work. For commands, source and actual observations, use the [runnable Boot 3.5 to 4 case study](/blog/claude-code-spring-boot-4-migration-walkthrough/). The two articles have different jobs: choose the relevant contracts here, then inspect an implemented example there.

## Select checks from the application's surface

Start with the application's entry points, clients, integrations and existing data. A small service without persistence needs a different acceptance set from a multi-module application with shared databases and browser sessions.

| Application surface | Contract to preserve | Evidence to request |
| --- | --- | --- |
| Public JSON API | Names, date representation, null handling, errors | Representative request/response fixtures through the configured mapper |
| Browser or authenticated API | Authentication, CSRF, authorization, ownership | Allowed and denied requests through the real security chain |
| Boot-managed integration | Required bean and effective behavior | Startup/context check followed by the feature's observable effect |
| Existing database | Schema compatibility, migrated data, query semantics | Upgrade from the previous schema plus a separate fresh installation |
| Configuration | Intended values actually influence the consumer | Active profile, binding assertion and a behavior check |
| Build and tests | The required cases execute and detect a defect | Fresh named reports and a controlled failing case |

This is a selection framework, not a universal test count. Identify the requirement and the failure each check should detect. A generated test that only agrees with the new implementation has not established preservation of the old contract.

## Resolve dependencies against the exact target

Read the [official migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) for the selected Boot line. Check compatibility for the integrations you actually use. Old coordinates may be removed, bridges, or still-valid libraries; avoid blanket substitutions.

The BOM manages dependency versions. It does not provide every plugin execution that a parent POM would configure. Require the agent to show the selected dependency graph and explain new integration modules. The [dependency diagnostic guide](/blog/codex-spring-boot-4-dependencies-silent-failures/) develops this distinction.

For Jackson, include client payloads in acceptance. Package migration has exceptions, including annotations. A plain mapper unit test may not exercise the mapper configured in the application.

## Treat persistence as an upgrade path

A fresh database answers whether the current migration chain can install. It does not answer whether existing schema and data can reach the same checked state. Request both paths when a deployed database is involved.

The [Flyway guide](/blog/flyway-checksum-mismatch-ai-agent/) handles edited history and repair. The [Hibernate guide](/blog/spring-boot-4-hibernate-7-silent-failures/) handles mappings, native-query types and time values. Schema validation supplies structural evidence but cannot establish every semantic or performance requirement.

The downloadable lab uses H2 to make a narrow history problem reproducible. Select the actual database engine and representative data for application-specific acceptance.

## Make security outcomes explainable

CSRF protection predates Boot 4. A POST rejection may involve CSRF, authentication, authorization or a later error dispatch. Establish which layer rejected the request before changing protection.

The [CSRF diagnosis guide](/blog/claude-code-spring-boot-4-403/) links a concrete example where error dispatch masks an initial 403 as 401. [Method security](/blog/claude-code-spring-boot-4-preauthorize/) and record ownership require separate checks. Neither a CSRF token nor an annotation proves the caller is authorized for a record.

## Define the agent's handoff

Keep the starting revision, versions, requirement, focused diff, exact commands, fresh reports and remaining blockers. Give recurring expectations to the agent through the [Boot 4 instruction template](/blog/spring-boot-4-agents-md-guide/), then enforce independent checks in CI.

A successful process and a green test summary provide limited observations. The [discovery guide](/blog/ai-junit-tests-not-running-spring-boot-4/) explains undiscovered cases; the [configuration guide](/blog/codex-spring-boot-4-yml-properties/) explains the difference between metadata and actual binding.

Use this map to decide what your application needs, and the [worked case](/blog/claude-code-spring-boot-4-migration-walkthrough/) to see the evidence format. Current support and release information belongs in the [Spring Boot project documentation](https://spring.io/projects/spring-boot/); this article does not impose a universal upgrade deadline or rank agents by unrecorded trials.
