---
title: "Why Does AI Make Things Up? 7 Ways to Stop AI Hallucinations"
description: "AI chatbots invent APIs, fake libraries, and wrong code. Here are 7 practical ways I stop AI hallucinations as a developer who uses AI to write Java every day."
pubDate: 2026-07-08
category: "ai-tools"
tags: ["ai hallucination", "reduce ai hallucinations", "chatgpt make things up", "ai code hallucination", "prompt engineering"]
image: "/og-ai-hallucination-tips.jpg"
imageAlt: "A developer checking AI-generated code against a compiler to catch a hallucinated method call, illustrating how to stop AI hallucinations"
keywords: ["ai hallucination", "why does ai make things up", "how to reduce ai hallucinations", "stop ai hallucinations", "ai makes things up"]
faq:
  - question: "Can AI hallucinations be completely eliminated?"
    answer: "No, and anyone telling you otherwise is selling something. Hallucination is baked into how these models work: they predict the most likely next token, not the truth. What you can do is make hallucinations rare and, more importantly, cheap to catch. A hallucinated method name that fails `mvn compile` in two seconds costs you nothing. A hallucinated API that ships to production is the real danger."
  - question: "Do newer models like GPT-5.5 and Claude 4.7 hallucinate less?"
    answer: "Yes, measurably less than the 2023-2024 models. On well-trodden topics (popular frameworks, common algorithms) they are genuinely reliable now. But they still invent things the moment you go off the beaten path: an obscure library, an internal API, a config flag for a version you didn't name. Newer models earned my trust faster, not my trust blindly."
  - question: "Is there a tool that automatically catches AI hallucinations?"
    answer: "For code, yes: your compiler, type checker, linter, and test suite are the best hallucination catchers ever built, and they are free. For facts and APIs, cross-checking is still manual, though guardrail frameworks that constrain the model's outputs help a lot. There is no magic filter that makes AI output safe to paste without review."
  - question: "Why is AI so confident when it is wrong?"
    answer: "Because confidence is not a signal of correctness, it is a side effect of how text is generated. A model that says 'use Thread.sleep(Duration)' with zero hesitation is just producing statistically fluent text. The certainty you read is packaging, not proof. Once I internalized that, I stopped being soothed by confident phrasing and started verifying anything I couldn't personally confirm."
---

Two weeks ago I let an AI write a small Java utility to parse a CSV export from our billing system. It compiled on my machine. It passed the one test I bothered to run. I shipped it. Three days later production threw a `NoSuchMethodError` at 2 a.m.

The AI had used a Guava method that simply does not exist in the Guava version we actually depend on. It looked completely reasonable. It read like real code. It was fake.

That incident is why I am skeptical of anyone who says "AI writes perfect code now." It doesn't. It writes *plausible* code, and plausible is exactly what gets past a tired reviewer. If you use ChatGPT, Claude, or Gemini to write or review code, **AI hallucination is the single most expensive habit you will have to manage.**

Here is what I have learned, mostly the hard way, about stopping it.

## The Difference Between a Bug and a Hallucination

A bug is wrong but real. A hallucination is *fiction that looks like fact*. When AI tells you to call `StringUtils.equalsAny()` from Apache Commons, and that method does not exist in the version you use, that is a hallucination. The code is syntactically perfect. It just references something that isn't there.

In my experience the most dangerous hallucinations are the quiet ones:
- A Maven `groupId` or `artifactId` that does not exist on Maven Central.
- A method name that is one word off from the real one (`readString` vs `readAllBytes`).
- A config key your framework never had (`spring.redis.timeout-ms` instead of `spring.data.redis.timeout`).
- A SQL function that only exists in PostgreSQL, pasted into a MySQL project.

None of these throw an error until runtime, and sometimes not even then.

## 1. Compile and Run Before You Trust a Single Line

This is the boring, non-negotiable rule. After AI writes anything, I do not read it for correctness. I run it.

Last month I asked GPT-5.5 for a quick file reader. It handed me back code using `Files.readString(Path)` and looked clean. I pasted it into the module and ran `mvn compile`. Instant failure:

```
[ERROR] cannot find symbol
  symbol:   method readString(java.nio.file.Path)
```

Our service was still on Java 11. `Files.readString` arrived in Java 12. The compile error exposed the hallucination in two seconds. If I had just eyeballed it, I would have shipped broken code and found out from a teammate.

If you take one thing from this article: **the compiler is the cheapest hallucination detector in the world, and it runs in seconds.** Use it like a seatbelt, not like an optional extra.

## 2. Paste the Real Context, Not a Vague Description

The biggest drop in hallucination I ever got came from a simple change: stop describing my code, start *pasting* it.

