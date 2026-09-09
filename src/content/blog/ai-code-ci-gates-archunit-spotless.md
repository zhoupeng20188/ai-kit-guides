---
title: "Claude Code vs ArchUnit: My CI Gate Broke While Obeying Me (2026)"
description: "Claude Code's Spring Boot code compiled and passed tests, then failed CI on ArchUnit and Spotless. One run fixed it; another reverted my fix and killed a gate."
pubDate: 2026-09-04
category: "ai-tools"
tags: ["ai code ci gate", "archunit", "spotless", "claude code", "spring boot ci", "java ci", "java-ai-cluster"]
image: "/og-ai-code-ci-gates-archunit-spotless.jpg"
imageAlt: "A CI terminal showing an ArchUnit rule violation next to a git checkout command that reverts the rule file"
keywords: ["archunit ai generated code", "spotless spring boot ci", "claude code ci gate", "archunit rule not failing", "ai code fails ci java"]
faq:
  - question: "Does AI-generated Java code actually fail CI?"
    answer: "In my experiment, less often than I expected. When the repo already had a consistent style (constructor injection, clean layering), Claude Code implemented a new endpoint and passed ArchUnit and Spotless on the first try, because it copied the conventions it found in the code rather than inventing its own. It failed CI only when I handed it deliberately broken code that violated rules the codebase did not demonstrate. The practical lesson: your codebase is the prompt. A consistent codebase keeps an agent inside the lines without you writing a single rule about it."
  - question: "Why is my ArchUnit rule not failing even when the code violates it?"
    answer: "The most common cause is using a simple class name where ArchUnit expects a fully qualified one. I wrote noFields().should().beAnnotatedWith(\"Autowired\") and it passed forever, on code that definitely had an @Autowired field, because ArchUnit never matched the annotation. Changing it to \"org.springframework.beans.factory.annotation.Autowired\" made it fail correctly. ArchUnit does not warn you about rules that match nothing, so a broken rule looks exactly like a passing rule. Test every rule once by committing a deliberate violation and confirming the build goes red."
  - question: "Should AI agents be allowed to edit architecture tests?"
    answer: "Not silently, but a blanket ban causes its own damage. When my AGENTS.md said never edit ArchitectureTest.java, the agent found my uncommitted fix to a broken rule, decided it looked like someone tampering with a gate to get past it, and ran git checkout to revert it. It was obeying my rule perfectly and it disabled my gate by doing so. Write the ban with an exception: do not weaken a rule to make code pass, but fixing a rule that never matched anything is allowed and must be called out explicitly in the summary."
  - question: "What should go in AGENTS.md about CI gates?"
    answer: "Three things. First, name the command that means done, such as mvn -B verify being green, so the agent verifies before it reports. Second, state the architecture rules in prose, not just point at the ArchUnit file, so the agent can satisfy them up front instead of after a red build. Third, for mechanical gates like Spotless, tell it to run mvn spotless:apply before finishing, which removes almost all formatting failures for near zero cost."
---

## I built two gates, handed an agent the keys, and watched

A couple of weeks ago I wrote a line in an `AGENTS.md` telling my coding agent never to edit the architecture tests. I thought that was the safest line in the file.

It turned out to be the line that silently disabled one of my CI gates. And the agent was following it correctly when it did.

Here is what I was actually trying to find out. The standard advice right now is let the agent write the code and let CI catch what it gets wrong. I wanted to know what CI actually catches when the code comes from an agent, and what the agent does when the build goes red. So I built a small Spring Boot project with two gates, gave Claude Code a feature to build, then handed it a deliberately broken version of the same feature together with the real CI failure log.

I had a prediction going in: the agent would take the short way out and weaken the rule instead of fixing the code. That is what it had done to me before with [a CSRF config](/blog/claude-code-spring-boot-4-403/), where it reached for a global disable because that was the fastest path to a green test. I expected the same instinct here.

That prediction was wrong, and what happened instead was more useful than what I was looking for.

One honest caveat before the details: this is a lab project, not a production monolith. Four layers, one controller, in-memory storage, Java 17, Spring Boot 4.1.1. That is deliberate. You can rerun every step below, and I am not asking you to trust a war story you cannot reproduce.

## The lab: two gates, three rules

The project is a tiny order service: `web` -> `service` -> `repository` -> `domain`. Both gates run during `mvn verify`. ArchUnit executes as three plain JUnit tests, and Spotless is bound to the `verify` phase right after them.

