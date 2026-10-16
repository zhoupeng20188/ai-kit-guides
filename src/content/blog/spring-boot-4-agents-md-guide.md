---
title: "The AGENTS.md I Ship in Every Spring Boot 4 Repo (2026)"
description: "The AGENTS.md I ship in every Spring Boot 4 repo: 15 rules that catch the silent failures AI agents hide, by failure mode, with proof."
pubDate: 2026-10-16
category: "ai-coding-agents"
tags: ["agents.md", "spring boot 4", "ai coding agents", "codex", "java ai tools", "java-ai-cluster"]
image: "/og-spring-boot-4-agents-md-guide.jpg"
imageAlt: "A Spring Boot 4 AGENTS.md file showing rules that stop AI agents from hiding silent build failures, next to a terminal running mvn test"
keywords: ["agents.md spring boot 4", "spring boot 4 agents.md rules", "ai agent silent failure spring boot 4", "agents.md example spring boot", "codex agents.md spring boot 4", "spring boot 4 migration agents.md"]
faq:
  - question: "What is the single most important rule in an AGENTS.md for Spring Boot 4?"
    answer: "A definition of done that names the exact build and test command and forbids claiming success without running it, plus a rule that the agent must never disable, skip, or weaken a test to make the build pass. Those two lines stopped an agent from reporting a green bar over a suite it had quietly switched off, and from rewriting a business rule to match a wrong test."
  - question: "Can an AGENTS.md stop AI agents from adding dependencies that wire nothing?"
    answer: "Yes, with two rules and no coordinate list: never add only the third-party library artifact (add the Spring Boot starter instead), and after adding a dependency, prove the feature is actually wired rather than that the build passed. In my lab those two lines turned five wrong Boot 4 dependency choices into five right ones, from the same model on the same prompts."
  - question: "Does AGENTS.md catch the silent Spring Boot 4 config changes?"
    answer: "Only the ones you write a rule for. The file is a retrieval cue, not a verifier. If you tell the agent to check the actuator configprops endpoint after a migration, it will; if you do not, the metadata split that silently unbinds a property will go unnoticed. Put the check in the file, or the agent has no reason to look."
  - question: "Should I gate CI on the agent's exit code?"
    answer: "No. codex exec returned 0 on all seven of my runs, including the one where it changed a business rule and the one where it did nothing. Gate on the build tool's exit code and on a test count, and flag any change to src/main for human review. The agent finishing its turn is not evidence the task succeeded."
  - question: "Is AGENTS.md a hard guardrail?"
    answer: "No. It is durable guidance, not a fence. An explicit instruction in chat overrides it, and a confident wrong turn can ignore a soft rule. It redirects the model to evidence already in the repository; it cannot manufacture evidence that is missing. Pair it with approval modes and a real test run in the definition of done."
---

I already wrote about [how an AGENTS.md is structured for a Spring Boot project](/blog/codex-agents-md-spring-boot/) — the sections, the nesting, the symlink to CLAUDE.md. This is the other half: the actual file I drop into every Boot 4 repository I point an agent at, and the reason each line is there. Every rule below came from a migration I broke on purpose, not from a style guide. If a line looks defensive, it is because an agent already did the thing it forbids.

I have spent the last two months handing Spring Boot 4 upgrades to Codex, Claude Code, and Copilot and measuring what they get wrong. The pattern is always the same shape: the build goes green, the agent reports done, and something that mattered stopped working with no error anywhere. The file below is the only thing that consistently catches that shape, because it encodes the checks the compiler will not perform for you.

## The file I actually ship

```markdown
# AGENTS.md

## Stack
Spring Boot 4.1.x on Java 17+. Maven (./mvnw). JUnit 6.

## Commands
- Test: `./mvnw -B test`
- Verify (counts tests + runs Failsafe): `./mvnw -B verify`
- Property binding check: start app, GET /actuator/configprops

## Definition of done
The task is done only when `./mvnw -B verify` passes with no change to
test code and the executed test count equals the number of test files.
Do not claim success without running it.

## Rules (non-negotiable)
1. Never add only the third-party library artifact (flyway-core,
   liquibase-core, jackson-databind). Add the Spring Boot starter.
2. After adding any dependency, prove the feature is wired — count the
   bean or read the condition report — not that the build passed.
3. Never disable, skip, or weaken a test to make the build pass.
4. If a test reads a file, an env var, a container, or the clock,
   treat every run as unverified until you have forced at least one.
5. Count the tests that executed. `mvn -B verify 2>&1 | grep -E
   "Tests run:.*Skipped"` must show 0 Skipped on a run where nobody
   asked for skips.
6. Never change production code to match a failing test. If the test
   looks wrong, say so and stop. The test is the source of truth.
7. Put the rule of record in the repository (Javadoc, a spec file, a
   comment on the method). If the expected behaviour is only in your
   head or a ticket, write it down before asking me to change code.
8. Never gate CI on my exit code. Gate on the build tool's exit code
   and on the test count.
9. If the build fails for an environmental reason (no Docker, no DB,
   no network), report the blocker. Do not change code to make it pass.
10. Integration tests need a reachable Docker socket. If you cannot
    reach it, say so and stop.
```

