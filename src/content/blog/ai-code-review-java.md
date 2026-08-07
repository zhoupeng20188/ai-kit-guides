---
title: "What AI Code Review Misses in Java (and How I Catch It) (2026)"
description: "My team runs every PR through an AI reviewer, but it once green-lit code that broke production. Here's what AI code review misses in Java, and my workflow."
pubDate: 2026-08-07
category: "ai-tools"
tags: ["ai code review", "java code review", "ai code review java", "github copilot code review", "claude code review"]
image: "/og-ai-code-review-java.jpg"
imageAlt: "Terminal showing an AI code review comment on a Java Spring Boot pull request, with a @Transactional annotation highlighted in the diff"
keywords: ["ai code review java", "ai code review for java", "what does ai code review miss", "github copilot code review java", "claude code review java"]
faq:
  - question: "Can AI review Java code?"
    answer: "Yes, and it is genuinely useful for the mechanical layer: unused imports, swallowed exceptions, dead variables, overly long methods, and obvious null-handling gaps. It reads a 40-file diff in seconds, which no human does consistently. What it misses is correctness in transactions, concurrency, Spring wiring, JPA access patterns, and newer Java features, because those depend on intent and runtime context, not just syntax. Treat it as a fast first pass, not the final approver."
  - question: "Is GitHub Copilot code review good for Java?"
    answer: "It is a solid style and obvious-bug checker on Java PRs and it runs automatically on every push, which alone makes it worth having. For Spring Boot specifically, it catches the easy stuff but routinely passes over @Transactional boundary mistakes, @Qualifier mixups, and JPA N+1 risks, because it reviews the diff in isolation. I keep it on, read its comments, but never let it be the only reviewer on code that touches money, inventory, or persistence."
  - question: "What does AI code review miss in Java?"
    answer: "Four zones: (1) transactions and concurrency, like a @Transactional that is never actually applied or a synchronized block that pins carrier threads under virtual threads; (2) Spring wiring, where a bean is @ConditionalOnProperty gated or a @Qualifier points at the wrong implementation; (3) JPA, where a lazily loaded collection inside a loop becomes an N+1 storm only in production; (4) Java 21 features used wrong, like a record holding a mutable list reference or a switch pattern that swallows a narrower case. All four compile, pass tests, and look fine to a token-level reviewer."
  - question: "How do I review AI-generated Java code?"
    answer: "Run the AI review first, then open the diff and read four zones by hand: anything with @Transactional, anything touching beans or @Qualifier, any JPA entity or repository method, and any Java 21 feature. For the hard parts, paste the code plus its surrounding context into the chat and ask specifically about transaction or concurrency bugs, because giving it context it did not have changes the answer. Finish with one full top-to-bottom read as if a stranger wrote it, because one did."
---

Every pull request on my team now runs through an AI reviewer first. Copilot comments inline, Claude Code Review posts a pass or a list of nits, and Cursor's BugBot pokes at the diff. I'm not anti-AI here. I set this up on purpose, and it catches real stuff: empty catch blocks, a missing null check, a variable named `temp2` that should have been deleted three sprints ago.

But about two months ago an AI reviewer green-lit a change that looked clean and then broke production on a Monday. Not a crash. A `@Transactional` boundary that was one level too high, so a batch job committed partway through and left the ledger half-written. The AI never flagged it. It looked fine to a tool that reads tokens, not intent.

So this is the post I wish I'd had before I trusted the green checkmark. I'll show you what **AI code review** misses in Java specifically, why those gaps are dangerous, and the concrete review workflow I use now so the AI helps instead of lulling me to sleep.

## What AI Code Review Actually Catches Well

Let me give it credit. The boring, mechanical stuff is where it shines, and that's exactly the stuff a tired human skips at 5pm on a Friday.

It spots unused imports and dead variables fast. It catches a swallowed exception (`catch (Exception e) {}`) that you wrote and forgot about. It flags when a method is 200 lines long and suggests a split. On a 40-file diff it reads every line in seconds; no human does that consistently.

I've also found it useful as a second set of eyes on style. If three reviewers all say "this naming is confusing," the author usually listens. So don't throw it out. The problem is what it misses, not what it finds.

## The Gap #1: Transactions and Concurrency

This is the one that bit me. Java backend code lives and dies on `@Transactional`, thread safety, and now virtual threads. These are exactly the places an AI reviewer struggles.

A `@Transactional` annotation only does something if the method is called through the Spring proxy. If the AI adds a `saveAndNotify()` that calls itself internally, or if it puts the annotation on a `private` method, the transaction silently doesn't apply. The code compiles, the tests pass, the AI says "looks good." Then in production a partial failure leaves data inconsistent, and you find out from a finance complaint, not a test.

