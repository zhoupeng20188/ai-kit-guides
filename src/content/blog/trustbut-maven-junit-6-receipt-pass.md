---
title: "Trustbut on Maven: A No-Op JUnit 6 Test Gets a PASS (2026)"
description: "Trustbut 0.7.0 on Maven: a no-op JUnit 6 test earned PASS, while adding no test earned WARN. Ten receipt cases, with the limits of what they prove."
pubDate: 2026-11-11
category: "java-testing-ci"
tags: ["trustbut", "junit 6", "maven", "surefire", "ci cd", "ai coding agents", "java testing", "java-ai-cluster"]
image: "/og-trustbut-junit6-receipt.jpg"
imageAlt: "trustbut 0.7.0 Maven receipts: a no-op JUnit 6 test gets PASS, no test gets WARN"
updatedDate: 2026-11-11
faq:
  - question: "Did trustbut flag JUnit tests that Surefire never discovered?"
    answer: "No. In this lab, adding PriceShould.java and PriceIT.java produced PASS receipts with 'Findings: None' and no 'New/changed tests' section at all. The off-by-one bug was still present in both cases. These are detection boundaries under Surefire's default includes, not a broken install."
  - question: "Why did a no-op test get PASS when adding no test got WARN?"
    answer: "Case 07 added a test class whose only assertion was assertTrue(true). Its receipt recorded '0 prove the change · 1 pass without it', raised no finding, and returned PASS / exit 0. Case 08 fixed the production code with no test change and got the 'nothing proves this change' WARN. Adding the no-op test suppressed the warning."
  - question: "Does --strict catch either case?"
    answer: "No. In the trustbut spec, --strict only changes WARN into exit code 1; WARN stays WARN and PASS stays PASS. Case 06 (@Disabled with --strict) moved from exit 0 to exit 1, while cases 09 and 10 (no-op test and undiscovered test, both with --strict) still returned PASS / exit 0."
  - question: "Is JUnit 6 responsible for *Should and *IT tests not running?"
    answer: "No. The discovery rule belongs to Maven Surefire, whose default includes are **/Test*.java, **/*Test.java, **/*Tests.java and **/*TestCase.java. *IT classes belong to Failsafe, which was not bound in this fixture. JUnit 6 is the engine, not the file selector."
  - question: "Is this a trustbut bug, and does it show that AI agents fake tests?"
    answer: "I am not calling it a defect: cases 01 and 02 show the Maven runner correctly returns FAIL for a genuinely failing test and credits a real fail-before / pass-after proof. I did not isolate why case 07 stays PASS. No coding agent was run for this lab, so it measures no agent behaviour and no cheating rate."
  - question: "Can I reproduce these receipts?"
    answer: "Yes. The fixture, verification script and 31 evidence files are in the trustbut-junit6-lab directory of my verification repository. On JDK 17, Maven 3.9+ and Node 22+, set JAVA_HOME and run bash verify.sh; a clean run prints checks passed: 10 failed: 0."
---

I added a test that could not fail, and the verifier said PASS. Then I removed the test, fixed the actual bug with no test change at all, and the same verifier said WARN.

