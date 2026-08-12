---
title: "Cursor with Spring Boot: A Practical Java Workflow (2026)"
description: "How I use Cursor on a real Spring Boot codebase in 2026: project rules, the prompts that work, and the bean-wiring traps that break the build."
pubDate: 2026-08-03
category: "ai-tools"
tags: ["cursor", "spring boot", "ai coding", "java ai tools", "cursor workflow", "java-ai-cluster"]
image: "/og-cursor-spring-boot.jpg"
imageAlt: "Cursor editor open on a Spring Boot Java project, showing the Agent panel editing a @Service class and the Gradle build output"
keywords: ["cursor spring boot", "cursor with spring boot", "cursor spring boot tutorial", "spring boot ai coding", "cursor java workflow"]
faq:
  - question: "Can Cursor handle a real Spring Boot project?"
    answer: "Yes, as long as you let it index the codebase and give it project rules. Out of the box Cursor knows Java syntax but not your bean wiring, your layering, or your DTO conventions. Point it at the repo, write a .cursor/rules file with your stack and a couple of hard rules, and it becomes useful fast. Without the rules it produces plausible code that quietly breaks the build."
  - question: "Is Cursor or IntelliJ better for Spring Boot?"
    answer: "They are not either-or. I use Cursor as the daily driver for AI-assisted edits, scaffolding, and in-editor help, and I keep IntelliJ for deep refactors and tracing dependency injection by hand. Cursor's Spring Boot Tools integration is good but it does not match IntelliJ's refactoring or its bean graph. Use Cursor for speed, IntelliJ for the careful work."
  - question: "Does Cursor write good Spring Boot tests?"
    answer: "It writes tests that compile and pass, but they often prove nothing: an assertNotNull on the response, a happy path with no edge case, a context that loads the whole app and runs slow. Treat every AI-written test as a draft you must read, not a result you can trust. Verify the assertions actually check the behavior you care about."
  - question: "How do I stop Cursor from adding Gradle dependencies?"
    answer: "Put one hard rule in your .cursor/rules file: 'Do NOT add new dependencies without asking first.' Then make a habit of diffing build.gradle after every change. Cursor tends to drop in a new starter to solve a problem instead of using what is already on the classpath, and that dependency creep is easy to miss in a large diff."
---

Most "Cursor + Spring Boot" tutorials I found start the same way: install the Extension Pack for Java, open Spring Initializr, generate a fresh project. Useful, I suppose, if you have never touched Spring. But I already run a Spring Boot service in production, and the real question is what Cursor is like once it is pointed at a codebase that has been growing for years. That is the part nobody writes about.

I have been writing Java backend code since before Spring Boot existed, and I picked up Cursor about a year ago after years of IntelliJ plus Copilot. This is not a "Cursor replaced my job" story. It is the workflow I have settled on for real Spring Boot work: how I point it at the code, what I tell it, and the three traps that have bitten me more than once. If you want the same codebase seen through Claude Code, I wrote [that version too](/blog/claude-code-spring-boot).

## Why Cursor, Not Just IntelliJ or Claude Code

I keep both Cursor and Claude Code installed, and they do different jobs. The split for me is simple: Cursor for tight, watch-it-happen edits and fast in-editor help; Claude Code for "go wander the whole repo and wire this up." Cursor's strength is that the AI sits inside the editor. Cmd+K handles a targeted change, Tab gives completions that know the surrounding method, and the chat sees the file you have open. When I am fixing a bug in one service, I do not want an agent spawning subagents. I want a smart autocomplete with a chat box.

That said, Cursor is not IntelliJ. The Spring Boot Tools integration is decent, but it will not match IntelliJ's refactoring or its bean graph. I still open IntelliJ when I need a careful rename across forty files or have to trace a dependency injection chain by hand. Cursor is the daily driver; IntelliJ is the specialist tool I keep around.

## Getting Cursor to Actually Understand Your Project

The setup tutorials tell you to install plugins. I will skip that. The thing that matters for Spring Boot is letting Cursor index the codebase and giving it rules.

First, open the project and let Cursor build its index. In recent Cursor builds this uses secure codebase indexing, and for a medium Spring Boot service it takes a minute or two on first open. Do not skip it. Without the index, `@Codebase` answers are guesses, and the Agent panel reads the wrong files.

Then create a project rules file. Rules live in `.cursor/rules/`. I keep one called `spring-boot.mdc`. Here is roughly what mine says for a Spring Boot 3.5 / Java 21 / Gradle app (most shops I know are still on 3.4–3.5, not the bleeding edge, and the rules are identical):

