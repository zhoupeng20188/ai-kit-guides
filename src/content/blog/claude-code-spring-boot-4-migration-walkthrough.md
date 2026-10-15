---
title: "I Ran the Spring Boot 4 Upgrade — and Scored What Agents Miss"
description: "A real, reproducible Boot 3.5.16 to 4.0.8 upgrade I drove on Java 17, scored against the silent-failure traps AI coding agents walk straight into."
pubDate: 2026-10-10
category: "spring-boot-4"
tags: ["spring boot 4", "spring boot migration", "claude code", "ai coding agents", "java-ai-cluster"]
image: "/og-claude-code-spring-boot-4-migration.jpg"
imageAlt: "A terminal window showing a Spring Boot 4 migration next to a checklist split into loud fixes the compiler forces and silent failures a green build hides"
keywords: ["spring boot 4 migration lab", "spring boot 3 to 4 upgrade", "spring boot 4 silent failures", "ai agent spring boot 4", "boot 4 migration checklist"]
faq:
  - question: "Can Claude Code or Codex migrate a Spring Boot 3 app to Spring Boot 4?"
    answer: "Yes, for the mechanical layer. In my own lab run the compiler-visible changes were forced and unambiguous: @MockBean became @MockitoBean, @AutoConfigureMockMvc moved to a new spring-boot-webmvc-test module with a changed package, and the JUnit version moved to 6. Every one of those fails the build until fixed, so an agent handles them. What it cannot do on its own is catch the silent half: a dependency sitting on the classpath with nothing wiring it up, a YAML key that stops binding with no log line, or a test class that compiles but runs zero times. Those need your own gates, not the agent's summary."
  - question: "What is the real difference between Claude Code and Codex for a Boot 4 migration?"
    answer: "In my side-by-side testing the only substantive behavioural difference is verification. Claude Code re-runs the prior version each loop to catch regressions; Codex does not. That makes Claude Code more trustworthy on the loud, compiler-visible layer, but it does nothing for the silent layer — a silent failure is green on both the old and the new version, so re-running the old version still shows green and teaches the agent nothing."
  - question: "How do I check that my tests still run after a Boot 4 upgrade, not just compile?"
    answer: "Count the executed tests, do not just grep for Skipped. In my lab I renamed a test class to OrderApiShould and surefire reported BUILD SUCCESS while running ZERO tests — there was no Tests run line at all, let alone a Skipped count, so the usual grep would have found nothing. Boot 4's default Surefire includes do not match *Should, *Spec, or *IT names and Failsafe is not wired by the parent, so a mis-named class is invisible and the build lies."
  - question: "Why does my Spring Boot 4 app start but behave differently after the upgrade?"
    answer: "Because Boot 4 split auto-configuration into per-technology modules. I measured the core spring-boot-autoconfigure jar dropping from 161 auto-configuration classes and 2112 metadata keys (3.5.16) to 15 classes and 135 keys (4.0.8); the JDBC slice moved into a new spring-boot-jdbc module. A property like spring.datasource.hikari.maxLifetime is only bound if that module is on the classpath, so changing a dependency can silently unbind it with zero log output. The actuator's configprops endpoint is the only source of truth; the build will not tell you."
  - question: "Should I trust an AI agent's 'migration complete' summary?"
    answer: "Treat it the way you would treat a summary written by a stranger who only ran the compiler. Run five checks yourself: confirm tests actually execute, check configprops for properties that stopped binding, verify the split-out modules are present and wired, start the app and fire a real POST that actually applies the Security 7 filter chain, and treat every removed deprecated API as a possible contract change. The agent's job is the half the compiler can see; yours is the half it cannot."
---

A few weeks ago I published a teardown of two *real* GitHub Copilot pull requests that attempted a [Spring Boot 4](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now) migration — one merged, one stalled at fifty errors. That post judged someone else's agent output against the silent-failure labs I had been running for two months. It was honest, but it left me with a gap I did not like: I had never put my own hands on the wheel. So I did. I built a minimal but genuine Spring Boot app and ran the [3.5.16 → 4.0.8 migration](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) myself on Java 17, capturing every command and output. This post is the walkthrough, plus the scorecard: which breaks the compiler forces you to fix, and which ones a green build hides — the exact ones an AI agent like Claude Code or Codex will report as "done."

If you want the broader frame first, the [Java + AI hub](/blog/ai-for-java-developers/) holds the rest of this series.

## The lab I ran (minimal, but real)

I did not upgrade a production monolith and call it a day. I built a small but genuine app: a controller, a service, a `SecurityConfig`, an `application.yml` that sets a Hikari `maxLifetime` and a Jackson flag, an in-memory H2 datasource, and two MockMvc tests — one that mocks the service with `@MockBean`, one that asserts the CSRF behaviour. It went green on Boot 3.5.16 on Java 17.

I pinned the toolchain explicitly — `JAVA_HOME` to Corretto 17 — because on this machine the default `java` is Corretto 8 and a Boot 4 build silently dies on JDK 8 with no useful message. I then flipped the parent version from `3.5.16` to `4.0.8` and let the compiler be the only feedback loop, the same way you would brief an agent: *upgrade this to Boot 4, run `mvn verify`, keep going until it is green.*

