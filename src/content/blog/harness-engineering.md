---
title: "Harness Engineering: What Prompt Engineering Couldn't Solve"
description: "Harness engineering is the 2026 AI paradigm shift. What it is, why prompt engineering hit its limits, and how to build your own agent harness."
pubDate: 2026-07-07
category: "prompt-engineering"
tags: ["harness engineering", "ai agents", "prompt engineering", "claude code", "cursor"]
image: "/og-harness-engineering.jpg"
imageAlt: "Harness Engineering concept diagram showing AI agent wrapped in a structured environment with verification loops, constraints, and observability"
keywords: ["harness engineering", "what is harness engineering", "harness engineering vs prompt engineering", "ai agent reliability"]
faq:
  - question: "What is harness engineering in simple terms?"
    answer: "Harness engineering is the practice of building a structured environment around an AI model — including constraints, verification loops, tools, and observability — so the model produces reliable, repeatable results. The model is the engine, the harness is the steering wheel, brakes, and dashboard."
  - question: "How is harness engineering different from prompt engineering?"
    answer: "Prompt engineering focuses on how to phrase instructions to get better outputs. Harness engineering focuses on the entire system around the model — what information it sees, what tools it can use, what rules it must follow, and how its outputs are verified. In practice, prompt engineering is now a small subset of harness engineering."
  - question: "Do I need harness engineering if I only use ChatGPT occasionally?"
    answer: "Probably not. Harness engineering matters most for AI agents that run autonomously — coding agents, customer service bots, research assistants. If you only use ChatGPT or Claude through their chat interface, prompt engineering is still enough."
  - question: "What tools do I need to start with harness engineering?"
    answer: "Most teams start with a CLAUDE.md or AGENTS.md file (under 100 lines) describing project rules, a linter or pre-commit hook for mechanical constraints, and a verification step where the agent runs tests before declaring success. You don't need any new frameworks — your existing dev tooling is enough."
---

Last month I spent four hours debugging an AI agent that kept "working" but breaking half my tests. Every prompt I tweaked produced a slightly different kind of failure. The model hadn't changed. The task hadn't really changed either. But the agent still felt unpredictable in a way I couldn't fix with clever wording.

That frustration sent me down a rabbit hole. I came out the other side convinced that **prompt engineering is hitting its ceiling, and the next paradigm is already here: harness engineering**.

This is a 2026 concept — coined by <a href="https://mitchellh.com/" target="_blank" rel="noopener noreferrer">Mitchell Hashimoto</a> (HashiCorp founder, the guy behind Terraform) in February of this year — that reframes the entire problem. Instead of asking "how do I write better prompts," you ask "how do I build a system where the AI almost *can't* fail in the ways I care about." It clicked hard for me. Maybe it will for you too.

## The Day I Realized Prompt Engineering Had Limits

I was using Claude Code to refactor a legacy module. The first attempt was beautiful. The second attempt, on a different file, completely broke the public API. The third attempt gave me a perfectly formatted response that silently skipped half the work.

I kept iterating on the prompt. Adding more context. Being more specific. Including examples. The output got marginally better — maybe 5% — but the *flavor* of failure kept changing. Sometimes it hallucinated, sometimes it skipped steps, sometimes it "completed" tasks that weren't actually complete.

Sound familiar?

The pattern I kept hitting: **I was trying to fix a system problem with a writing problem**. The agent had too much freedom, no way to verify its own work, and no memory of what it had tried. Tweaking prompts felt like putting a stronger horse in front of the same broken carriage.

That's when I started reading about harness engineering.

## What Is Harness Engineering, Exactly?

The term "harness" borrows from horse riding. A horse is powerful but unpredictable. A harness — the saddle, the reins, the blinders, the bridle — doesn't make the horse faster. It makes the horse **usable**. It channels that power toward a specific goal and away from disaster.

Harness engineering applies the same idea to AI. You don't try to make the model smarter. You build a structured environment around the model so its intelligence gets channeled into reliable behavior.

Harrison Chase (the <a href="https://www.langchain.com/" target="_blank" rel="noopener noreferrer">LangChain</a> founder) put it cleanly:

> "Harness is everything around the model — context assembly, tool orchestration, verification loops, architectural constraints, observability, cost control."

When you swap a model, you might see a 10-15% quality change. When you swap a harness, you change whether the system is **usable at all**.

That line hit me. I'd been chasing 5% prompt improvements on a fundamentally broken setup.

## The Three Paradigms: Prompt → Context → Harness

This didn't come out of nowhere. We're at the third major shift in how engineers think about working with AI:

**1. Prompt Engineering (2023–2024)**: How do I phrase my request? The model is the bottleneck. If the output is bad, it's because I didn't prompt well enough. We produced frameworks, techniques, and endless blog posts about "the perfect prompt." A lot of it was useful at the time.

**2. Context Engineering (2025)**: What does the model need to *know*? The shift was giving the agent the right information — project structure, coding conventions, documentation, current task state. Files like `CLAUDE.md` and `AGENTS.md` became standard. Prompt wording still mattered, but knowledge became the lever.

**3. Harness Engineering (2026, now)**: What system do I build around the model? This is bigger than context. It's the whole environment — what tools the agent can call, what rules it must follow, how its work gets verified, how errors become permanent rules instead of repeat mistakes.

Here's the part that took me a while to internalize: **the earlier paradigms don't disappear, they get absorbed**. A good harness still uses good prompts. It still feeds the agent good context. But those are now small pieces of a much larger system.

If you've been writing prompts for two years and feeling like diminishing returns are kicking in — you're not crazy. The lever has moved.

## The 4 Components That Actually Matter

The full "anatomy of an agent harness" is six components deep, but four of them are what most teams should focus on first. I'm going to walk through what they actually look like in practice, because theory without examples is just vocabulary.

### 1. Architectural Constraints (The Hardest One to Accept)

This is the most counterintuitive part: **limiting the agent's freedom makes it produce better work**.

I know. I resisted this for weeks. "But the agent is smart, why am I telling it things it already knows?" Because LLM behavior in open spaces is unpredictable. The more you constrain the solution space, the more reliably the agent lands on something correct.

In practice, this looks like:

- Linter rules that auto-reject code violating your dependency direction (`utils → services → API`, never the other way)
- A pre-commit hook that runs before any agent-written code is even considered
- A pre-approved list of tools the agent can call — anything outside the list is denied by default

The first time I set up a pre-commit hook that ran the agent's output through the same linter the human team used, I watched the error rate drop from "I have to review every change" to "occasional edge cases." Constraints are leverage.

### 2. Verification Loops (The Most Important One)

The harsh truth about agents: **they cannot evaluate their own work**. If you ask an agent to rate its own output, it will give itself a 9/10 every time. Self-assessment is not verification.

A real verification loop has three layers, and you need all of them for serious work:

- **Mechanical (zero tolerance)**: Tests, linter, type checks, build success. These pass or fail. No judgment call.
- **AI-driven (advisory)**: A second agent reviews the first agent's output against a checklist. Useful for style, design quality, completeness — but always with a human in the loop for the final call.
- **Human (final say)**: For architectural decisions, anything touching security, or any case where stakes are high.

The mechanical layer is what most teams skip. It's also the most valuable. An agent that *must* pass `npm test` before it can declare a task complete produces a fundamentally different quality of work than one that just declares completion. (For a deeper look at how to test AI code reliably, my guide on [ChatGPT API rate limits](/blog/openai-rate-limits-guide/) covers some of the operational discipline that translates here.)

### 3. Sub-Agents and Context Firewalls

Long-running agent sessions have a hidden problem: **context rot**. The longer the conversation, the more the early instructions get diluted, errors accumulate, and the agent drifts. By hour four, it might be following maybe 40% of what you actually told it.

The fix is to split work into sub-tasks, each with a clean context window. A parent agent breaks the problem down. Sub-agents do focused work in isolation. The parent assembles results.

I started using this workflow about six weeks ago:

1. First session: explore the problem, plan the approach, write a detailed spec
2. Open a **brand new session** for the actual implementation
3. Paste the spec, execute, verify, done

It feels wasteful — "all that planning context, gone!" — but the new session with a clean slate and a clear spec produces better work than one carrying 50 turns of conversation history. This is one of those things you have to try to believe.

### 4. Observability and Self-Improvement

The final piece: when the agent fails, the failure should make the system better, not just be a one-off incident.

Every time something breaks, you should ask: **what rule would have prevented this?** Then add that rule to the harness. Slowly, the system gets harder to break.

A simple version: every caught error becomes a new linter check, a new entry in `CLAUDE.md`, or a new test case. After a few months, your harness has absorbed a hundred small failure modes that won't happen again.

This is why harness engineering compounds. Every project you do, every bug you fix, every weird edge case the agent stumbles into — all of it makes the next project more reliable. The "flywheel" metaphor is overused but genuinely applies here.

## What Changed for Me

I've been doing this for about two months now. The honest results:

- I spend less time re-prompting and more time designing the harness
- Agent-generated code needs less rework, because mechanical constraints catch the obvious stuff before I see it
- Long-running tasks (4+ hours of agent work) are actually viable now, where before they were a coin flip
- The agent still surprises me sometimes, but the surprises are smaller and less catastrophic

