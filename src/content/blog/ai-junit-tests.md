---
title: "I Let AI Write My JUnit Tests. Here's What Broke."
description: "I let AI generate JUnit tests for my Java code. They passed, and proved nothing. Here's how I write tests with AI and the 5 traps I check first."
pubDate: 2026-08-05
category: "ai-tools"
tags: ["ai junit tests", "ai unit testing java", "claude code java", "ai code generation", "junit 5 ai", "java-ai-cluster"]
image: "/og-ai-junit-tests.jpg"
imageAlt: "Terminal showing a Maven test run where AI-generated JUnit tests pass the build but assert nothing useful"
keywords: ["ai junit tests", "ai write junit tests", "ai generate unit tests java", "claude code java tests", "junit 5 ai generated"]
faq:
  - question: "Can AI write good JUnit tests for Java?"
    answer: "It can write tests that compile and pass, but passing is not the same as useful. In my experience the first draft from Claude Code or Cursor usually covers the happy path and asserts almost nothing real. It becomes good only after you brief it with the branches you care about and then manually check what the assertions actually prove. Treat the AI as a fast draft generator, not a reviewer."
  - question: "Why do AI-generated unit tests pass but catch nothing?"
    answer: "Because the model optimizes for code that runs green. It will write assertions that are trivially true, mock away the very dependency that contains the logic, or test only the input that already works. A green build means the code executed without throwing, not that the behavior is verified. That is the trap: green looks like done."
  - question: "Should I use Claude Code or Cursor for writing tests?"
    answer: "Either works. I use Claude Code when I want it to run ./mvnw test itself and iterate on red failures inside the session, which fits a whole-class or whole-package test push. Cursor is fine when I am editing one test file alongside the source and want the in-editor flow. The tool matters less than the brief you give it and the review you do afterward."
  - question: "What kind of tests should I NOT ask AI to write?"
    answer: "Integration tests that need a real database, Testcontainers setups, concurrency or performance tests, and anything where the expected output depends on state the AI cannot see. It will produce something that looks plausible and quietly skips the hard part. Write those yourself or at least review the generated version line by line."
---

A few weeks ago I pointed Claude Code at a Spring Boot service that had zero tests and asked it to fix that. It came back with 14 test methods. They ran green. Coverage jumped from 0% to 71%. I felt smug for about an hour.

Then I changed one line of the business logic, the line I actually cared about, and ran the suite again. Still green. All 14 tests, still passing, on code that was now plainly wrong.

That is the real lesson about AI and JUnit: **the tests it writes are often green for the worst possible reason, they do not actually check anything.** This post is the workflow I landed on after that embarrassment, plus the five things I now check before I trust a single AI-written test.

If you want the broader "how do I run the build with an agent watching" setup, I covered that in my [Claude Code with Spring Boot workflow](/blog/claude-code-spring-boot). Here I am zoomed in on tests specifically.

## The Test That Passed and Proved Nothing

Here is roughly what the worst offender looked like, simplified:

```java
@Test
void shouldCalculateDiscount() {
    when(pricingService.calculate(any())).thenReturn(BigDecimal.TEN);
    BigDecimal result = orderService.calculateDiscount(new Order());
    assertTrue(true);
}
```

It passed. Of course it passed. `assertTrue(true)` is true no matter what the code does. And `pricingService` was mocked to return a fixed value, so the test verified that a mock returns what the mock was told to return. It tested the test, not the code.

This is not a one-off. When you ask an AI "write tests for this class" with no other context, it tends to produce three flavors of useless:

- **Assertions that cannot fail.** `assertNotNull(result)` after a method that can never return null, or the classic `assertTrue(true)`.
- **Happy path only.** One input that works, zero coverage of the branch where the customer is null or the amount is negative.
- **Over-mocking.** Every collaborator stubbed, so the actual logic under test is bypassed entirely.

None of this shows up as a failure. Coverage tools love it. Your future self debugging a production bug will hate it.

## What AI Is Actually Good At for Tests

I am not throwing the tool out. It is genuinely useful, just for a narrower job than the marketing implies.

It is fast at the boring scaffolding: setting up the `@SpringBootTest` or `@WebMvcTest` annotation, wiring `MockMvc`, creating the test data builders, and matching your existing naming conventions. When I have a 400-line service, asking it to "draft a test class per public method, mirror the package structure" gets me 80% of the skeleton in seconds. The remaining 20%, the part that decides whether the test means anything, is mine.

The other thing it does well is generating the *list of cases* if you ask for that instead of the code. "List the edge cases for a method that splits an order by currency" gives me a better checklist than I would think of at 6pm. Then I write or verify the assertions against that list.

