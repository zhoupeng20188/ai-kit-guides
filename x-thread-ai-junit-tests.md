# X Thread — AI-written JUnit tests (from `ai-junit-tests`)

6 posts, English, each ≤280 chars. Based on the article published 2026-08-05. This is the natural follow-up to the Cursor/Claude Code Spring Boot threads — same "green ≠ correct" theme, zoomed into tests.

---

**Post 1** (~242 chars)

I pointed Claude Code at a Spring Boot service with zero tests. It returned 14 tests, all green. Coverage jumped 0% → 71%.

Then I changed one line of the logic I cared about. Ran the suite. Still green. All 14. On code that was now wrong. 🧵

---

**Post 2** (~230 chars)

The worst offender:

when(pricingService.calculate(any())).thenReturn(TEN);
assertTrue(true);

It passed. Of course it passed. A mock returned what the mock was told to. It tested the test, not the code. Green meant "ran," not "verified."

---

**Post 3** (~252 chars)

The fix wasn't a better tool. It was a better brief.

I stopped saying "write tests for OrderService." I list the cases and expected outcomes: throws DiscountLimitException over limit, INVALID on null customer, round to 2 decimals.

Then I review against that checklist, line by line.

---

**Post 4** (~250 chars)

The 5 traps I check in every AI test diff:
1. assertions that trivially pass (assertTrue(true))
2. the real logic mocked away
3. missing edge cases (null / negative / overflow)
4. wrong test slice (@SpringBootTest vs @DataJpaTest)
5. shared state / order dependence

---

**Post 5** (~234 chars)

Nice loop: run ./mvnw test, paste failures back, tell it to "fix the test when the test is wrong, the code when the code is wrong, and tell me which."

That last clause stops it weakening the assertion to green. Which is exactly how you got back to assertTrue(true).

---

**Post 6** (~150 chars)

Full workflow + the 5-trap checklist:

👉 https://aikitguides.com/blog/ai-junit-tests

What's your AI-test horror story? 👇

---

## Posting notes
- Post after the claude-code-spring-boot / cursor-spring-boot threads, not the same day — this is the "tests" beat of the same story.
- Best windows: 21:00–23:00 or 08:00–09:00 Beijing time.
- The "14 tests, still green on wrong code" opener is the hook — keep it verbatim, it's the one people quote.
- r/java and r/ExperiencedDevs are good homes for this one if you cross-post.
