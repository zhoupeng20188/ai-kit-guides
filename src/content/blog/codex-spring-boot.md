---
title: "OpenAI Codex with Spring Boot: A Practical Workflow (2026)"
description: "How I use OpenAI Codex on a real Spring Boot project in 2026: AGENTS.md, approval modes, the cloud sandbox, and the habits that stop it breaking the build."
pubDate: 2026-08-24
category: "ai-tools"
tags: ["openai codex", "spring boot", "ai coding", "java ai tools", "codex cli", "java-ai-cluster"]
image: "/og-codex-spring-boot.jpg"
imageAlt: "Terminal running OpenAI Codex inside a Spring Boot project, showing the AGENTS.md file and a passing Maven test run"
keywords: ["openai codex spring boot", "codex spring boot", "openai codex java", "codex cli spring boot", "openai codex tutorial", "spring boot ai coding"]
faq:
  - question: "Is OpenAI Codex good for Spring Boot development?"
    answer: "Yes, but it fits a different job than Claude Code or Cursor. Codex is built for delegation: you hand it a scoped task like 'fix this issue and open a PR', it runs in an isolated sandbox, runs the build, and comes back with a diff. It is excellent for well-scoped, testable Spring Boot tasks and for batching several of them in parallel. For tight edits where you want to watch every keystroke, Cursor is still my pick, and for interactive 'let's work through this together' sessions I reach for Claude Code on Spring Boot."
  - question: "What is AGENTS.md and do I need one for a Spring Boot app?"
    answer: "AGENTS.md is Codex's project-instructions file, the OpenAI equivalent of the CLAUDE.md that Claude Code reads. Drop one at your repo root and Codex reads it before every task. For a Spring Boot app put your build command (./mvnw or ./gradlew), your layering rules, your DTO and validation conventions, and the single most useful line: 'run the build and only report done if it passes'. Codex also supports cascading AGENTS.md, so a monorepo can have a per-module file that overrides the root."
  - question: "Which Codex model should I use for Java work?"
    answer: "As of mid-2026 Codex runs on OpenAI's GPT-5.6 family, which ships in three tiers: Sol (the flagship, for the hardest work and deep refactors), Terra (the balanced everyday tier, and the default for daily Java edits), and Luna (the fast, cheap tier for high-volume grunt work). OpenAI renames these fairly often, so treat the exact label as a snapshot and check what your dashboard or `codex --version` shows. The practical advice does not change: use Terra for daily edits, escalate to Sol for gnarly refactors, and drop to Luna for bulk tasks. The model name matters far less than giving Codex a clear task and a real build check."
  - question: "Does Codex run locally or in the cloud?"
    answer: "Both. The Codex CLI is open source (Apache 2.0) and can run locally against your own machine, authenticated with a ChatGPT account or an OpenAI API key. Codex Cloud runs each task in an isolated sandbox that you trigger from the dashboard or by tagging @codex in a GitHub issue or PR. The sandbox is great for safety but it cannot reach your internal Maven mirror, your database, or anything on your local network, which is the single biggest gotcha for Spring Boot work."
---

I've been a Java backend engineer longer than I care to admit, and most of my AI coding setup this year has been Claude Code for the interactive sessions and Cursor for the in-editor edits. Then OpenAI's Codex got good enough that I started handing it actual Spring Boot work, and the experience was different enough from Claude Code that it earned its own writeup. Not because it's "better" in some headline sense, but because the workflow is a different shape and pretending the two are interchangeable cost me a messy afternoon.

So this isn't a "Codex beats Claude Code" post. It's the setup I've actually landed on for running Codex on a Spring Boot monorepo in 2026: how I install it, what goes in AGENTS.md, which approval mode I trust next to a Java build, and the ways it has quietly torn up my morning. If you want the interactive counterpart, I wrote about [Claude Code on Spring Boot](/blog/claude-code-spring-boot/) separately, and the deeper "teach the agent your codebase" angle lives in [making Claude Code remember a Spring Boot project](/blog/claude-code-remember-spring-boot/).

## Why Codex Is a Different Animal

The thing that confused me at first is that "Codex" is now two products wearing one name. There's the open-source Codex CLI that runs in your terminal, and there's Codex Cloud, the async agent you trigger from a dashboard or by tagging @codex in a GitHub issue. The CLI runs locally; Cloud spins up an isolated sandbox per task. Both are the same agent, just a different surface.