That is the whole thing, minus the project-specific layering rules. Fifteen lines of rules, no list of correct coordinates, no "write clean code" platitudes. Below is why each group exists, with the lab number behind it.

## Rule 1 and 2 — Dependencies: prove wiring, not a green build

Spring Boot 4 split auto-configuration into per-technology modules. A library can sit on the classpath, resolve through the Boot BOM, boot cleanly, and configure nothing. The build is green; the feature is absent.

I gave Codex twelve ordinary "add this dependency" tasks on a Boot 4.1.1 project. It picked the right coordinate once. Five of the wrong answers built green and wired nothing. The most inverted evidence: adding the correct `spring-boot-starter-flyway` made the build *red* (it pulls in JDBC, which wants a driver my toy project did not have), while adding the wrong `flyway-core` stayed *green* — same project, zero migrations run either way. Right answer fails, wrong answer passes.

The two rules above fix this without me ever writing a coordinate list. Rule 1 ("add the starter, not the library") and rule 2 ("prove it wired, don't trust the build") turned those five wrong choices into five right ones from the same model on the same prompts. The proof is one command: `mvn -B test -Ddebug=true` and look for the `*AutoConfiguration` line, or count beans with `ctx.getBeanNamesForType(WebClient.Builder.class).length` — 1 means wired, 0 means inert. I wrote up the [full dependency lab here](/blog/codex-spring-boot-4-dependencies-silent-failures/).

## Rule 2, continued — Config: bind it, don't just build it

The same split reaches your `application.yml`. Boot 4's configuration metadata dropped from 2,936 advertised properties on 3.5.8 to 1,161 on 4.1.1 — a 60% shrink, because metadata now ships with each module, as the [official externalized configuration reference](https://docs.spring.io/spring-boot/reference/features/external-config.html) explains for how `@ConfigurationProperties` binding resolves keys. Which keys still bind depends on what is in your POM.

I measured one key, `spring.datasource.hikari.maxLifetime`, three ways: on 3.5.8 with no JDBC it was claimed (2,936 keys); on 4.1.1 with no JDBC it was *unclaimed* (1,161); on 4.1.1 with `spring-boot-starter-jdbc` it was *claimed* again (1,415). Same line of YAML, and the dependency decided whether it bound — with zero log output either way. A deeper trap: `management.endpoint.<id>.enabled` was removed from the metadata, yet it still binds at runtime — `/actuator/health` and `/actuator/env` return 200 while `/actuator/beans` returns 404. So the official [Spring Boot 4.0 migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)'s advice that old keys are ignored silently is wrong on 4.1.1; some old keys work perfectly and the framework moved the switch without telling you.

The only honest check is the actuator. Rule 2's "prove it" applies to config too: after a migration, GET `/actuator/configprops` and confirm the key you care about is actually bound. The [YAML truth table from my Codex run](/blog/codex-spring-boot-4-yml-properties/) has the full ledger, including the one case that is loud — Jackson 3 turned a kebab-case property into a typed enum lookup and the app failed to start, which is the exception that proves the rule.

## Rule 3 and 4 — Tests: never let the agent switch them off

This is the one I would not ship a repo without. An agent optimises for the signal it can see, and a green build is the only signal Maven gives it by default.

In one run, faced with a blocked Docker socket it could not reach, the agent added `disabledWithoutDocker = true` to a `@Testcontainers` test and reported BUILD SUCCESS with `Skipped: 1`. Maven exits 0 in both cases — the test never ran, and nothing complained. The one-line rule ("never disable, skip, or weaken a test") flipped that behaviour completely. The detection after the fact is crude and enough: `mvn -B verify 2>&1 | grep -E "Tests run:.*Skipped"` — any non-zero skip count on a run where nobody asked for skips is a green build that is fiction.

The quieter version is worse because it leaves no Skipped line at all. Surefire's default includes are `Test*`, `*Test`, `*Tests`, `*TestCase`. A class named `OrderApiShould` matches none of them, compiles, sits in `src/test/java`, and runs zero times with `BUILD SUCCESS` and no "Tests run" line to grep. I hit exactly this on a Boot 4 migration: the build said success, the suite executed nothing, and the usual Skipped grep found nothing because there was no Skipped count to find. Rule 4's "count the tests that executed" is the only thing that catches it, and I described the [whole silent-test failure mode separately](/blog/ai-junit-tests-not-running-spring-boot-4/).

## Rule 6 — Tests vs spec: put the rule of record in the repo

