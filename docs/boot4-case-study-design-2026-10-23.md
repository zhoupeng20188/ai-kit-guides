# Runnable case study and Java entry points

User-approved direction: strengthen a complete original example, distinguish the migration overview from the walkthrough, and expose the Java learning path and source download on the homepage. Complete the local, reviewable implementation and verification, then use the commit/push workflow already authorized for this ongoing site remediation. AdSense account submission remains a separate action.

## Decisions

Extend the existing plain Java sample only: small dependency footprint, but would still not establish any Spring Boot behavior. Use a Docker/PostgreSQL lab: closer to some deployments, but a container runtime would add an unnecessary barrier for the first public fixture. Selected approach: a standalone Maven project using Java 17, two pinned Spring Boot profiles and disposable H2 databases.

The baseline profile uses Boot 3.5.7 and the target uses Boot 4.0.0. They are historical comparison versions, not recommended latest deployment versions. Tests cover HTTP security through MockMvc with the actual Spring filter chain and a separate loopback HTTP server; an intentionally unsecured harness; startup activation of Flyway; editing an applied migration, metadata repair, and a forward corrective migration; and an explicitly selected failing test outside default class-name patterns.

The lab must state its limits: H2 does not establish PostgreSQL behavior, MockMvc is not a real socket request, and the tests do not benchmark an AI agent or reproduce old transcripts. Shared contracts should behave consistently across both profiles; CSRF and test naming are not newly introduced Boot 4 features.

## Content and presentation

- Preserve article URLs and publication dates.
- Migration overview explains how to scope an upgrade and routes readers to specific checks. Remove its duplicate step-by-step procedure.
- Walkthrough becomes the reproducible lab guide: project map, commands, observed results, explanation, and limitations.
- CSRF, Flyway and discovery guides link directly to the relevant test and exercise, with concise observed results.
- Homepage introduces AI-assisted Java development, shows the learning path and runnable source near the top, and features the walkthrough. Keep existing site styles and responsive patterns.
- Add an indexable example page with source download, tested versions, results and file map. A bare ZIP alone does not explain the artifact to readers.

## Execution checklist

- [x] Inspect current source, prior audit and primary documentation.
- [x] Reuse the direction approved in the conversation and record scope and alternatives.
- [x] Implement and execute both profiles; retain raw reports and environment.
- [x] Verify the expected discovery failure separately from a build/environment failure.
- [x] Package source with sanitized evidence and a repeatable verification command.
- [x] Revise the overview, walkthrough, focused guides, example page and homepage.
- [x] Build the site, validate links and metadata, and inspect local desktop/mobile rendering.
- [x] Report observed results and limits; publish through the previously authorized Git workflow after checks.
