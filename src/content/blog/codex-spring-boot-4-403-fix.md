---
title: "Codex Fixed My Boot 4 403 — AGENTS.md Changed the Fix (2026)"
description: "I ran OpenAI Codex on the same broken Boot 4 upgrade twice. Without an AGENTS.md it killed CSRF app-wide; with one, the exemption stayed scoped to /api/**."
pubDate: 2026-09-11
category: "ai-tools"
tags: ["openai codex", "agents.md", "spring boot 4", "spring security csrf", "codex cli", "java-ai-cluster"]
image: "/og-codex-spring-boot-4-403-fix.jpg"
imageAlt: "A terminal showing Codex scoping a Spring Boot 4 CSRF exemption to /api/** next to a probe result proving a non-API path still returns 403"
keywords: ["codex spring boot 403", "codex agents.md", "spring boot 4 403", "spring security csrf", "codex cli spring boot"]
faq:
  - question: "Did Codex disable CSRF to fix a 403 on Spring Boot 4?"
    answer: "In my experiment it did — with no project context, Codex CLI reached for csrf(AbstractHttpConfigurer::disable), which turns CSRF off for every endpoint in the application. With a 38-line AGENTS.md in the repository, the same model and the same prompt produced csrf.ignoringRequestMatchers(\"/api/**\") plus STATELESS session management instead, leaving every non-API path protected. Same model, same prompt, same project — only the text file differed."
  - question: "Why does a Spring Boot POST return 401 instead of 403 when CSRF fails?"
    answer: "Because the status code reflects whether the request was authenticated when CsrfFilter ran, not whether CSRF caused the rejection. CsrfFilter sits earlier in the chain than BasicAuthenticationFilter, so an HTTP Basic client is still anonymous at that point. ExceptionTranslationFilter sees an anonymous principal and sends the request to the authentication entry point, which answers 401 with a WWW-Authenticate header. Pre-authenticate the request and the same CSRF rejection surfaces as 403. If you grep your logs for 403, you will miss the CSRF problem entirely."
  - question: "Does AGENTS.md work the same way for Codex as for Claude Code?"
    answer: "It changed the outcome identically in my runs — both agents went from a global csrf.disable() to a scoped exemption once the file was present. The difference I measured was verification, not the fix. Claude Code re-ran the test on Boot 3.5.16 to check whether the 403 was really a Boot 4 regression, in both of its runs. Codex did not run the cross-version check in either of its runs; it verified only that the test suite went green on the version in front of it."
---

## Last time I could not finish the experiment

At the end of my last piece I admitted something I do not like admitting: I set up two runs and only got to publish one. I handed a broken Spring Boot 4 upgrade to Claude Code twice — once with no context, once with an `AGENTS.md` in the repository — and the gap between the two fixes was the whole article. Then I tried to run the same project through OpenAI's Codex as a third arm, and it never reached the code. The CLI was pinned to an older version whose default model the API rejected, and once I worked around that, every file operation died with `sandbox_apply: Operation not permitted`.

I said then that I would run it and report what it did, and that a guess is not data. So here is the Codex arm, finally run. Two runs. Same broken project, same prompt, same model. One file's difference.

## The lab, unchanged on purpose

The project is the same three-file lab as before: a `LabApplication`, an `OrderController` exposing `GET` and `POST` on `/api/orders`, and a `SecurityConfig` that sets `authorizeHttpRequests` plus HTTP Basic and says **nothing at all about CSRF**. It builds against Boot 3.5.16 and 4.1.1 from one source tree via `-Dboot.version`, on Java 17.

I rebuilt it from scratch because the old directory had been cleaned out, and I ran the baseline again before any agent touched it. The numbers came back where the last article left them:

| Boot version | `GET /api/orders` | `POST /api/orders` |
|---|---|---|
| 3.5.16 | 200 | **403** |
| 4.1.1 | 200 | **403** |

Same behaviour on both. If you read the last article, you know what that means: CSRF has been on by default in Spring Security for years, and Boot 4 did not flip a switch. Whatever your new 403 is, it is not a Boot 4 regression. If you are still working out what the upgrade *did* change, and which of those changes fails with no compiler signal at all, I sorted them into [mechanical renames versus silent behaviour changes](/blog/spring-boot-4-migration-ai-agents/).

## The number that changed, and why it matters

The rebuild did turn up one thing I got wrong, and it is worth a paragraph before the agent results because it changes how you should search for this bug.

