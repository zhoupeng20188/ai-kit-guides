---
title: "Claude Code on Gradle: BUILD SUCCESSFUL With Zero Tests (2026)"
description: "Gradle printed BUILD SUCCESSFUL in 401ms and ran zero tests. On Spring Boot 4.1.1, I pointed Claude Code at it five times. It caught it all five."
pubDate: 2026-09-23
category: "ai-tools"
tags: ["gradle", "spring boot 4", "claude code", "java testing", "ci cd", "build cache", "ai coding agents", "java-ai-cluster"]
image: "/og-gradle-zero-tests.jpg"
imageAlt: "A Gradle console showing BUILD SUCCESSFUL next to a test task marked UP-TO-DATE with no tests executed"
keywords: ["gradle build successful zero tests", "gradle test up to date", "gradle test from cache", "gradle build cache stale results", "spring boot 4 gradle", "gradle rerun tests", "gradle test not running", "ai agent gradle false green", "claude code gradle", "claude code tests not running"]
faq:
  - question: "Why does ./gradlew test report BUILD SUCCESSFUL when no tests ran?"
    answer: "Because Gradle's default is to skip work whose declared inputs have not changed, and to reuse stored outputs when they have. When the test task is skipped that way it prints an outcome label instead of a test summary, and the build still exits 0. Nothing in BUILD SUCCESSFUL means 'tests executed'. It means no task that ran failed. In my lab the same repository produced BUILD SUCCESSFUL in 401ms with zero tests executed, and BUILD FAILED with one failure, ten seconds apart, with no file changing in between."
  - question: "How can I tell whether my Gradle tests actually executed?"
    answer: "Two places. The outcome label, printed as '> Task :test UP-TO-DATE' or '> Task :test FROM-CACHE', which you only see with --console=plain or --console=verbose, not in the default terminal progress display. And the summary line at the end, 'N actionable tasks: N up-to-date', which is printed in every mode. For an independent check, read the timestamp attribute inside build/test-results/test/*.xml — a restored result keeps the timestamp of the run that produced it, so the file's modification time is new while the timestamp inside is old."
  - question: "Does the build cache make this worse on CI?"
    answer: "Yes, and in the specific way CI is set up. A CI runner usually starts from a fresh checkout, so the build directory is empty, while the Gradle cache in the user home survives between jobs. With org.gradle.caching=true, an empty build directory is exactly the condition for a cache hit: my run restored a green result in 493ms on a repository where the tests would have failed. The runner never executed anything and the job went green. This is the case where reading the outcome label matters most, because nobody watches a CI log line by line."
  - question: "Should I turn off caching for the test task?"
    answer: "Not globally. Caching is why your second build takes 500ms instead of 30s. The narrower fix is to declare anything outside the compiled classes that your tests read as an input, so the cache key actually covers it: inputs.file('flags/discount-enabled.txt').withPathSensitivity(PathSensitivity.NONE) makes the file's content part of the key without making its absolute path part of it, so the cache still works across machines. If a test depends on something you cannot model, use --rerun for that task or outputs.upToDateWhen { false }. Gradle's own issue tracker has an open request since 2019 to make test caching opt-in rather than default."
  - question: "Is this the same problem as Maven Surefire silently skipping AI-written tests?"
    answer: "No, and the difference matters for how you look for it. With Maven Surefire the test file is never discovered, because the class name does not match the default include patterns, so nothing runs and nothing is cached. With Gradle the task is discovered and would run; what gets reused is a previous result. Maven hides files, Gradle replays outcomes. Gradle is also louder in one place Maven is silent: a --tests filter that matches nothing fails the build in Gradle, where Surefire quietly reports zero tests."
---

## Two commands, one repository, ten seconds apart

I flipped a single character in a config file and ran the suite.

```
$ ./gradlew test
> Task :test UP-TO-DATE
BUILD SUCCESSFUL in 401ms
```

Then I ran it again with one flag added.

```
$ ./gradlew test --rerun
> Task :test FAILED
FeatureFlagTest > discountFlagIsEnabledInDeployedConfig() FAILED
7 tests completed, 1 failed
BUILD FAILED in 1s
```

No source file changed between those two commands. Same repository, same commit, same JVM. One says the build is successful and names no tests. The other fails a test that the first one claims to have covered.

The second one is the truth. The first one is what you get by default, and it is what your CI job gets by default too.

I have spent the last few weeks writing about what coding agents get wrong in Spring Boot projects, mostly on the Maven side. This started as another entry in that series: put Claude Code in front of a Gradle build that lies, and record what it reports. It went somewhere else, and I want to show you both the mechanism and the part where my prediction was wrong.

## The lab