The mindset difference from Claude Code is the part that matters. Claude Code is interactive: you watch it work, you approve the risky steps as they come up. Codex is built for delegation. You describe a task, walk away, and come back to a diff or a pull request. I'll queue three small Codex tasks, close the laptop, and review the results after dinner. You can't really do that with Claude Code in the same fire-and-forget way, and you don't want to babysit Codex the way you babysit Claude Code. That split is the whole reason I bother keeping both installed.

Under the hood it runs on OpenAI's GPT-5.6 family (Sol / Terra / Luna at the time I'm writing this). OpenAI has renamed these models a few times in 2026, so check what your dashboard says and don't treat the labels as permanent. Terra is the default for day-to-day work; Sol is the tier I reach for on the hardest refactors, and Luna is the fast, cheap option I use for high-volume grunt work. It also supports MCP servers and Skills (SKILL.md), so the ecosystem overlap with Claude Code is bigger than you'd expect.

## Getting It Installed (and the Auth Trap)

Install is the usual npm story:

```bash
npm install -g @openai/codex
codex --version
```

The trap is authentication. The CLI wants either a ChatGPT account or an OpenAI API key, and which one you use changes your billing. The ChatGPT account path is bundled into a Plus or Pro plan but moves to credit-based, token-metered billing, which I'll complain about later. The API-key path is pay-per-token. I started on the account path, hit a wall the first time I tried to run it in a CI script, and had to switch to an API key there. If you're automating anything, set the key up front and save yourself the confusion.

One nice detail: Codex reads an `AGENTS.md` from your repo, and it will offer to draft one on first run. I let it, then threw half of it away, exactly like I do with Claude Code's `/init`. Generated instruction files guess at conventions they can't actually know, and the file you keep should be yours.

## The AGENTS.md That Actually Helps

This is where most of the value lives, and it's the direct twin of the CLAUDE.md I described for Claude Code. A useful Spring Boot `AGENTS.md` is short and concrete. Here is close to what I run on a Spring Boot 3.4 / Java 21 / Maven app:

```markdown
## Project
- Spring Boot 3.4, Java 21, Maven. Use the wrapper: `./mvnw`.
- Layering: controller -> service -> repository. No business logic in controllers.
- MapStruct for DTO mapping. Constructor injection only.

## Conventions
- Records for read DTOs. Validation in the DTO via Bean Validation, not in the service.
- Return `ResponseEntity<T>`; route errors through the global
  `@RestControllerAdvice`, never inline try/catch in controllers.
- Tests: JUnit 5 + AssertJ; MockMvc for controllers, @DataJpaTest for repos.

## Commands
- Build and test: `./mvnw -q test`
- Do NOT run `./mvnw clean` unless I explicitly ask.

## Rules
- After any change, run `./mvnw -q test` and only tell me you are done
  if it passes.
- Match the surrounding file style. Do not "modernize" working code to streams.
```

The "only say done if tests pass" line is the single instruction that has saved me the most time across every coding agent I use. On its own, Codex will happily hand you a diff it never compiled. That one sentence forces it to find its own compile errors and failing tests before it talks to you.

Codex also supports cascading AGENTS.md, which Claude Code does too. In a multi-module build I drop a tighter file in the module that needs it, and Codex reads the more specific one when it's working in that subtree. That's genuinely handy in a monorepo where the payments module has rules the shared library doesn't.

## Approval Modes: Why I Don't Run Full-Auto on Java

Codex has three approval modes: `suggest` (proposes everything, you approve), `auto-edit` (edits files freely, asks before shell commands), and `full-auto` (runs the whole loop including commands, in a sandbox with network off). Full-auto is tempting because it feels like the future, and for a clean throwaway branch it's fine. On a real Spring Boot working copy it's how you lose an afternoon.

The problem is that full-auto with network disabled will still run `./mvnw clean` if it decides the build is stale, wipe `target`, and then sit there unable to reach your internal Nexus mirror to re-download a dependency. It also can't reach your database, so any test that expects a live datasource just fails in the sandbox and Codex reports "tests failed" with no obvious reason. On Java, I keep Codex on `suggest` almost always. `auto-edit` is the middle ground I use for refactoring a single module where I trust the file edits but want to eyeball the commands.