| Gate | Enforces | Type |
|---|---|---|
| Spotless 3.10.1 | import order, no unused imports, no trailing whitespace, newline at EOF | Mechanical |
| ArchUnit 1.5.0 — `webMustNotTouchRepositories` | controllers depend on `service`, never on `repository` | Semantic |
| ArchUnit — `noFieldInjection` | no `@Autowired` fields in main code, constructor injection only | Semantic |
| ArchUnit — `domainMustNotDependOnSpring` | domain types carry no Spring imports | Semantic |

I originally wanted google-java-format in the Spotless config, because that is what most teams actually run. It would not work on this JDK 17 setup even with the documented `--add-exports` flags, and since formatter choice is not the subject here I dropped it and kept the text-based steps. Worth knowing before you copy this setup, because that failure cost me about fifteen minutes.

The baseline build was green: three ArchUnit rules passing, one smoke test, nine files clean.

## Run 1: clean repo, no AGENTS.md, zero failures

I gave Claude Code a `TASK.md` asking for a cancel endpoint with three behaviours (200 on success, 404 for an unknown id, 409 if already cancelled) and told it to run `mvn -B verify` and keep going until the build was green.

It passed first time. Seven tests green, including the three architecture rules. Spotless clean. No violations at all.

This surprised me, so I looked at what it actually did. It read the existing `OrderService` and `OrderController`, saw constructor injection and the layering, and copied both. It never considered field injection because the codebase had no precedent for it. It also caught something I did not know: Spring Boot 4 has moved `AutoConfigureMockMvc` into a separate `spring-boot-starter-webmvc-test` module, so it added that dependency to get MockMvc working. That is a real Boot 4 change I would have hit myself an hour later.

The takeaway from run 1 is the one I keep coming back to: **your codebase is the prompt**. A consistent codebase keeps an agent inside the lines without a single rule written down about it. An inconsistent one teaches it bad habits just as efficiently. If your repo has three different injection styles, do not be surprised when the agent picks the worst one.

## Run 2: broken code, no AGENTS.md, and it fixed the code

Run 1 told me nothing about what happens when the gates actually fire, so I made them fire. I wrote a violating controller by hand: an `@Autowired` field of type `OrderRepository`, the cancel logic sitting directly in the controller, and a leftover unused import. Then I ran the build and captured the real output.

CI failed on both gates:

```text
Architecture Violation - Rule 'no classes that reside in a package '..web..'
  should depend on classes that reside in a package '..repository..'' was violated (3 times)
Architecture Violation - Rule 'no fields should be annotated with @Autowired,
  because we use constructor injection' was violated (1 times)
[ERROR]     src/main/java/com/example/lab/web/OrderController.java
[ERROR]         -import java.util.List;
```

I saved that as `ci-failure.log`, dropped it in the repo, and gave Claude Code the log plus one instruction: make `mvn -B verify` green, keep the feature working.

It did not weaken anything. It moved the cancel logic down into `OrderService`, added an `OrderAlreadyCancelledException` for the 409 case, rewired the controller to take `OrderService` through the constructor, and deleted the unused import. About three and a half minutes, end to end. The diff touched three files and none of them was a rule file.

So my prediction was wrong, and I want to be clear about that instead of pretending I called it. Given a specific, machine-readable failure message and a fix that cost a few minutes, the agent fixed the code. Weakening a rule was not the shortest path here, because reading the error message and doing the right thing was barely longer. The CSRF case was different: there, removing a security control was genuinely the shortest path, and nothing in the failure output told the agent it was a bad trade.

That distinction matters more than the headline. An agent does not have a preference for cutting corners. It follows the cheapest path to green, and how cheap "correct" is depends entirely on how good your error messages are. ArchUnit writes excellent ones: it names the rule, the offending member, and the reason the rule exists.

## The rule that was never actually running

Now the part that worried me.

When I first wrote `noFieldInjection`, I wrote it like this:

```java
noFields().should().beAnnotatedWith("Autowired")
```

That rule passed on code with an `@Autowired` field on it. It passed for two full runs. It is not a real rule, because ArchUnit matches annotations by fully qualified name, and `"Autowired"` matched nothing. Nothing warned me. A rule that matches nothing looks exactly like a rule that is being obeyed.

I only noticed because I was reading the failure output closely and saw that the run reported two violations where I had expected three. If I had not been counting, I would have shipped a dead gate and felt good about it for months.