I once asked Claude 4.7 to write a JPA query for "the user table." It came back with a query referencing `created_at`, `updated_at`, and a `status` column. None of those existed in my `@Entity`. My actual class used `gmtCreate`, `gmtModified`, and `userStatus` (legacy naming from an old DBA, don't ask). The AI invented columns because I never showed it the real shape.

The fix was embarrassingly simple. I pasted the actual `User` entity class into the prompt. The next query was correct, first try. The model wasn't stupid. It was guessing, and I had given it permission to guess by being vague.

Rule I now follow: **if the answer depends on a schema, an interface, or a signature, that schema goes in the prompt.** Don't describe your database. Paste the DDL. Don't describe your API. Paste the interface.

## 3. Pin the Version and Name the Stack Out Loud

I used to open prompts with "write me a Spring Boot controller." That was a mistake. "Spring Boot" spans a decade of changes, and the AI will pick the version *it* is most confident about, not the one *you* run.

A few months back I forgot to say we were on Spring Boot 3.4 with Java 21. The AI wrote imports from `javax.persistence.*` — the old namespace. Spring Boot 3 moved everything to `jakarta.persistence`. The code looked right, compiled locally only because my IDE auto-fixed two imports, and then broke in CI. One line would have prevented it: "Spring Boot 3.4, Java 21, Jakarta namespace, no javax."

Now every code prompt starts with the stack on a single line:

```
Stack: Spring Boot 3.4, Java 21, Jakarta, PostgreSQL 16, Guava 33.
```

That one line has saved me more debugging time than any clever prompt technique. The model stops guessing your environment and starts respecting it.

## 4. Ask "Which Version Introduced This?" to Smoke Out Fake APIs

This is my favorite trick, because it turns the model's confidence against itself.

When AI suggests a method I don't recognize, I don't argue. I ask: *"Which JDK version added that method?"* A real method has a real answer. A hallucinated one gets wobbly.

I did this with a suggestion to use `String.repeat(n)` to build a separator line. I asked which version introduced it. The model said "Java 8." I was fairly sure that was wrong, so I checked the docs: `String.repeat` actually arrived in Java 11. The model's own answer didn't hold together, which was the tell that I should verify before trusting.

You can do the same for libraries: *"What's the Maven coordinates for that, and what's the latest stable version?"* If the `artifactId` or version feels off, it usually is. This question costs nothing and catches a surprising number of invented APIs.

## 5. Cross-Check With a Second Model

Some hallucinations are subtle enough that one model will defend them confidently. Running the same prompt through a different model is a cheap sanity check, because they tend to hallucinate in *different* places.

I was generating a Kubernetes Ingress YAML and asked both ChatGPT and Claude. ChatGPT included an `ingressClassName` field; Claude omitted it and used an annotation instead. Only one matched our cluster's actual API version. Side by side, the disagreement was obvious, and it pushed me to open the real API reference instead of trusting either.

This is exactly why I keep both tools around. My [Claude vs ChatGPT comparison](/blog/claude-vs-chatgpt-2026/) goes deeper, but the short version for hallucination-hunting: two models that disagree are a red flag waving at the exact spot you need to verify. When they agree, I still check, but I check lighter.

## 6. Constrain the Output So There's Less Room to Invent

The more freedom you give the model, the more room it has to make things up. A vague request like "write a function to validate an email" invites it to invent a whole `EmailValidator` utility class with methods that don't exist.

I now constrain hard. Instead of "validate an email," I write:

```
Write a Java method `boolean isValidEmail(String s)` using ONLY
java.util.regex.Pattern with this exact regex:
[A-Za-z0-9+._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}
No external libraries. Return false on null.
```

The constrained version never invented a class, because I took the class off the table. This is the same instinct behind [harness engineering](/blog/harness-engineering/): you don't make the model smarter by hoping, you make it reliable by removing the ways it can fail. Give it a narrow box and a clear rule, and hallucination drops because there's nothing left to improvise.

## 7. Treat Total Confidence as a Warning, Not a Green Light

The most confident wrong answer I ever got was also the most plausible. I asked an AI for a MySQL query to bucket rows by day. It returned `DATE_TRUNC('day', created_at)` without a hint of uncertainty. `DATE_TRUNC` is a PostgreSQL function. MySQL does not have it. It would have failed silently in a report nobody checks closely.

Here is the pattern I have come to trust: **the more certain the model sounds about a specific API name, the more I verify it.** Hesitation in AI output is rare, so confidence tells you nothing about truth. It only tells you the model found a fluent-sounding sequence of tokens.

My rule now is simple. If I can't personally confirm an API, a version, or a config key, I check it before it touches the codebase. Not because the model is bad, but because it is fluent, and fluent lies are the ones that slip through.

## A Realistic Mindset, Not Paranoia

I don't want to sound like I hate these tools. I use GPT-5.5 and Claude 4.7 every single workday, and they've made me faster than I was a year ago. The point isn't to distrust AI. The point is to **trust it the way you'd trust a very confident junior hire**: great output, zero immunity to making things up, and your job is the review.

The seven habits above are not heavy. Compile before you trust. Paste real context. Name your stack. Question suspicious APIs. Cross-check the big ones. Constrain the output. Verify anything you can't confirm. None of them slow you down once they're muscle memory, and all of them are cheaper than a 2 a.m. `NoSuchMethodError`.

If you want to go deeper on the prompting side, my [prompt engineering techniques guide](/blog/prompt-engineering-techniques/) covers how I structure requests so the model needs to guess less in the first place. And if you build anything with agents, the [harness engineering piece](/blog/harness-engineering/) explains how to put guardrails around AI so hallucinations get caught automatically instead of by you at midnight.
