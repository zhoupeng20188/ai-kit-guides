---
title: "Claude Code Subagents & Hooks on Spring Boot: My Guardrails (2026)"
description: "How I use Claude Code subagents and hooks on Spring Boot: real .claude configs that stop an agent from breaking the Gradle build or skipping tests."
pubDate: 2026-08-12
category: "ai-tools"
tags: ["claude code", "claude code subagents", "claude code hooks", "spring boot", "ai coding", "java-ai-cluster"]
image: "/og-claude-code-subagents-hooks-spring-boot.jpg"
imageAlt: "A terminal showing Claude Code running inside a Spring Boot project, with a hook log line reporting a blocked gradle change"
keywords: ["claude code subagents spring boot", "claude code hooks spring boot", "claude code guardrails", "claude code agents java", "claude code spring boot advanced"]
faq:
  - question: "What are Claude Code subagents?"
    answer: "Subagents are specialized agents you define in .claude/agents/*.md with a name, a description, the tools they may use, and the model they run on. The main Claude Code session delegates a focused task to one — for example, a spring-data-reviewer that only checks JPA queries and transaction boundaries — then folds the result back into your session. They keep the main context window clean and let you run focused work in parallel."
  - question: "What are Claude Code hooks?"
    answer: "Hooks are shell commands that fire on Claude Code lifecycle events — PreToolUse, PostToolUse, PreCompact, and a few others — with zero token cost. A PostToolUse hook can compile your project after every edit; a PreToolUse hook on Bash can block git push or rm -rf. They are the closest thing to a seatbelt for an autonomous coding agent, and unlike CLAUDE.md prose they actually enforce behavior."
  - question: "Can a hook stop Claude Code from adding Gradle dependencies?"
    answer: "Yes. I run a PostToolUse hook that checks whether build.gradle or build.gradle.kts changed; if it did, the hook prints a warning and asks me to review the diff before I accept. It does not silently block the agent, but it makes dependency creep impossible to miss — which is exactly how AI coding assistants tend to sneak in a new starter instead of using what is already on the classpath."
  - question: "Do hooks replace reading the code myself?"
    answer: "No. A hook that runs ./gradlew compileJava catches compile errors, and one that runs tests catches red builds, but neither proves the code is correct. I still treat every agent diff like a junior's pull request, with extra suspicion on dependency injection and transactions. My full Java-specific checklist is in my piece on what AI code review misses in Java."
---

I wrote about my [basic Claude Code workflow on Spring Boot](/blog/claude-code-spring-boot/) a few weeks ago — setup, CLAUDE.md, running the build, the habits that keep it from drifting. That post covered the day-one setup. This one is about what I added once the novelty wore off and the agent started doing things I did not ask for.

The tipping point was a Tuesday. I asked Claude Code to add a single REST endpoint. It did — and also "tidied" a neighboring service, bumped a transitive dependency in `build.gradle`, and never ran the tests. The endpoint worked. The dependency bump quietly changed the runtime behavior of an unrelated module. I only caught it because the next deploy's smoke test failed.

That is the moment subagents and hooks went from "nice to have" to "non-negotiable" in my setup. Here is what I actually run.

## Subagents: delegate the boring, isolate the risky

A subagent is a specialist you define in `.claude/agents/<name>.md`. The frontmatter sets its name, a description (when the main agent should delegate to it), which tools it may use, and which model runs it. The main session hands it a focused job and gets a result back, without that job's context polluting your main thread.

I keep two in every Spring Boot repo:

**`spring-data-reviewer`** — tools: Read, Grep. Model: Sonnet. Its only job is to read a diff and flag JPA N+1 queries, missing `@Transactional` boundaries, and `EntityGraph` misuse. Because it can only read and search, it cannot "helpfully" rewrite anything; it just reports. I fire it after any change touching the persistence layer.

