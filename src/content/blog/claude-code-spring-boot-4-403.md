---
title: "Claude Code Fixed My Boot 4 403 — AGENTS.md Changed the Fix (2026)"
description: "I gave Claude Code the same broken Boot 4 upgrade twice — no context, then with an AGENTS.md. One disabled CSRF globally, one scoped it. Here is the diff."
pubDate: 2026-09-02
category: "ai-tools"
tags: ["spring boot 4", "claude code", "agents.md", "spring security csrf", "java ai tools", "java-ai-cluster"]
image: "/og-claude-code-spring-boot-4-403.jpg"
imageAlt: "A terminal showing Claude Code fixing a Spring Boot 4 403 next to a diff where a global csrf.disable() becomes a scoped ignoringRequestMatchers exemption"
keywords: ["spring boot 4 403", "claude code csrf", "agents.md spring boot", "spring security csrf disable", "ai agent fix 403"]
faq:
  - question: "Why does my Spring Boot 4 POST return 403 but GET works?"
    answer: "CSRF protection is enabled by default in Spring Security and has been for years — Boot 4 does not turn it on. The common claim that Spring Boot 4 enables CSRF for API endpoints is wrong about the default; I verified the same POST returns 403 under both Boot 3.5.16 and 4.x with identical config. What an upgrade can do is surface a CSRF gap your old config masked. GET keeps working while POST, PUT and DELETE return 403 with nothing in the logs. For a stateless API, scope the exemption to your API matcher rather than disabling CSRF globally."
  - question: "Will Claude Code disable CSRF if I ask it to fix a 403?"
    answer: "In my experiment it did — when given no project context, Claude Code reached for a global csrf.disable() because that is the shortest path to a green test. When the same broken project included an AGENTS.md instructing it to scope the exemption instead, the same model changed to csrf.ignoringRequestMatchers('/api/**') plus STATELESS. The model did not get smarter; the repo just told it what good looked like."
  - question: "What should I put in AGENTS.md for Spring Boot security?"
    answer: "State the security model (for example, stateless HTTP Basic with no browser session), note that CSRF being on by default is not a Boot 4 regression, and require a scoped exemption rather than a global disable — match on your API path and set SessionCreationPolicy.STATELESS. Make the rule explicit and scoped, not a bare prohibition, so the agent has no gap to fill with imagination."
---

## I broke a POST endpoint on purpose

A few weeks ago I moved a tiny Spring Boot REST service from 3.5 to 4.1. It compiled. The test suite was green. And then a `POST` endpoint that had answered requests for a year started returning 403, while the `GET` on the same resource was fine.

I did not open a search tab. Instead I did something I normally tell people not to do: I handed the broken project to an AI coding agent and said fix it. Then I did it again — but the second time I left a file in the repository. The gap between those two runs is the whole point of this article, and it is a stronger argument for writing an `AGENTS.md` than any checklist I could paste into a README.

Why run it as an experiment instead of just fixing it? Because I kept seeing the same advice repeated — let your agent handle the Boot 4 upgrade — and I wanted to know, concretely, where that advice stops being safe. The CSRF 403 is the perfect probe: it is a one-line fix, it makes the test green instantly, and it quietly removes a security control. If an agent reaches for it by default, that tells you more about agent behaviour than any benchmark score.

One caveat up front, because it affects how much you should trust this: I am not claiming I migrated a production monolith and lived to tell the tale. I built a minimal, reproducible lab project — one controller, one security config, one test — and broke it on purpose by upgrading. That is better than a war story here, because you can see every line and rerun it yourself.

## The lab, and a myth I almost repeated

The project is deliberately boring. A `LabApplication`, an `OrderController` exposing `GET` and `POST` on `/api/orders`, and a `SecurityConfig` that sets `authorizeHttpRequests` plus HTTP Basic and says **nothing about CSRF**. I drove it with Maven and a `-Dboot.version` property, so the exact same source compiles against Boot 3.5.16 and 4.1.1 on Java 17. Boot 4 needs Java 17 or later, and I did not reach for 21 because the baseline here is what a cautious team already runs.

