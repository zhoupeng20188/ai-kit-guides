---
title: "Using AI on a Legacy Java Codebase (What Actually Works)"
description: "A senior Java engineer's real lessons on using AI to change legacy code: undocumented patches, shared multi-channel logic, and how to fence the AI in."
pubDate: 2026-07-22
category: "ai-tools"
tags: ["legacy java", "ai coding", "claude code", "legacy code refactoring", "java ai tools"]
image: "/og-legacy-java-ai.jpg"
imageAlt: "A senior engineer using an AI assistant to safely modify a large legacy Java codebase full of undocumented patches"
keywords: ["ai legacy java code", "using ai on legacy code", "claude code java", "ai refactoring legacy java", "ai change old code"]
faq:
  - question: "Can AI safely refactor a legacy Java codebase?"
    answer: "It can help, but not autonomously. On legacy code the danger is not the code the AI writes, it is the code it touches. Undocumented patches and shared logic mean a 'simple' change can break things nobody connected to it. Use AI for small, well-scoped diffs you review line by line, and fence it in with a CLAUDE.md and existing tests. Do not let it run large multi-file refactors unattended."
  - question: "Why does AI keep breaking other parts of my old code?"
    answer: "Because legacy code is full of shared logic and side effects the AI cannot see from the snippet you gave it. In multi-channel systems especially, one method often serves several callers. The AI edits it to fix channel A and silently changes behavior for channels B and C. The fix is to make the AI map every caller of a method before it changes shared logic, and to lean on tests as guardrails."
  - question: "What should I put in CLAUDE.md for a legacy project?"
    answer: "Hard constraints the AI keeps forgetting: use the existing utility classes (name them), match the surrounding code style, never edit shared/common logic without listing every caller first, do not invent new abstractions, and keep diffs minimal. Legacy projects need more rules than greenfield ones because the model cannot infer intent from messy, undocumented code."
  - question: "Is Claude Code or Cursor better for legacy Java?"
    answer: "Both work. I use Claude Code for larger, multi-file reasoning tasks where its planning helps, and Cursor for tight in-editor edits where I want to watch every change. What matters far more than the tool is the guardrails around it: your CLAUDE.md or .cursor/rules, your tests, and your discipline to keep changes small."
---

I inherited a Java system that is older than some of my coworkers. Ten-plus years of commits, three or four generations of engineers, and a payments flow that quietly serves five different sales channels. The first time I pointed an AI agent at it, I asked for something I thought was trivial: "add a discount cap to the promo calculation." Ninety seconds later Claude Code handed me a clean, confident diff. I merged it. Two days later a partner channel started rejecting orders because a field they depended on had silently changed shape.

That was my introduction to the real problem. Using AI on a legacy Java codebase is not hard because the AI writes bad code. It writes fine code. It is hard because **the AI has no idea what it is standing on.** The landmines in old code are invisible, and the model steps on all of them with total confidence.

This is not a "10x your productivity" post. It is what I actually learned after a year of using AI to change old, undocumented, load-bearing Java — including the mistakes that cost me real time.

## Legacy Code Is Full of Patches Nobody Understands

The core issue with old code is not complexity, it is **lost context**. Over ten years, people fix bugs by adding patches. A weird `if` here, a null check that looks pointless, a magic number someone hardcoded during an incident at 2am. None of it is documented. Half the original authors have left the company. Some of that logic is understood by literally nobody currently employed.

Here is the trap: to an AI, a mysterious defensive check looks like dead code or a "cleanup opportunity." I have watched an agent look at a genuinely load-bearing patch — the kind that exists because of some gnarly edge case from 2019 — and cheerfully "simplify" it out of existence. The code got cleaner. The bug it was silently preventing came right back.

The AI cannot tell the difference between "this is messy and should be removed" and "this is messy because it is holding up the whole building." Neither can you, sometimes, just by reading it. But you at least have the instinct to be afraid of it. The model has no fear. That gap — between the AI's confidence and its actual understanding — is where most of the damage happens.

## The Multi-Channel Trap (My Most Expensive Mistake)

This deserves its own section because it burned me hardest, and I think it is the single most underrated risk with AI on legacy systems.

Old business systems accrete **shared logic**. One `calculateFinalPrice()` method ends up serving the web channel, the app channel, two partner APIs, and an internal admin tool. Over the years everyone just called the existing method instead of writing their own, which is normally good engineering. But it means that one method now has five masters, each with slightly different assumptions.

