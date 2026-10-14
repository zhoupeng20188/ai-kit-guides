---
title: "Claude Code's Boot 4 Upgrade Silently Broke @PreAuthorize (2026)"
description: "I let Claude Code migrate method security to Boot 4. Build green, @PreAuthorize intact — until an admin endpoint returned 200 for a normal user."
pubDate: 2026-10-14
category: "ai-tools"
tags: ["spring boot 4", "claude code", "spring security 7", "preauthorize", "java ai tools", "java-ai-cluster"]
image: "/og-claude-code-spring-boot-4-preauthorize.jpg"
imageAlt: "A terminal showing Claude Code migrating a Spring Security 7 config next to a test where a normal user unexpectedly reaches an admin method that should throw AccessDeniedException"
keywords: ["spring boot 4 preauthorize", "claude code spring security 7", "@PreAuthorize not working", "spring security 7 method security silent", "ai agent broke security"]
faq:
  - question: "Why does @PreAuthorize do nothing after a Spring Boot 4 upgrade?"
    answer: "Spring Security 7 removes @EnableGlobalMethodSecurity. If your migration drops that old annotation and never adds @EnableMethodSecurity, the @PreAuthorize annotations are still on your methods but nothing processes them — every call is allowed. The build compiles, your tests pass, and an admin endpoint answers a normal user with 200. Method security is either on (via @EnableMethodSecurity) or off; there is no compile error for the off state. The [Spring Security method security reference](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html) documents exactly when method security is active."
  - question: "How do I catch a silently disabled @PreAuthorize in a test?"
    answer: "Write at least one 'wrong role' test that must throw AccessDeniedException. Load the real service bean with @SpringBootTest (not @WebMvcTest, which does not apply method-security AOP) and call the protected method as a user who lacks the role, then assert the exception is thrown. If method security is off, this test fails instead of passing — that failure is the signal. A test suite that only asserts happy-path 200s will stay green no matter what."
  - question: "Can Claude Code migrate Spring Security 7 safely?"
    answer: "It can do the loud parts — the Lambda DSL SecurityFilterChain, the requestMatchers, the Argon2 encoder — and the build goes green. What it misses is the quiet contract: that @EnableMethodSecurity must be present for @PreAuthorize to mean anything. Treat the agent's Boot 4 diff the way I treat every agent output: read the security config line by line, fire a real request as a low-privilege user, and keep one test that must deny. The full map of these agent-on-JVM failure modes lives in my AI for Java Developers guide."
---

## The endpoint that should have said no

I keep a small Spring Boot order service around for exactly this kind of experiment. It has an `OrderAdminService` with one method guarded by `@PreAuthorize("hasRole('ADMIN')")`:

```java
@PreAuthorize("hasRole('ADMIN')")
public void purgeOldOrders(int days) {
    // deletes everything older than `days`
}
```

On Boot 3.5 that method refused anyone without the `ADMIN` role. A normal `USER` calling it got `AccessDeniedException`. I wanted to move the service to Boot 4.1, so — against my own better judgement — I handed the upgrade to Claude Code and asked it to make the build green.

It did. The build was green. The `@PreAuthorize` annotation was still sitting on the method, untouched and innocent-looking. And when I later logged in as a plain `USER` and called `purgeOldOrders`, it ran. No exception. The endpoint that should have said no said yes.

That is the whole article. Not a crash, not a compile error, not even a warning. Just a security control that stopped being a security control while every dashboard in the building reported success.

## What Spring Boot 4 actually changed about method security

Before the agent touched anything, I want to be precise about the moving parts, because the trap lives in the gap between a rename and a behaviour.

