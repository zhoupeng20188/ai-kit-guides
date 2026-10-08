---
title: "I Read 2 Real Copilot Spring Boot 4 PRs. Here Is What AI Missed"
description: "Two real Copilot Spring Boot 4 PRs, judged against my silent-failure lab: what AI migration agents catch, and what they sail straight past."
pubDate: 2026-10-08
category: "ai-tools"
tags: ["github copilot", "spring boot 4", "copilot coding agent", "ai coding agents", "java-ai-cluster", "spring boot migration"]
image: "/og-copilot-boot4-pr.jpg"
imageAlt: "A split view of two GitHub pull requests, one merged and one stalled, overlaid with a checklist of Spring Boot 4 silent-failure points an AI agent missed"
keywords: ["copilot coding agent spring boot 4", "github copilot spring boot 4 migration", "spring boot 4 pr teardown", "ai agent missed boot 4 changes", "camunda copilot spring boot 4", "azure sdk spring boot 4 copilot"]
faq:
  - question: "Did GitHub Copilot successfully migrate a project to Spring Boot 4?"
    answer: "One of the two did. Copilot's branch upgraded Camunda's client artifacts from Spring Boot 3.5.8 to 4.0.0 across a tight, well-scoped set of modules and was merged. A second attempt on the Azure SDK for Java upgraded 68 POM files to 4.0.0-RC2 but stalled with roughly 50 compilation errors in the auto-configuration module and was handed back to humans. The difference tracks the size and shape of the codebase more than the tool."
  - question: "What Spring Boot 4 changes does an AI coding agent catch reliably?"
    answer: "The mechanical, compiler-enforced ones. Package and class renames are the cleanest example: both PRs moved org.springframework.boot.actuate.health to org.springframework.boot.health.contributor and the Jackson auto-configuration import to its new location, because the old imports stop compiling. Copilot also correctly added the new spring-boot-health and spring-boot-jackson modules, and stripped 41 deprecated org.springframework.lang @NonNull annotations that Spring Framework 7.0 rejects. If the compiler yells, the agent fixes."
  - question: "What does an AI agent miss in a Spring Boot 4 migration?"
    answer: "The silent half. Bumping JUnit to 6.0.1 does not prove the tests still execute under Boot 4's new naming rules. Moving configuration metadata into per-module jars means a property can stop binding with zero log output. Spring Security 7 API changes like CSRF need a running app, not a code edit. These are exactly the failures my own Boot 4 labs reproduced, and a coding agent has no signal that tells it they happened."
  - question: "Why did the Azure SDK Spring Boot 4 PR fail to compile?"
    answer: "About 50 errors clustered in the auto-configuration module because roughly seven classes could not find relocated properties classes such as KafkaProperties, RedisProperties and DataSourceProperties. That is the same Boot 4 modularization split that breaks plain dependency upgrades. The agent also ran inside a firewall that blocked it from fetching the Spring Boot 4.0.0-RC2 source tree to verify the API changes, so it was working partly blind and documented the remaining work for a human team instead of merging."
  - question: "Should I let a coding agent do my Spring Boot 4 migration?"
    answer: "Let it do the mechanical layer and review what it returns like a stranger wrote it. Hand it the rename and dependency work, then run your own gates: confirm tests actually execute, check the configprops endpoint for properties that stopped binding, and start the app to catch Security 7 behavior changes. The Camunda PR shows the agent can finish a scoped migration; the Azure PR shows it stalls on a sprawling one. Your job is the half the compiler cannot see."
---

I have spent the last two months breaking Spring Boot 4 migrations on purpose. Not for sport — because every time I hand an AI coding agent a "upgrade this to Boot 4" task, it comes back green and I have learned, the hard way, that green is not the same as correct. So when I stumbled on two *real* GitHub Copilot coding-agent pull requests that attempted exactly this, I could not help judging them against my own silent-failure checklist.

One of them was merged. The other stalled at about fifty compilation errors and was handed back to humans. Both are more honest than any "here is my migration guide" post, because they are what an agent actually produced when a real maintainer pointed it at a real codebase. Here is what Copilot caught, what it sailed past, and the scorecard I would hand any team about to trust an agent with a framework bump. The labs I am judging them against, and the rest of my Java-and-AI work, live in the [Java + AI hub](/blog/ai-for-java-developers/).

## The two PRs at a glance