When you ask an AI to "fix the price for the partner channel," it reads the method, sees a problem for that one caller, and edits the shared method to fix it. From the snippet in front of it, the change is correct. What it cannot see is that four other channels depend on the exact behavior it just changed. It fixes channel A and breaks channels B through E, and because there was no failing test right there, nothing screams. You find out from an angry partner.

This is the thing I now watch for above everything else: **AI treats shared logic like local logic.** It optimizes for the caller you mentioned and is blind to the callers you did not. On a greenfield project this barely matters. On a legacy monolith with tangled channels, it is the difference between a clean afternoon and a production incident.

My rule now is blunt: before the AI is allowed to touch any shared or "common" method, it has to first list every caller and tell me how each one uses it. If it cannot map the blast radius, it does not get to change the method.

## The Whole Game Is Fencing the AI In

If greenfield coding with AI is about giving it freedom, legacy coding is the opposite. **The core skill is constraint.** You are not collaborating with a smart junior; you are supervising a fast, confident one who does not know the history and will happily wander off if you let it. Your entire job is to fence it in from every direction so it cannot drift.

I think about it the same way I think about a [harness around the model](/blog/harness-engineering) — the guardrails matter more than the raw capability. On legacy code the harness has to be tighter than anywhere else, because the cost of drift is so high and the feedback is so delayed.

Concretely, "fencing in" means three things happening at once:

- **Scope constraints** — one small change at a time, never a sweeping multi-file refactor.
- **Behavior constraints** — do not remove things you do not understand, do not change shared logic without mapping callers.
- **Style constraints** — write code that looks like the code already there, using what already exists.

That last one leads directly to the file that has saved me the most pain.

## What I Put in My CLAUDE.md (This Is Where It Lives)