The last experiment's test pressed a Basic-authenticated `POST` through MockMvc with the principal already in the security context, and it failed with 403. My rebuilt test does the same and also gets 403. But when I pointed a real HTTP client at the same running application — `java.net.http.HttpClient`, HTTP Basic, no session — the same CSRF rejection came back as **401**, with a `WWW-Authenticate: Basic realm="Realm"` header and an empty body.

I did not trust that, so I ran a control: add `csrf.disable()` and the identical request returns 201. So the rejection is CSRF. Then I re-ran the MockMvc version, where the request is already authenticated when `CsrfFilter` executes, and it returns 403 again. Both are the same rejection from the same filter.

The explanation is filter order. `CsrfFilter` runs well before `BasicAuthenticationFilter`, so on a real HTTP request the principal is still anonymous at the moment CSRF fails. `ExceptionTranslationFilter` checks whether the current authentication is anonymous, and if it is, it hands the request to the authentication entry point — which answers 401 — instead of the access-denied handler that would answer 403. Pre-authenticate the request, as a test harness can, and you get the 403 everyone writes about.

The practical consequence is blunt. If your API authenticates with Basic and you are grepping logs for `403` because that is the number in every blog post, **you will never see it**. You will see a 401 and go hunting for a credentials problem, and your credentials are fine.

One more detail from that probe, because it is relevant later: a successful Basic-authenticated `GET` returned no `Set-Cookie` at all. There is no session to hijack here. The API really is stateless in practice, not just in intent.

## Run 1: Codex with no project context

The blocker last time was that Codex applies its own OS-level sandbox — Seatbelt on macOS — and this shell is already inside one, so the second sandbox refuses to initialise: `sandbox_apply: Operation not permitted`. That is not a Codex bug I can fix, so this time I passed `-s danger-full-access`, which tells Codex to skip its sandbox entirely, and the run went through. I also pinned `-m gpt-5.5`, because this CLI version's configured default model is newer than the CLI can decode and the API rejects it.

Same prompt as the Claude Code runs, verbatim:

> A Spring Boot 4 upgrade just landed. POST /api/orders returns 403, GET returns 200. Fix the 403 and make the test green. Don't change the controller or the URL.

Codex finished in 54 seconds and used 35,842 tokens. It changed one file, and here is the entire diff:

```java
http
        .csrf(AbstractHttpConfigurer::disable)
        .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
        .httpBasic(Customizer.withDefaults());
```

That is CSRF switched off for the whole application, to make one write endpoint's test pass. Its final report read, in full:

> Fixed the 403 by disabling CSRF in the Spring Security filter chain for the Basic-auth JSON API. [...] Result: BUILD SUCCESS, 2 tests passing.

No mention of a trade-off. No mention that the exemption covers every endpoint. If you only read that summary, you would ship it. The `AbstractHttpConfigurer::disable` idiom is actually tidier than the `csrf -> csrf.disable()` form Claude Code reached for — it sidesteps a deprecation warning — so the fix looks *more* considered while doing exactly the same thing.

## Run 2: the same prompt, one file added

I dropped the identical 38-line `AGENTS.md` from the last article into a fresh copy of the same broken repository. Nothing else changed. Codex finished in 63 seconds and used 40,043 tokens, and produced this:

```java
http
        .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
        .csrf(csrf -> csrf.ignoringRequestMatchers("/api/**"))
        .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .httpBasic(Customizer.withDefaults());
```

CSRF stays on everywhere except `/api/**`, which is exactly what the file asked for. And its report changed too:

> The change scopes CSRF ignoring to `/api/**` and sets stateless session management, leaving CSRF enabled for non-API paths. I did not change the controller or URL.

That last sentence about non-API paths is the part worth noticing. Run 1's summary described what it did; Run 2's summary described **what it deliberately did not break**. The file did not just redirect the fix, it redirected the reporting.

## What the green tests do not tell you

Both runs ended with `Tests run: 2, Failures: 0` and `BUILD SUCCESS`. Two passing tests, two entirely different security postures. A green suite is the worst possible evidence here, because both answers satisfy it.

So I proved the difference instead of asserting it. I added a throwaway controller with a `POST` on `/internal/orders` — deliberately outside `/api/**` — and asked both fixed versions what happens to it:

| `POST` target | Broken baseline | Run 1 (no `AGENTS.md`) | Run 2 (with `AGENTS.md`) |
|---|---|---|---|
| `/api/orders` | 403 | 201 | 201 |
| `/internal/orders` | 403 | **201** | **403** |

Run 1 answers 201 on a path it was never asked to touch. Run 2 answers 403 there, because CSRF is still guarding it. That single row is the difference between a scoped exemption and a disabled control, and no amount of test-passing output would have surfaced it.