Concurrency is worse. I've seen an AI suggest `synchronized` on a method that does blocking I/O, which on a virtual-thread-heavy service is exactly the wrong call. It reads as "thread safe" to a pattern matcher but it pins carrier threads. The AI knows the word `synchronized`. It doesn't know your throughput.

My rule now: for any PR touching money, inventory, or anything with `@Transactional`, I read that section by hand. The AI did not earn the right to approve that one.

## The Gap #2: Spring Wiring and Dependency Injection

If you've read my piece on [using AI on a legacy Java codebase](/blog/using-ai-legacy-java-codebase), you know I'm cautious about AI touching shared Spring beans. The review side has the same trap.

The AI can't always tell whether a bean is actually wired. It sees `@Autowired private PaymentGateway gateway;` and assumes the gateway exists. But if that bean is `@ConditionalOnProperty` gated, or only present in a profile you don't run locally, the AI's "looks complete" is a lie your startup will tell you about at 2am. I wrote about this class of break in my [Cursor + Spring Boot workflow](/blog/cursor-spring-boot) post, and it shows up just as often in review as in generation.

`@Qualifier` mixups are another favorite. Two implementations of an interface, the AI picks the wrong one, the diff is tiny, and the reviewer (human or AI) glances past it. I've started grepping for every `@Qualifier` change in a PR before I approve.

## The Gap #3: JPA, N+1, and Lazy Loading

ORM code is where AI review is most confidently wrong. It generates a fetch plan that looks reasonable in a unit test with three rows and explodes in production with three million.

A common miss: the AI adds a getter that lazily loads a collection inside a loop, and suddenly you've got an N+1 query storm. The code is "correct" (no exception), the tests are green (small dataset), the AI says "LGTM." Then the endpoint that took 40ms in staging takes 9 seconds in prod and the on-call person is you.

Lazy vs eager is a judgment call that depends on your actual access patterns, not on what compiles. An AI reviewer reads the entity in isolation. It does not know that `Order.getItems()` is called inside a hot loop. I treat any JPA fetch or `@Transactional(readOnly=true)` change as hand-review-only.

## The Gap #4: Java 21 Features Used Wrong

We moved to Java 21 and the newer syntax is a double-edged sword for reviewers. Records, sealed types, pattern matching in switch, virtual threads. They're great, and the AI loves generating them, but it gets the semantics subtly wrong.

Example: a `record` is supposed to be immutable, but the AI stuffs a mutable `List` field into it and returns the internal reference. Callers mutate it, your "immutable" data structure lies. Or a sealed interface where the AI forgets a `permits` clause and the compiler error is cryptic enough that someone "fixes" it by removing the seal.

Pattern matching in switch is another spot. The AI writes cases in an order where a broader pattern swallows a narrower one, and the logic is silently wrong for one input type. The code runs. The tests for that type don't exist. The AI says nothing.

## The Review Workflow I Actually Use

None of this means "don't use AI review." It means use it as the fast first pass, not the final word. Here's my actual flow on a Java PR:

1. AI reviews first (Copilot inline plus Claude Code Review on the PR). I read its comments but assume they're about style and obvious bugs, not correctness.
2. I open the diff and jump straight to four zones: anything with `@Transactional`, anything touching beans or `@Qualifier`, any JPA entity or repository method, and any Java 21 feature (record, sealed, switch). These get my eyes, not the AI's.
3. For the tricky parts, I paste the relevant code plus the surrounding context into the chat and ask it to find concurrency or transactional bugs specifically. Giving it context it didn't have changes the answer completely. "Is this `@Transactional` actually applied given how it's called?" gets a much better answer than a blind diff scan.
4. I read the final diff top to bottom once, like a stranger wrote it, because one did.

I cover the generation-side habits in my [Claude Code on Spring Boot](/blog/claude-code-spring-boot) writeup, and the review discipline is the same muscle. The point isn't paranoia. It's that the AI is fast and confident and context-blind, and the parts it's blind to are the parts that take down production.

## Summary

AI code review is a genuine time saver for the mechanical stuff, and I'd never go back to reviewing 40-file diffs by hand. But on a Java backend, the expensive bugs live in transactions, concurrency, Spring wiring, ORM access patterns, and the newer language features. The AI misses those precisely because they need intent and context, not just pattern matching.

If you take one thing from this: treat the green checkmark as "no obvious typos," not "safe to merge." Read the four zones yourself, give the AI context when you need its help, and keep the final read for your own eyes.