```markdown
---
description: Spring Boot conventions for this project
globs: ["src/main/java/**/*.java"]
alwaysApply: true
---

## Stack
- Spring Boot 3.5, Java 21, Gradle. Use the wrapper: `./gradlew`.
- Layering: controller -> service -> repository. No business logic in controllers.
- MapStruct for DTO mapping. Constructor injection only.

## Conventions
- Match the surrounding style. If a file uses explicit types and for-loops,
  do not "modernize" it to streams.
- Validation lives in the DTO via Bean Validation, never in the service.
- Return ResponseEntity<T>; route errors through the global
  @RestControllerAdvice, not inline try/catch.

## Hard rules
- Do NOT add new Gradle dependencies without asking me first.
- Before editing a shared @Service or @Repository, list every caller.
- After any change, run `./gradlew -q test` and only say done if it passes.
```

Two lines in there have saved me more times than I can count. "Do NOT add new Gradle dependencies without asking" because Cursor loves to solve a problem by dropping in a new starter instead of using what is already there. And "list every caller before editing shared logic." That one is the difference between a clean diff and a 2am production incident, and I will get to why in a second.

## The Prompt Patterns I Actually Use

Cursor's chat is only as good as what you type. After a lot of trial and error, these four patterns are the ones I reach for constantly:

1. **"Follow the existing package structure and naming. Don't create a new package."** Left alone, Cursor will happily invent `com.example.demo.featureX` because that is what the demos show. My repo has opinions; this reminds it.
2. **"Use constructor injection and match the project's Lombok style."** Without this it slips into field injection (`@Autowired` on a field), which my team banned years ago. Now it matches.
3. **"List every place that calls `X` before you change it."** This is the one I lean on hardest for services shared across controllers. I will expand on the trap below.
4. **"Reuse the existing MapStruct mapper; do not write a new one."** Cursor will recreate mapping logic inline instead of using the mapper that already exists, and then the two drift apart.

None of these are magic. They are just the things I would tell a new teammate on day one, written down so the AI does not have to guess. If you want the deeper version of writing these rules, I covered the [Cursor rules system](/blog/cursor-rules-tutorial) separately.

## A Real Example: Adding a Feature End to End

Last month I needed a "retry failed webhooks" admin endpoint on a service I had inherited. I opened Cursor's Agent panel (Cmd+I) and typed: "Add POST /admin/webhooks/retry that takes a list of ids, calls the existing `WebhookRetryService.retry(id)`, and returns a count of successes. Use the existing `WebhookRepository`, reuse the `WebhookMapper`, and write one MockMvc test that posts two ids and asserts 200 and a body count of 2."

About four minutes later it came back with the controller, the wiring, and a test that passed. Honestly, that is the part Cursor is great at: the mechanical scaffolding across layers. What it got wrong: it declared the request DTO as a class when my convention is records for input DTOs, and it added `spring-boot-starter-validation` to build.gradle even though validation was already on the classpath through another starter. Both showed up in the diff. Both took me a minute to fix. The dependency one I would have missed if I had not trained myself to scan build.gradle first.

## The Three Traps

This is the part I wish someone had told me.

**Trap 1: bean wiring looks fine, breaks at startup.** Cursor edited a `@Service` and referenced a helper bean that existed, but it was `@ConditionalOnProperty`-guarded and off in the profile I was running. It compiled clean and failed at `ContextLoader` startup. The fix is the "list every caller" rule plus actually running the app or a context-load test, not just `./gradlew compile`.

**Trap 2: it adds dependencies.** Covered above, but it is worth repeating because it is the most common one. New starters in build.gradle "just to be safe." Always diff the build file.

**Trap 3: green tests that prove nothing.** Cursor's generated `@SpringBootTest` will often assert `assertNotNull(response)` and call it a day. The test passes, the build is green, and the actual behavior is unverified. I treat any AI-written test as a draft I have to read, not a result I can trust. This is the same discipline I wrote about for [legacy Java codebases](/blog/using-ai-legacy-java-codebase): the AI is fast and confident and context-blind, and you hold the business history.

There is also the N+1 problem, and Cursor is just as blind to it. A query that passes the test can still hammer the database in production. Unit tests do not catch that.

## Review Like It's Legacy Code

I will keep this short because I have said it before, but it is the whole ballgame: read the diff like a stranger wrote it, because one did. `git diff`, line by line. The agent is fast; you are the skeptic. For the deeper mindset on not trusting confident AI output, the habits in [avoiding AI hallucinations](/blog/ai-hallucination-tips) apply here too.

## Summary

Cursor is my daily driver for Spring Boot not because it is magic, but because it sits inside the editor and handles the mechanical 80% fast. The setup that makes it trustworthy is small: let it index, drop a `.cursor/rules/spring-boot.mdc` with your stack and two hard rules (no new deps, list callers before editing shared logic), and review every diff like legacy code. Use it for tight edits and scaffolding; reach for [Claude Code](/blog/claude-code-spring-boot) when the task spans the whole repo and needs to run the build itself. Do that, and Cursor becomes a fast pair of hands that compiles its own code. Skip the discipline and it becomes the fastest way yet to merge something that builds green and behaves wrong.


If you want the full map of how I use AI across Java and Spring Boot — every tool, every failure mode — I pulled it together in my [AI for Java Developers guide](/blog/ai-for-java-developers/).
