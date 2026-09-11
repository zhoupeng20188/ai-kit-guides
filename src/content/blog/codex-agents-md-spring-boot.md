---
title: "An AGENTS.md for Spring Boot That Codex Actually Understands (2026)"
description: "A real AGENTS.md for a Spring Boot project: the layers, bean rules, and build commands I put in so Codex stops guessing. What worked and the traps I hit."
pubDate: 2026-08-28
category: "ai-tools"
tags: ["openai codex", "agents.md", "spring boot", "codex spring boot", "java ai tools", "java-ai-cluster"]
image: "/og-codex-agents-md-spring-boot.jpg"
imageAlt: "A Spring Boot AGENTS.md file open next to the OpenAI Codex CLI, showing layered architecture rules and Maven build commands"
keywords: ["agents.md spring boot", "codex agents.md", "openai codex spring boot", "agents.md example", "spring boot ai coding"]
faq:
  - question: "Does OpenAI Codex read AGENTS.md automatically?"
    answer: "Yes. Codex CLI reads AGENTS.md from the repo root before it touches any code, and it also walks the directory tree so a closer AGENTS.md overrides a farther one. Claude Code does not read AGENTS.md natively (it reads CLAUDE.md); the common bridge is `ln -s AGENTS.md CLAUDE.md` so both tools share one file. I keep AGENTS.md as the source of truth and symlink CLAUDE.md to it."
  - question: "How long should a Spring Boot AGENTS.md be?"
    answer: "Short. The file loads on every turn, so every wasted line costs context and money. I keep the root AGENTS.md under about 120 lines: build/test commands, the layered-architecture rule, three or four non-negotiable bean conventions, a 'do not edit' list (target/, build/, generated sources), and a definition of done. Anything longer, like full DTO field lists, goes in docs/ and gets linked, not pasted."
  - question: "What is the single most useful section in an AGENTS.md?"
    answer: "A 'Definition of done' block that names the exact commands to run. For a Maven project that is `mvn -q test` or `./mvlew build`; for Gradle it is `./gradlew build`. Tell Codex it must actually run the build and not report success without it. That one section cut my 'looks done but doesn't compile' round-trips more than anything else."
---

A few weeks ago I published a piece on [running OpenAI Codex against a Spring Boot project](/blog/codex-spring-boot/). The feedback I kept getting was not about the CLI or the approval modes — it was "how do you actually make Codex *understand* the codebase?" My answer is boring: an `AGENTS.md` file. Not prompts. Not a long intro message every session. One markdown file at the repo root that the agent reads before it does anything.

