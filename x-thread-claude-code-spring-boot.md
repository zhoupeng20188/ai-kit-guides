# X Thread — Claude Code with Spring Boot (from `claude-code-spring-boot`)

6 posts, English, each ≤280 chars. Based on the article published 2026-07-31.

---

**Post 1** (~232 chars)

I'm a Java backend dev. First week with Claude Code on Spring Boot, it "refactored" a service and silently broke a validation path I missed until next morning's build went red.

The tool is good. The discipline is the job. 🧵

---

**Post 2** (~252 chars)

The one line in CLAUDE.md that saved me more than anything:

"After any change, run ./mvnw -q test and only tell me you're done if it passes."

On its own Claude Code hands you a diff it never compiled. That sentence forces it to find its own errors first.

---

**Post 3** (~244 chars)

Setup is boring (good): cd into the project, run /init, keep half of what it drafts for CLAUDE.md.

As of late July 2026 the default model is Sonnet 5 (1M context). I switch to Opus 5 with /model for gnarly refactors. The 1M window is the part I underrated.

---

**Post 4** (~250 chars)

Real win: I asked for GET /api/orders?page=&size= with a total count. 6 min later it returned controller + service + repo query + DTO map + a test, all passing.

What it got wrong: named the DTO OrderPageResponse when my rule says PagedOrderResponse. Small, caught in diff.

---

**Post 5** (~234 chars)

Where it still trips:
→ N+1 queries it can't see (tests never catch them)
→ "modernizes" your code to its own dialect
→ edits application.yml and breaks a profile you forgot

Green build ≠ correct. I treat its "done" as "compiles, worth reading."

---

**Post 6** (~150 chars)

Full workflow + the exact CLAUDE.md I run on Spring Boot 3.4 / Java 21:

👉 https://aikitguides.com/blog/claude-code-spring-boot

What's your worst Claude Code-on-Java surprise? 👇

---

## Posting notes
- Post standalone, not back-to-back with another thread.
- Best windows: 21:00–23:00 or 08:00–09:00 Beijing time (US East Coast commute + European morning overlap).
- After posting, reply to your own thread with the link again — it lifts impressions.
- Hook targets the exact gap GSC/Bing proved converts: "Claude Code" + "Spring Boot" (real codebase, not a fresh tutorial project).