Before any agent touched it, I ran the test myself on both versions. Here is what I expected to write: Spring Boot 4 turns on CSRF for API endpoints by default, so your POST suddenly 403s. That story is circulating right now, and it is wrong.

The actual numbers:

| Boot version | `GET /api/orders` | `POST /api/orders` |
|---|---|---|
| 3.5.16 | 200 | **403** |
| 4.1.1 | 200 | **403** |

Same code, same config, identical behaviour. CSRF protection has been on by default in Spring Security for years — Boot 4 did not flip a switch. To be certain the 403 was CSRF and not authorization, I added an explicit `csrf.disable()` as a control run: both versions then returned 201. So the 403 is CSRF, but the *default* was already there in 3.5. If you meet a new 403 after upgrading, your old config was masking the gap, or your Boot 3 setup handled CSRF in a way your rewrite quietly dropped.

That correction matters enough that I have since fixed the CSRF wording in my own [Spring Boot 4 migration write-up](/blog/spring-boot-4-migration-ai-agents/) — the version that still said Boot 4 enables CSRF for APIs was simply wrong, and I am not going to leave it up.

## Run 1: Claude Code with no project context

I opened a fresh copy of the repo, gave Claude Code this prompt, and let it work:

> A Spring Boot 4 upgrade just landed. `POST /api/orders` returns 403, `GET` returns 200. Fix the 403 and make the test green. Don't change the controller or the URL.

It diagnosed the problem correctly. Its summary said the 403 came from Spring Security's `CsrfFilter`, not from authorization, and it even re-ran the test on Boot 3.5.16 to confirm the behaviour was consistent across versions. That is exactly what you want an agent to do — it did not guess, it verified.

Then it edited one line in `SecurityConfig`:

```java
.csrf(csrf -> csrf.disable())
```

The test went green on both versions. Job done, from the agent's point of view. From a security point of view, it had just turned off cross-site request forgery protection for the entire application because one write endpoint had no token. For a stateless HTTP Basic API that is a defensible choice — CSRF needs a browser session to exploit, and there is no session here — but the agent did not reason about that distinction. It took the shortest path to a green test, which is literally what fix the 403 asks for.

The dangerous part is not the `csrf.disable()` itself — for this specific stateless API it is arguable. The dangerous part is that nothing in the output flagged it as a trade-off. The test went green, the agent reported success, and a reader who trusted the summary would ship code that no longer protects any of its write endpoints against CSRF. That is the silent failure mode I keep warning about: the build passes, the agent is happy, and the security posture quietly changed.

## Run 2: the same prompt, with an AGENTS.md in the repo

Before the second run I dropped a 38-line `AGENTS.md` into the project root. Nothing clever. It stated three things plainly:

1. This is a stateless REST API authenticated with HTTP Basic; there is no browser session to hijack.
2. Spring Security enables CSRF by default and has for years — do not describe it as a Boot 4 regression.
3. Never call `csrf.disable()` globally to make a test pass. If a write endpoint has no token, scope the exemption with `csrf.ignoringRequestMatchers("/api/**")` and set the session policy to `STATELESS`.

Same broken project. Same prompt. Same model. The only difference was that file. I have reproduced it below because the wording is the entire experiment:

```markdown
# AGENTS.md

You are working in a Spring Boot REST API.

## Security model
- Authentication is HTTP Basic. There is no browser session and no cookie-based
  session state, so CSRF is not exploitable for this API's clients.
- Spring Security enables CSRF protection by default. This is NOT a Spring Boot 4
  regression — the same POST returns 403 on Boot 3.5 and 4.x alike.

## Rules
- Do NOT call `csrf.disable()` globally to make a test green.
- If a write endpoint has no CSRF token, scope the exemption instead:
  `csrf.ignoringRequestMatchers("/api/**")` and set
  `SessionCreationPolicy.STATELESS`.
- Keep CSRF protection enabled for every path outside `/api/**`.
```

This time the agent opened by correcting the premise I had accidentally fed it: *This is not a Boot 4 regression — I ran the same test on 3.5.16 and POST 403s there too.* Then it made a smaller, targeted change:

```java
.csrf(csrf -> csrf.ignoringRequestMatchers("/api/**"))
.sessionManagement(session -> session
    .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
```

CSRF stays on for every path that is not `/api/**`. The POST test passes. Nothing else lost its protection.

## The only variable was a text file

Put the two runs side by side:

| | Run 1 (no context) | Run 2 (with AGENTS.md) |
|---|---|---|
| Diagnosed CSRF correctly | Yes | Yes |
| Verified against Boot 3.5.16 | Yes | Yes |
| Final change | `csrf.disable()` (global) | `ignoringRequestMatchers("/api/**")` + `STATELESS` |
| CSRF protection elsewhere | Off | On |
| Why | Shortest path to green | Scoped per the repo rule |

The model did not get smarter between runs. The prompt did not get longer. The project did not change. The single thing that separated a globally-disabled CSRF from a correctly-scoped one was **38 lines of plain text in the repo**.

This is also the flip side of the point I made in the migration write-up — that agents are structurally bad at silent behaviour changes. An agent will happily disable a security control to satisfy a red test, because the test is the only feedback loop it trusts. A file in the repo that says do not do that, and here is the why gives it a second feedback loop, one that encodes your judgement instead of the compiler's. The agent did not become more capable in Run 2. It became more constrained, and constraint is what turned a dangerous fix into a safe one.

## Why your team should care

If you are going to let an agent touch a Spring Boot 4 upgrade, write the security rules down before it touches the code, not after the incident. Two takeaways I would put in a team guide today:

**Make the constraint explicit and scoped, never a bare prohibition.** Don't disable CSRF invites the agent to find another shortcut — maybe it rewrites the test to skip the security filter chain, or it swaps HTTP Basic for something it can satisfy. Scope the exemption to `/api/**` and set STATELESS tells it exactly what good looks like, so there is no gap for it to fill with imagination.

**Put the historical context in the file, not in your head.** The agent I ran had no memory of my earlier Boot 4 reading, so when my prompt implied it was a regression, it would have agreed with me. The `AGENTS.md` pre-empted that by stating the fact up front, in the repo, where the agent would actually read it. Context handed at prompt time is fragile; context that lives in the project survives the next session.

If you want the deeper version of how I structure these files — what goes in, what stays out, and how Claude Code and Codex read the same document — I wrote a [companion piece on AGENTS.md for Spring Boot](/blog/codex-agents-md-spring-boot/), and a [note on keeping project memory in Claude Code](/blog/claude-code-remember-spring-boot/) that covers the `CLAUDE.md` side of the same idea.

One honest gap: I intended to run this same broken project through Codex as a third arm. The Codex CLI on this machine was pinned to an older version whose default model rejected the request, and once I worked around that, the workspace sandbox rejected every file operation with `sandbox_apply: Operation not permitted`, so it never reached the code. I will run it and report what it does with and without the `AGENTS.md` in a follow-up — my guess is the same pattern holds, but a guess is not data, so I am not claiming the third result here.

## Reproduce it yourself

The whole lab is three files. A `SecurityConfig` with only `authorizeHttpRequests` and `httpBasic`, a controller with one GET and one POST, and a test that posts and asserts 201. Build with `-Dboot.version=3.5.16` and again with `4.1.1`; both 403 on POST. Then hand the repo to your agent with and without an `AGENTS.md` and diff the two `SecurityConfig` files. The experiment costs an afternoon and it will change how you write project rules.

## The short version

A 403 after a Boot 4 upgrade is CSRF, and CSRF has been the default for years — not a Boot 4 surprise. More usefully for your day-to-day: the difference between an agent that disables a security control and one that scopes it is often just whether you left it a note. Write the note.

Looking for the bigger picture on AI coding agents and Java? Start at the [Java + AI hub](/blog/ai-for-java-developers/).
