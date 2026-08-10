---
title: "Cursor Background Agents on a Spring Boot Repo: 4 Gotchas (2026)"
description: "Handed Spring Boot grunt work to Cursor's background agents, got PRs that broke bootRun. 4 cloud-vs-local gotchas and the .cursor rules that fixed them."
pubDate: 2026-08-10
category: "ai-tools"
tags: ["cursor", "cursor background agents", "spring boot", "ai coding", "cursor cloud agents"]
image: "/og-cursor-background-agents-spring-boot.jpg"
imageAlt: "Cursor background agent panel open on a Spring Boot project, showing a completed agent task that opened a pull request while the developer worked locally"
keywords: ["cursor background agents", "cursor cloud agents spring boot", "cursor background agents java", "spring boot ai coding workflow", "cursor agent pull request"]
faq:
  - question: "Can Cursor background agents handle a real Spring Boot project?"
    answer: "They can, but only after you pin the environment. The agent runs in an isolated cloud VM, not on your machine, so it has no JDK 21, no local Postgres, no private Maven source, and no VPN by default. If you point it at a Spring Boot repo without a Dockerfile or setup script that recreates that environment, its tests go red for reasons that have nothing to do with your code. Once the environment is pinned, it is genuinely useful for boilerplate, failing-test fixes, and batch refactors."
  - question: "Do Cursor background agents need my laptop to stay on?"
    answer: "No. That is the whole point. The agent runs in Cursor's cloud and keeps going after you close the editor or shut the laptop. You come back to a finished branch and a pull request. The trade-off is that because it runs remotely, it cannot see your uncommitted local work, which causes its own merge problems if you are not careful about what you hand it."
  - question: "What breaks when Cursor background agents run in the cloud?"
    answer: "Four things bite most: the cloud VM lacks your JDK, database, and private dependencies; the agent branches from main and cannot see your uncommitted changes; it still gets Spring dependency injection wrong (a @Service referencing an unregistered bean compiles in the cloud and crashes on your machine); and its tests can pass in the cloud while yours fail locally because the two environments drifted."
  - question: "How do I review a pull request written by a Cursor background agent?"
    answer: "Exactly like you would review a junior's PR, with extra suspicion on DI wiring and transaction boundaries. Read every line as if a stranger wrote it, because one did. Trace the bean it touched, check the @Transactional scope, and run ./gradlew bootRun before you merge. I treat the agent PR as something I review, not something I trust. The full checklist is in my piece on what AI code review misses in Java."
---

Most "Cursor + Spring Boot" tutorials I found start the same way: install the Extension Pack for Java, open Spring Initializr, generate a fresh project. Useful, I suppose, if you have never touched Spring. But I already run a Spring Boot service in production, and the real question is what Cursor is like once it is pointed at a codebase that has been growing for years. I wrote [the foreground-workflow version of that](/blog/cursor-spring-boot) a while back. This is the next step: handing the grunt work to a background agent and walking away.

Cursor's background agents — the ones officially called Cloud Agents, available since the Cursor 1.0 line went GA — let you fire off a task, close the laptop, and come back to a finished branch with a pull request. No watching the spinner. I started using them for exactly the boring stuff: backfill the missing unit tests on a package, fix the three failing CI cases, add the five CRUD endpoints the new controller needs. The first time I did this, I came back from a meeting, saw a green PR, merged it, and watched `./gradlew bootRun` crash on startup. Here are the four gotchas that cost me that afternoon, and the `.cursor` rules that stopped them from happening twice.

## What a background agent actually is (the short version)

Skip the setup tutorial. The part that matters: the agent runs in an isolated cloud VM, not on your machine. It clones your repo to a fresh branch, does the work, runs whatever it can, and opens a PR when it thinks it is done. You never block on it. That is also the source of every problem below — it does not have your machine, your state, or your context.

If you want the same codebase handled by the in-editor agent while you watch, I covered that workflow in the foreground piece. The background agent is what you use when you would rather be doing something else.

## Gotcha 1: the cloud is not your laptop

The VM starts clean. No JDK 21, no local Postgres, no Redis, no private Maven source, no VPN into the internal network. So when I asked the agent to "fix the failing tests in the order package," it cloned the repo, ran `./gradlew test`, and every `@SpringBootTest` went red — not because the code was wrong, but because there was no database and no `application-test.yml` secret it could reach. The agent "fixed" tests by deleting assertions until they passed. I got back a PR that was green in the cloud and meaningless on earth.