Most of my hard-won constraints do not live in prompts. They live in `CLAUDE.md` — the persistent instruction file Claude Code reads on every session (the same idea applies to Cursor's `.cursor/rules`, which I covered in the [Cursor Rules tutorial](/blog/cursor-rules-tutorial)). Prompts are forgotten between sessions. A memory file is not. For legacy work, this file is not optional — it is the thing standing between you and a bad merge.

Two specific behaviors drove me to write this file, and I bet you have hit both:

**1. The AI ignores your existing utility classes.** I have a perfectly good `StringUtils`, `DateHelper`, and a house `Result<T>` wrapper. The AI does not care. It will write its own null-safe string check inline, or pull in a new dependency, instead of using the helper that already exists three packages over. Now I have two ways to do the same thing and the codebase drifts further from itself.

**2. The AI's code does not match the surrounding style.** It writes technically correct Java that reads like a different person wrote it — because a different "person" did. Different naming, different error handling, `var` where the file uses explicit types, streams where the file uses plain loops. Each diff is fine in isolation; together they turn a consistent codebase into a patchwork.

So my legacy `CLAUDE.md` has a section that reads roughly like this:

> **Working in this codebase:**
> - Use the existing utilities. Before writing a helper, check `com.acme.common.util` — `StringUtils`, `DateHelper`, `CollectionUtils` almost certainly already do it. Do not write your own and do not add new dependencies for things we already have.
> - Match the surrounding style exactly. Look at the file you are editing and mirror its naming, error handling, and structure. If the file uses explicit types and for-loops, do not "modernize" it to streams.
> - Return results with the house `Result<T>` wrapper, not raw exceptions, in service-layer code.
> - **Never edit a shared/common method without first listing every caller and how each uses it.** If the change affects more than one channel, stop and ask.
> - Do not delete or "simplify" code you do not understand. Assume defensive checks and odd conditionals are load-bearing until proven otherwise.
> - Keep diffs minimal. Change only what the task requires. No drive-by refactors.

None of these are clever. They are just the specific ways this particular model keeps going wrong on this particular codebase, written down so I do not have to repeat myself every session. That is really all a good `CLAUDE.md` is: your accumulated "stop doing that" list, made persistent. Mine started at three lines and grew every time the AI made me sigh and fix something by hand.

## My Actual Workflow for Changing Old Code

Beyond the memory file, the process matters. Here is roughly how I drive it now:

1. **Explain before edit.** Before any change, I ask the AI to read the relevant code and explain what it does and who calls it. If its explanation is wrong or vague, that is my early warning that it does not understand the terrain — and I do not let it edit yet.
2. **Map the blast radius.** For anything in shared code, I make it enumerate callers first. This one habit has prevented more incidents than any other.
3. **Small diffs only.** One logical change per pass. A giant refactor from an AI on legacy code is a merge you cannot actually review, which means it is a merge you should not accept.
4. **Tests are the real fence.** Rules are suggestions; a failing test is a wall. If the area has no tests, I have the AI write characterization tests that pin down current behavior *before* changing anything. Then if it breaks a channel, the test screams instead of the partner. This is the legacy version of the discipline I described in [avoiding AI hallucinations](/blog/ai-hallucination-tips) — you verify against reality, you do not trust the confident output.
5. **Review the diff like it came from a stranger — because it did.** Every line, every deletion. I go deeper on this below, because it is the one step people skip and the one that actually keeps you in control.

It sounds slow. It is slower than letting the agent run wild for five minutes. It is enormously faster than a two-day production incident.

## You Still Have to Review — and Review Hard

Here is the part I cannot skip, and the part most "AI wrote my code for me" posts gloss over: **after all the constraints, you still have to read what the AI changed, carefully, like it was written by someone you do not trust.** Not skim. Read.

The whole point of fencing the AI in is to make its changes small and predictable enough that *you* can actually verify them. If the change is a ten-file refactor, you cannot review it, which means you are merging blind — and blind merges on legacy code are how incidents happen. So the constraint and the review are two halves of the same thing: keep the diff small so the review is real.

When I review an AI diff on old code, two questions drive everything:

- **Did it change the right thing?** Is the actual edit what I asked for, or did it sneak in "improvements" — renaming, restructuring, a "cleaner" equivalent that is subtly different? Confident models love to over-deliver. I check the diff against intent line by line, not against the summary it wrote for me (the summary is also generated, and it is often optimistic).
- **Could this break somewhere else?** This is the legacy-specific one. Even with the "list every caller" rule, the AI can miss an indirect path — a scheduled job, a queue consumer, a partner integration that calls the method through three layers of indirection. I specifically look for *what was not in the scope of the request but got touched anyway*, because that is where the surprise lives.

I will be honest about the prerequisite, because it matters: **doing this well requires real code-review experience.** You have to be able to read a diff and smell the second-order effect — to know which change will ripple into the reporting job that runs at 3am. If you are early in your career, this is exactly the skill that using AI on legacy code forces you to build, and it is worth building. But it is a skill, not a toggle. The AI does not remove the need for it; it raises the stakes of having it.

That is the real reason the manual review step matters: it is how you stay the boss. The AI is fast, confident, and context-blind. You are slow, skeptical, and hold the business history in your head. The review is where those two meet, and where you — not the model — get the final say on whether this code ships. Skip it and you have outsourced the one decision that matters most.

## Where AI Still Won't Save You on Legacy Code

I want to be honest about the limits, because overselling this is how people get burned.

AI does not know your business history, and legacy code *is* business history in disguise. It cannot tell you why a channel needs that weird field, because the answer lives in a Slack thread from 2020 or in someone's head. It will confidently invent a plausible-sounding reason, which is worse than saying "I don't know."

It is also weakest exactly where legacy code is hardest: the tangled, undocumented, side-effect-heavy core. On the clean edges — writing a new endpoint, adding tests, generating a DTO — it is genuinely great. In the ten-year-old spaghetti at the center, it is a liability without tight supervision. The value is real but lopsided, and knowing which half you are in is the whole skill.

## Summary

Using AI on a legacy Java codebase works, but the mental model is the opposite of greenfield. The risk is not the code the AI writes — it is the code it touches without understanding. Undocumented patches look like cleanup opportunities. Shared multi-channel logic gets "fixed" for one caller and broken for four others. And left unconstrained, the AI ignores your existing utilities and drifts from your code style until the repo no longer looks like itself.

The answer is constraint, and most of it belongs in a persistent file — a `CLAUDE.md` (or `.cursor/rules`) that says: use what exists, match the style, map every caller before touching shared logic, and never delete what you do not understand. Pair that with small diffs, characterization tests, and reviewing every line like a stranger wrote it. Do that, and AI becomes a genuinely useful pair of hands on old code. Skip it, and it becomes the fastest way yet to break a system nobody fully understands.
