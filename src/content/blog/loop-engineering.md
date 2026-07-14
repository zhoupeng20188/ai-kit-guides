---
title: "Loop Engineering: Your Prompts Are the Bottleneck, Not the AI"
description: "Tired of prompting AI agents one by one? Loop Engineering replaces you with a self-running system that iterates. Here's what it means for your work."
pubDate: 2026-07-14
category: "prompt-engineering"
tags: ["loop engineering", "ai agents", "ai coding", "agent workflow", "peter steinberger"]
image: "/og-loop-engineering.jpg"
imageAlt: "Diagram showing the shift from manual Prompt Engineering to a self-running Loop Engineering system for AI agents"
keywords: ["loop engineering", "peter steinberger", "ai agent loops", "agentic workflow 2026", "self-running ai agents"]
faq:
  - question: "What is Loop Engineering?"
    answer: "Loop Engineering is a 2026 AI development approach where you design a self-running system that sets goals, runs an agent, checks the result, and decides the next step — instead of prompting the agent manually every time."
  - question: "Who coined the term Loop Engineering?"
    answer: "The idea went viral from a June 7, 2026 tweet by Peter Steinberger (founder of OpenClaw): 'You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents.' Google engineer Addy Osmani then systematized it into a framework."
  - question: "Is Loop Engineering better than Prompt Engineering?"
    answer: "They solve different problems. Prompt Engineering improves a single message; Loop Engineering automates the whole workflow. A loop built on weak prompts just produces weak results faster, so prompt skills still matter."
  - question: "Do I need to be a developer to use Loop Engineering?"
    answer: "Most practical loops today are glue code, scripts, and CI config, so coding helps. But the concept applies to any repeating AI task — even no-code automation tools can implement a basic loop with a goal, a check, and a stop condition."
---

A few weeks ago I caught myself doing something stupid. I had a Spring Boot service with eight public methods that all needed the same null-check guard. I opened Cursor, typed "add null checks to UserService," watched it handle four of them, then spent the next 20 minutes re-prompting it for the other four because it kept "forgetting" which ones it had already done. That's when it hit me: the bottleneck wasn't Cursor. It was me, sitting inside the loop, acting as the human relay between the task and the AI.

That is exactly the problem Loop Engineering is trying to kill.

## What Is Loop Engineering?

Loop Engineering is a term that blew up in June 2026. On June 7, Peter Steinberger — the founder of OpenClaw — posted a 12-word tweet that racked up somewhere around 8 million views: "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents."

It sounds like a hot take. But a day later, Google Cloud engineer Addy Osmani published a long write-up that turned the one-liner into a real framework. And Boris Cherny, the person who runs Claude Code at Anthropic, said almost the same thing on stage: "I don't prompt Claude anymore. I have loops that are running." His job, he said, is to write loops — not prompts.

So what is it, in plain terms? Traditional AI coding is a relay race. You write a prompt, the AI does one thing, you read it, you write the next prompt. You are always inside the loop, handing off instructions. Loop Engineering flips that. You design a system that sets a goal, runs the agent, checks the result, decides what to fix, and runs again — without you standing in the middle.

The catch that most people miss: it is not about "automation." A cron job that fires the same prompt every night is not Loop Engineering. A loop is a closed circuit that can judge its own output and decide whether it is actually done.

## The 4 Generations: From Prompt to Loop

If you have been following AI tooling, this is the fourth shift in how we work with models. I wrote earlier about [prompt engineering techniques](/blog/prompt-engineering-techniques) and [Harness Engineering](/blog/harness-engineering), and Loop is where both of those were always heading.

- **Prompt Engineering** — you optimize a single message. Ceiling: your time.
- **Context Engineering** — you stuff the right docs, history, and tool definitions into the model. Ceiling: how much context you can manage.
- **Harness Engineering** — you build the wrapper (rules, guardrails, project config) so the AI behaves consistently. Ceiling: how well your harness is designed.
- **Loop Engineering** — you stop operating the harness by hand and let a system drive it. Ceiling: how much of the workflow you can safely automate.

