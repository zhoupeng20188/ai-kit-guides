---
title: "Spring Boot 4 Migration: What AI Agents Can and Can't Fix (2026)"
description: "Boot 3.5 hit EOL in June 2026. I read Spring's Boot 4 migration guide: which breaking changes AI really automates, and which ones it quietly gets wrong."
pubDate: 2026-08-31
category: "ai-tools"
tags: ["spring boot 4", "spring boot migration", "claude code", "java ai tools", "spring security 7", "java-ai-cluster"]
image: "/og-spring-boot-4-migration-ai-agents.jpg"
imageAlt: "A Spring Boot 4 migration guide open beside an AI coding agent session, showing Jackson 3 package renames and a Spring Security 7 CSRF config"
keywords: ["spring boot 4 migration", "spring boot 4 breaking changes", "jackson 3 spring boot", "spring security 7 csrf 403", "ai agent spring boot migration"]
faq:
  - question: "When did Spring Boot 3.5 reach end of life?"
    answer: "Spring Boot 3.5 is the final minor release of the 3.x line and its open-source support ended on June 30, 2026. After that date no further open-source security patches are published for 3.x. Commercial backports remain available through HeroDevs NES. Spring Boot 4.0 itself went GA on November 20, 2025 alongside Spring Framework 7.0, so by the time 3.5 hit EOL the 4.x line had already been generally available for about seven months."
  - question: "Can an AI coding agent do a Spring Boot 4 migration for me?"
    answer: "Partly. Agents are genuinely good at the mechanical half: package and class renames (com.fasterxml.jackson to tools.jackson, antMatchers to requestMatchers, hibernate-jpamodelgen to hibernate-processor) because the compiler tells them when they are wrong. They are unreliable at the silent half — behaviour changes that compile cleanly, like Jackson 3 writing dates as ISO-8601 strings instead of timestamps, or Spring Security 7 enabling CSRF for REST endpoints. Those need tests and a running app, not a code rewrite."
  - question: "Why does my REST API return 403 after upgrading to Spring Boot 4?"
    answer: "CSRF protection is enabled by default in Spring Security and has been for years — Boot 4 does not turn it on. The common claim that 'Spring Boot 4 enables CSRF for API endpoints' is wrong about the default; I verified the same POST returns 403 under both Boot 3.5.16 and 4.x with identical config. What an upgrade can do is surface a CSRF gap your old config masked. GET requests keep working while POST, PUT and DELETE return 403 with nothing useful in the logs. If GET passes and POST fails, that is CSRF. Confirm with logging.level.org.springframework.security.web.csrf set to DEBUG. For a stateless JWT API, scope the exemption to your API matcher rather than disabling CSRF globally."
  - question: "Is Jackson 2 still supported in Spring Boot 4?"
    answer: "Yes, as a deprecated stop-gap. Boot 4 provides a spring-boot-jackson2 module and a spring.jackson.use-jackson2-defaults property so you can move to 4.0 first and deal with Jackson later. Jackson 2 properties moved under the spring.jackson2 prefix. The Spring team has been explicit that this is a bridge, not a destination: Jackson 2 auto-configuration is deprecated in Boot 4 and slated for removal in a future release."
---

Let me get the awkward part out of the way first: I have not migrated my own Spring Boot services to 4.0 yet. So this is not a war story. I am not going to tell you what broke at 2 a.m. on my watch, because that did not happen.

What I did do is read the official Spring Boot 4.0 Migration Guide end to end, cross-check it against the Spring team's own commentary, and sort every breaking change into two buckets: the ones a coding agent can genuinely grind through for you, and the ones it will sail straight past while your tests stay green. That split is the actual useful output here, and it is the part nobody writes about. Most Boot 4 content is either a changelog rewrite or a "here is my security config" post. Almost nothing tells you where to trust the agent and where to stop trusting it.

## The Clock Already Ran Out

Spring Boot 3.5 is the last minor release of the 3.x line, and its open-source support ended on **June 30, 2026**. No more free security patches for 3.x. Commercial backports still exist through HeroDevs if you want to buy time, but the free ride is over.

