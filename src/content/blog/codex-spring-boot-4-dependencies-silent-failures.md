---
title: "Codex Added 12 Spring Boot 4 Dependencies. 5 Failed Silently (2026)"
description: "I asked Codex to add 12 dependencies to a Spring Boot 4.1.1 project. One was right. Five built green and wired nothing. Here is the test that tells them apart."
pubDate: 2026-09-18
category: "ai-tools"
tags: ["openai codex", "spring boot 4", "maven", "dependency management", "ai coding agents", "java testing", "java-ai-cluster"]
image: "/og-codex-spring-boot-4-deps.jpg"
imageAlt: "A table of twelve Spring Boot 4 dependencies added by an AI agent, with five rows marked green build but nothing wired and one marked correct"
keywords: ["spring boot 4 dependencies", "spring boot 4 starter renamed", "codex spring boot 4", "flyway core not running spring boot 4", "webclient builder bean not found spring boot 4", "spring boot 4 restclient builder", "spring boot 4 webmvctest package"]
faq:
  - question: "Why does adding flyway-core not run my migrations in Spring Boot 4?"
    answer: "Because flyway-core is the library, not the Spring Boot integration. Boot's Flyway auto-configuration now lives in its own module, spring-boot-flyway, which the starter spring-boot-starter-flyway brings in. With only flyway-core on the classpath, Maven resolves it happily — the Boot BOM still manages its version — the app starts, and zero migrations run. I confirmed this with two identical projects: the starter logged 'Successfully applied 1 migration', flyway-core alone left the table missing and threw Table \"ORDERS\" not found."
  - question: "Is spring-boot-starter-web still valid in Spring Boot 4?"
    answer: "It resolves and it works, but it is deprecated. The 4.1.1 POM's own description says 'deprecated in favor of spring-boot-starter-webmvc'. It is still in the dependency management BOM, so you get no warning at build time. It is the wrong answer for a subtler reason too: it does not give you a RestClient.Builder bean, because RestClient auto-configuration moved to spring-boot-starter-restclient. I measured RestClient.Builder beans at 1 with the right starter and 0 with spring-boot-starter-web."
  - question: "Why does @WebMvcTest fail to compile after upgrading to Spring Boot 4?"
    answer: "The annotation moved package. In Boot 3 it was org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest; in Boot 4.1.1 it is org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest, and it ships in a separate starter, spring-boot-starter-webmvc-test. If your agent added spring-boot-starter-web and stopped there, the annotation is not on the classpath at all, and the error you get is 'package org.springframework.boot.webmvc.test.autoconfigure does not exist' — which points at your import, not at your pom."
  - question: "How do I check whether a dependency Spring Boot 4 actually wired anything?"
    answer: "Run the build with the condition report on: mvn -B test -Ddebug=true. Boot prints every auto-configuration it evaluated. If you added Flyway and no FlywayAutoConfiguration line appears anywhere in that report, the Boot integration is not on the classpath and nothing will run. For HTTP clients I count beans instead: getBeanNamesForType(WebClient.Builder.class) returned 1 with spring-boot-starter-webclient and 0 with spring-boot-starter-webflux."
  - question: "Does an AGENTS.md file stop Codex from picking the wrong dependency?"
    answer: "In my run it fixed all five silent failures. I added fifteen lines containing three rules — do not reuse Boot 3 starter names, never add the third-party library on its own, and prove the feature is wired rather than trusting a green build — with no list of correct coordinates in it. The same model, on the same five prompts, went from flyway-core to spring-boot-starter-flyway, from spring-boot-starter-webflux to spring-boot-starter-webclient, and from jackson-databind to spring-boot-starter-jackson."
---

I gave Codex twelve small dependency tasks on a Spring Boot 4 project. It got one right.

That number is not the interesting part. The interesting part is what the other eleven did, because only two of them broke the build. Five produced a green build, a clean start-up, and nothing wired into the application context at all. If I had done what most of us do — run `mvn test`, see `BUILD SUCCESS`, move on — I would have shipped all five.

I have been writing about Spring Boot 4 for a while now, mostly about [what the migration actually breaks](/blog/spring-boot-4-migration-ai-agents/). This is the narrower version of that problem: not "can an agent migrate my app", but the much more common daily task of "add a dependency for me". It is the least glamorous thing you hand an agent, and on this framework it is one of the least reliable.

## The lab: twelve identical projects, one instruction each

Every row below comes from the same throwaway project, copied twelve times.

- Spring Boot 4.1.1 through the `spring-boot-dependencies` BOM, JDK 17 (Corretto), Maven 3.9.11
- Nothing in it but `spring-boot-starter`, `spring-boot-starter-test`, a `@SpringBootApplication` class, and one `@SpringBootTest`
- codex-cli 0.135.0, pinned to `-m gpt-5.5` for every run, because my configured default model is newer than this CLI can decode and the API rejects it

