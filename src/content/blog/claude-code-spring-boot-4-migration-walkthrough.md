---
title: "Spring Boot 3.5 to 4: A Runnable Verification Lab"
description: "Run a Java 17 project on Boot 3.5.7 and 4.0.0. Inspect CSRF, real HTTP error dispatch, Flyway history, and two deliberately failing checks."
pubDate: 2026-10-10
category: "spring-boot-4"
tags: ["spring boot 4", "spring boot migration", "claude code", "ai coding agents", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["spring boot 4 migration lab", "spring boot 3 to 4 upgrade", "spring boot 4 silent failures", "ai agent spring boot 4", "boot 4 migration checklist"]
updatedDate: 2026-10-23
featured: true
---

This case study supplies one complete Java project, two pinned Spring Boot profiles, and the run records needed to check its results. It was created with AI assistance and executed on October 23, 2026. All inputs are synthetic; the project does not reconstruct an earlier production incident or benchmark a coding agent.

Start with the [source, results and download page](/examples/boot4-verification-lab/). The [migration overview](/blog/spring-boot-4-migration-ai-agents/) helps choose which application contracts to protect; this article shows a bounded implementation of that process.

## What changes between the profiles

Both profiles use Java 17, the same source and the same assertions. `boot3` selects Spring Boot 3.5.7, the web starter and Flyway core. `boot4` selects 4.0.0, the web MVC starter and Boot's Flyway starter. The BOM manages library versions; compiler and test-runner plugins are explicit in the POM.

These are historical comparison releases, not a recommendation about the latest production patch. Consult the [official migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) for changes relevant to your target release. The fixture deliberately uses shared APIs and does not exercise every removed API or integration.

## Run the project and inspect the evidence

Extract [the ZIP](/examples/boot4-verification-lab.zip), enter its directory, and check that Maven uses JDK 17 or later:

```bash
java -version
mvn -version
python3 verify.py
```

The first run needs Maven repository access. The lab uses H2 and a loopback HTTP server, so no Docker or external database is required. `verify.py` saves raw logs locally and checks the names and results of the expected suites. It also verifies two deliberate failures rather than treating any nonzero exit as success.

The recorded environment was macOS arm64, Corretto 17.0.19 and Maven 3.9.11. The published snapshot contains these outcomes:

| Run | Tests | Failures | Errors | Skipped | Exit |
| --- | ---: | ---: | ---: | ---: | ---: |
| `-Pboot3 clean test` | 11 | 0 | 0 | 0 | 0 |
| `-Pboot4 clean test` | 11 | 0 | 0 | 0 | 0 |
| Explicit discovery sentinel | 1 | 1, intentional | 0 | 0 | 1 |
| Error-dispatch fault enabled | 1 | 1, intentional | 0 | 0 | 1 |

The two normal runs execute the same eleven cases, not twenty-two different requirements. Read [the result manifest](/examples/boot4-verification/results.json) and [Boot 4 log](/examples/boot4-verification/boot4.log) to inspect versions and observations. Source digests bind the record to the included POM and source files. Machine paths were redacted from the published logs and XML; the README explains what was removed.

## Check HTTP security at two layers

`SecurityContractTest` creates MockMvc from the application context and applies `springSecurity()`. Its six cases cover an authenticated GET, anonymous GET, missing/invalid CSRF tokens, a valid CSRF request, and an intentionally unsecured standalone harness.

With the configured chain, an authenticated POST without a token returns 403; adding a valid test token permits the fixture's 200 response. A standalone controller without security filters also returns 200, even without the protections. That is evidence about a different harness, not evidence that the application's endpoint is public.

`NetworkContractTest` starts the embedded server on a random loopback port and sends actual Java HTTP client requests. It checks anonymous GET 401, valid Basic GET 200, and valid Basic POST without a CSRF token 403. It also checks that a direct request to `/error` remains protected. Test-user injection and a real Basic exchange are separate checks.

See [Spring's MockMvc setup](https://docs.spring.io/spring-security/reference/servlet/test/mockmvc/setup.html) and the [CSRF diagnosis guide](/blog/claude-code-spring-boot-4-403/) for the relevant wiring.

## Reproduce the error dispatch that masks a 403

During development of this fixture, a catch-all authenticated rule produced a surprising real HTTP 401 for the missing-token POST. The trace showed an initial CSRF rejection with 403, followed by an error dispatch to `/error` that reached the authentication entry point.

The normal configuration permits the servlet's `ERROR` dispatcher type before applying the authenticated rule to ordinary requests. It keeps CSRF protection enabled. This follows Spring's documented [dispatcher-type matching](https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html#_matching_by_dispatcher_type). It does not globally permit the `/error` URL.

The teaching switch below removes that dispatcher permission. The existing network assertion still expects 403, so the command must fail when it observes 401:

```bash
mvn -B -Pboot4 test -Dtest=NetworkContractTest \
  -Dlab.allow-error-dispatch=false \
  -Dlogging.level.org.springframework.security=TRACE
```

Inspect [the fault trace](/examples/boot4-verification/error-dispatch.log) for `Invalid CSRF token`, `Responding with 403`, and the subsequent `/error` authorization. This is a configuration-specific result in the fixture. It does not establish that Basic authentication universally changes CSRF failures into 401, or that Boot 4 introduced the behavior.

## Prove migration activation and history separately

`DatabaseActivationTest` checks a real Flyway bean and a marker row inserted by the application's classpath migration. That distinguishes a resolving library from a migration actually run by Boot.

`FlywayHistoryTest` then creates independent disposable databases for three cases:

1. Apply V1 and original V2, edit V2, and assert that validation reports a checksum mismatch.
2. Run repair against the edited history. Validation succeeds, but the existing database's `tag` remains nullable while a fresh database's column is not nullable. The old row has null in one database and `new` in the other.
3. Restore original V2 and add V3 to backfill data and apply the constraint. Migrate and validate both upgrade and fresh-install paths; the checked nullability, data value and applied migration count now agree.

A standalone validation after creating an unapplied V3 may report that pending migration. The fixture validates restored history before introducing V3, then migrates and validates again. Read the source for the precise ordering rather than treating a validation error as a reason to run repair.

The [Flyway guide](/blog/flyway-checksum-mismatch-ai-agent/) explains the operational decisions this example illustrates. The tests use H2 SQL; they do not establish production locking, PostgreSQL syntax, or complete schema equivalence.

## Expose a test that the normal suite omits

`UndiscoveredShould` contains a deliberate failing assertion but is outside Surefire's default class-name patterns. Both normal runs pass eleven tests without discovering it. Explicit selection runs it and fails with `DISCOVERY_SENTINEL`:

```bash
mvn -B -Pboot4 test -Dtest=UndiscoveredShould
```

The verification script requires that exact test failure. A compilation error or unavailable dependency is not equivalent. The [discovery guide](/blog/ai-junit-tests-not-running-spring-boot-4/) describes how to apply this check to an existing repository.

## Apply the pattern to your application

Choose the contracts your application needs, preserve a baseline, and run the same meaningful assertions on the target version. These profile runs use independent JVMs and disposable databases; they do not carry one persistent database through a cross-version engine upgrade. Add that path, real database fixtures, JSON contracts, and other integrations when your application requires them.

The [Java guide](/blog/ai-for-java-developers/) organizes the next steps. This lab's value is its inspectable code, observed failures, and bounded claims; passing it does not establish that an arbitrary Boot migration is complete.

**Revision note:** The earlier article described an AI-built migration without a complete retained project. This revision replaces that account with a newly created source package and run evidence. The new record does not validate historical model scores.
