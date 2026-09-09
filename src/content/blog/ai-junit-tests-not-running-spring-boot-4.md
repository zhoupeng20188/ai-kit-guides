---
title: "AI Wrote 18 Tests. Only 14 Ran: Spring Boot 4 + JUnit 6 (2026)"
description: "Claude Code added tests to my Spring Boot 4 app and reported 14 passing. Three more never ran. Here is how Surefire hides them, and the AGENTS.md fix."
pubDate: 2026-09-09
category: "ai-tools"
tags: ["junit 6", "spring boot 4", "surefire", "ai generated tests", "claude code", "java testing", "java-ai-cluster"]
image: "/og-ai-junit-tests-not-running-spring-boot-4.jpg"
imageAlt: "A Maven build log showing BUILD SUCCESS next to a list of test files, three of which are greyed out and never executed"
keywords: ["junit 6 tests not running", "spring boot 4 surefire no tests", "ai generated tests silently skipped", "maven surefire test not executed", "spring boot 4 mockbean removed"]
faq:
  - question: "Why does Maven report Tests run: 0 when my test file exists?"
    answer: "Because Surefire only picks up classes whose names match its default include patterns: Test*, *Test, *Tests, and *TestCase. A file named OrderServiceShould.java or OrderArchSpec.java compiles, sits in src/test/java, and is never executed, with no warning at all. I hit exactly this in a Spring Boot 4.1.1 project: two files holding three tests produced zero executed tests and the build still said BUILD SUCCESS. Rename the class or add an <includes> block to your Surefire configuration."
  - question: "Do integration tests named *IT run in Spring Boot 4?"
    answer: "Not by default. Surefire does not match *IT, and Maven Failsafe is not configured for you by the Spring Boot parent. I confirmed that a class named CancelOrderIT.java ran zero tests under mvn test and still ran zero under mvn verify. Either name it *Test, or add maven-failsafe-plugin with its integration-test and verify goals and run mvn verify."
  - question: "Is @MockBean still available in Spring Boot 4?"
    answer: "No, not in 4.1.1. I checked the jars directly: org/springframework/boot/test/mock/mockito/MockBean.class exists in spring-boot-test 3.5.16 and is gone from spring-boot-test 4.1.1. Importing it is a compile error, not a deprecation warning. Use @MockitoBean from org.springframework.test.context.bean.override.mockito instead, which now comes from Spring Framework 7 rather than Spring Boot."
  - question: "How do I check whether every test file on my project actually ran?"
    answer: "Compare two numbers. Count the test sources with find src/test/java -name '*.java' | wc -l, then run mvn -B test and count the distinct classes in the Tests run: ... -- in <class> lines. If the second number is lower, you have test files that never executed. I put this comparison into AGENTS.md as a definition-of-done rule and the agent found and fixed every skipped file on its own."
  - question: "Does JUnit 6 warn when a test method is private?"
    answer: "Yes. JUnit 6.0.3 prints a WARNING saying the method must not be private and will not be executed, but the build still finishes green. So it is not fully silent, but the signal is one line buried in the build output rather than a failure. A private test method whose assertions would fail produces no failure, which is the dangerous part."
---

## The number that did not add up

Claude Code finished a feature on my Spring Boot service and told me fourteen tests were passing. The build was green. The report looked clean.

There were eighteen `@Test` methods on disk.

Four of them had not run. Three of those produced no warning, no error, and nothing in the build output that a human or an agent would notice. They just were not there.

I have spent the last few weeks writing about what agents get wrong in Java projects, mostly around [CI gates and architecture rules](/blog/ai-code-ci-gates-archunit-spotless/). This is the same problem one layer earlier. Before a gate can fail, the test has to actually execute. On Spring Boot 4 with JUnit 6, a surprising amount of agent-written test code never gets that far, and the build says nothing about it.

This is a lab project and I am going to give you the exact versions, because every number below depends on them.

| Piece | Version |
|---|---|
| Java | 17.0.19 (Amazon Corretto) |
| Spring Boot | 4.1.1 |
| JUnit Jupiter | 6.0.3 (managed by the Boot BOM) |
| Maven Surefire | 3.5.6 (managed by the Boot parent) |
| Maven | 3.9.11 |

I verified the JUnit version at runtime rather than trusting the BOM, by printing `Test.class.getPackage().getImplementationVersion()` from a test. It returned 6.0.3. That detail matters later.

## The baseline was already lying to me

The starting project is a four-layer order service: `web` -> `service` -> `repository` -> `domain`. Seven test files, all in `src/test/java`, all compiling.