Meanwhile Spring Boot 4.0 went GA on **November 20, 2025**, together with Spring Framework 7.0. By the time 3.5 hit EOL, 4.x had been generally available for roughly seven months. That is not a bleeding-edge release you would be reckless to adopt. It is a settled one.

The baseline is friendlier than people assume: **Java 17 is still the minimum**, Java 21 is what I would target, and Java 25 is supported. Jakarta EE 11 underneath (Tomcat 11, Hibernate ORM 7.1, Jakarta Persistence 3.2). If you are coming from 3.x on Java 17 or 21, the JDK is not your problem. The dependency surface is.

That last point matters more than any individual rename: Boot 4 pulls Spring Security 7, Spring Data 2025.1, Hibernate 7.1 and Jackson 3 all at once. You are not doing one migration. You are doing four that happen to share a version bump.

## Bucket One: Mechanical Renames, Where the Agent Earns Its Money

These changes are loud. The compiler yells, the agent fixes, the compiler confirms. This is the category where handing the work to Claude Code or Codex is not just faster, it is arguably more reliable than a human doing it by hand across four hundred files.

The Jackson 3 move is the biggest one. The group ID and package change from `com.fasterxml.jackson` to `tools.jackson`, with one deliberate exception: `jackson-annotations` keeps the old `com.fasterxml.jackson.core` group ID and `com.fasterxml.jackson.annotation` package, so `@JsonProperty` and friends are untouched. Several classes got renamed for consistency too:

- `ObjectMapper` → `JsonMapper` as the recommended entry point
- `Jackson2ObjectMapperBuilderCustomizer` → `JsonMapperBuilderCustomizer`
- `@JsonComponent` → `@JacksonComponent`
- `@JsonMixin` → `@JacksonMixin`
- `JsonObjectSerializer` → `ObjectValueSerializer`
- `SerializerProvider` → `SerializationContext`

Then there is the rest of the mechanical pile: `antMatchers()` became `requestMatchers()`, `authorizeRequests()` became `authorizeHttpRequests()`, `spring-boot-starter-aop` became `spring-boot-starter-aspectj`, and `hibernate-jpamodelgen` became `hibernate-processor`.

Why agents do well here is worth understanding, because it tells you when to delegate. These renames are **compiler-verified**. The agent does not need to understand your domain to fix them, the pattern is uniform, and a `./mvnw compile` gives it a hard yes or no. Give it the whole module, let it iterate on the error output, and verify with grep afterwards:

```bash
grep -r "com.fasterxml.jackson" src/main/java --include="*.java" -l
grep -r "antMatchers" src/main/java --include="*.java" -l
```

One caveat I would hold onto: an agent will happily invent a Boot 4 API that does not exist. Its training data is dominated by Boot 3 patterns, so when it is unsure it interpolates. Every rename it produces should be greppable in the official migration guide. If it cannot point at a documented rename, treat it as a guess.

## Bucket Two: Silent Behaviour Changes, Where the Agent Will Burn You

This is the bucket that actually costs weekends, and it is exactly the bucket an agent is structurally bad at. These changes compile cleanly. Some of them even pass a shallow test suite. They just quietly alter what your application does at runtime.

**Jackson 3 flipped two serialization defaults.** Dates no longer serialize as Unix timestamps — `WRITE_DATES_AS_TIMESTAMPS` now defaults to false, so your `LocalDateTime` fields turn into ISO-8601 strings. And `SORT_PROPERTIES_ALPHABETICALLY` now defaults to true, so JSON properties come out alphabetised. Both are defensible choices. Both will break any client or snapshot test that assumed the old shape.

**Jackson 3 changed the exception hierarchy.** `JsonProcessingException` extended `IOException`; `JacksonException` extends `RuntimeException`. If you have `catch (IOException e)` blocks that were incidentally swallowing Jackson errors, they no longer catch anything, and a serialisation failure that used to become a handled error response now propagates as an unhandled one. No compile error. Nothing in your build.

**CSRF protection has been on by default in Spring Security for years — Boot 4 does not turn it on.** This is the standout trap, and the most misreported one. The claim you will see repeated — "Spring Boot 4 enables CSRF for API endpoints" — is wrong about the default. I confirmed it directly: a minimal REST `SecurityConfig` with no CSRF bean returns 403 on POST under **both** Boot 3.5.16 and 4.1.1. So if you meet a new 403 after upgrading, do not assume Boot 4 flipped a switch. The default was already there; your old config may have masked the gap, or your Boot 3 setup handled it in a way the rewrite dropped. The tell is simple: if GET succeeds and POST fails with the same credentials, it is CSRF. Confirm it with:

