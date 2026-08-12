---
title: "Claude Code with Spring Boot: A Practical Workflow"
description: "How I actually use Claude Code on a Spring Boot project in 2026: setup, CLAUDE.md, running the build, and the habits that keep the AI from drifting off."
pubDate: 2026-07-31
category: "ai-tools"
tags: ["claude code", "spring boot", "ai coding", "java ai tools", "claude code workflow", "java-ai-cluster"]
image: "/og-claude-code-spring-boot.jpg"
imageAlt: "Terminal running Claude Code inside a Spring Boot project, showing the AI editing Java files and running the Maven build"
keywords: ["claude code spring boot", "claude code with spring boot", "claude code spring boot tutorial", "ai coding spring boot", "spring boot ai workflow"]
faq:
  - question: "Is Claude Code good for Spring Boot development?"
    answer: "Yes, especially for tasks bigger than a single file: adding an endpoint end to end, wiring a service through the layers, or writing tests. It can read the whole repo, run ./mvnw test itself, and act on its own failures. For tight one-file edits I still prefer Cursor, but Claude Code is the better tool when the change touches several files or needs the build to verify it."
  - question: "Which Claude model should I use in Claude Code for Java work?"
    answer: "As of late July 2026, Claude Code ships with Claude Sonnet 5 as the default (1M-token context, cheap introductory pricing). Use it for daily coding. Switch to Claude Opus 5 for the hardest refactors or architecture decisions where deeper judgment is worth the higher token cost. You pick the model with /model inside a session."
  - question: "Do I need a CLAUDE.md for a Spring Boot project?"
    answer: "Strongly recommended. Put the build commands, your layering rules, your DTO and validation conventions, and one rule that saves the most pain: 'run ./mvnw test and only report done if it passes.' Without it, Claude Code writes plausible code that was never actually compiled or tested in your project."
  - question: "Can Claude Code run my Spring Boot tests?"
    answer: "Yes. It can run ./mvnw test or ./gradlew test inside the session and read the output. The habit that matters is making it run the tests as part of the task and only tell you it is finished when they are green. A green build is not proof the code is correct, but a red build is proof it is not done, and that check catches most of the obvious mistakes."
---

I've been a Java backend engineer longer than I'll admit, and for most of that time "AI coding" meant a Copilot autocomplete or a chat window where I pasted snippets back and forth. Claude Code changed that for me on Spring Boot work, but not in the magic way the demos show. The first week I tried it, it "refactored" a service and quietly broke a validation path I didn't notice until the next morning's build went red.

So this is not a "10x your Spring Boot productivity" post. It is the actual workflow I've landed on after a few months of using Claude Code on real Spring Boot services, including the parts where it still makes me nervous. If you want the big-picture "be careful on legacy code" version, I wrote that separately in [using AI on a legacy Java codebase](/blog/using-ai-legacy-java-codebase). Here I'm focused on the day-to-day: how I set it up, what I tell it, and how I keep it from wandering off.

## Why I Reach for Claude Code on Spring Boot

I like Cursor's in-editor flow, and I've written about its [rules system](/blog/cursor-rules-tutorial) at length. But when the task is bigger than a single file, I want an agent that can poke around the whole repo, run the build, and read its own test failures instead of guessing. Claude Code lives in the terminal and treats your project like a real workspace, not a chat box with a file attached.

My rough split: Cursor for tight, watch-every-keystroke edits; Claude Code for "go figure out how this works and wire it up across the layers." Both are Claude under the hood as of mid-2026, but the shape of the work decides which one I open.

## Getting It Running on a Spring Boot Project

Install is boring and that's good:

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

Then `cd` into your project and just run `claude`. First launch asks about permission handling. I keep the default (it prompts before running commands) and switch into plan mode when I want to see a diff before anything touches disk. You can cycle into plan mode by pressing `Shift+Tab`, which is the setting I use most for anything I'm not 100% sure about.

A nice detail: on a fresh checkout, run `/init` and Claude Code will offer to draft a `CLAUDE.md` from your source. I let it, then throw half of what it writes away. The generated file is a decent skeleton, but it guesses at conventions it can't really know. The file you keep should be yours, not its.

As of late July 2026 the default model in Claude Code is **Claude Sonnet 5**, with a 1M-token context window that comfortably holds a medium Spring Boot service. For the occasional gnarly refactor I switch to **Claude Opus 5** with `/model`. The 1M context is the part I underrated at first. It means the agent actually reads the controller, the service, and the repo together instead of working from a snippet I pasted.

## The CLAUDE.md That Actually Helps

This is the meat of the workflow, and where most of the value lives. A useful Spring Boot `CLAUDE.md` is short and concrete. Here is close to what I run on a Spring Boot 3.4 / Java 21 / Maven app:

