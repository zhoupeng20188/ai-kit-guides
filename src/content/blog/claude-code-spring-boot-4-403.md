---
title: "Spring Boot 4 403: Diagnose CSRF and Verify the Security Chain"
description: "Distinguish CSRF, authentication, authorization, and missing test filters. Verify a scoped security change without weakening protection for a green build."
pubDate: 2026-09-02
updatedDate: 2026-10-23
category: "spring-boot-4"
tags: ["spring boot 4", "claude code", "agents.md", "spring security csrf", "java ai tools", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["spring boot 4 403", "claude code csrf", "agents.md spring boot", "spring security csrf disable", "ai agent fix 403"]
---

A Spring Boot 4 POST returning 403 needs a diagnosis before a security change. CSRF is one possible cause, but the status alone does not identify the failing filter, handler, or authorization rule.

This guide consolidates the earlier Claude Code and Codex lab reports. Those labs were built and run with AI assistance; complete original projects and transcripts were not retained. Historical model scores, token totals, and the incorrect “real Basic client implies 401” explanation have been removed.

## Establish which protection rejected the request

Record the request method and path, authentication mechanism, active security chain, response, and relevant exception. Check whether the request is authenticated and authorized before changing CSRF settings.

Spring's [CSRF reference](https://docs.spring.io/spring-security/reference/7.0/servlet/exploits/csrf.html) describes protection for unsafe methods. It predates Boot 4. An upgrade can change your configuration without changing that historical default.

A GET working while a POST fails is a clue, not proof. Look for the CSRF exception and configured denial handler. An authentication failure may be 401; a CSRF failure should not be reclassified solely because the request also uses Basic authentication.

## Verify the test harness before trusting its status

MockMvc must include the Spring Security integration for a security test to establish application behavior. Use the supported Boot configuration or apply `springSecurity()` when constructing it manually, with the required test dependency.

For a protected endpoint, establish both an allowed request and a rejected request. A harness that returns 200 without running the filters can make an insecure change appear correct.

The following is a fragment for a configured MockMvc with an authenticated user; imports and application wiring must match the project:

```java
mockMvc.perform(post("/orders").with(user("alice")))
        .andExpect(status().isForbidden());
mockMvc.perform(post("/orders").with(user("alice")).with(csrf()))
        .andExpect(status().isCreated());
```

The created-status expectation assumes that the valid handler is designed to return 201. Test the actual application's contract. This fragment is not a complete lab or evidence of a run against a specific Boot version.

## Do not equate stateless with CSRF-safe

A stateless session policy does not establish that a browser cannot send credentials automatically. Spring's [stateless-browser discussion](https://docs.spring.io/spring-security/reference/7.0/features/exploits/csrf.html#csrf-and-stateless-browser-applications) specifically covers HTTP Basic.

Identify all browser and non-browser clients and their authentication paths. Preserve protection for flows that need it. A JWT label alone is also incomplete context: the way the browser supplies the credential matters.

## Scope only a justified exemption

If the application's threat model supports an exemption for a particular API, define the exact matcher and verify the resulting behavior. A missing token is not, by itself, justification for switching off protection.

Test the intended exempted path and a write path outside it. A global `csrf.disable()` and a scoped exemption can both pass a narrow API test while changing unrelated paths differently.

Also verify authorization and ownership. A CSRF token does not prove the caller may modify a specific record. The [ownership guide](/blog/claude-code-insecure-api-spring-boot/) and [method-security guide](/blog/claude-code-spring-boot-4-preauthorize/) cover those independent obligations.

## Give the agent a behavior contract

State the authentication model, client types, permitted paths, and required rejected cases. Ask it to report the diagnosis before editing security configuration. Require a diff and the commands that actually executed.

Do not accept a green suite whose security filters were removed or whose assertions were weakened. The [JUnit guide](/blog/ai-junit-tests/) covers assertions and the [CI guide](/blog/codex-ci-spring-boot-green-build/) covers independent verification.

For a migration, repeat the same request contract against the pinned old and new versions and preserve the complete project and output before publishing results. The [Boot 4 migration map](/blog/spring-boot-4-migration-ai-agents/) and [Java hub](/blog/ai-for-java-developers/) provide the wider checklist.