Everything below was run on one machine, and every number depends on these versions.

| Piece | Version |
|---|---|
| Java | 17.0.19 (Amazon Corretto) |
| Spring Boot | 4.1.1 |
| Spring Framework | 7.0.9 |
| Gradle | 8.14 (wrapper) |
| JUnit Jupiter | 6.0.3 (JUnit Platform 6.0.x) |
| Build cache | enabled, `org.gradle.caching=true` |

The project is a small order service: `PricingService` applies a 10% discount at 100.00, four test classes, seven test methods. Two of them are there on purpose:

- `PricingServiceShould` — BDD-style naming, to see whether Gradle's discovery behaves like Maven's.
- `FeatureFlagTest` — reads `flags/discount-enabled.txt` from the project root and asserts it says `true`. This is the one that carries the experiment, because that file is not a compiled class, not a resource, and not a declared input of anything.

## Four ways Gradle goes green without running a test

I ran the suite repeatedly under different conditions and recorded three things each time: the outcome label Gradle prints, the wall time, and the number of tests that actually executed, taken from the JUnit XML rather than from the console.

| Command | Label on `:test` | Time | Tests executed |
|---|---|---|---|
| `./gradlew test`, first run | `> Task :test` | 29s | 7 |
| `./gradlew test`, nothing changed | `> Task :test UP-TO-DATE` | 612ms | 0 |
| `./gradlew cleanTest test`, cache warm | `> Task :test FROM-CACHE` | 493ms | 0 |
| `./gradlew build -x test` | task never appears | 719ms | 0 |
| `./gradlew test -q` | nothing printed at all | — | 0 |

`UP-TO-DATE` means the inputs and outputs are unchanged since the last run, so Gradle declines to do the work. `FROM-CACHE` means the outputs were not in the build directory but were found in the cache, so Gradle copies them back instead of producing them. Neither one runs a test. Both exit 0.

The 29s on the first row is mostly dependency resolution on a cold cache. A normal re-run that actually executes is about one second. That is the number to compare against the 400–600ms of the skipped runs: a green build that finishes in half a second did not run your suite, and the speed is the tell.

## The one line that tells the truth, and the one that lies

There are two places where Gradle admits what happened, and they behave differently depending on how you invoked it.

The outcome label is the clear one — `> Task :test UP-TO-DATE` — but it is only printed in plain or verbose console mode. In a terminal, Gradle uses the rich console, which replaces those lines with a progress bar. Here is the same skipped run, once as an agent sees it through a non-interactive shell and once as you see it in your terminal:

```
$ ./gradlew test --console=plain          # non-TTY, what an agent sees
> Task :test UP-TO-DATE
BUILD SUCCESSFUL in 370ms
3 actionable tasks: 3 up-to-date

$ ./gradlew test --console=rich           # your terminal
BUILD SUCCESSFUL in 339ms
3 actionable tasks: 3 up-to-date
```

The label is gone in the second one. What survives in every mode is the last line: `3 actionable tasks: 3 up-to-date`. That line is the cheapest check you have, and almost nobody reads it.

The second place is the result files, and here is where it gets interesting. After a `FROM-CACHE` run I looked at `build/test-results/test/`:

```
$ ls -l build/test-results/test/
11:24:11  TEST-com.example.orders.OrdersApplicationTest.xml
11:24:11  TEST-com.example.orders.pricing.PricingServiceShould.xml
11:24:11  TEST-com.example.orders.pricing.PricingServiceTest.xml

$ grep -h timestamp build/test-results/test/*.xml
timestamp="2026-09-23T03:24:08.087Z"
timestamp="2026-09-23T03:24:08.390Z"
timestamp="2026-09-23T03:24:08.393Z"
```

The files were written three seconds ago. The timestamps inside them are from the earlier run that produced them. `ls -l` tells you the result is fresh. The XML tells you the result is old. If you want one command that cannot be fooled by a cache restore, it is that `grep`.

## What a fresh CI checkout does with it

Now the version that should worry you, because it is the normal shape of a CI job.

I set the flag to `false`, which makes `FeatureFlagTest` fail, and then simulated a runner: delete the build directory, keep the Gradle home cache, run the suite.

```
$ rm -rf build && ./gradlew test
> Task :test FROM-CACHE
BUILD SUCCESSFUL in 493ms
3 actionable tasks: 1 executed, 2 from cache

$ ./gradlew test --rerun
7 tests completed, 1 failed
BUILD FAILED in 1s
```

A fresh checkout is not a safety net here. It is the precondition. An empty build directory is exactly the situation where a cache hit is useful, and Gradle cannot know that the thing which changed is a file it has never heard of. On a runner with a warm cache, that failure is invisible.