This article is the companion to [my CLAUDE.md write-up](/blog/claude-code-remember-spring-boot/). Same job, different tool: where CLAUDE.md is what Claude Code reads, AGENTS.md is what Codex (and Cursor, and GitHub Copilot's coding agent, and a couple dozen others) reads. If you run more than one coding agent — and most Spring Boot teams do — AGENTS.md is the one file worth getting right, because it configures several tools at once.

## What AGENTS.md Actually Is

AGENTS.md is plain markdown with no required schema. No frontmatter, no YAML, no special syntax. It is a "README for agents": the same idea as README.md, except it is written for a coding agent instead of a human. You tell it the build and test commands, the code-style conventions, the architectural constraints, and the things it must never touch.

It was introduced by OpenAI in 2025 and is now stewarded by the Linux Foundation's Agentic AI Foundation, with 60,000+ open-source repos adopting it. That governance matters more than it sounds: it means AGENTS.md is not one vendor's convention that competitors merely tolerate. Codex CLI, Cursor, Google Jules, and GitHub Copilot's coding agent all read it. Before this standard existed, every tool had its own file — `.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md` — and teams maintained three copies of the same rules that drifted apart. AGENTS.md collapsed that into one. Claude Code reads CLAUDE.md natively, but the standard bridge is a symlink:

```bash
ln -s AGENTS.md CLAUDE.md
```

After that, one file drives both Codex and Claude Code. I keep AGENTS.md as the source of truth and symlink CLAUDE.md to it — that way I edit once.

## How I Structure It for a Spring Boot Project

Here is the root `AGENTS.md` I ship on a typical Spring Boot service. It is under 120 lines on purpose (more on why that matters below).

```markdown
# AGENTS.md

## What this is
Spring Boot 3 service (Java 21) using Maven. Layered: controller → service → repository.
MapStruct for DTO mapping, Lombok sparingly. PostgreSQL via Spring Data JPA.

## Commands
- Build: `./mvnw -q package -DskipTests`
- Test: `./mvnw test`
- Single test: `./mvnw -pl order-service test -Dtest=OrderServiceTest`
- Run: `./mvnw spring-boot:run`

## Architecture rules (non-negotiable)
- Controllers never inject a Repository. Go controller → service → repository.
- One transaction boundary per service method that writes. No @Transactional on controllers.
- DTOs in `api/dto`; entities in `domain`; mappers in `api/mapper`. Do not put logic in DTOs.
- New endpoints return a standard `ApiResponse<T>` wrapper. Do not hand-build ResponseBody.

## Do not edit
- `target/` — build output, regenerated every build
- `**/generated/` — MapStruct and OpenAPI generated sources
- `src/main/resources/application-prod.yml` — env-specific, edited by ops only

## Definition of done
A task is done only when `./mvnw test` passes. Run it. Do not claim success without it.
```

That is the whole thing. No philosophy, no "write clean code" platitudes. Just the facts that, if missing, make Codex produce code that does not compile or violates our layering.

## The Sections That Actually Change Codex's Behavior

I learned the hard way that most of what people put in an AGENTS.md is decorative. Three sections do the heavy lifting.

**1. The build and test commands.** This is the single highest-value block. If Codex does not know how to build and test *your* project, it will invent a command, fail, and quietly move on. Naming the exact Maven wrapper invocation stopped a whole class of "it looks done" bugs.

**2. A definition of done.** Tell Codex it must run the build and not report completion without it. I cannot overstate how much this helped. Codex is happy to say "done" after an edit that does not even compile. The definition-of-done line is the only thing standing between you and that.

**3. A "do not edit" list.** Spring Boot projects are full of generated code — `target/`, MapStruct mappers, OpenAPI clients. If you let Codex wander in there, it will "fix" a generated file and the next build will overwrite it, or worse, it will hand-edit something the build owns. Listing those paths explicitly is cheaper than explaining it after the fact.

## Cascade: One File Per Module in a Monorepo

If your Spring Boot app lives in a monorepo with several Maven modules, AGENTS.md supports nesting. The nearest file wins. So I keep a short root AGENTS.md with the shared commands, and each module (`order-service/`, `billing-service/`) gets its own AGENTS.md with module-specific rules. Codex walks from the global config down to the file it is editing, and the closer file overrides the farther one.

```text
/
├── AGENTS.md                # shared: Java 21, Maven, run tests
├── order-service/
│   └── AGENTS.md            # order-specific: saga pattern, outbox table
└── billing-service/
    └── AGENTS.md            # billing-specific: idempotency keys, ledger writes
```

This is the same pattern I use for CLAUDE.md, and it is why the two files feel like twins — the structure is identical, only the reader differs.

## Traps I Hit (So You Don't)

**Trap 1: I wrote too much.** My first AGENTS.md was 340 lines — full DTO field lists, every exception type, a style guide. Codex read all of it on every turn, and the signal-to-noise was terrible. Worse, the important rules got buried. I cut it to ~110 lines and moved the long reference material to `docs/`, linked from AGENTS.md. Quality went up, cost went down. Remember: context-file content loads every turn, unlike a skill body that is pulled on demand.

**Trap 2: I assumed Codex reads CLAUDE.md.** It does not, natively. For a week I maintained two files and they drifted — Codex followed AGENTS.md, Claude Code followed CLAUDE.md, and the two said slightly different things about our transaction boundaries. The symlink fix (`ln -s AGENTS.md CLAUDE.md`) ended the drift. Now there is one source of truth.

**Trap 3: Vague rules that change nothing.** "Write clean, maintainable code" is decoration. "Controllers never inject a Repository" is a rule. Early on I had too many soft lines; Codex ignored them because they were not checkable. I rewrote every convention as something verifiable, and the output got noticeably better.

**Trap 4: Secrets and local paths.** I briefly pasted a database URL and a local path into AGENTS.md. Do not. AGENTS.md is committed and read by every agent and every contributor. Keep env-specific values out; point to `application-local.yml` and let the agent load it from the environment, not from the instruction file.

## Local Overrides Without Polluting the Repo

Sometimes you want a rule that applies only to you, not the whole team — say, "skip the integration tests, they need a Docker container I don't have running." Codex supports a local-only `AGENTS.override.md` that is never committed. I add it to `.gitignore` and use it for machine-specific quirks. The root `AGENTS.md` stays clean and shareable; my override handles the local weirdness. The same idea exists for Claude Code as `CLAUDE.local.md`, so the pattern transfers if you symlink the two.

```text
# .gitignore
AGENTS.override.md
CLAUDE.local.md
```

One caveat: the override is read by Codex, but if you symlinked `CLAUDE.md -> AGENTS.md`, Claude Code will not automatically pick up `AGENTS.override.md`. For Claude Code you still need `CLAUDE.local.md`. It is a minor seam between the two tools, worth knowing before you assume one file covers everything.

## A Concrete Before/After

To show the file earns its keep, here is a real edit. Without AGENTS.md, Codex once added a `findAll()` call straight into a controller because "it was faster." With the layering rule written down, the same request came back as a service method that the controller calls. Same feature, but the version with the rule did not force me to refactor the controller an hour later. The file did not make Codex smarter; it made the *constraint* impossible to miss.

I have since measured that on a change with a real blast radius — a [Boot 4 upgrade where the shortest path to a green test is switching CSRF off application-wide](/blog/codex-spring-boot-4-403-fix/). Same model, same prompt, and the only variable was whether the file was in the repository.

That is the whole point. Codex is capable either way. AGENTS.md is what keeps its capabilities pointed at *your* architecture instead of the generic one it learned from everyone else's repos.

## An Honest Take: AGENTS.md Is Policy, Not a Fence

I want to be straight about the limits. AGENTS.md is durable *guidance*, not a hard guardrail. Codex will follow it most of the time, but an explicit instruction in chat overrides the file, and a sufficiently confident wrong turn can still ignore a soft rule. It is not a substitute for the hooks and approval modes I described in the [Codex workflow article](/blog/codex-spring-boot/) — those actually block actions. AGENTS.md tells Codex what you want; approval modes decide what it is allowed to do without asking.

For a Spring Boot team, the combination is what works: AGENTS.md for the "understand my codebase" layer, approval modes (suggest / auto-edit / full-auto) for the "don't surprise me" layer, and a real `./mvnw test` in the definition of done for the "prove it" layer.

## My Recommendation

If you use Codex on a Spring Boot project and have not written an AGENTS.md yet, do it today. Keep it under 120 lines. Lead with the build/test commands and a definition of done. List the layering rule and the generated-code paths you never want touched. Symlink it to CLAUDE.md so Claude Code benefits too. Then watch how many fewer "it compiled on my machine" moments you have.

The file is not magic. It is just the context you would repeat in every chat, written down once. For a codebase with real architecture — which every Spring Boot project is — that context is the difference between Codex guessing and Codex knowing.

Want the broader picture of AI coding agents on Java? Start from the [Java + AI hub](/blog/ai-for-java-developers/), where this fits alongside the Claude Code and Cursor pieces.