Spring Security 7 — the version Boot 4.1 ships — removes `@EnableGlobalMethodSecurity` (the [Spring Boot 4.0 release notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes) list it among the Security 7 breaking changes, and the [official method security reference](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html) explains why `@EnableMethodSecurity` is now what makes `@PreAuthorize` real). That annotation was already the legacy switch; the modern one is `@EnableMethodSecurity`, available since Security 6 and the default-capable replacement. For a practitioner walkthrough of how method security actually behaves once enabled — and how easy it is to leave it off — [Baeldung's introduction to Spring Method Security](https://www.baeldung.com/spring-security-method-security) is the reference I keep bookmarked. When `@EnableMethodSecurity` is present, the `@PreAuthorize`, `@PostAuthorize`, and `@Secured` annotations on your beans are turned into AOP advice that actually enforces them. When it is absent, those annotations are decoration. The method runs for whoever calls it.

The loud part of the migration is the `SecurityFilterChain`. Boot 4 / Security 7 makes the Lambda DSL mandatory: `authorizeHttpRequests` with `requestMatchers`, no `.and()` chaining, no `WebSecurityConfigurerAdapter`. That part fails loudly if you get it wrong — the compiler or the context startup tells you. The method-security switch fails silently. There is no exception for "you forgot to enable the thing that makes your annotations real."

This is the same split I keep landing on in my [Spring Boot 4 migration write-up](/blog/spring-boot-4-migration-ai-agents/) — the compiler can see the mechanical rename, and it is blind to the behavioural contract. Method security is the purest version of that split I have found, because the contract is a single missing annotation and the failure is a security hole.

## Run 1: Claude Code migrates, the build goes green

I gave Claude Code the upgraded project — Boot 4.1 parent, Security 7 on the classpath — and a minimal prompt: get it building and keep the security behaviour the same. It did what agents do well. It rewrote the `SecurityFilterChain` into Lambda DSL, swapped `antMatchers` for `requestMatchers`, and handled the config without drama. The build passed. The `@PreAuthorize` line was still on `purgeOldOrders`.

Here is the subtle part. The old config had carried `@EnableGlobalMethodSecurity(prePostEnabled = true)` on the configuration class. That annotation no longer exists in Security 7. Claude Code removed it — correctly, from a "this won't compile" point of view — and did not add `@EnableMethodSecurity` in its place. The diff was clean, the build was green, and method security was now off for the entire application.

## The two-line diff that hid the hole

Here is the entire change that disabled my security, and why a reviewer — human or AI — would skim past it:

```java
// Before (Boot 3.5)
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class MethodSecurityConfig { ... }

// After Claude Code's migration (Boot 4.1)
@Configuration
public class MethodSecurityConfig { ... }
```

The old annotation does not exist in Security 7, so removing it is the correct, compile-clean move. The missing line is the problem: `@EnableMethodSecurity`. Without it, `@PreAuthorize` is still valid Java — the import resolves, the annotation compiles, the method runs — but no advice is ever woven around the call. The compiler is happy, the test that only checks the happy path is happy, and the one annotation that made the other annotations real is simply gone. Nothing in the diff screams "security disabled" because, to the toolchain, nothing broke.

I did not notice for a while, because nothing told me to. The annotation was gone from the file, not from my memory of the file. The `@PreAuthorize` was still there, looking load-bearing. My existing test asserted that an `ADMIN` user could purge orders and got 200. That test still passed — of course it did, an admin can do the thing, and so could everyone else, but the test never checked the negative case.

## The trap is a green test with zero coverage

This is the part I want you to internalise, because it is the same shape as the [AI-generated JUnit tests that never execute](/blog/ai-junit-tests-not-running-spring-boot-4/) on Boot 4: a passing summary line that proves nothing.

A test that only ever asserts the happy path — "admin calls purge, expects 200" — stays green whether method security is on or off. The dangerous test is the one that should fail. If you write "user calls purge, expects AccessDeniedException" and method security is off, that test fails. That failure is the only honest signal you get. My suite had no such test, so it reported success while protecting nothing.

The second trap is the slice. If you verify authorization with `@WebMvcTest`, you are loading a mock of the service, not the real bean, and method-security AOP does not apply to a Mockito mock. The test passes, the security is unverified, and you have measured the wrong thing. The verification has to go through the real service bean — `@SpringBootTest` with the actual `OrderAdminService` wired in — or it is theatre.

I covered the URL-layer version of this same mistake in my [Claude Code Boot 4 403 piece](/blog/claude-code-spring-boot-4-403/): there, the agent disabled CSRF to make a test green; here, it dropped the annotation that makes `@PreAuthorize` real. Different line, identical failure mode — the agent optimises for the build being green, and a security control is not part of "the build being green."

## How I finally caught it

I caught it the way you should: I stopped reading the build output and fired a real request. As a `USER` (no admin role), I called the purge endpoint over HTTP. It returned 200. On Boot 3.5 the same call returned 403. Nothing in the agent's summary, the test report, or the startup logs had mentioned that this was now open.

Then I wrote the test that should have been there all along:

```java
@SpringBootTest(classes = {OrderAdminService.class, MethodSecurityConfig.class})
class OrderAdminServiceSecurityTest {

    @Autowired OrderAdminService service;

    @Test
    @WithMockUser(roles = "USER")
    void userCannotPurgeOrders() {
        assertThatExceptionOfType(AccessDeniedException.class)
            .isThrownBy(() -> service.purgeOldOrders(30));
    }
}
```

On the agent's diff this test failed — `purgeOldOrders` ran to completion instead of throwing. That red line is worth more than a page of green. It is the exact moment the silent failure becomes visible. The fix was one annotation: `@EnableMethodSecurity` on the config class. After that, the `USER` test passed (the exception was thrown) and the `ADMIN` test still passed. Both directions now mean something.

## Why the agent missed it, and what I changed

Claude Code is not stupid about security. It produced a correct Lambda DSL config and a green build. What it cannot do is treat "a security control is now inactive" as a failure, because nothing in the toolchain flags it. The old annotation was removed because it does not compile; the new one is optional from the compiler's perspective; the behavioural consequence lives three layers away from the line that changed. That is precisely the [kind of work where I lean on Claude Code for the mechanics and keep the verification for myself](/blog/claude-code-spring-boot/).

The change I made to my own workflow afterward was small and permanent. First, a "wrong role" test in every service that has a `@PreAuthorize` — if it does not throw, the build is lying. Second, I added one line to the `AGENTS.md` I keep in Java repos:

```
Method security must stay enabled after any Security 7 migration.
If you remove @EnableGlobalMethodSecurity, add @EnableMethodSecurity.
Never verify authorization with @WebMvcTest on the service bean.
Keep a test where a non-admin user MUST get AccessDeniedException.
```

The rule did not make the model smarter. It gave it a second feedback loop that encodes my judgement instead of the compiler's, which is the entire point of an `AGENTS.md`.

## The one habit that would have caught this immediately

If you take nothing else: assert the denial, not just the grant. Every secured method in your codebase deserves one test that proves the wrong person is rejected. That single habit would have turned this silent hole into a red build on the agent's first pass, instead of something I found by hand two days later while writing about it.

The broader pattern — agents are excellent at the half of a Boot 4 migration the compiler can see, and structurally blind to the half it cannot — is the reason I write these labs at all. The [AI for Java Developers guide](/blog/ai-for-java-developers/) collects every one of them in one place, including the ones where the build goes green and the behaviour quietly breaks.