It's not magic. The agent is still an LLM. It still hallucinates occasionally. It still makes bad calls in edge cases. But the *floor* is much higher, which is what actually matters for shipping real work.

## When Harness Engineering Is Overkill

I want to be honest about when this is the wrong approach.

If you're using ChatGPT or Claude through the chat interface to draft an email, summarize a document, or brainstorm ideas — you don't need a harness. Prompt engineering is still fine for that.

Harness engineering matters when:

- An agent is running **autonomously** (no human in the loop for every step)
- The cost of failure is high (production code, customer-facing systems, anything you'd hate to debug at 2 AM)
- The work spans multiple sessions or hours of agent time
- Multiple people or teams depend on consistent, reliable output

If none of that applies, you're over-engineering. The right answer is still "use a good prompt and review the output."

## How to Start Tomorrow

You don't need to boil the ocean. Here's the minimum viable harness I've landed on, in order of priority:

1. **Write a `CLAUDE.md` or `AGENTS.md` file** — under 100 lines, project rules, conventions, hard "don't do this" list. Treat it as a directory pointing to deeper docs, not a complete manual.

Here's mine (lightly sanitized). It's not pretty, it's not exhaustive, and that's the point — it's a living document that grew from real failures:

```markdown
# CLAUDE.md — Project Rules for AI Agents

## Project Overview
TypeScript + Astro blog deployed on Cloudflare Pages. Content is in src/content/blog/.
Build: `npm run build`. Dev: `npm run dev`.

## Architecture Rules (HARD)
- Dependency direction: components/ → layouts/ → pages/. NEVER import from pages/ into components/.
- Markdown files MUST NOT contain H1 (#). The layout renders <h1> from frontmatter. Body starts with H2 (##).
- All internal links MUST end with a trailing slash: /blog/my-article/ not /blog/my-article
- Do not modify astro.config.mjs without explicit confirmation from the author.

## Coding Conventions
- Tailwind CSS 4. No custom CSS files. Use utility classes.
- Astro components only. No React/Vue/Svelte.
- File names: kebab-case. Component names: PascalCase.
- Every new article needs an OG image (1200x630, generated via scripts/generate-og-images.mjs).

## Verification Checklist (before declaring a task complete)
1. `npm run build` must succeed with zero errors
2. `npm run lint` must pass (no warnings, no errors)
3. All new internal links must end with /
4. Frontmatter must include: title, description, pubDate, category, tags, image, imageAlt, keywords, faq
5. Article body must NOT contain H1

## Known Failure Modes (rules learned the hard way)
- DO NOT change the frontmatter `title` field without also updating the OG image and sitemap.
- DO NOT add `# Title` to markdown — it creates a duplicate H1 on the page.
- DO NOT use `target="_blank"` without `rel="noopener noreferrer"`.
- DO NOT add scripts to the head without checking if Astro's built-in script handling covers it.

## When You're Unsure
- Ask before modifying config files (astro.config.mjs, tailwind.config, tsconfig).
- Ask before deleting any file in public/.
- If a build error mentions "duplicate", stop and check for H1 in markdown.
```

This file took me about two months to build up. Each entry under "Known Failure Modes" is a real bug I hit, debugged, and turned into a rule. That's the self-improvement loop in action — the harness gets tighter every time something breaks.

2. **Add a pre-commit hook** that runs the linter and the test suite. Anything failing this gets rejected, regardless of whether a human or an agent wrote it.
3. **Set up a "completion checklist"** — before the agent can declare a task done, it must run a specific set of commands (tests, build, type check) and show you the output.
4. **Add a verification agent** — a second agent that reviews the first agent's output against a checklist. Don't trust self-review.
5. **Track your failures** — when something breaks, ask "what rule would have caught this?" and add it.

You can do all of this in a day. The marginal value of each step is enormous.

## Where This Is Going

The current models are all roughly comparable in raw capability. The differentiator in 2026 and beyond won't be "which model you use" — it'll be "how good is your harness." That's the part that's hard to replicate and easy to build advantage with.

The folks I know shipping the most agent-driven work aren't the ones with access to the best models. They're the ones who spent six months tightening their harness, learning the failure modes, and turning them into rules. That's the work now.

If you want a deeper look at the operational side of running AI agents in production — how to handle the rate limits, cost control, and reliability questions that come up — my [Claude API rate limits guide](/blog/openai-rate-limits-guide/) covers a lot of the same discipline from a different angle. And for the prompting layer that sits inside a good harness, the [prompt engineering techniques I use every day](/blog/prompt-engineering-techniques/) are still worth knowing. Harness engineering is the new outer ring. The inner rings haven't gone anywhere.