Here is the part that matters: none of these replace the one before it. A loop filled with bad prompts just produces bad results faster. Your [prompt skills](/blog/prompt-engineering-techniques) and your [harness rules](/blog/harness-engineering) become the ingredients the loop feeds on. Skip them and the loop has nothing good to chew on.

## Why I Stopped Prompting and Started Designing Loops

Back to my UserService disaster. The real fix was not a better prompt — it was removing myself from the loop. I wrote a small script: it listed every public method in the file, checked which ones lacked the guard, and only then asked the agent to handle the remaining ones, one at a time, with a verification step after each. It ran once, reported back, and I reviewed the diff. Twenty minutes of re-prompting collapsed into a 40-second review.

That is the whole shift. I am no longer the operator relaying instructions. I am the person who designed the relay.

Is it always worth it? No. For a one-off task, designing a loop is slower than just doing it. The moment a task repeats — daily reports, batch refactoring, test generation, triaging incoming issues — the loop pays for itself. I learned this the hard way on a Friday when I manually re-prompted the same "explain this stack trace" task across twelve tickets. Twelve. I could have written the loop in the time I spent copy-pasting.

## The 5 Building Blocks of a Loop

Osmani's framework breaks a useful loop into five pieces, and I have come to trust all five after breaking loops that missed one:

1. **A clear goal.** "Fix all null-check gaps in UserService" beats "improve the service." Vague goals make the loop spin forever, burning tokens and confidence.
2. **Context management.** The loop needs the right files, schemas, and prior runs fed in — same idea as Context Engineering, but automated instead of you pasting things by hand.
3. **Callable tools.** The agent must be able to actually do things: read files, run tests, call an API. A loop with no hands is just an expensive chatbot.
4. **Output evaluation.** This is the part most people skip. The loop needs a way to check if the result is good — a test suite, a lint run, a diff review. Without evaluation, the loop confidently produces garbage and calls it done.
5. **A stop condition.** "Stop when all methods pass tests, or after 5 iterations." Without this, you get an agent burning tokens in circles at 2 a.m. while you sleep.

Miss any one of these and your "loop" is really just an expensive `while(true)`.

## A Real Example You Can Steal

I will be honest: my first loop was ugly. I tried to automate "refactor this module to use records" and gave it no stop condition. It rewrote the file three times, each version more aggressive than the last, and I came back to a class that no longer compiled. Lesson learned — evaluation and stop conditions are not optional decorations, they are the load-bearing walls.

The loop that actually stuck: a nightly script that scans our repo for TODO comments tagged `AI-FIX`, opens each one in the agent with the surrounding context, runs the project's existing test suite, and only commits if the tests pass. If tests fail, it logs the failure and moves on. No human in the loop, no broken builds, no 2 a.m. surprises. The agent does the grunt work; I review the morning's diffs with coffee.

## When Loop Engineering Isn't Worth It

- **One-off tasks.** Designing the loop takes longer than doing it once. If you will never repeat it, just prompt it.
- **Tasks with fuzzy success criteria.** If you cannot define "done," the loop cannot either. It will either stop too early or loop forever.
- **High-stakes changes.** I would never let a loop touch auth or payments without a human gate. The loop is great for grunt work, terrible for judgment calls.

Also: the tooling is still rough in mid-2026. Most of this is glue code, shell scripts, and CI config. It is not a polished product yet. If you were hoping for a "Loop Engineering button" in your editor, it does not exist. You are the button.

## How to Start

Do not rebuild your whole workflow. Pick one annoying repeating task this week — generating tests for new methods, summarizing standup notes, triaging bug reports, whatever. Write down the goal, the tools it needs, how you would check the result, and when to stop. Then wire the dumbest possible version. Iterate from there.

And keep your [prompt and harness skills](/blog/prompt-engineering-techniques) sharp. The loop is only as good as what is inside it. A weak prompt in a loop is not a clever automation — it is a faster way to ship mistakes.

## Summary

Loop Engineering is not about replacing AI with automation. It is about moving yourself from "the person typing prompts" to "the person designing the system that types them." Steinberger, Osmani, and Cherny all landed on the same idea in June 2026: the bottleneck was never the model. It was us, stuck in the loop.

Start small. Pick one repeating task. Design the loop. Then go do something a human should be doing.