The first is [camunda/camunda #42114](https://github.com/camunda/camunda/pull/42114), opened from a `copilot/upgrade-spring-boot-to-4-0` branch and merged in December 2025. It bumps the Spring Boot client artifacts from **3.5.8 to 4.0.0**, pins **Spring Framework 7.0.1** and **JUnit 6.0.1**, and touches a contained set of modules that inherit from a shared library parent. Six commits, spotless-formatted, done.

The second is [Azure/azure-sdk-for-java #47195](https://github.com/Azure/azure-sdk-for-java/pull/47195). It tries to add **Spring Boot 4.0.0-RC2** support across **68 POM files**, bumps Spring Framework to 7.0.0-RC3, and was never merged. The agent documented its own remaining work in a `SPRING_BOOT_4_UPGRADE.md` and handed the auto-configuration fixes to a human team. Core modules compiled; the auto-configuration module did not.

Same tool, same target framework, two very different outcomes. The split tells you more about your codebase than about Copilot.

## What the agent nailed: the loud failures

These are the changes a compiler enforces, and Copilot handled them the way I would expect an agent to — because failure is immediate and unambiguous.

**Package relocations.** Both PRs moved imports that no longer exist in Boot 4. Camunda's branch rewrote:

```text
org.springframework.boot.actuate.health
  -> org.springframework.boot.health.contributor   (AbstractHealthIndicator, Health, HealthIndicator)

org.springframework.boot.autoconfigure.jackson.JacksonAutoConfiguration
  -> org.springframework.boot.jackson.autoconfigure.JacksonAutoConfiguration
```

Leave the old import and the build stops before it starts. The agent found every occurrence and fixed it. This is the category where handing the work to an agent is not just faster than a human, it is arguably more reliable across hundreds of files, because the feedback loop is the compiler and the compiler does not get tired.

**The modularization split, caught the right way.** This is the one I want to flag, because it is where my own labs say agents usually go wrong. Boot 4 pulled Spring's auto-configuration apart into per-technology modules. Camunda's agent did not just change versions — it *added* the new `spring-boot-health` and `spring-boot-jackson` modules explicitly, because without them the health indicators and Jackson auto-configuration have nobody to wire them up. In my dependency labs I measured the trap from the other direction: carry a Boot 3 starter spelling forward and a library can sit on the classpath with zero configuration and no warning. Camunda's agent avoided that by adding the split-out modules. That is the loud failure done right — the build fails loudly without them, so the agent had a signal.

**Deprecated API removal.** The Azure PR stripped **41 deprecated `@NonNull` annotations** from `org.springframework.lang`, which Spring Framework 7.0 rejects. Again, compiler-enforced. The agent found and removed all of them.

So far, so good. If your mental model of "AI migration" stops at renames and version bumps, both PRs look like wins.

## What the agent structurally cannot see

Here is the part I care about, and it is the part my labs exist to expose. None of the following breaks the build. All of it changes behavior. An agent has no feedback loop for any of it.

**The JUnit 6.0.1 bump is not the same as "tests still run."** Camunda's PR pins JUnit 6.0.1 "for Spring Boot 4.0 test compatibility." In my JUnit 6 lab I found the real trap is not the version — it is that Boot 4's default Surefire includes do not match `*Should`, `*Spec`, or `*IT` test names, and Failsafe is not wired by the Boot parent. A test class compiled fine and ran **zero** times, with no warning. The agent bumped the version (loud, required) and reported success. Whether those tests still *execute* is a silent question the PR never answers, because nothing in the diff would reveal it. I would not merge a Boot 4 migration without grepping the skip count myself:

```bash
mvn -B verify 2>&1 | grep -E "Tests run:.*Skipped"
```

Any non-zero `Skipped` on a test you expected to run is a green build that is fiction.

**The 50 errors in Azure's auto-configuration module are the modularization split, again.** The PR's own "known issues" list says roughly seven classes could not find relocated properties classes — `KafkaProperties`, `RedisProperties`, `DataSourceProperties`. That is the exact same Boot 4 per-module breakup that bit Camunda's agent (and my labs). The difference is scale: Camunda touched a few modules and finished; Azure touched 68 POM files and the agent could not resolve the relocated classes fast enough to merge. This is the most important pattern in both PRs — the agent is good at the *loud* version of a problem (add a missing module, fix a broken import) and stalls on the *sprawling* version of the same problem.

**Spring Security 7 was filed under "needs review."** Azure's known-issues list includes "Spring Security 7.0 API changes need review" as an open item. In my Security 7 labs I measured the quiet one: CSRF behavior around REST endpoints, where a POST that worked on Boot 3 returns 403 on Boot 4 with nothing useful in the logs, and the rejection actually surfaces as **401** over real HTTP rather than the 403 everyone expects from a unit test. An agent that "needs review" on Security 7 has, in practice, not verified the running app. The compiler will not tell it. Only a live request will.

**The `@NonNull` removals changed a contract, not just a compile.** This is subtle and I think it is the most under-rated risk in the Azure PR. Removing 41 `@NonNull` annotations makes the code compile under Spring 7. But those annotations were null-contract signals. Deleting them is loud (the build demanded it) while the *behavioral* question — do the callers now need null checks the agent never added? — is silent. The agent cannot see it because no tool complains. I am not saying Camunda or Azure shipped a bug here; I am saying the diff that "fixes the migration" can silently move a null-checking responsibility that the compiler will never re-raise.

**The agent was working blind, by policy.** My favorite detail in the Azure PR is in its own log: the firewall blocked it from fetching `api.github.com/repos/spring-projects/spring-boot/git/trees/v4.0.0-RC2` and from reaching `oss.jfrog.org`. The agent literally could not check the upstream source to confirm the API changes it was supposed to adapt to. That is the same wall I hit in my sandbox labs, where an agent cannot diagnose the policy that is restricting it — it reports a confident story about the wrong layer. An agent migrating a framework it is not allowed to read is guessing from error messages, and error messages describe symptoms, not intent.

## The honest scorecard

I am not going to tell you "Copilot is bad at migrations" or "Copilot is great at migrations," because both PRs are sitting there contradicting either claim. Here is what they actually show.

- **A tight, well-scoped migration the agent can finish.** Camunda's client artifacts are a contained surface: a library parent, a Spring Boot starter, a testing example. The agent upgraded versions, fixed the renames the compiler demanded, added the two split-out modules, and merged. That is a genuine win and it is the shape of work I would happily hand to an agent.
- **A sprawling ecosystem migration the agent stalls on.** Azure's 68 POM files, four related Spring sub-projects (Cloud, Integration, Kafka, Security), and a shared version-management system are too wide for one agent pass. It got the versions and the obvious removals done, then documented ~50 errors and a security review as "remaining work." That is also a reasonable outcome — better than a fake-green merge — but it is not "the agent did the migration."

The difference is not the model. It is the blast radius. The agent is a fast, compiler-driven typist; a migration that fits in a handful of modules is a typing problem, and a migration that spans an ecosystem is an architecture problem the compiler cannot see.

## The checklist I now run on any AI Boot 4 PR

After reading these two PRs against my own labs, here is the gate I would apply to *any* agent-produced Boot 4 diff, including my own. None of it is in the agent's summary.

1. **Confirm tests actually execute, not just compile.** Grep the skip count. A renamed test class is invisible to Boot 4's includes and runs zero times silently. (My [Codex JUnit 6 lab](/blog/ai-junit-tests-not-running-spring-boot-4/) walks the exact trap.)
2. **Check the configprops endpoint for properties that stopped binding.** Boot 4 moved metadata into per-module jars, so a key can lose its binder with no log line. The actuator is the only source of truth. (This is the heart of my [YAML silent-failure post](/blog/codex-spring-boot-4-yml-properties/).)
3. **Verify the split-out modules are present and wired, not just the version number.** If `spring-boot-starter-jdbc` or `spring-boot-health` is missing, a library can be on the classpath with nothing configuring it. (The [dependency silent-failure write-up](/blog/codex-spring-boot-4-dependencies-silent-failures/) has the measured numbers.)
4. **Start the app and fire a real POST for Security 7.** CSRF and related changes announce themselves only over real HTTP, and often as 401, not 403.
5. **Treat "removed deprecated API" as a contract change, not a cleanup.** Every deprecated annotation or method the agent deletes may have been carrying a check the new code now skips.

If you want the full frame for where agents help and where they silently fail on this upgrade, the [Spring Boot 4 migration guide I wrote from Spring's own docs](/blog/spring-boot-4-migration-ai-agents/) lays out the two buckets before you point an agent at anything.

## What I would put in AGENTS.md

The single most useful instruction I have found, across every agent I have run, is the one that stops the "get it green" reflex from quietly disabling the thing that was failing. For a Boot 4 migration I would write something like:

```markdown
Never disable, skip, or weaken a test or a verification gate to get a green
build. If a check fails for environmental reasons you cannot resolve, report
the blocker and change nothing. After any version bump, prove the test suite
still executes (not just compiles) and that the app starts and answers a real
HTTP request before declaring success.
```

That one paragraph would have forced the Azure agent to *say* "I cannot verify Security 7 because the firewall blocks the source tree" instead of filing it under "needs review" — which is the difference between an agent that tells you the truth and one that hands you a quiet liability.

## The takeaway

Two real Copilot PRs, judged against a lab that exists precisely to catch silent failures, land on the same conclusion my own runs keep landing on: agents are excellent at the half of a Boot 4 migration the compiler can see, and structurally blind to the half it cannot. Camunda's merged PR is the proof of the first half. Azure's stalled PR, with its 50 errors and its "needs review" security item and its firewall-blind log, is the proof of the second.

Point an agent at your migration. Then do the five checks above yourself, because the agent already told you it was done — and in one of these two cases, it was not.