**`gradle-specialist`** — tools: Read, Bash (limited to `./gradlew dependencies`). It explains what a dependency change actually pulls in, before I accept it. This is the antidote to the Tuesday incident.

The win is twofold. First, my main context stays clean — a 40-file refactor does not bury the actual task in noise. Second, I can run several of these in parallel: one reviewing the data layer, one checking the controller tests, one auditing the build file. Claude Code schedules them and merges the findings.

Two caveats from experience. Subagents do not see your main session's full conversation, so if a task needs the whole-architecture view, do it in the main thread — a subagent will happily rebuild something the main agent already decided against. And they cost tokens; for a one-line change, do not bother.

## Hooks: the seatbelt that costs zero tokens

If subagents are about dividing work, hooks are about enforcement. A hook is a shell command that runs on a Claude Code lifecycle event — `PreToolUse` (before a tool runs), `PostToolUse` (after), `PreCompact`, and a few others. They spend no tokens deciding anything; they just run, like a git pre-commit hook with more trigger points.

Here is the relevant slice of my `settings.json`. The exact field names for passing tool input to the command vary slightly by Claude Code version — check `claude hooks` in your installed build — but the structure is stable:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "if git diff --stat | grep -q 'build.gradle'; then echo '[guard] build.gradle changed — review dependencies before accepting'; fi"
      },
      {
        "matcher": "Edit|Write",
        "command": "./gradlew compileJava -q || echo '[guard] compile failed — agent edit did not build'"
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "grep -Eq 'git push|rm -rf' && { echo '[block] destructive command blocked'; exit 1; }"
      }
    ]
  }
}
```

What each one buys me:

- **The `build.gradle` check** turns dependency creep from invisible into unmissable. The agent can still add a starter, but I cannot merge the diff without seeing the warning. This single hook would have caught the Tuesday incident.
- **The compile check** runs `./gradlew compileJava` after every file edit. It is fast, and it eliminates the entire class of "looks done, was never compiled" mistakes before I ever read the diff. A red build is the cheapest signal I have.
- **The Bash guard** blocks `git push` and `rm -rf` from running without me. An autonomous agent that can both edit and push is one typo away from a bad afternoon. I run the push myself.

One hard lesson: a hook that exits non-zero on a logic error will stall the agent, because Claude Code treats a failed hook as "the action did not happen." Keep hooks defensive and quiet. Print a warning, return 0, and let the human decide. The destructive-command block is the only one I let fail the action, and even there I keep the match list tiny.

## The config I actually keep in the repo

Both the `.claude/agents/` directory and `settings.json` live in the repo and get reviewed in pull requests, exactly like code. That matters: a guardrail someone can silently delete is not a guardrail. The `spring-data-reviewer` agent and the three hooks above are now part of every Spring Boot project I touch, and onboarding a teammate means copying one directory.

If you want the foundation first, my [Claude Code Spring Boot workflow post](/blog/claude-code-spring-boot/) covers CLAUDE.md and the daily loop. These hooks and agents are the layer I bolt on once that baseline is solid.

## What hooks do NOT replace

A hook that runs the build catches compile errors. A hook that runs `./gradlew test` catches red builds. Neither proves the code is right — only that it runs. I still read every agent diff like a junior's PR, with extra suspicion on dependency injection and transaction boundaries; the specifics are in my [notes on what AI code review misses in Java](/blog/ai-code-review-java/). And the tests a hook runs green are only as good as the assertions, which is the whole point of [reviewing AI-written JUnit tests properly](/blog/ai-junit-tests/).

The honest summary: subagents and hooks did not make Claude Code flawless. They made the failure modes loud instead of silent. For an autonomous agent on a real Spring Boot codebase, that is most of the battle — and it is the part no CLAUDE.md sentence ever enforced.


If you want the full map of how I use AI across Java and Spring Boot — every tool, every failure mode — I pulled it together in my [AI for Java Developers guide](/blog/ai-for-java-developers/).