Each copy got one sentence. The instruction ended with the same constraint every time: edit `pom.xml` only, do not run Maven, do not touch any Java file. That constraint matters. I did not want the agent's second guess after watching a build fail — I wanted the coordinate it reaches for first, because that is what lands in your pom when you ask for something in a hurry.

Then I built each result myself and measured what the dependency actually did.

## All twelve answers

| # | I asked for | Codex added | Boot 4.1.1 wants | What happened |
|---|---|---|---|---|
| 1 | AOP | `spring-boot-starter-aop` | `spring-boot-starter-aspectj` | Maven refuses to read the POM |
| 2 | Flyway | `flyway-core` | `spring-boot-starter-flyway` | Green build, zero migrations ran |
| 3 | WebClient | `spring-boot-starter-webflux` | `spring-boot-starter-webclient` | Green build, 0 `WebClient.Builder` beans |
| 4 | RestClient | `spring-boot-starter-web` | `spring-boot-starter-restclient` | Green build, 0 `RestClient.Builder` beans |
| 5 | Undertow | `webmvc` + `tomcat` + `spring-boot-starter-undertow` | not possible | Maven refuses to read the POM |
| 6 | OAuth2 login | `spring-boot-starter-oauth2-client` | `spring-boot-starter-security-oauth2-client` | Works, old name still managed |
| 7 | Spring MVC | `spring-boot-starter-web` | `spring-boot-starter-webmvc` | Works, deprecated |
| 8 | Liquibase | `liquibase-core` | `spring-boot-starter-liquibase` | Green build, nothing wired |
| 9 | `@WebMvcTest` | `spring-boot-starter-web` | `spring-boot-starter-webmvc-test` | Compile error, annotation not on classpath |
| 10 | Security test | `spring-security-test` | `spring-boot-starter-security-test` | Resolves at 7.1.1, works |
| 11 | Jackson | `com.fasterxml.jackson.core:jackson-databind` | `spring-boot-starter-jackson` | Green build, 0 mapper beans |
| 12 | Validation | `spring-boot-starter-validation` | same | Correct |

One out of twelve. Three loud failures, five silent ones, three deprecated-but-working, one right.

## Failure mode one: the build dies before it compiles

Two runs never got as far as `javac`. Both failed the same way, and both failed on the same underlying fact — the 4.1.1 BOM simply does not manage these artifactIds any more, so a dependency with no explicit version cannot be read:

```text
[ERROR] 'dependencies.dependency.version' for
        org.springframework.boot:spring-boot-starter-aop:jar is missing.
```

`spring-boot-starter-aop` is `spring-boot-starter-aspectj` now. `spring-boot-starter-undertow` does not exist at any version — Boot 4 dropped Undertow because it does not implement Servlet 6.1, and the [migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) lists it among the removed features rather than the renamed ones.

This is the good failure. It is unmissable, and it names the exact coordinate that is wrong. The Undertow one is worth a closer look, though, because it shows something about how the agent reasons. It did not just add Undertow. It added `spring-boot-starter-webmvc`, `spring-boot-starter-tomcat`, *and* `spring-boot-starter-undertow` — it correctly worked out that swapping a servlet container means excluding one and adding another, and then reached for a name that stopped being published two major versions ago. The reasoning was right and the fact was stale. Those are different problems, and only one of them is fixable by giving the agent more context.

## Failure mode two: loud, but pointing at your code

The `@WebMvcTest` request is the one I would have hated to debug without knowing this already.

Codex added `spring-boot-starter-web`. Reasonable: in Boot 3 that is what you needed for a controller slice test. In Boot 4.1.1 two things changed at once. The annotation moved package —

```java
// Boot 3
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
// Boot 4.1.1
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
```

— and it now ships in its own starter, `spring-boot-starter-webmvc-test`. With only `spring-boot-starter-web` on the classpath, the annotation is not there at all, so the build fails with `package org.springframework.boot.webmvc.test.autoconfigure does not exist`.

That error is honest but it points at your import statement. The fix is in `pom.xml`. If you do not already know the annotation moved, you will spend a while looking in the wrong file, and an agent that only sees the compiler output will happily start rewriting your imports.

I ran the control: same project with `spring-boot-starter-webmvc` plus `spring-boot-starter-webmvc-test`, and the slice test starts and passes.

## Failure mode three: green build, nothing wired

These five are why I wrote this down.

**Flyway.** Codex added `org.flywaydb:flyway-core`. I built two versions of the same project — H2, `spring-boot-starter-jdbc`, one migration file creating a table, one test asserting the table exists. With `spring-boot-starter-flyway`:

```text
Migrating schema "PUBLIC" to version "1 - init"
Successfully applied 1 migration to schema "PUBLIC"
Tests run: 2, Failures: 0, Errors: 0
```

With `flyway-core` alone:

```text
Caused by: org.h2.jdbc.JdbcSQLSyntaxErrorException: Table "ORDERS" not found
Tests run: 2, Failures: 0, Errors: 1
```

Identical to a project with no Flyway dependency at all. The library is on the classpath, its version is managed by the Boot BOM so Maven raises nothing, the app starts, and the migration count is zero. I have hit silence like this before with [a Flyway checksum that never surfaced](/blog/flyway-checksum-mismatch-ai-agent/); the pattern is always the same, and it is always worse than a crash.

This is not an obscure corner case I had to go looking for. Flyway is the worked example in the Spring team's own announcement of this change: in Boot 3, Flyway was auto-configured whenever the jar was on the classpath; in Boot 4 you need the starter so that the `spring-boot-flyway` module comes with it ([Modularizing Spring Boot](https://spring.io/blog/2025/10/28/modularizing-spring-boot), October 2025). That also explains why the answer was wrong in one specific direction rather than randomly wrong. `flyway-core` was the correct coordinate for roughly a decade of Spring Boot releases. What the model has here is not invented knowledge — it is expired knowledge, which is a far harder thing for it to notice about itself.

Then the experiment handed me the inversion that convinced me. When I later ran the *correct* starter in this same minimal project, the build went red:

```text
Error creating bean with name 'dataSource': Failed to determine a suitable driver class
```

`spring-boot-starter-flyway` pulls in JDBC, JDBC auto-configuration switches on, and my toy project has no database driver — so the right answer fails and the wrong one passes. Read that again: the dependency that does its job breaks the build, and the dependency that does nothing leaves it green. In a real project with a configured datasource the correct starter is fine, so this is an artefact of the lab. But it measures something real — how little work `flyway-core` actually does.

**WebClient and RestClient.** These two are the cleanest measurements in the whole experiment, because I could count beans.

| Starter added | `WebClient.Builder` beans |
|---|---|
| `spring-boot-starter-webclient` | 1 |
| `spring-boot-starter-webflux` (Codex) | 0 |

| Starter added | `RestClient.Builder` beans |
|---|---|
| `spring-boot-starter-restclient` | 1 |
| `spring-boot-starter-web` (Codex) | 0 |

Boot 3 trained everyone — me included — to expect `spring-boot-starter-webflux` to bring WebClient along with it, and `spring-boot-starter-web` to bring RestClient. In 4.1.1 the client auto-configuration lives in its own module behind its own starter. Add the old starter and you get a green build, an application context that starts, and a `NoSuchBeanDefinitionException` the moment anything injects a builder — which is at least loud, but again points at your code.

**Jackson.** Codex added `com.fasterxml.jackson.core:jackson-databind`. Boot 4 moved to Jackson 3, where the group ID is `tools.jackson.core` and the mapper is `tools.jackson.databind.ObjectMapper`. I counted `ObjectMapper` beans the same way: 1 with `spring-boot-starter-jackson`, 0 with `jackson-databind`. You asked for JSON customisation, got a Jackson 2 library on the classpath that nothing in Boot is managing, and no signal that anything is off.

**Liquibase.** `liquibase-core`, same shape as Flyway. I checked it a different way, by looking at the condition report: with the correct starter, `LiquibaseAutoConfiguration` appears in Boot's auto-configuration report. With `liquibase-core`, there is no Liquibase line in the report at all. The Boot integration was never on the classpath.

## Why the silent ones are silent

I had a hypothesis going in, and the experiment killed it.

I assumed the trap was starter names versus bare module names — that adding `spring-boot-flyway` instead of `spring-boot-starter-flyway` would be the silent failure. It is not. I built that variant and it worked: `Successfully applied 1 migration`. The bare Boot module carries the auto-configuration with it.

The real dividing line is somewhere else entirely. Boot 4 [split its auto-configuration out of the monolithic jar](/blog/spring-boot-4-migration-ai-agents/) into per-technology modules, and the starter is now mostly an aggregator that pulls the module plus the library plus whatever else the feature needs. So:

- `spring-boot-starter-flyway` → Boot integration + Flyway. Works.
- `spring-boot-flyway` → Boot integration, no library. Works here, because Flyway was already reachable.
- `flyway-core` → library, no Boot integration. **Nothing happens.**

The agent picked the one option that has no Spring wiring in it at all. And it stayed quiet because the Boot BOM still manages the version of `flyway-core`, `liquibase-core` and `jackson-databind`. Maven has no complaint to raise. The version resolves. The build is green. The only thing missing is the feature.

