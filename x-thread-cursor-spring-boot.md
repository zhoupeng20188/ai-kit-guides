# X Thread — Cursor + Spring Boot (from `cursor-spring-boot`)

6 posts, English, each ≤280 chars. Based on the article published 2026-08-03.

---

**Post 1** (~234 chars)

I read 10 "Cursor + Spring Boot" tutorials. Every one started: install the Java pack, open Spring Initializr, generate a fresh project.

None covered pointing Cursor at a codebase that's grown for 5 years. That's the part that breaks. 🧵

---

**Post 2** (~258 chars)

Trap 1: bean wiring looks fine, breaks at startup.

Cursor edited a @Service and used a helper bean that was @ConditionalOnProperty-guarded and off in my profile. Compiled clean. Failed at startup.

Fix: list every caller before editing shared logic, then run the app.

---

**Post 3** (~240 chars)

Trap 2: it adds dependencies "just to be safe."

I asked for a webhook-retry endpoint. Cursor returned the controller, the test, AND a new spring-boot-starter-validation in build.gradle — even though validation was already on the classpath.

Always diff the build file.

---

**Post 4** (~150 chars)

Trap 3: green tests that prove nothing.

Cursor's @SpringBootTest asserted assertNotNull(response) and called it a day. Build green. Behavior unverified.

Every AI-written test is a draft I read, not a result I trust.

---

**Post 5** (~190 chars)

My .cursor/rules/spring-boot.mdc has two lines that saved me more than everything else:

→ Do NOT add new Gradle dependencies without asking
→ List every caller before editing shared logic

That second one is the difference between a clean diff and a 2am incident.

---

**Post 6** (~150 chars)

Full writeup + the exact .cursor/rules file I use on real Spring Boot code:

👉 https://aikitguides.com/blog/cursor-spring-boot

What's your worst Cursor-on-Spring-Boot surprise? 👇

---

## Posting notes
- Post standalone, not back-to-back with another thread.
- Best windows for this audience: 21:00–23:00 or 08:00–09:00 Beijing time (US East Coast commute + European morning overlap).
- After posting, reply to your own thread with a comment that includes the link — it lifts impressions.
- Hook targets the exact gap GSC/Bing proved converts: "real Spring Boot codebase" + "Cursor" (rank 2.36 on Bing, 16.4 on Google).