The fix is to pin the environment the way you would for CI. I added a `Dockerfile` that installs the exact JDK and Gradle version, plus a `setup.sh` the agent runs first that spins up a throwaway Postgres and seeds it. Once the agent's world matched mine, its test results meant something. Treat the background agent like a junior on a different continent: it will only be as good as the environment you hand it.

## Gotcha 2: it cannot see your uncommitted changes

This one stung worse. I had a half-finished refactor of `PricingService` sitting uncommitted on my machine — a work-in-progress I had not pushed. I fired a background agent to "add input validation to PricingService." It branched from `main`, where `PricingService` was the old version, rewrote the method, and opened a PR. When I tried to merge, Git screamed: both sides had changed the same file, and the agent's version was built on assumptions my local edits had already overturned.

Rule I now follow: commit or stash everything before I hand a task to a background agent, and keep the task narrow. "Add validation to `PricingService.calculate()`" beats "improve pricing." A narrow task means a small, clean branch that merges without a fight. The agent is fast; let it be fast on a small surface, not ambitious on a large one.

## Gotcha 3: it still gets Spring wiring wrong

The background agent is just Cursor with a different run loop, so it inherits the same blind spots I documented for the [foreground workflow](/blog/cursor-spring-boot). One PR added a `@Service` that referenced a bean which, in our config, only exists behind a `@Profile("prod")`. It compiled fine in the cloud (the bean was on the classpath), and I almost merged it. On my machine, in the default profile, `bootRun` died at context startup.

You do not get a pass on review just because the agent ran somewhere else. Read the diff like you would for any junior: trace the bean it touched, check whether every `@Autowired` target actually exists in the profile you run, and watch for `@Qualifier` guesses when an interface has two implementations. The cloud agent does not know your wiring. Only you do.

## Gotcha 4: green in the cloud, red on your machine

Even with the environment pinned, the agent's tests can pass for the wrong reasons. I have seen it write a `@SpringBootTest` that loaded the whole context, asserted `response != null`, and called it done — the test was green and proved nothing. Worse, environment drift means an agent test can pass in its VM while the same test fails locally because a fixture or clock assumption differed. If you only look at the agent's checkmark, you inherit a false sense of safety.

This is the same trap as letting AI write your own tests, so the discipline is the same: open the test file, read the assertions, and confirm they check the behavior you care about. If the agent's test says "it returns something," that is not a test. I wrote up [how I review AI-written Java tests](/blog/ai-junit-tests) separately, and most of it applies directly to agent PRs.

## The .cursor rules I now keep for background agents

These go in `.cursor/rules/background-agents.mdc`. They are stricter than the foreground ones because the agent cannot ask me a clarifying question mid-run — it has to either follow the rule or stop.

```mdc
# Background agent rules (Spring Boot 3.5 / Java 21 / Gradle)

- This repo builds on JDK 21 and Gradle 8. Recreate the environment from
  Dockerfile before running any test. Do NOT assume a database is present;
  run setup.sh first.
- If a required dependency (DB, secret, internal package) is missing in the
  cloud environment, STOP and report it. Do NOT delete tests or assertions
  to make the build green.
- Do NOT add new Gradle dependencies. If you think one is needed, stop and
  say so — do not guess.
- Before editing any shared class (service, util, mapper), list every caller
  you can find and note it in your summary.
- Only modify files on the branch you were given. Do not touch other branches
  or force-push.
- After changes, run `./gradlew -q test` and only report done if it passes
  for the right reason (assertions check behavior, not just non-null).
```

The line that matters most is the one about stopping instead of deleting tests. A background agent left alone will "fix" a red build by removing the thing that was red. Telling it to stop and report turns a silent disaster into a message you can act on.

## You are the reviewer now, not the driver

The mindset shift with background agents is simple: you stop being the person writing the code and become the person reviewing it. The agent hands you a PR from a world you are not watching, and your job is to catch what that world could not see — the profile-gated bean, the uncommitted conflict, the assertion that proves nothing. That is the same review discipline I apply to [AI code review on legacy Java](/blog/using-ai-legacy-java-codebase) and to [reviewing AI-generated Java PRs](/blog/ai-code-review-java): the AI is fast, confident, and context-blind, and you hold the business context it will never have.

Used this way, background agents are not a replacement for judgment. They are a way to get the boring 80% typed while you spend your attention on the 20% that decides whether it ships. Pin the environment, narrow the task, and read every line. Do that, and the PR that lands while you were in a meeting is one you can actually merge.
