---
title: "Make Claude Code Remember Your Spring Boot Project (2026)"
description: "How I made Claude Code remember my real Spring Boot codebase (CLAUDE.md + auto memory): the rules that stopped it breaking the build, and the traps I hit."
pubDate: 2026-08-19
category: "ai-tools"
tags: ["claude code", "spring boot", "claude code remember", "java ai tools", "claude code setup", "java-ai-cluster"]
image: "/og-claude-code-remember-spring-boot.jpg"
imageAlt: "Terminal showing a Spring Boot project's CLAUDE.md next to Claude Code, with auto memory notes about Java 21 and bean wiring conventions"
keywords: ["claude code remember", "claude code spring boot", "claude code CLAUDE.md", "spring boot ai coding", "claude code setup", "claude code project context"]
faq:
  - question: "Does Claude Code remember my Spring Boot project between sessions?"
    answer: "It remembers whatever you put in CLAUDE.md and whatever it saved to auto memory. The project-root CLAUDE.md is re-read from disk after every /compact, so it survives long sessions. Auto memory lives in ~/.claude/projects/<project-path>/memory/ and is plain markdown you can read, edit, or delete with the /memory command. It does not remember things you never wrote down or that it never chose to save, so do not assume it knows your bean wiring by magic."
  - question: "Where should I put the CLAUDE.md for a Spring Boot app?"
    answer: "Put the team-shared one at the repository root as ./CLAUDE.md (or ./.claude/CLAUDE.md) and commit it. Put personal, machine-specific notes in ~/.claude/CLAUDE.md, which applies to every project. For a multi-module build, add a nested CLAUDE.md inside each module directory; Claude Code lazy-loads those only when it reads files in that subtree."
  - question: "Why does my CLAUDE.md say one thing but Claude Code does another?"
    answer: "CLAUDE.md is injected as a user message after the system prompt, not as a hard rule. Claude tries to follow it but vague or conflicting instructions get ignored or picked arbitrarily. Keep each rule specific ('Use 2-space indentation', 'Do not add dependencies without asking'), avoid contradictions across files, and move anything you must enforce 100% into a hook instead of prose."
  - question: "Can auto memory leak secrets from my Spring Boot project?"
    answer: "It can, in theory, if you paste a real credential into a chat and Claude decides to remember it. Auto memory is just local markdown, not encrypted. I keep application.properties out of scope, tell Claude never to store secrets, and run /memory every couple of weeks to scrub anything sensitive. For shared machines you can also disable auto memory in settings."
---

A few months ago I was using Claude Code on a three-module Spring Boot monorepo and quietly losing patience. It wrote service classes that looked right and compiled in its head, then broke the build because it invented a bean that did not exist. It added a new starter to `build.gradle` instead of using the one already on the classpath. It called my DTOs `Model` when the whole team used `Dto`. None of that was a model problem. It was a memory problem: I had never told the agent how this project actually worked.

I run Claude Code on Claude Sonnet 4.5 for the daily edits and switch to Opus 4.7 when I am asking it to plan a sprawling refactor. Both are sharp. But a sharp model with no project context is just a confident guesser. Once I treated memory as a first-class part of the setup, the breakage dropped off a cliff. This is how I wired it up on a real Spring Boot codebase, the rules that mattered, and the traps I walked into so you do not have to.

## What Claude Code actually "remembers"

People talk about Claude Code memory like it is some mysterious persistent brain. It is not. Under the hood it is file injection. At the start of every session Claude Code collects a set of markdown files and drops their contents into the conversation. That is the whole trick. There is no hidden state, which is honestly a relief: every "memory" is a plain file you can open, read, and delete.

There are two layers that matter for a Spring Boot project.

The first is `CLAUDE.md`, the file you write on purpose. It loads in full every session, no matter how long it is, though shorter files get followed more reliably. There is a hierarchy: an enterprise file at the OS level, a project file at the repo root, a user file in your home directory, and a now-deprecated local file. The project one is what your team shares through git.

The second layer is auto memory. As you work, Claude can decide a fact is worth keeping and write it to `~/.claude/projects/<project-path>/memory/`. An index file called `MEMORY.md` gets loaded at startup (only the first 200 lines or 25KB, whichever hits first), and deeper topic files are read on demand. You can browse all of it with the `/memory` command. I will come back to why that command became part of my weekly routine.

## My project-level CLAUDE.md for a Spring Boot app

This is the file I wish I had written on day one. It is roughly 60 lines, which is deliberate. The official guidance says keep it under 200 lines, and in my experience the shorter it is, the more obedient Claude is. Here is a trimmed version of what sits at the root of my project:

```markdown
# Project: orders-service (Spring Boot 3.5, Java 21, Gradle)

## Stack
- Spring Boot 3.5, Java 21, Gradle (not Maven)
- PostgreSQL via Spring Data JPA; use Flyway for migrations
- Spring Security with JWT, stateless sessions only

## Layout
- com.acme.orders.api       -> REST controllers, request/response DTOs
- com.acme.orders.domain    -> entities, aggregates, domain services
- com.acme.orders.infra     -> JPA repos, external clients, config
- Controllers must NOT contain business logic. Put it in domain services.

## Hard rules
- DTO classes end in `Dto`. Entities end in `Entity`. No `Model` naming.
- Do NOT add new Gradle dependencies without asking first.
- Use Java 21 records for read-only DTOs.
- Run `./gradlew compileJava` after any change that touches wiring.
- Keep transactions on the domain service layer, not the controller.

## Commands
- Build: ./gradlew build
- Run: ./gradlew bootRun
- Tests: ./gradlew test
```