```yaml
logging:
  level:
    org.springframework.security.web.csrf: DEBUG
```

The lazy fix is a global `csrf(csrf -> csrf.disable())`. Please do not. For a stateless JWT API, scope the exemption instead — match on `/api/**`, set `SessionCreationPolicy.STATELESS`, and exempt only that matcher. If you run session or cookie auth, keep CSRF on and wire up `CookieCsrfTokenRepository` with the `X-XSRF-TOKEN` header. An agent asked to "fix the 403" will reach for the global disable almost every time, because that is the shortest path to a green test.

**Liveness and readiness probes are now enabled by default**, so the health endpoint exposes those groups without you asking. Disable with `management.endpoint.health.probes.enabled` if you do not want them.

Notice the pattern across all four: no compiler signal, no obvious test failure, and no way for an agent to detect the problem by reading code. An agent predicts what code *should* do. It cannot observe what your running app *actually* does. That gap is where migrations go wrong.

## Where the Agent Actively Makes Things Worse

Two failure modes I would watch for specifically.

The first is **confident fabrication**. Ask an agent to migrate a Boot 3 config class and it will occasionally produce a Boot 4 API that reads plausibly and does not exist. This is worse than a compile error, because a compile error is information. A fabricated API looks like progress.

The second is **mixed-generation code**. Agents drift between Boot 3 and Boot 4 idioms within a single file, especially on long migrations where the context window has rolled over. You end up with `spring.jackson.read.*` in one place and `spring.jackson.json.read` in another, both looking reasonable in isolation. The official guidance is blunt about this for library authors: supporting Boot 3 and Boot 4 inside one artifact is strongly discouraged.

## The Workflow I Would Actually Run

If I were starting my own migration tomorrow, this is the order I would do it in, and the agent's role changes at each step.

1. **OpenRewrite first, agent second.** Let the recipe handle the mechanical renames. It is AST-based, so it is safer than string replacement and it catches type references in inheritance chains the agent will miss. Then let the agent handle what the recipe did not cover.
2. **Give the agent the migration guide as context, not just the error output.** Paste the relevant section. An agent that can see the documented rename table hallucinates far less than one inferring from training data. This is the same reason I keep a [project rules file for the agent](/blog/claude-code-remember-spring-boot/) — the agent performs against the context you hand it, not against what it remembers.
3. **Write tests for the silent changes before you upgrade, not after.** Assert on your actual JSON date format and property order. Assert that a POST returns 200 and not 403. These are cheap to write now and they are the only thing that will catch bucket two.
4. **Migrate the domain module first.** In a multi-module build, everything else has to finish the namespace and dependency move together anyway, so starting with the leaves just means more merge pain.
5. **Run the app and click through it.** Not optional. Every change in bucket two is invisible to static analysis.

For anything touching an older service, I would also reread what I wrote about [pointing AI at a legacy Java codebase](/blog/using-ai-legacy-java-codebase/) — the failure modes compound when the code is old and the tests are thin.

## What I Would Tell My Team

Do not ask an agent to "migrate us to Spring Boot 4." That prompt guarantees it optimises for the compiler going quiet, which is precisely the wrong target here. Ask it to do the renames, one module at a time, with the migration guide open beside it. Then take the silent changes yourself and write tests for them, because those are judgement calls about your API contract, not mechanical edits. Then check that those tests actually execute: on Spring Boot 4 with JUnit 6 I ended up with [agent-written tests that never ran](/blog/ai-junit-tests-not-running-spring-boot-4/) while the build stayed green, which is the same silent failure one layer further down.

The honest summary: the agent is excellent at the 80% that is tedious and compiler-verified, and it is close to useless at the 20% that will actually page you. Knowing which is which is the whole job.

Want the broader picture of AI coding agents on Java? Start from the [Java + AI hub](/blog/ai-for-java-developers/), where this sits alongside the Claude Code, Cursor, and Codex pieces.