The baseline was real and clean:

```
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

And the compiler had already warned me about the first breakage before I even migrated — on 3.5.16, `@MockBean` compiled but printed: *"org.springframework.boot.test.mock.mockito.MockBean 已过时, 且标记为待删除"* — deprecated, and **marked for removal**. Boot 4 removed it.

## The loud half — what the compiler forced (and how an agent nails it)

Boot 4.0.8's first build failed to **compile**. Four errors, verbatim:

```
[ERROR] package org.springframework.boot.test.autoconfigure.web.servlet does not exist
[ERROR] package org.springframework.boot.test.mock.mockito does not exist
[ERROR] cannot find symbol: class AutoConfigureMockMvc
[ERROR] cannot find symbol: class MockBean
```

These are the changes a compiler enforces, and any agent fixes them without thinking, because failure is immediate and unambiguous:

**Removed and relocated annotations.** `@MockBean` is gone in Boot 4 (confirmed at 4.0.8). The replacement is `@MockitoBean`, but it does not live where `@MockBean` did — it moved into Spring Framework itself, at `org.springframework.test.context.bean.override.mockito.MockitoBean` (spring-test 7). `@AutoConfigureMockMvc` also moved: its import changed from `org.springframework.boot.test.autoconfigure.web.servlet` to `org.springframework.boot.webmvc.test.autoconfigure`.

**The module split, done the right way — but it bites twice.** Here is the part that surprised me. `@AutoConfigureMockMvc` did not just change package; it moved into a **brand-new module, `spring-boot-webmvc-test`**, that `spring-boot-starter-test` no longer pulls in transitively. So fixing the import is not enough — the build still fails to compile until you add the dependency. An agent that only reads the compiler error fixes both steps, because each is a hard failure. The trap from the other direction is the one my [dependency silent-failure lab](/blog/codex-spring-boot-4-dependencies-silent-failures/) measured: carry a Boot 3 starter spelling forward and a library can sit on the classpath with zero configuration and no warning. The compiler caught the *missing* module here; it never catches the *present-but-unbound* one.

So far, so predictable. If your mental model of "AI migration" stops at renames, version bumps, and removed APIs, this pass looks like a clean win. The problem is that none of these are the part of a Boot 4 migration that actually breaks you.

## The silent half — my five-point checklist

Here is the part my labs exist to expose. None of the following breaks the build. All of it changes behaviour, and an agent has no feedback loop for any of it, so its summary says "done" while the application quietly drifts.

**1. The module split you cannot see.** I measured this directly against the jars. The core `spring-boot-autoconfigure` artifact collapsed from **161 auto-configuration classes and 2112 metadata keys (3.5.16)** to **15 classes and 135 keys (4.0.8)**. The missing slices did not vanish — they moved. The JDBC auto-configuration, including `DataSourceAutoConfiguration`, relocated from `org.springframework.boot.autoconfigure.jdbc` into a new `spring-boot-jdbc` module (`org.springframework.boot.jdbc.autoconfigure`), carrying 9 auto-configuration classes and 272 of its own metadata keys. The old tell I used — `unzip -l spring-boot-autoconfigure-<ver>.jar | grep -ci jdbc` — now returns `0` on 4.0.8 not because JDBC auto-config is gone, but because it moved. A bare `flyway-core` or `jackson-databind` with no starter still sits unbound; the build stays green either way. The fix is the starter, and the build will not complain about the difference.

**2. YAML keys that stop binding with no log line.** This is the one that should scare you most, and the module split above is its root cause. The metadata for a property now lives in the module that owns it — Hikari's `spring.datasource.hikari.*` metadata is in `spring-boot-jdbc`. If that module is not on the classpath, the key is *unclaimed* and silently unbound, with zero log output. My earlier across-all-modules measurement on 4.1.1 showed the total metadata collapsing from **2936 to 1161 keys (-60%)**; the single-jar numbers above show the same split concretely. Change a dependency and your YAML goes blind, silently. The actuator's `configprops` endpoint is the only source of truth.

**3. Tests that compile but run zero times.** I renamed the test class to `OrderApiShould` — a JUnit 5/6 convention some teams use — and re-ran. Surefire reported **BUILD SUCCESS and ran zero tests**. There was not even a "Tests run" line, let alone a `Skipped` count, so my old advice of grepping for `Tests run:.*Skipped` would have found *nothing*. Boot 4's default Surefire includes (`*Test`, `Test*`, `*Tests`, `*TestCase`) do not match `*Should`, `*Spec`, or `*IT`, and Failsafe is not wired by the parent. A renamed or mis-named class is invisible and the build lies. My [JUnit 6 silent-failure write-up](/blog/ai-junit-tests-not-running-spring-boot-4/) walks the exact trap.

**4. The MockMvc security trap — the one that fooled my own first attempt.** I expected a CSRF flip. It was not one. With default CSRF on both 3.5.16 and 4.0.8, a POST without a token returns **403** — I measured the same status on both versions, so the default did not change. The real trap is subtler. When I first rebuilt the test I used `MockMvcBuilders.webAppContextSetup(wac).build()` by hand and forgot `.apply(springSecurity())`. The Spring Security filter chain was never applied, and the same POST returned **200** — a false-green security test. Only `@AutoConfigureMockMvc` (which I had to add as a module anyway) or an explicit `.apply(springSecurity())` wires the chain. So after a migration, the danger is not "CSRF changed"; it is "your security test silently stopped applying the security filter," and it passes while protecting nothing. An agent that "fixed the build" has no trigger to start the app and fire a real request, so it never observes this.

**5. Jackson 3's loud-and-quiet pair.** Boot 4 pulls Jackson 3 (I confirmed the starter resolves it). From my 09-28 serialisation lab, a `spring.jackson.serialization.*` property can fail startup outright on Boot 4 — that one is loud. The quiet neighbour is a hand-rolled `catch (IOException)` around serialisation that stops catching Jackson's exceptions because Jackson 3 changed the exception hierarchy; it produces no compile error and only bites in production when a serialisation failure escapes as an unhandled exception. I flag it as a review item, not a measured break.

## The one behaviour that separates Claude Code from Codex

I want to be precise, because "use Claude Code, it is smarter" is not what my data says. Across my runs the only substantive behavioural difference between the two agents on Boot 4 work is **verification**: Claude Code re-runs the prior version each loop to catch regressions; Codex does not. That is real and it matters on the loud layer, because the agent actually looks at the old behaviour.

But notice the limit. A silent failure is green on *both* the old and the new version. Re-running the prior version therefore still shows green and teaches the agent nothing. The `flyway-core` that sits unbound, the `maxLifetime` key that stopped binding, the test that runs zero times, the MockMvc test that returns 200 — all of those are green on 3.5.16 too. So Claude Code's regression reflex, genuinely useful as it is, does not reach the layer where Boot 4 actually hurts you. The verification advantage is real; it is just orthogonal to the silent-failure problem.

## My Boot 4 migration checklist (when any agent does the upgrade)

After running the migration myself, here is the gate I now run on *any* agent-produced Boot 4 diff, including ones I generate. None of it appears in the agent's summary.

1. **Confirm tests actually execute, not just compile.** Count the executed classes — a mis-named class shows no "Tests run" line and BUILD SUCCESS with zero runs, so grepping for Skipped misses it. My [JUnit 6 silent-failure write-up](/blog/ai-junit-tests-not-running-spring-boot-4/) has the exact trap.
2. **Check the configprops endpoint for properties that stopped binding.** Boot 4 moved metadata into per-module jars, so a key's binder lives in the module, not the core jar. The [dependency silent-failure lab](/blog/codex-spring-boot-4-dependencies-silent-failures/) has the measured numbers.
3. **Verify the split-out modules are present and wired, not just the version number.** `spring-boot-jdbc`, `spring-boot-webmvc-test`, `spring-boot-health` — if one is missing, a library can be on the classpath with nothing configuring it.
4. **Start the app and fire a real POST that actually applies the [Security 7](https://docs.spring.io/spring-security/reference/migration/index.html) filter chain.** And confirm your MockMvc tests apply the security chain too, or you will get a false 200.
5. **Treat "removed deprecated API" as a contract change, not a cleanup.** Every deprecated annotation the agent deletes may have been carrying a check the new code now skips.

## Where AGENTS.md earns its keep

A migration-focused AGENTS.md is where this gets practical. I wrote fifteen lines stating three things: do not reuse Boot 3 starter names, never add only the third-party library artifact itself, and after adding a dependency *prove the feature is actually wired, not just that the build is green*. That last rule is the one my dependency lab proved generalises — it is what stops an agent from calling a red build "fixed" by adding the wrong artifact. The file did not make the agent smarter; it gave it a second feedback loop that encodes my judgement instead of the compiler's.

The honest caveat, which I have learned to state up front: an AGENTS.md only catches what the evidence in the repository can support. For a migration, that means you write the dependency and YAML rules *into* the file, because those are the ones the build will not tell you about.

## The scorecard, and the Copilot echo

Two real Copilot PRs and one real lab run land on the same conclusion my own labs keep landing on: agents are excellent at the half of a Boot 4 migration the compiler can see, and structurally blind to the half it cannot. The Camunda Copilot PR is proof of the first half — a contained, well-scoped migration an agent can finish. The Azure PR, stalled at fifty errors, is proof that the same agent stalls on the sprawling version of the same problem. My lab run is the proof that even the agent with the regression reflex still needs a human at the silent layer, because the things that hurt you after a Boot 4 upgrade are precisely the things that are green on both versions.

The companion piece that judges the same upgrade through someone else's pull requests is the [Copilot PR teardown](/blog/copilot-spring-boot-4-pr-teardown/).

## The takeaway

Point Claude Code, Codex, or any agent at your Boot 4 migration and it will hand you a green build faster than you would have done it by hand, and it will re-run the old version to catch the regressions it can see. Then do the five checks above yourself, because the agent already told you it was done — and on the silent layer, it was not. The tool that verifies is better than the tool that does not, but neither one is a substitute for a checklist written by someone who has already broken the upgrade on purpose.