This is not a hypothetical concern someone raised in a mailing list. It is an open request in Gradle's own tracker, filed in 2019 and still open: test tasks should not be cacheable by default, because *"choosing to cache tests as the default choice is very dangerous because tests may pass when they should fail"*. The workaround in that thread is the same one that works today: declare your inputs, or force the run.

## This is not the Maven bug with a different logo

If you have read my earlier lab on [AI-generated JUnit tests that never execute](/blog/ai-junit-tests-not-running-spring-boot-4/), the shape looks familiar and it is worth separating them, because the checks are different.

On the Maven side, the failure is discovery. Surefire's default includes are `**/Test*.java`, `**/*Test.java`, `**/*Tests.java` and `**/*TestCase.java`, so a file called `OrderServiceShould.java` is not a test as far as Maven is concerned, and it produces no warning. In this lab, `PricingServiceShould` ran both of its methods. Gradle's JUnit Platform support does not filter by class name, so the naming trap that eats Maven projects does not exist here.

Maven hides files. Gradle replays outcomes. And in one place Gradle is louder than Maven: a filter that matches nothing.

```
$ ./gradlew test --tests "com.example.orders.pricing.PriceingServiceTest"
> Task :test FAILED
> No tests found for given includes: [com.example.orders.pricing.PriceingServiceTest](--tests filter)
BUILD FAILED in 370ms
```

A typo in a `--tests` filter fails the build. The equivalent on the Maven side reports zero tests and exits 0. So this is not "Gradle is worse". It is "Gradle has a different hole, in a different place, and the hole is only open when something outside the compiled sources changed".

## Then I handed the repository to Claude Code

My prediction was simple: it would run `./gradlew test`, see `BUILD SUCCESSFUL`, and report that everything passes. That is the failure mode I have been documenting for months — the agent treats the build tool's summary as evidence.

I ran five sessions. Every one of them caught it.

One note on what I was actually running: the commands went through the Claude Code CLI, and the model behind it on this machine is `glm-5.3-flash`. I am naming it because the point of the next section is not "this model is smart". It is that the information needed to catch the lie was sitting in the output the whole time.

### The control run

First, a task where nothing is being hidden: change the discount threshold from 100.00 to 150.00 and make the suite pass. The source changed, so the inputs changed, so the tests actually ran.

It changed the threshold, updated the one assertion that encoded the old boundary, added a case for the gap between the old and new thresholds, and reported eight tests passing. I checked the result XML: eight tests, correct. When Gradle runs your tests, the agent's report is accurate. Worth stating, because it is the boring majority of runs.

### Five attempts at the lie

| Run | Condition | What Gradle offered | What it reported |
|---|---|---|---|
| a2 | flag flipped, local build dir | `:test UP-TO-DATE`, green | Caught it: forced a re-run, reported 6 pass / 1 fail |
| a3 | flag flipped, fresh checkout | `:test FROM-CACHE`, green | Caught it: *"a plain ./gradlew test gave a false green"* |
| b1 | `org.gradle.console=rich` (label gone) | no label, green | Caught it: read `3 actionable tasks: 3 up-to-date` |
| b4 | `org.gradle.logging.level=quiet` (no output) | silence, exit 0 | Caught it: compared timestamps inside the result XML |

The last one is the one I keep thinking about. With logging silenced, `./gradlew test` prints nothing and exits 0. There is no label, no summary line, no test names. It still found the failure, and here is how it described the method:

> *"I only caught it because the restored result XMLs kept their old internal timestamps."*

That is the same instrument I built by hand, reached independently, by a process that had no reason to distrust the build. It also noticed, unprompted, that someone had added `org.gradle.logging.level=quiet` to `gradle.properties` and flagged it as the reason the first run was silent.

So the prediction was wrong, and the reason it was wrong is more useful than the prediction. The agent did not trust a single invocation. It ran the build more than once, with a flag that forces execution, and compared. That is not a model capability. It is a habit: do not accept the first summary.

Which is the uncomfortable part. The default human workflow is exactly one command:

```
./gradlew test
BUILD SUCCESSFUL in 401ms
```

One command, no `--rerun`, and you are the one holding the false green. The agent is safer here not because it understands Gradle better, but because it verifies by default and you probably do not.

## The fix it wrote, and whether it actually works

In the first run, alongside its diagnosis, it proposed two fixes: change the test, or close the cache blind spot. I asked for the second one.

It added four lines to `build.gradle`:

```groovy
tasks.named('test') {
    useJUnitPlatform()
    // FeatureFlagTest reads this file at runtime; declaring it as an input
    // (content-only, path-insensitive) keeps up-to-date checks and the build
    // cache key honest when the flag flips.
    inputs.file('flags/discount-enabled.txt')
        .withPathSensitivity(PathSensitivity.NONE)
}
```

`PathSensitivity.NONE` matters: only the file's content enters the cache key, not its path, so the cache still works across checkouts and machines.

Then it did something I did not ask for and should have: it flipped the flag in both directions and recorded what happened each time.

| Scenario after the fix | Result |
|---|---|
| flag = `false` | `:test` re-ran → FAILED |
| flag = `true` | `:test` re-ran → PASSED |
| flag unchanged | `:test UP-TO-DATE`, no spurious run |
| flag back to `false` | `:test` re-ran → FAILED |
| flag back to `true` | `:test FROM-CACHE`, green — content matches, reuse is legitimate |

I verified the first row independently with `--rerun`: seven tests, one failure. The fix closes the hole in both directions without giving up the cache. That is a better answer than the one I had, which was "turn caching off for tests".

## What I got wrong

I set up this lab expecting to write about an agent being fooled by a green build. Five runs, five catches, including one where the build tool said nothing at all. The honest version of this experiment is that Gradle is the one handing out false greens, and the agent in the loop was the thing that refused to accept one.

The second thing I got wrong was smaller and worth keeping: I assumed the outcome label was the signal, and that removing it would break the detection. It did not. The failure was detectable from the summary line and from the result files. If you are building a guardrail, do not build it on the label.

And one limit on all of this: I ran one agent, on one model, on one project, five times. I am not claiming any model catches this every time. I am claiming that "BUILD SUCCESSFUL" carries no information about whether your tests ran, and that the two cheap checks below do.

## Three things I now do

1. **Read the last line, not the last word.** `N actionable tasks: N up-to-date` tells you what the build skipped. Set `org.gradle.console=plain` in CI so the per-task labels survive too, and never set `org.gradle.logging.level=quiet` in a project where anyone checks builds by eye.

2. **Force the run when something outside the sources changed.** `./gradlew test --rerun` re-runs that one task; `--rerun-tasks` re-runs everything. If a test reads a file, an environment variable, a container, or the clock, treat every run of it as unverified until you have forced at least one.

3. **Declare what your tests actually read.** One `inputs.file(...)` line per external dependency of the suite, with `PathSensitivity.NONE` unless the path is meaningful. It costs four lines and it turns a silent reuse into a correct re-run.

If you want the Maven-side version of this problem, where the tests are never discovered at all, it is a different mechanism with a different check, and I wrote that one up separately. The [Spring Boot 4 migration write-up](/blog/spring-boot-4-migration-ai-agents/) covers the larger set of changes that compile fine and behave differently, which is this category of problem one level up. The same "green but nothing happened" shape turns up when an agent [adds a dependency that wires nothing](/blog/codex-spring-boot-4-dependencies-silent-failures/) and when [Codex reports a green CI build](/blog/codex-ci-spring-boot-green-build/) after changing the business rule. If you are pointing agents at JVM projects in general, the [Java + AI hub](/blog/ai-for-java-developers/) collects the rest of these experiments.

## Frequently asked questions

### Why does ./gradlew test say BUILD SUCCESSFUL when no tests ran?

Gradle skips work whose declared inputs have not changed and reuses stored outputs when they have. A skipped test task prints an outcome label instead of a test summary and still exits 0. `BUILD SUCCESSFUL` means no task that executed failed; it says nothing about what executed.

### How do I check whether my Gradle tests actually ran?

Look for `> Task :test UP-TO-DATE` or `FROM-CACHE` with `--console=plain` or `--console=verbose`, or read the final `N actionable tasks: N up-to-date` line, which prints in every mode. For an independent check, compare the `timestamp` attribute inside `build/test-results/test/*.xml` against the current time — a restored result keeps the timestamp of the run that produced it.

### Does the build cache make this worse in CI?

Yes. A fresh checkout empties the build directory while the Gradle home cache survives, which is precisely the condition for a cache hit. In my run that restored a green result in 493ms on a repository where the suite failed.

### Should I disable caching for the test task?

Not globally. Declare external inputs instead, so the cache key covers them, and use `--rerun` for anything you cannot model. Gradle has an open request since 2019 to make test caching opt-in, which tells you this is a known sharp edge rather than a misconfiguration on your side.

### Is this the same as Maven Surefire silently skipping AI-written tests?

No. Maven never discovers the file, because the class name does not match its include patterns. Gradle discovers everything and replays a previous result instead. Maven hides files, Gradle replays outcomes — and Gradle fails loudly on an empty `--tests` filter, where Surefire reports zero and exits 0.
