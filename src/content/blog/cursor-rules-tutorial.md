---
title: "Cursor Rules Tutorial: Make AI Write Code the Way You Do"
description: "An engineer's guide to Cursor rules in 2026: why .cursorrules is dead, how .cursor/rules works, and the setup that makes AI write code like you."
pubDate: 2026-07-15
category: "ai-tools"
tags: ["cursor rules", "cursorrules", "cursor ai", "ai coding tools", "cursor tutorial"]
image: "/og-cursor-rules-tutorial.jpg"
imageAlt: "Cursor editor showing a .cursor/rules directory with .mdc rule files controlling how the AI writes code"
keywords: ["cursor rules tutorial", "cursorrules", ".cursor/rules", "cursor project rules 2026", "cursor mdc rules"]
faq:
  - question: "Is .cursorrules still supported in 2026?"
    answer: "It still works for backward compatibility, but it is legacy. Cursor now recommends the .cursor/rules/ directory with .mdc files. More importantly, a single root .cursorrules file is often ignored in Agent mode, so relying on it will quietly bite you."
  - question: "What is the difference between .cursorrules and .cursor/rules?"
    answer: ".cursorrules is a single Markdown file at your project root (the old format). .cursor/rules/ is a directory of .mdc files, each with its own metadata and activation mode. The new format lets you scope rules to specific files, keep them modular, and control exactly when each rule loads."
  - question: "What are the four Cursor rule activation modes?"
    answer: "Always (injected into every request), Auto Attached (loads when files matching a glob are in context), Agent Requested (the AI decides based on the rule's description), and Manual (only loads when you reference it with @). Choosing the right mode is what keeps your context window from bloating."
  - question: "Why is Cursor ignoring my rules?"
    answer: "The most common reason in 2026 is using a root .cursorrules file with Agent mode, which often skips it. Other causes: the rule's activation mode never triggers, the glob pattern doesn't match your files, or the rule is too long and vague. Move to .cursor/rules/*.mdc and set an explicit activation mode."
---

The first time I set up Cursor rules, I did it wrong and did not even know it. I dropped a `.cursorrules` file at my project root, filled it with my Java conventions — constructor injection, no field injection, SLF4J for logging, AssertJ in tests — and felt very organized. Then I spent two weeks wondering why Agent Mode kept handing me `@Autowired` field injections and `System.out.println` calls like I had written none of it down.

Turns out I had written it down. Cursor was just ignoring the file. If you are here because your rules "aren't working," that is very likely your problem too, and this tutorial is going to fix it.

## What Cursor Rules Actually Are

Cursor rules are persistent instructions you give the AI so you stop repeating yourself. Instead of typing "use constructor injection" in every single prompt, you write it once as a rule, and Cursor injects it into the model's context automatically. Think of it as a [harness](/blog/harness-engineering) around the AI — the guardrails that make its output consistent with how your team actually writes code.

Without rules, Cursor writes generic, tutorial-flavored code: the kind you would find in a Medium post from 2022. With good rules, it writes code that looks like it came out of your repo. That is the whole point of this — not magic, just removing the gap between "technically correct" and "the way we do it here."

## The Big Change: .cursorrules Is Legacy Now

Here is the part almost every outdated tutorial gets wrong, and the reason my early setup failed.

There are two formats, and they are not equal:

- **`.cursorrules`** — a single Markdown file at your project root. This is the **legacy** format. It still works for backward compatibility, but Cursor is actively steering people away from it. The critical gotcha: in Agent Mode, a root `.cursorrules` file is frequently **ignored outright**. It was designed for the older chat/edit flow, and the agent does not reliably pick it up.
- **`.cursor/rules/*.mdc`** — a directory of `.mdc` (Markdown + metadata) files. This is the **current** format. Each file is a self-contained rule with a header that tells Cursor *when* to load it. This is what you should be using in mid-2026.

When I moved my conventions out of the root `.cursorrules` and into `.cursor/rules/java-style.mdc`, the difference was immediate. The field injection stopped. The logging came out as SLF4J. Same instructions, different file location — and suddenly the agent actually read them.

If you take one thing from this tutorial: **stop using the root `.cursorrules` file, especially if you live in Agent Mode.**

## The Four Activation Modes (This Is the Real Skill)

The `.mdc` format's superpower is that each rule declares *when* it should load. This matters more than the rule content itself, because dumping everything into "always on" bloats your context window and makes the model dumber, not smarter. This is basically [context management](/blog/loop-engineering) applied to your editor.

There are four modes:

1. **Always** — the rule is injected into every single request. Use this only for truly global conventions (your language version, your core architectural rules). Keep it short. Everything you put here is tax you pay on every prompt.
2. **Auto Attached** — the rule loads only when a file matching a glob pattern is in context. This is the one I use most. Example: a `*.test.java` glob that loads my testing conventions only when I am touching tests. My React rules never pollute my backend work, and vice versa.
3. **Agent Requested** — you write a description, and the AI decides whether the rule is relevant to the current task. Powerful but less predictable; the quality depends entirely on how clearly you describe the rule.
4. **Manual** — the rule only loads when you explicitly reference it with `@ruleName`. Good for occasional, heavy rules you do not want running all the time (like a full API design checklist).

The mistake beginners make — the one I made — is putting everything on Always. Your context fills up with React rules while you are writing SQL, the model gets distracted, and output quality drops. Scoping rules with Auto Attached globs is where the real leverage is.

## My Actual Setup (Steal This)

Here is roughly what my `.cursor/rules/` directory looks like on a Spring Boot project. I am keeping it real — this is not a demo, it is close to what I actually run.

**`.cursor/rules/core.mdc`** (Always, kept deliberately short):
> - Java 21. Use records for DTOs, sealed classes where they fit.
> - Constructor injection only. Never field injection, never `@Autowired` on fields.
> - Logging via SLF4J. Never `System.out.println` in production code.

**`.cursor/rules/testing.mdc`** (Auto Attached, glob `**/*Test.java`):
> - JUnit 5 + AssertJ. No Hamcrest, no raw `assertEquals`.
> - One assertion concept per test. Name tests `should_doX_when_conditionY`.
> - Mock external dependencies with Mockito; never hit a real DB in unit tests.

**`.cursor/rules/api.mdc`** (Agent Requested, described as "REST controller and endpoint conventions"):
> - Return `ResponseEntity`. Validate inputs with Bean Validation.
> - Errors go through the global `@ControllerAdvice`, never inline try-catch in controllers.

Notice the structure: a tiny always-on core, and everything else scoped so it only shows up when relevant. That is the entire trick.

## Writing Rules That Actually Work

A few things I learned the hard way after my rules got ignored (or worse, followed too literally):

- **Be specific and concrete.** "Write clean code" does nothing. "Constructor injection only, never field injection" changes the output. The model cannot act on vibes.
- **Keep each rule short.** A 600-line rule file is worse than three focused ones. Long rules dilute attention and blow your context budget. If you have read my [Cursor deep-dive](/blog/cursor-ai-editor-tutorial), you have seen how fast context fills up in real work.
- **One concern per file.** Testing rules in one file, API rules in another. This lets you scope activation properly and makes rules easy to maintain.
- **Show, do not just tell.** For tricky conventions, include a tiny code example inside the rule. The model mirrors examples far more reliably than prose.
- **Do not restate the obvious.** You do not need to tell a 2026 model what a `for` loop is. Spend your rule budget on the things it would *not* guess — your team's specific choices.

## When Rules Won't Save You

I want to be honest, because too many tutorials oversell this. Rules are not a substitute for reviewing the diff. Cursor will still occasionally ignore a rule under a long, messy context, or follow it in a way you did not intend. On big refactors, the further into a task the agent gets, the more the earliest rules seem to fade. I have caught it drifting back to old habits after 15 minutes of agent work.

Rules also cannot fix a bad prompt. If your request is vague, no amount of rule-writing rescues it — that is still on your [prompt skills](/blog/prompt-engineering-techniques). Rules set the baseline behavior; the prompt still steers the specific task.

And they will not enforce architecture decisions the way a linter or a test does. If something absolutely must not happen, encode it in a test or a CI check, not just a rule. A rule is a strong suggestion, not a hard gate.

## How to Start Today

Do not overthink it. Here is the 15-minute version:

1. Delete or ignore your old root `.cursorrules` if you have one.
2. Create `.cursor/rules/core.mdc`, set it to Always, and put your 3–5 most important global conventions in it. Keep it under 20 lines.
3. Add one Auto Attached rule for whatever you touch most — tests, or a specific framework — with a glob that matches those files.
4. Work for a day. Every time Cursor does something that makes you sigh and fix it by hand, ask: "Is this a rule I should have written?" If yes, add it.

That last loop is the whole game. Your rule set should grow out of real friction, not a template you copied from someone else's blog. Mine took about two weeks of small additions before Cursor genuinely started feeling like it had read my mind.

## Summary

Cursor rules are the difference between an AI that writes generic code and one that writes *your* code. The two things that matter most in 2026: stop using the legacy root `.cursorrules` file (it gets ignored in Agent Mode), and move to `.cursor/rules/*.mdc` with deliberate activation modes so you only load what is relevant. Start with a short always-on core, scope everything else with globs, and grow the set from real friction. Do that, and Cursor stops arguing with your style and starts matching it.