```text
[INFO] Tests run: 2 ... -- in com.example.orders.OrderServiceTest
[INFO] Tests run: 1 ... -- in com.example.orders.OrderControllerTest
[INFO] Tests run: 1 ... -- in com.example.orders.OrdersApplicationTest
[INFO] Tests run: 1 ... -- in com.example.orders.OrderReportTest
[INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

Seven files. Four of them appear in the output. Three do not, and nothing says so.

That is the whole problem in one screen. `BUILD SUCCESS` with five tests means "the five tests I ran passed". It does not mean "your suite ran". Maven has no opinion about the files it ignored.

## Silent failure 1: a class name Surefire does not match

Surefire's default include patterns are `**/Test*.java`, `**/*Test.java`, `**/*Tests.java`, and `**/*TestCase.java`. Anything else is not a test as far as Maven is concerned.

Two files in the baseline were named `OrderServiceShould.java` and `OrderArchSpec.java`. Both contained valid JUnit 6 tests with correct imports. Both contributed zero executed tests. No warning.

This matters more now than it did two years ago, because BDD-style naming is exactly what coding agents reach for. Ask an agent to write tests for a service and you will regularly get `OrderServiceShould`, `PaymentSpec`, `UserBehaviour`. Every one of those is invisible to Maven. The agent is not wrong about JUnit; it is wrong about one build plugin's defaults, and nothing in the loop tells it so.

There is a second-order effect here that I did not expect. In an earlier experiment I wrote a throwaway file called `JunitVersionProbe.java` to print the JUnit version. It did not run, for exactly this reason. I only noticed because I knew to look for it, and it took a rename to `JunitVersionProbeTest` before the probe produced output. I nearly recorded "no version printed" as a JUnit quirk instead of my own naming mistake.

## Silent failure 2: `*IT` does not run under `mvn test` either

Everyone knows `*IT` belongs to Failsafe, not Surefire. What caught me is what happens next.

I put a `CancelOrderIT.java` in the project and ran `mvn test`. Zero tests from it, as expected. Then I ran `mvn verify`, on the theory that at least the full lifecycle would pick it up.

Also zero. Failsafe is not configured by the Spring Boot parent, so there is no plugin bound to the `integration-test` phase and the file simply never runs at any phase. If your CI job says `mvn verify`, an agent-written `*IT` file is still dead code.

You need an explicit plugin binding for `*IT` to mean anything:

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-failsafe-plugin</artifactId>
  <executions>
    <execution>
      <goals>
        <goal>integration-test</goal>
        <goal>verify</goal>
      </goals>
    </execution>
  </executions>
</plugin>
```

Without that, the only fix is the name. And renaming is usually the better answer anyway, because a name that Maven silently ignores is a landmine for the next person regardless of which plugin eventually picks it up.

## Silent failure 3: private test methods, which are only half silent

JUnit 6 refuses to execute `private` test methods. I expected total silence and got something slightly better.

```text
[WARNING] @Test method 'private void com.example.orders.OrderReportTest
  .privateTestMethodIsNeverDiscovered()' must not be private. It will not be executed.
```

So there is a signal. But it is a `WARNING`, buried in a few hundred lines of Spring startup logging, and the build still reports `BUILD SUCCESS`. The test in my baseline contained `assertTrue(false)`. Under any normal reading, that is a failing test. In practice it produced a warning nobody reads and a green build everyone trusts.

Half silent is the worst category. It is loud enough that you can tell yourself you would have caught it, and quiet enough that nobody does.

## Two things I assumed were silent that are not

This is where I was wrong, and the two corrections are more useful than the three failures above.

**JUnit 4 imports are a compile error, not a silent skip.** The standard migration horror story is that tests using `org.junit.Test` quietly stop running when the Vintage engine is gone. I wrote a file with the JUnit 4 import and expected zero executed tests. The build failed at `testCompile`: `package org.junit does not exist`. JUnit 4 is not on the Spring Boot 4 test classpath at all, so the wrong import cannot even compile. One of the most repeated Boot 4 testing warnings turns out to be self-solving.

**`@MockBean` is not deprecated but working. It is gone.** I have seen this described as a deprecation you can live with for a release or two. I checked the jars instead of the docs:

```text
spring-boot-test-3.5.16.jar  ->  org/springframework/boot/test/mock/mockito/MockBean.class   present
spring-boot-test-4.1.1.jar   ->  org/springframework/boot/test/mock/mockito/MockBean.class   absent
```

Importing it in 4.1.1 is a hard compile error: `package org.springframework.boot.test.mock.mockito does not exist`. Use `@MockitoBean` from `org.springframework.test.context.bean.override.mockito`, which now ships in Spring Framework 7 rather than Spring Boot.

There is a related migration trap that bit the agent in my second run. It wrote `org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc`, the Boot 3 package, and the build failed. In Boot 4 the class lives in the new webmvc test module at `org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc`. That one is genuinely easy to get wrong, because the annotation name is unchanged and only the package moved.

If you are working through the wider upgrade, I wrote up the [mechanical-versus-silent split across the whole Boot 4 migration](/blog/spring-boot-4-migration-ai-agents/) separately, and the pattern there is the same one here: renames are loud and easy, behaviour changes are quiet and expensive.

## Why `Tests run: 0` does not always mean something is broken

Before you go auditing, one honest complication. A test class that contains only `@Nested` classes reports this:

```text
[INFO] Tests run: 1 ... -- in com.example.orders.NestedInjectionTest$WhenCreatingAnOrder
[INFO] Tests run: 0 ... -- in com.example.orders.NestedInjectionTest
```

The outer class shows zero because the nested class ran the tests. That is normal and correct. So `Tests run: 0` is an ambiguous signal: sometimes it means "your file was ignored", sometimes it means "your tests live one level down".

This ambiguity is precisely why the failure mode survives. Nothing in the output distinguishes the two cases, so the only reliable check is a count of distinct classes that appear in the output versus the number of test files on disk.

I also want to correct something I expected to reproduce and could not. Several migration writeups warn that Spring Framework 7 changes `SpringExtension`'s context scope and breaks dependency injection inside `@Nested` classes. On 4.1.1, field injection into a `@Nested` class worked fine. The documented risk is real but narrower than those summaries suggest: it affects custom `TestExecutionListener` implementations calling `testContext.getTestClass()`, not ordinary `@Autowired` fields.

## Run 1: no AGENTS.md, three tests lost

I gave Claude Code a feature to build and told it to include an integration test that boots the whole application, then run `mvn -B test` until green.

It did well in most respects. It implemented the cancel endpoint with 404 and 409 handling, added unit tests and a slice test, and reported fourteen passing tests, which was an accurate reading of the Surefire output.

Two things are worth pulling out.

It renamed the existing `CancelOrderIT.java` to `CancelOrderIntegrationTest.java` and filled it in. Three tests that had never run before started running. I did not ask it to do that and it did not mention doing it. I suspect it simply wanted a file that matched the codebase's conventions, which is the same instinct I described in [an earlier experiment](/blog/claude-code-remember-spring-boot/): the codebase is the prompt.

But it left `OrderServiceShould` and `OrderArchSpec` completely alone. Three tests, zero executions, not a word in the report. The agent had no reason to go looking, because from inside its loop the build was green and the number it reported was the number Maven gave it. Asking an agent to make the build green cannot catch a test the build never ran.

It did spot the `private` test method, because JUnit 6 warned about it and the warning was in the output it read. That is the difference between the two categories: the one with a signal got caught, the two without a signal did not.

## Run 2: one rule in AGENTS.md, all three found

I reset the repo and added this to `AGENTS.md`, then gave it the identical task.

```markdown
## Testing rules
- Test classes must be named *Test, *Tests, Test*, or *TestCase.
  Never Should, Spec, IT, Probe, or Integration on its own. Maven Surefire will
  silently skip any other name and the build still reports BUILD SUCCESS.
- Test methods must not be private.
- Use @MockitoBean from org.springframework.test.context.bean.override.mockito.
  @MockBean does not exist in Spring Boot 4.1.
- Never import org.junit.Test. JUnit 4 is not on the test classpath in Spring Boot 4.

## Definition of done
Before you report, cross-check the suite:
1. List every file under src/test/java.
2. Run mvn -B test and read the "Tests run: ... -- in <class>" lines.
3. Every test file on disk must appear in that list. Any file that does not
   appear executed zero tests.
Report the number of tests actually executed, and name any file that contributed zero.
```

Seventeen tests executed, up from fourteen. It renamed `OrderServiceShould` to `OrderServiceBehaviorTest`, renamed `OrderArchSpec` to `OrderArchTest`, folded the `*IT` file into a properly named integration test, and then produced a table mapping every test file to its executed count.

The naming rules on their own would probably have been enough for code it wrote itself. The part that did the real work was the third step in the definition of done. Telling the agent what "done" means is not the same as telling it to verify that every file it can see actually did something. The first is a style guide. The second is a check, and checks are what catch silence.

## The audit command, if you want to check right now

Two numbers. That is the whole thing.

```bash
echo "files: $(find src/test/java -name '*.java' | wc -l)"
mvn -B test | grep -oE -- "-- in [a-zA-Z0-9._$]+" | sed 's/-- in //' \
  | sed 's/\$.*//' | sort -u | wc -l