## Where Codex and Claude Code actually differed

Put the four runs side by side and the headline is a replication, not a contest. Same broken project, two different agents, and the presence or absence of one text file flipped both of them from a global disable to a scoped exemption.

| | Claude Code | Codex CLI |
|---|---|---|
| Run 1, no `AGENTS.md` | `csrf.disable()` — global | `AbstractHttpConfigurer::disable` — global |
| Run 2, with `AGENTS.md` | `ignoringRequestMatchers("/api/**")` + STATELESS | `ignoringRequestMatchers("/api/**")` + STATELESS |
| Checked whether this was a Boot 4 regression | Yes, re-ran on 3.5.16 in both runs | **No, in neither run** |
| Run 1 report flagged the trade-off | No | No |

The one real gap is verification. Claude Code re-ran the suite against Boot 3.5.16 both times, on its own initiative, and reported that the 403 was not a Boot 4 regression — that is why its second run could correct the premise my own prompt had implied. Codex verified that the test passed on the version in front of it and stopped there. It never asked whether the number was new.

I do not think that makes one agent better. I think it makes the *file* more important for Codex. If an agent will not go looking for the historical context, you have to hand it over in the repository, in writing, or it will silently accept whatever premise your prompt implies.

## The sandbox wall is real, and it is not a setting

Worth recording, since I promised to explain why the third arm fell over last time. Codex's sandbox is not the same kind of thing as an approval flag. It calls the OS — Seatbelt on macOS — to confine the process, and a process that is already confined cannot ask the kernel to confine it again. `sandbox_apply: Operation not permitted` is that refusal, and it takes out `exec_command`, `apply_patch` and the tool sandbox together, so the agent cannot read a file let alone edit one.

That is why the fix that has worked for me elsewhere — `workspace-write` plus `sandbox_workspace_write.network_access=true`, which is the right answer on a normal machine — does nothing here. There is no flag that makes a nested Seatbelt work. For an experiment in a throwaway directory I am comfortable with `danger-full-access`; for anything touching a real repository I would run Codex on the host, where its sandbox can actually initialise, and keep the isolation.

The honest summary is that my earlier failure was environmental, not a Codex limitation, and I should have said that at the time rather than leaving it as an open question.

## What I would put in a team guide

**Make the file scoped, not prohibitive.** A bare don't disable CSRF just tells the agent what to avoid, and an agent under pressure to turn a test green will find something else — weaken the rule, rewrite the test, or swap the auth scheme for something it can satisfy. Naming the mechanism, the matcher and the session policy gives it a target instead of a gap.

**Write the definition of done as a probe, not a test result.** Run 1 and Run 2 are indistinguishable from their test output. If your `AGENTS.md` says only make the suite green, you have described a bar that a global disable clears just as easily as a scoped exemption. Say what must remain true afterwards — CSRF stays enabled for every path outside the API matcher, and here is how to check it — and the agent has to verify a boundary rather than a colour.

**Grep for the symptom, not the status code.** The 401-versus-403 split above cost me a wrong assumption in a published article. If you are matching on one number because that is what the internet says, you are filtering out the case that actually applies to your client.

## Reproduce it yourself

Three source files, one `pom.xml`, two Boot versions. Build with `-Dboot.version=3.5.16` and again with `4.1.1`; both return 403 on `POST`. Then hand the repo to Codex or Claude Code with and without an `AGENTS.md`, diff the two `SecurityConfig` files, and add a `POST` route outside your API matcher to see which version still answers 403. The whole experiment is an afternoon, and the probe is the part that makes it worth running.

For the file itself, the format, and how the same document is read by both agents, I wrote a [dedicated guide to AGENTS.md for Spring Boot projects](/blog/codex-agents-md-spring-boot/), and the [Codex-on-Spring-Boot starting point](/blog/codex-spring-boot/) covers the approval modes and sandbox tiers that this experiment kept tripping over. If you want the companion arm with Claude Code doing the same two runs, it is [here](/blog/claude-code-spring-boot-4-403/).

## The short version

Codex disabled CSRF application-wide to fix a 403, and a 38-line `AGENTS.md` was the only thing that made it scope the exemption instead — the same result I measured with Claude Code last time. The number I had wrong was the status code: with HTTP Basic over real HTTP, the same CSRF rejection arrives as 401, not 403, so the log line most people search for never appears. And two passing tests proved nothing about either fix, which is why the probe exists.

If you are working through a Spring Boot 4 upgrade with an agent in the loop, start at the [Java + AI hub](/blog/ai-for-java-developers/).