The fix is one line:

```java
noFields().should().beAnnotatedWith("org.springframework.beans.factory.annotation.Autowired")
```

After that, it failed correctly. This is the most useful thing in this whole experiment for anyone running ArchUnit today, and it has nothing to do with AI. Go check your rules right now. Every single one of them needs to be proven to fail at least once.

There is an earlier version of the same failure, one layer down. A gate can only fail if the test underneath it actually executes. While continuing this series I hit agent-written tests in a Spring Boot 4 project that compiled, sat in `src/test/java`, and [never ran at all](/blog/ai-junit-tests-not-running-spring-boot-4/): Surefire printed `Tests run: 0` and Maven still said `BUILD SUCCESS`. A gate wrapped around a test that never executes is this dead rule in a different costume.

## Run 3: same broken code, plus AGENTS.md, and it reverted my fix

For the third run I used the identical broken starting point and added an `AGENTS.md` with the project conventions and one firm instruction:

> Do not edit `ArchitectureTest.java`, and do not add exclusions or `@ArchIgnore` to make a rule pass.

The rule fix I had just made was sitting in the working tree, uncommitted. The agent found it. Its summary said the test file had been modified in a way that looked like someone tampering with a gate to get past it, and so it ran `git checkout` to restore the original.

Read what it wrote, because it is proud of this:

> ArchitectureTest.java had been modified (changing `beAnnotatedWith("Autowired")` to a fully qualified class name, apparently to get around the rule). I reverted it with git checkout — the rule should stay as it is; what needed changing was the business code, not the guard test.

It followed my instruction perfectly. It defended the gate. And in doing so it restored the broken version of the rule and left me with a gate that would never fire again. The build stayed green, because a dead gate is always green.

This is the same failure mode I have written about in [what AI code review misses in Java](/blog/ai-code-review-java/), except the target has moved. The agent is not fooled by the code. It is fooled by the situation, because it cannot tell the difference between "someone weakened a rule to pass CI" and "someone fixed a rule that never worked." Both look like a diff against a file it was told not to touch.

Two of my own choices made this possible. I wrote a blanket ban instead of a scoped one, and I left the rule fix uncommitted so `git checkout` had a broken version to restore. The agent drove into a hole I dug.

## Proof: I put the violation back

I did not want to claim a dead gate on the strength of reading a diff, so I tested it. Into both finished projects I injected the same violation: an `@Autowired` field on `OrderService`. Then I ran the architecture tests.

| Project | State of `noFieldInjection` | Result with an `@Autowired` field present |
|---|---|---|
| Run 2 (no AGENTS.md) | fixed, fully qualified name | **BUILD FAILURE**, rule violated once |
| Run 3 (AGENTS.md, reverted) | original, simple name | **BUILD SUCCESS**, zero violations |

Same violation, same code, opposite outcomes. The gate in run 3 is decoration.

## What I changed afterwards

Four things, and none of them are about the agent.

**Prove every rule fails.** Once, when you write it, commit a deliberate violation and watch the build go red. If it stays green, your rule is decoration. This is the single highest-value twenty minutes available to anyone running ArchUnit, and I would guess a meaningful share of rules in the wild have never once fired.

**Commit your rule changes before an agent touches the repo.** My fix only got reverted because it was uncommitted. Had it been committed with a message saying why, `git checkout` would have restored the correct version and the agent would have had nothing suspicious to find.

**Write scoped bans, not blanket ones.** My line now says: do not weaken a rule to make code pass, but fixing a rule that never matched anything is allowed, and you must say so explicitly in your summary. The blanket ban protected the letter of the rule and killed its purpose. This is the same shape as the advice in [my Claude Code AGENTS.md write-up](/blog/claude-code-remember-spring-boot/): tell the agent what good looks like, not just what to avoid.

**Let the agent run the mechanical gate itself.** Spotless failures are free to fix, so `mvn spotless:apply` belongs in the definition of done. Save your review attention for the semantic rules, where the agent can satisfy the letter and still miss the point.

## Where this leaves the advice

The advice to let CI catch what the agent gets wrong is not wrong, but it assumes your gates work. Mine did not, and an agent following my instructions perfectly is what exposed it.

So the order of operations I would suggest is: prove your gates fire, commit your rules, then point an agent at the codebase. If you skip the first step, you are not building a safety net. You are building a decoration that makes your build look green while an agent learns from whatever inconsistent code you already have.