This is the one place where I miss Claude Code's hooks. Claude Code lets me write a script that blocks `rm -rf` or `./mvnw clean` no matter what mode I'm in. Codex enforces safety at the OS level with a coarse sandbox rather than fine-grained rules, so you get strong isolation but weak "don't touch that specific file" control. For trusted code on my own machine, Claude Code's hooks are the better governance story. I say that as someone who likes Codex.

## The Cloud Sandbox Is Both the Best and Worst Part

The sandbox is Codex's headline safety feature and its biggest Spring Boot gotcha at the same time. When Codex Cloud runs your task, it does so in an isolated container with restricted file and network access. That's great when you're reviewing an untrusted PR or letting it run something you don't fully trust. It's maddening when your test suite assumes a database on localhost.

What bit me: I handed Codex a task that included an integration test hitting a Postgres on my machine. Locally it was green. In the sandbox, Postgres wasn't there and network was off, so the test failed and Codex spent its budget refactoring the test instead of the feature. Now I scope Codex tasks to things covered by `@DataJpaTest` with an embedded or testcontainer database, or I run the verification locally after it hands back the diff. The lesson is simple: if the task needs your real network or your real database, treat Codex Cloud as a code generator and do the verification yourself.

## A Concrete Example: "Fix This Issue and Open a PR"

Last week a teammate filed a bug: pagination on `GET /api/orders` ignored the sort parameter and silently returned insertion order. I tagged @codex on the issue with a one-line brief: "sort by `createdAt desc` when no sort param is given, add a test proving it, open a PR." About fifteen minutes later I had a branch, a three-line controller change, a new test, and a PR description in my inbox.

What it got right: the fix was correct, and the test actually proved the regression. What it got wrong: it added the sort inside the controller instead of pushing it down into the repository query method, which is exactly the layering rule my AGENTS.md says not to break. The AGENTS.md slowed it down but didn't fully stop it, same as with every agent. I moved the logic down into the repo in about a minute and merged. That's the real shape of the win: it does the bulk of the mechanical work and I own the last five percent and the judgment.

I review every Codex diff like a stranger wrote it, because a stranger effectively did. `git diff`, read every line, run `./mvnw -q test` on my machine even when Cloud says it passed. The agent is fast and confident; I am slow and skeptical. That pairing is the point.

## Where Codex Still Trips Up on Spring Boot

I won't pretend it's clean. The failure modes I hit most:

- **The network wall.** Anything that needs your Maven mirror, your database, or an internal service simply doesn't run in Cloud. Plan around it or run locally.
- **Credit billing stings.** OpenAI moved Codex to token-metered credits in April 2026, and a Spring Boot build with a long tool-call loop burns through them faster than the flat-rate days. I watch the dashboard now the way I used to watch my cloud bill.
- **No persistent local state.** Each Cloud task starts from a fresh checkout of what you gave it. It doesn't remember your last session's context the way a long Claude Code session can, so you re-explain the terrain every time unless AGENTS.md carries it.
- **Business logic it can't see.** It will write code that compiles and passes the tests it wrote, then get the business rule subtly wrong because the rule was never in the issue. A green build is not a correct behavior, and that part stays on me.
- **Weaker enforcement than hooks.** As I said, the sandbox is coarse. If you need "never touch this file" governance, Claude Code's hooks still win.

## Summary

Codex earns a permanent spot in my Spring Boot toolkit the moment a task is scoped, testable, and safe to delegate. My setup is small: install the CLI, write a tight AGENTS.md (build command plus the "only done if tests pass" rule), keep approval on `suggest` for anything on a real working copy, and do the final verification on my own machine when the task needs a database Cloud can't reach. Use it for "go fix this and open a PR" fire-and-forget work, where its async, parallel nature beats sitting in a terminal watching Claude Code think. Reach for [Cursor](/blog/cursor-spring-boot/) when you want to watch every edit, and [Claude Code](/blog/claude-code-spring-boot/) when you want to work through a hard refactor interactively. Do that, and Codex becomes a reliable junior pair that ships its own PRs. Skip the discipline, and it becomes the fastest way yet to merge something that builds green and behaves wrong.

For the full map of how I run AI across Java and Spring Boot, every tool and every failure mode, I pulled it together in my [AI for Java Developers guide](/blog/ai-for-java-developers/).