This is the exact inverse of what makes a migration hard to review. A renamed starter name is a compiler-verifiable, mechanical change — the kind agents are genuinely good at. "The library is present but the framework never picked it up" is not visible anywhere in the build output. It is the same split I keep running into: mechanical renames that AI handles well, and silent behaviour changes that only a test catches.

## The three that worked anyway

Not every wrong answer is wrong in practice. `spring-boot-starter-web` still resolves and still gives you MVC — its own POM description says `deprecated in favor of spring-boot-starter-webmvc`, which is about as close to an official warning as you will get, and you would only see it if you opened the POM. The [official migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide#starters) collects these under "Deprecated Starters" — `web` → `webmvc`, `oauth2-client` → `security-oauth2-client`, `web-services` → `webservices` — which is how I confirmed the POM description was policy rather than a leftover string. `spring-boot-starter-oauth2-client` is still in the BOM and `OAuth2ClientAutoConfiguration` still fires. `spring-security-test` resolved at 7.1.1 and works.

I am not going to pretend these are urgent. But they are the reason "it built" is such a bad signal: the same green build covers a correct coordinate, a deprecated coordinate, and one that wired nothing.

## Run 2: fifteen lines, no cheat sheet

I wanted to know whether this is fixable without hand-feeding the answer, so I re-ran the five silent ones with an `AGENTS.md` in the project root. It contains three rules and no list of coordinates:

```markdown
## Dependencies (Spring Boot 4.x)

- Never reuse a Spring Boot 3 starter name. Many were renamed or split.
- Always add the Spring Boot starter for a technology, never the third-party
  library on its own. `flyway-core` and `liquibase-core` do not wire anything
  into the application context by themselves.
- After adding a dependency, prove the feature is actually wired in, not just
  that the build passes. A green build proves Maven resolved the coordinates.
  It does not prove Spring configured anything.
```

Same model, same prompts, same constraint. Five for five:

| Task | Without AGENTS.md | With AGENTS.md |
|---|---|---|
| Flyway | `flyway-core` | `spring-boot-starter-flyway` |
| WebClient | `spring-boot-starter-webflux` | `spring-boot-starter-webclient` |
| RestClient | `spring-boot-starter-web` | `spring-boot-starter-restclient` |
| Liquibase | `liquibase-core` | `spring-boot-starter-liquibase` |
| Jackson | `jackson-databind` | `spring-boot-starter-jackson` |

Every coordinate correct, and none of them copied from a list I gave it. The rules were general enough to generalise. That is the same mechanism I saw when [AGENTS.md redirected a security fix](/blog/codex-agents-md-spring-boot/) — the file does not add knowledge, it tells the model which knowledge to reach for.

One honest footnote: two of those five builds then failed, and they failed because the answer was right. Flyway and Liquibase starters bring JDBC with them, JDBC wants a datasource, and this lab project has no driver on the classpath. The three remaining builds passed. I am counting all five as fixes, because a dependency that demands a datasource is doing its job and one that never asks is not.

## The check I now run

For any dependency an agent adds to a Boot 4 project, one of these two takes under a minute:

```bash
mvn -B test -Ddebug=true
```

Boot prints the full condition-evaluation report. Grep it for the technology — `FlywayAutoConfiguration`, `LiquibaseAutoConfiguration`, `WebClientAutoConfiguration`. If the line is absent, the Boot integration is not on the classpath and the feature will not run, whatever the build says.

For anything that produces a bean, count the beans instead of trusting the report:

```java
@Autowired ApplicationContext ctx;

@Test
void probe() {
    System.out.println("WebClient.Builder = "
        + ctx.getBeanNamesForType(WebClient.Builder.class).length);
}
```

Zero means the dependency resolved and nothing was configured. Those are very different states and the build treats them identically.

## What I am taking from this

The uncomfortable part is not that Codex got eleven of twelve wrong. It is that the failure I would have noticed — the loud one — was the minority. Two of twelve stopped the build. Five of twelve told me everything was fine.

Boot 4 is a particularly bad framework to guess on, because the change that matters is invisible from the outside: auto-configuration moved into per-technology modules, the library coordinates did not change, and the BOM kept managing their versions. An agent reasoning from Boot 3 knowledge produces something plausible, resolvable, and inert.

Two things changed for me after running this. I no longer accept a dependency change on the strength of a green build — I check the condition report or count the bean. And my Spring Boot projects now carry those three rules in `AGENTS.md`, because fifteen lines of "do not add the library on its own" turned five silent failures into five correct answers.

If you want the full set of Boot 4 changes I have measured rather than read about, they are collected in [the Java + AI cluster overview](/blog/ai-for-java-developers/), alongside the [Codex sandbox work](/blog/codex-sandbox-maven-spring-boot/) that started this series.