The verifier was [trustbut 0.7.0](https://github.com/isAlmogK/trustbut), running its Maven runner against a JUnit 6 project. The no-op test was a new class called `PriceWeakenedTest` whose entire body was `assertTrue(true)`. Its receipt said, in the tool's own words, `New/changed tests: 0 prove the change · 1 pass without it` — and then printed `Findings: None`, a PASS verdict, and exit code 0. The other commit changed `Price.qualifies` from `>` to `>=`, which is the real fix, and got `nothing proves this change ⚠` with a WARN.

So the commit that left the bug in place and added a fake test looked cleaner than the commit that fixed the bug. That is worth understanding before anyone wires a receipt into a CI gate.

This is a synthetic teaching fixture, not a production incident. I ran ten single-commit changes against one small Java project and kept every receipt. Everything below is either an executed observation from those runs, a quote from the tool's own documentation, or a clearly labelled suggestion I did not test.

## Why I checked this tool at all

I have spent a lot of this site on one family of failure: a build that finishes green while the test that would have caught the problem never ran, or ran with an assertion that observes nothing. The [CI acceptance guide](/blog/codex-ci-spring-boot-green-build/) covers the version where an agent process result gets mistaken for an application result. trustbut is interesting to me because it is one of the few tools that tries to answer that question without asking another model for an opinion.

Its [README](https://github.com/isAlmogK/trustbut) describes the mechanism plainly: it reruns the suite in a clean checkout, runs every new or changed test against the base revision to see whether it fails there, flags skipped tests and removed assertions, and emits a PASS / WARN / FAIL receipt. No LLM, no account, no network call in the core. For Maven it detects `pom.xml` and runs `mvn -B test`, reading Surefire reports. That is exactly the runner I care about.

The project also publishes its own pilot measurements rather than just claims. In ["What we've measured"](https://github.com/isAlmogK/trustbut#what-weve-measured), the author reports trustbut 0.7.0 on 201 real merged pull requests: 53 of 103 agent PRs and 56 of 98 human PRs could be run at all; 275 of 283 (97%) agent-written new or changed tests failed without their change, against 294 of 333 (88%) for people; 6 of 53 agent PRs and 7 of 56 human PRs had no test proving the change. A [third-party write-up](https://clawdbytes.com/article/2026-10-19-trustbut-checks-if-an-ai-agents-new-tests-fail-without-its-change.html) covers the same pilot. Those are the author's own numbers on merged PRs that already survived CI and review, and the README says so. I cite them as context, not as an independent reproduction.

The [design spec](https://github.com/isAlmogK/trustbut/blob/main/docs/SPEC.md) is unusually candid about a separate limitation. In its receipt section it says that runners whose results do not carry file paths — Go, Maven, Gradle, .NET, Swift — cannot resolve an unchanged failing test back to a source file, so "an unchanged failing test there never gets `test-regressed`". I want to be careful here: that statement is about regression detection on a failing unchanged test. My lab is about the fail-before / pass-after proof path on new tests. They are different mechanisms, and I did not isolate the relationship between them. The spec's honesty is why I picked this tool to probe, not evidence for any conclusion I reached.

What I actually wanted to know was narrow: on a plain Maven / JUnit 6 project with Surefire defaults, what does a receipt prove when a test never runs, when a test runs but asserts nothing, and when `--strict` is on?

## Ten commits, one business rule

The whole fixture is one static method:

```java
public static boolean qualifies(int cents) {
    return cents > 10000;
}
```

The boundary should qualify, so the base revision has an off-by-one. The base test class `PriceTest` contains one passing test at 10001. `pom.xml` pins JUnit Jupiter 6.0.3, Surefire 3.5.6, `maven.compiler.release=17`, and deliberately leaves Surefire at its **default** configuration: no `failIfNoTests`, no Failsafe binding, no custom includes. That last choice is the point of the lab, and it also means these results do not transfer to a project that configures those gates.

Each case starts from the same base commit in a temporary git repository, applies one change, commits it, runs `mvn -B test`, then runs `trustbut verify -b main` with `--receipt-md` and `--receipt-json` pointed at the evidence directory. Four cases repeat with `--strict`. The script never touches the verification repository's history. Toolchain: Amazon Corretto 17.0.19, Maven 3.9.11, Node 22.22.2, trustbut 0.7.0.

Two environment details are worth recording because they can silently change the evidence. `JAVA_HOME` was empty on my machine, and `mvn` was picking OpenJDK 27 while `java` resolved to Corretto 17, so `verify.sh` refuses to run unless `JAVA_HOME` is set explicitly and prepends that JDK to `PATH`. And an untracked `target/` directory made early receipts add an "Uncommitted changes are not included in this receipt" note, so the script writes a `.gitignore` before the base commit. Neither is a finding about trustbut; both are the kind of dirt that makes a matrix uniformly wrong in the same direction.

## The ten receipts

| Case | Change | `mvn -B test` | Receipt | exit |
| --- | --- | --- | --- | ---: |
| 01 | real boundary assertion, production code unchanged | FAIL | **FAIL** | 1 |
| 02 | fix `>=` plus the same real assertion | pass | **PASS**, "1 proves the change" | 0 |
| 03 | new `PriceShould.java` (not discovered) | pass | **PASS**, Findings None | 0 |
| 04 | new `PriceIT.java` (not discovered by Surefire) | pass | **PASS**, Findings None | 0 |
| 05 | new `@Disabled` test class | pass, 1 skipped | **WARN**, "Test skipped" | 0 |
| 06 | case 05 with `--strict` | pass, 1 skipped | **WARN** | 1 |
| 07 | new test with `assertTrue(true)` | pass | **PASS**, "1 pass without it" | 0 |
| 08 | fix `>=`, no test added or changed | pass | **WARN**, "nothing proves this change" | 0 |
| 09 | case 07 with `--strict` | pass | **PASS** | 0 |
| 10 | case 03 with `--strict` | pass | **PASS** | 0 |

A clean run prints `checks passed: 10 failed: 0`, which only means all ten verdicts matched the recorded behaviour on a re-run. Cases 01 and 02 are the forward controls: a genuinely failing test is detected, and a real fail-before / pass-after proof is credited. The tool and the Maven runner are working.

## A no-op test is quieter than no test at all

Here are the two receipts side by side, shortened only by removing the commit hashes:

```text
07-weakened                              08-code-only
## Receipt: PASS                         ## Receipt: WARN
Tests (clean checkout): 2 passed         Tests (clean checkout): 1 passed
New/changed tests:                       Proof: nothing proves this change
  0 prove the change
  1 pass without it
Findings: None                           Findings:
                                           Nothing proves the change
                                           (no test added or changed)
```

Case 07 did not fix anything. `Price.qualifies` still returns `cents > 10000`. Its only new test asserts a literal `true`. The receipt sees a new test, sees it pass both with and without the change, records `0 prove the change`, and then raises no finding. Case 08 does fix the off-by-one and gets a warning for not adding a test.

I expected case 07 to be WARN. The README's [test-integrity table](https://github.com/isAlmogK/trustbut#what-it-checks) describes `change-not-proven` as a WARN when "code changed, and no test changed, no new or changed test that ran was found in the changed test files, or none fails without the change". The [spec's verdict rule](https://github.com/isAlmogK/trustbut/blob/main/docs/SPEC.md#6-receipt) says WARN if there is "any warning or non-constraining test". A test that passes without the change is the definition of non-constraining. On the wording alone, `0 prove the change · 1 pass without it` looks like the case that finding was made for.

The observed verdict was PASS. I am not going to call that a bug, because I have not done the work to establish why. It could be a deliberate choice to warn only when no new test file exists, an artefact of how the Maven runner reports cases, something about this fixture, or a gap between the 0.7.0 implementation and the wording of the docs. My lab isolates the verdict, not the cause. Anyone who wants the cause should read the proof engine for this runner and re-run against the version they deploy.

The practical asymmetry does not depend on the cause. In a CI pipeline, adding a one-line tautological test is nearly free; it is also the kind of thing an agent might produce when asked to "add a test". On this fixture, that one line converts a WARN into a PASS. A gate that counts findings or watches exit codes gets *less* signal after the fake test is added. That is the opposite of what a verification step is for, and it is why I would not treat PASS as "the change is proven" without reading the proof line.

The same split shows up in the [JUnit assertions guide](/blog/ai-junit-tests/): a test that executes can still fail to observe the behaviour it claims to check. Here the receipt actually prints the observation — `1 pass without it` — and still returns the clean verdict. The information is present; the verdict does not act on it.

## Tests that never ran leave no trace

Cases 03 and 04 add a test that asserts the boundary correctly. `PriceShould` and `PriceIT` would both fail if Surefire ran them, because `Price.qualifies(10000)` is false on the base revision. Neither runs.

The reason is Maven Surefire's default selection, documented in the [`test` goal reference](https://maven.apache.org/surefire/maven-surefire-plugin/test-mojo.html): `**/Test*.java`, `**/*Test.java`, `**/*Tests.java`, `**/*TestCase.java`. `PriceShould` matches none of them. `PriceIT` belongs to [Failsafe](https://maven.apache.org/surefire/maven-failsafe-plugin/usage.html), which this fixture deliberately does not bind. JUnit 6 is the test engine here, not the file selector — blaming JUnit for the missing discovery would send you to the wrong configuration. The [Surefire discovery audit](/blog/ai-junit-tests-not-running-spring-boot-4/) walks through that diagnosis in a Spring Boot 4 project.

What matters for this article is what the receipt says about a test that never ran. Case 03's entire receipt is:

```text
## Receipt: PASS
Tests (clean checkout): 1 passed · 0 failed · 0 skipped
### Findings
None.
```

There is no `New/changed tests` section at all, no "not run" line, no count of test source files invented but not executed. Case 07's receipt says `2 passed`, so when the new test class *is* discovered it does appear in the runner's results. The difference is entirely upstream of trustbut: a runner report only contains cases the build executed. I would describe the invisibility as a structural consequence of that boundary rather than a measured finding of mine — the lab did not instrument the runner's report parsing.

This also explains why the pilot numbers and my table are not in conflict. The pilot ran on merged PRs that already passed CI, where a test named `PriceShould` would typically have been caught by review or by a configured build. About half of those PRs could not be run at all, mostly because dependencies or toolchains would not install. Neither setting says anything about what a receipt does on a deliberately misconfigured local fixture.

## --strict changes the exit code, not the verdict

The [spec](https://github.com/isAlmogK/trustbut/blob/main/docs/SPEC.md#6-receipt) states the rule exactly: "Exit code is 1 on FAIL, and also on WARN with `--strict`; 2 on a usage or runtime error." It is an exit-code switch. It does not promote a PASS.

My four strict cases confirm it. Case 06 is case 05 with `--strict`: the verdict stays WARN and the exit code moves from 0 to 1. Cases 09 and 10 — the no-op test and the undiscovered `PriceShould`, both with `--strict` — stay PASS and exit 0. So a CI step written as `trustbut verify --strict` and gated on the exit code accepts cases 03, 04, 07, 09 and 10: five of the ten changes, including all the ones where the bug is still present.

If I were building the gate, I would read the JSON receipt with `--receipt-json` and assert on its `verdict` **and** on the proof count, then cross-check the executed test count from `target/surefire-reports` against the test classes I expect. That is a suggestion based on the shape of these receipts, not a gate I implemented and measured here. I would also treat exit code 2 as an environment failure rather than a pass, which is a general CI habit rather than something this lab tested.

## What I would put in a Maven CI gate

Separating what the ten runs support from what I am recommending:

1. **Make every test class discoverable.** Cases 03 and 04 show a receipt cannot report on a test the build never ran. Check the Surefire includes and bind Failsafe's `integration-test` and `verify` goals if you use `*IT` classes. This is supported by the lab.
2. **Do not let a receipt judge assertion strength.** Case 07's receipt contains the evidence that the test proves nothing and still returns PASS. Assertions need review, or a complementary technique such as mutation testing on changed lines. The limitation is measured; the remedy is a suggestion.
3. **Require a proof, not just a green exit.** Ask for at least one new or changed test that fails without the change, and read that from the receipt rather than inferring it from exit 0. Case 02 shows the positive form; cases 07 and 08 show why the exit code alone is not enough.
4. **Pin the toolchain and the verifier version.** The spec and README both note receipt behaviour changes between releases; the README's pilot is explicitly labelled 0.7.0. Re-run the matrix against the version you deploy. My `JAVA_HOME` problem is a small example of why the environment belongs in the record.
5. **Keep the receipt as evidence, not as an acceptance decision.** A receipt describes what ran and what it proved. It cannot tell you whether the business rule is right. That framing is the whole point of the [verification-first hub](/blog/ai-for-java-developers/) and of the [Codex Spring Boot guide](/blog/codex-spring-boot/), where a plausible-looking "done" is treated as a claim until an independent run supports it.

## What this lab does not prove

No coding agent was run to produce any of these results. This is not a measurement of agent behaviour, not an estimate of how often agents write weak tests, and not a ranking of verification tools. The pilot statistics I quoted belong to trustbut's author and are about merged open-source PRs, not about my fixture.

The scope is one business rule, one `pom.xml`, one JDK, one Maven version, one Surefire version, and the `maven` runner of trustbut 0.7.0. Other runners, languages and versions may behave differently. The `pom.xml` keeps Surefire defaults on purpose; adding `failIfNoTests`, a Failsafe binding or custom includes changes the inputs and would change the outcomes. The spec's Maven/Gradle `test-regressed` limitation concerns regression detection on unchanged failing tests, and this lab did not isolate whether it has any bearing on the proof path. I did not establish why case 07 stays PASS. Cases 01 and 02 rule out a broken install, but they do not turn the other eight verdicts into a general statement about the tool.

## Reproduce it

The fixture, the script, `summary.tsv`, ten Markdown receipts, ten JSON receipts and the Maven summary lines are in the [trustbut-junit6-lab directory of my verification repository](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/trustbut-junit6-lab).

```bash
git clone https://github.com/zhoupeng20188/ai-kit-guides-verification-labs
cd ai-kit-guides-verification-labs/trustbut-junit6-lab
export JAVA_HOME=/path/to/your/jdk-17
bash verify.sh
```

The script builds a temporary git repository, commits each case on the same base, runs Maven and trustbut, records both exit codes, and checks every verdict against the recorded behaviour:

```text
checks passed: 10   failed: 0
```

If there is one habit I would take from this, it is to read the proof line and not just the verdict. In case 07 the receipt told the truth — `0 prove the change` — and the PASS sat right above it. The evidence was there. The gate I would have written was not.