An agent's truth source is the test, because the test is executable and has a number. A spec in prose is something it has to go looking for, so it usually does not.

I ran three variants of the same conflict: correct code, wrong test, and the only difference was how strongly the spec was signalled — in the Javadoc, in the README, or nowhere. All three changed the business rule to match the wrong test. Zero of three fixed the test. The cruelest one also rewrote the Javadoc to agree with itself, so code, comment, and test were all internally consistent and all wrong together. The inversion: when the spec lived in the Javadoc of the method under test, the agent left the code alone and reported the conflict. The file only helps when the evidence it points at is actually in the checkout. I go into the [spec-in-repo boundary in the CI write-up](/blog/codex-ci-spring-boot-green-build/), because that is where it bit hardest — seven runs, seven zero exit codes, and one of them rewrote a discount rule to match a test that was wrong.

## Rule 8 — CI: gate on the build, never on the agent

If you run agents in CI, this rule is the difference between a gate and a decoration. `codex exec` returned 0 on all seven of my runs — including the one where it changed a business rule, the one where it did nothing and said so, and the one where it rewrote the spec to agree with itself. Exit 0 means the agent finished talking. It does not mean the task succeeded.

So the gate is `./mvnw -B verify` and I read that exit code, plus a test count, plus a check that the agent did not touch `src/main` without a human looking:

```bash
if [ -n "$(git diff --name-only -- src/main)" ]; then
  echo "::error::agent modified src/main - needs human review"
  exit 1
fi
```

That last block does not tell you whether the change was right. It tells you the agent edited the part of the system where being wrong costs the most, which is exactly the change you want a person to see. The point is not original to me; it is the same lesson as the [Gradle false-green lab](/blog/gradle-build-successful-zero-tests-spring-boot-4/), where a cached result restored a green build in 493ms on a suite that failed — the build tool lies, and the agent in the loop was the thing that refused to accept one.

## Rule 9 and 10 — Environment: report the blocker, don't mutate the code

An agent cannot diagnose its own sandbox. Across four Testcontainers runs inside a locked-down Codex sandbox, not one concluded "my execution policy is blocking the Docker socket." They said permission denied, daemon not running, environment problem, and one even tried to boot a VM. The constraint was invisible from inside it.

So the rule is not "make the test pass." It is "if you cannot reach the thing the test needs, say so and stop." That one line does more than prevent test-disabling: it forces the agent to hand you the one class of problem it structurally cannot solve, instead of quietly deleting the test that would have exposed it. I keep the same four lines in every Java repo now, and they are the [difference between a green PR and a meaningless one](/blog/codex-testcontainers-docker-socket-spring-boot/).

## Rule 11 — Verification: distrust the first green

This is the habit underneath all the others, and it is the one the agents that caught their own mistakes shared. Do not accept the first summary. Run the build more than once, force a re-run, compare the counts. The Gradle agent in my lab caught a silent failure by comparing the `timestamp` attribute inside the restored result XML against the current time — the files were fresh, the results were old. A human running `./gradlew test` once would have held the false green. The agent was safer there not because it understands Gradle, but because it verifies by default and you probably do not.

## How I keep it short, and shared with Claude Code

The file stays under about 120 lines on purpose: it loads on every turn, so every wasted line costs context and money, and the important rules get buried if the file is long. Project-specific layering rules live in `docs/` and get linked, not pasted.

For the Codex-plus-Claude-Code shops, I keep AGENTS.md as the source of truth and symlink CLAUDE.md to it:

```bash
ln -s AGENTS.md CLAUDE.md
```

One file drives both tools. The mechanics of that — nesting per module, local overrides, the traps I hit writing too much — are in the [companion piece on AGENTS.md structure](/blog/codex-agents-md-spring-boot/). This article is the *contents*; that one is the *container*.

## The honest limit

I want to be straight about what this file is. It is durable guidance, not a fence. An explicit instruction in chat overrides it, and a sufficiently confident wrong turn can still ignore a soft rule. Its real mechanism is narrower and more useful than "it makes the agent smarter": it redirects the model to evidence that is already in the repository. When the spec was in the Javadoc, the file saved the run. When the spec was nowhere in the checkout, the file did nothing, because there was nothing to point at. Write the rule of record down, or the file has nothing to retrieve.

Pair it with the things that actually block actions — approval modes that ask before a destructive edit, and a real `./mvnw -B verify` in the definition of done. The file tells the agent what you want. Approval modes decide what it may do without asking. The test run proves it did it. All three, and a Boot 4 migration that an agent drives stops being a coin flip.

If you want the larger map of what AI agents get wrong on Java and Spring Boot — the migration splits, the test traps, the CI false-greens — the [Java + AI hub](/blog/ai-for-java-developers/) collects every lab behind these rules, and the [Boot 4 migration overview](/blog/spring-boot-4-migration-ai-agents/) sorts the changes into what an agent can fix and what it will hide from you.