```markdown
## Project
- Spring Boot 3.4, Java 21, Maven. Use the wrapper: `./mvnw`.
- Layering: controller -> service -> repository. No business logic in controllers.
- MapStruct for DTO mapping. Lombok is allowed but not @Builder on entities.

## Conventions
- Constructor injection only. Records for read DTOs.
- Validation lives in the DTO via Bean Validation, not in the service.
- Return `ResponseEntity<T>`; route all errors through the global
  `@RestControllerAdvice`, never inline try/catch in controllers.
- Tests: JUnit 5 + AssertJ; MockMvc for controllers, @DataJpaTest for repos.

## Commands
- Build and test: `./mvnw -q test`
- Run locally: `./mvnw spring-boot:run`
- Do NOT run `./mvnw clean` in a session unless I explicitly ask. It is
  slow and wipes target, which wastes the next build.

## Rules
- After any change, run `./mvnw -q test` and only tell me you are done
  if it passes.
- Match the surrounding style of the file you edit. If it uses explicit
  types and for-loops, do not "modernize" it to streams.
```

Two things in there earn their place. The "run `./mvnw -q test` and only report done if it passes" line is the single instruction that has saved me more time than anything else. On its own, Claude Code will happily hand you a diff it never compiled. That one sentence forces it to find its own compile errors and failing tests before it talks to you. The "do not modernize to streams" line stops the habit I hate most: it rewrites a clean file into its own dialect and the repo slowly stops looking like itself.

If your project is old and tangled, the constraints need to be tighter, and I cover that deeper in the [legacy Java piece](/blog/using-ai-legacy-java-codebase). For a normal Spring Boot app, the file above is enough to make the agent behave.

## My Actual Daily Loop

The tool is only as good as the loop around it. Here is how I drive it on a typical task:

1. **Make it explain before it edits.** I start with "read `OrderService` and tell me what `finalizeOrder` does and who calls it." If the explanation is vague or wrong, that's my early warning that it doesn't understand the terrain, and I don't let it touch anything yet.
2. **One intent per prompt.** "Add a paginated GET endpoint for orders" is a task. "Also fix the logging and tidy the DTOs while you're in there" is three tasks wearing a trench coat. I keep them separate so the diff stays reviewable.
3. **Force the build check.** I bake this into the request: "after your change, run `./mvnw -q test` and only tell me it's done if it passes." When it fails, I make it read the failure and fix it, not summarize it.
4. **Review the diff like a stranger wrote it.** `git diff`, read every line. The agent is fast and confident; I am slow and skeptical. That pairing is the point.

It sounds slow. It is slower than letting the agent run wild for five minutes. It is much faster than a red build the next morning.

## A Concrete Example: Adding a Paginated Endpoint

Last week I needed `GET /api/orders?page=&size=` with a total count. I told Claude Code: scaffold the controller method, a service call that returns a `Page<OrderDto>` using the existing `OrderRepository`, map with the existing MapStruct mapper, and write one MockMvc test that asserts the page size and status 200.

It came back about six minutes later with a controller, a service method, a repo query, the DTO mapping, and a test, then reported the test had passed. On my own that's roughly twenty minutes of boilerplate plus the test. The paging was correct. What it got wrong: it named the response DTO `OrderPageResponse` while my convention is `PagedOrderResponse`, and it used field injection in the test config. Both were small, both showed up in the diff, and I fixed them in a minute.

That's the real shape of the win. It does the bulk of the mechanical work, makes fewer silly mistakes than I'd make typing at 11pm, and I still own the final five percent and the judgment.

## Where It Still Trips Up

I won't pretend it's clean. A few honest failure modes I hit regularly:

- **Performance it can't see.** It'll write a query that passes the test and then does an N+1 against the database under real load. Unit tests never catch that, and neither does the agent unless you point it at it.
- **Over-eager polish.** Left to its own devices it renames things and "modernizes" code. The `CLAUDE.md` style rule helps but doesn't fully stop it, especially deep into a long session.
- **Config drift.** It has edited `application.yml` in a way that changed a profile I wasn't thinking about. Now I keep `application*.yml` out of scope unless I name it explicitly.
- **Green build is not correct.** The build passing means it compiles and the tests it wrote pass. It does not mean the behavior is what the business wanted. That part is still on me, and I treat the agent's "done" as "compiles and is worth reading," not "ship it."

If you want the broader mindset for not trusting confident output, the habits in [avoiding AI hallucinations](/blog/ai-hallucination-tips) apply here too: verify against reality, don't trust the summary it writes for you.

## Summary

Claude Code earns its place on Spring Boot work the moment a task spans more than one file. The setup that makes it useful is small: install it, run `/init` then trim the `CLAUDE.md`, and put two rules in that file, the build command and the "only say done if tests pass" line. Drive it with explain-first, one intent per prompt, and a real `git diff` review at the end. Use Sonnet 5 for the daily work and Opus 5 for the refactors that need judgment. Do that, and it becomes a fast pair of hands that compiles its own code. Skip the discipline, and it becomes the fastest way yet to merge something that builds green and behaves wrong.


If you want the full map of how I use AI across Java and Spring Boot — every tool, every failure mode — I pulled it together in my [AI for Java Developers guide](/blog/ai-for-java-developers/).