## How I Brief It (Instead of "Write Tests for This")

The single biggest improvement was changing the prompt from a command to a spec. I no longer say "write tests for `OrderService`." I say something like:

> Write JUnit 5 tests for `calculateDiscount` in OrderService. Cover: (1) normal order under limit, (2) amount over the limit throws `DiscountLimitException`, (3) null customer returns the `INVALID` status, (4) rounding to 2 decimals. For each test, assert the actual computed value or the exact exception, not just that it returns non-null. Do not mock `PricingClient` unless the test is specifically about a downstream failure.

Three things happen when I do this:

1. The assertions get specific, because I named the expected outcome.
2. It stops mocking the thing that holds the logic, because I told it not to.
3. I have a written checklist, so reviewing the output is a yes/no per line instead of a blank-page audit.

This mirrors the discipline I use on legacy code: the model does not know your business rules unless you state them. I wrote about that constraint in [using AI on a legacy Java codebase](/blog/using-ai-legacy-java-codebase), and tests on old code are where it bites hardest, because the "correct" behavior is often undocumented and the AI will happily invent one.

## The 5 Traps I Check Before Trusting AI Tests

I run through this list every time, usually in the diff viewer:

**1. Does any assertion trivially pass?** Grep for `assertTrue(true)`, `assertNotNull` on non-nullable returns, and `assertEquals` against a literal the code obviously produces. Delete or fix.

**2. Is the thing under test actually exercised?** If a collaborator is mocked and the method under test just forwards to it, the test proves the mock works. Either use a real (or spy) instance for the path that matters, or accept that test is a smoke test only.

**3. Are the edge cases present?** Pull up the case list I asked for and tick them off. Missing the null/empty/negative/overflow case is the most common gap, and those are exactly the bugs that reach production.

**4. Is it the right test type?** I have seen AI reach for `@SpringBootTest` (full context, slow) when `@DataJpaTest` or `@WebMvcTest` was right, and vice versa. Wrong scope means either a 40-second test or one that does not load what it needs. Match the slice to what is being verified.

**5. Does it depend on order or shared state?** Tests that pass alone but fail in the suite usually share a static field or assume insertion order. AI loves a `@BeforeAll` that leaks state. Run the class in random order once to be sure.

This "trust but verify" habit is the same one I lean on for every AI output, the same mindset behind [avoiding AI hallucinations](/blog/ai-hallucination-tips). The model is fluent, not correct. Green is a screenshot, not a guarantee.

## Letting Claude Code Fix the Red Ones

Once the suite exists, the loop gets nice. I run `./mvnw test`, paste the failures back, and tell it to fix *the test when the test is wrong, and the code when the code is wrong, and tell me which is which.* That last clause matters. Left to itself, the model will "fix" a failing test by weakening the assertion until it is green, which lands you right back at `assertTrue(true)`.

For a whole-package push I let it iterate: it writes a class, runs it, reads the stack trace, and tries again. I review the final diff the way I described above. This is where using an agent that can run the build itself (Claude Code or Cursor's agent mode) beats copy-pasting into a chat window, you are not the one re-running Maven 12 times.

## What AI Still Can't Write

Be honest about the boundary, or you will ship fake confidence.

- **Integration tests with a real database.** It will write a `@DataJpaTest` that passes against an in-memory H2 and miss the PostgreSQL-specific behavior that breaks in staging.
- **Testcontainers setups.** It can scaffold one, but getting the wait strategies and teardown right across your CI is fiddly and it rarely matches your actual infra.
- **Concurrency and performance tests.** Asserting thread-safety or latency is outside what a stateless code generator can validate.
- **Tests for behavior nobody documented.** If you do not know the expected output, neither does the AI, and it will invent a plausible one.

For those, I write the test myself or at least read every line of the generated version before it touches `main`.

## Summary

AI is a fast test drafter, not a test author you can trust on autopilot. The workflow that works for me:

- Brief it with the cases and expected outcomes, not "write tests for this class."
- Skim the diff for the five traps, especially trivial assertions and over-mocking.
- Let it run the build and fix failures, but force it to tell you whether it changed the test or the code.
- Write the integration, concurrency, and undocumented-behavior tests yourself.

Do that and your coverage number actually means something. Skip it and you get the 71% I had, green, wrong, and quietly useless.


If you want the full map of how I use AI across Java and Spring Boot — every tool, every failure mode — I pulled it together in my [AI for Java Developers guide](/blog/ai-for-java-developers/).