```

If the second number is lower than the first, you have test files that never executed. On my Run 1 state the two numbers were 7 and 5. After the AGENTS.md run they were 7 and 7.

There are cleaner ways to do this in a real pipeline. Surefire can be configured with `failIfNoSpecifiedTests`, and JaCoCo or a coverage floor will catch whole files that never contribute. Both are better than a shell one-liner for a team. I like the one-liner anyway, because it fits in a prompt, and you can hand it to an agent before it writes a single test.

## What I am taking from this

Compilers catch renames; they do not catch absence. Every failure in this experiment shared one property: nothing was wrong, so nothing was reported. The code compiled, the build succeeded, and the only evidence of a problem was a number nobody was comparing to anything.

That is the shape of the problem with agent-written tests generally. An agent optimises for the signal it can see, and Maven gives it a green build. If you want it to notice silence, you have to name the silence in the instructions: not "write good tests", but "count the test files, count the classes that ran, and tell me if they differ".

Absence is one half of the problem. The other half is tests that do run and still prove nothing: assertions that pass trivially, collaborators mocked so hard the test only proves the mock works, edge cases nobody asked for. I wrote up [the five traps I check before trusting an AI-written test](/blog/ai-junit-tests/) separately. You need both questions, and this one comes first: did it run, and then, did it mean anything.

Four tests did not run in my project and I only found them because I went looking. The fix took one paragraph in a markdown file.