Two lines do most of the heavy lifting. "Do NOT add new Gradle dependencies without asking first" killed the dependency-creep habit. "Controllers must NOT contain business logic" stopped it from bolting logic onto the first class it touched. These are not profound insights, but Claude Code only knows them once you write them down.

If you want the broader workflow this file plugs into, I wrote up my day-to-day [Claude Code + Spring Boot routine](/blog/claude-code-spring-boot/) separately.

## The afternoon it actually saved me

I want to give you a concrete moment, not a vague "it got better." Last month I asked Claude Code to add a `findAllOpenByCustomer` query to the orders module. Old me, no memory, would have gotten a method that compiled and a controller that called it, then a runtime `NoSuchBeanDefinitionException` two minutes later because the repository was never actually wired into the service.

This time, because the CLAUDE.md spells out the layout, Claude created the JPA repository interface in `infra`, injected it into the existing `OrderService` in `domain`, and added a thin controller method in `api` that just delegates. It ran `./gradlew compileJava` itself before reporting done. The build was green. I still read the diff, because I am not reckless, but there was nothing to fix. That single afternoon probably saved me the usual twenty minutes of "why is this bean missing" Googling.

The honest caveat: memory does not make the code correct, only more aligned. I still caught a transaction that was opened on the wrong layer. The file tells Claude where logic should live; it does not guarantee Claude puts it there every time.

## Auto memory is great until it isn't

Auto memory sounds like free documentation, and for a while I loved it. Claude remembered that we use Java 21 records for DTOs and stopped asking. It remembered our Postgres needs a Testcontainers instance for integration tests. Handy.

Then I ran `/memory` out of curiosity and found it had saved a "fact" that our auth used OAuth2. It does not. I had mentioned OAuth2 in passing as something we considered and dropped, and Claude filed it as current state. Left alone, that wrong memory would have steered future sessions. I deleted the file, told Claude explicitly not to record speculative decisions, and now I check `/memory` every couple of weeks.

My rule of thumb: treat auto memory like a junior's notebook. Useful, sometimes wrong, always worth a glance. If a memory looks off, it is a plain markdown file. Edit it or delete it. There is no mysterious backend to fight.

One more warning that bit me once. Auto memory is local markdown, not encrypted. Do not paste real credentials into a chat and assume they stay private. I keep `application.properties` out of scope, tell Claude never to store secrets, and on shared machines I disable auto memory entirely in settings. Secrets belong in your environment or a vault, not in a file Claude reads at startup.

## Soft instructions are not seatbelts

Here is the part I underestimated. `CLAUDE.md` is delivered as a user message after the system prompt, not as a hard constraint. Claude tries to follow it, but vague or conflicting lines get ignored, and when two files disagree it may pick one arbitrarily. So prose alone is not enough for the things you must enforce.

For the rules that really matter, I moved them into hooks, which are shell commands that fire on Claude Code lifecycle events with zero token cost. A `PostToolUse` hook compiles the project after every edit, so a broken bean wiring cannot hide. A `PreToolUse` hook on Bash blocks `git push` so the agent never ships on its own. These actually enforce behavior; `CLAUDE.md` only suggests it. My full setup, including the exact hook config for a Spring Boot build, is in my piece on [Claude Code subagents and hooks](/blog/claude-code-subagents-hooks-spring-boot/).

If you take one thing from this article: use `CLAUDE.md` for guidance, use hooks for guarantees. Mixing them up is how agents quietly do the one thing you told them not to.

## A tip for multi-module Spring Boot builds

If your project is a single module, one root `CLAUDE.md` is enough. Mine is three modules: `api`, `worker`, and `shared`. The root file covers the shared stack, and each module has its own nested `CLAUDE.md` with module-specific rules, like "the worker module must not import web controllers." Claude Code discovers these nested files and lazy-loads them only when it reads files in that subtree, so the agent gets the right context exactly where it needs it without bloating the root file.

You can also split a large root file using `@import` lines, which pull in other markdown files (up to five levels deep). I use that for the long list of Gradle commands so the main file stays short. Both tricks keep the root file under the 200-line mark where adherence stays high.

## What I would do differently

If I started over, I would write the `CLAUDE.md` before the first agent session, not after a week of breakage. I would also keep it shorter; my first draft was 140 lines and Claude followed maybe two-thirds of it. The trimmed 60-line version gets obeyed far more reliably.

The bigger lesson is that memory is a maintenance task, not a one-time setup. Projects drift, conventions change, and auto memory quietly accumulates half-truths. Budget a few minutes every couple of weeks to run `/memory` and re-read your `CLAUDE.md`. It is the cheapest insurance against an agent that slowly drifts away from how your team actually works.

## Wrapping up

Claude Code memory on a Spring Boot project is not magic, and that is the point. `CLAUDE.md` tells the agent your stack, your layout, and your hard rules. Auto memory captures the small facts so you stop repeating yourself, as long as you audit it. Hooks turn the must-never rules into guarantees. Put those three together and the agent stops guessing and starts fitting in.

If you are building out a Java + AI workflow, start from the [Java + AI hub](/blog/ai-for-java-developers/) where I link every article in this cluster, then come back and write your own `CLAUDE.md` today. It took me two afternoons to get right, and I have not had a mystery `NoSuchBeanDefinitionException` since.
