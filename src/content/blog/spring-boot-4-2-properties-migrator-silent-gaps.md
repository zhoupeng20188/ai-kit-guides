---
title: "Spring Boot 4.2 Properties Migrator: Four Gaps That Stay Silent"
description: "Tested spring.properties.migrator.fail in 4.2.0-RC1: on-error skips renamed keys, @PropertySource is invisible, and typos stay silent."
pubDate: 2026-10-30
category: "spring-boot-4"
tags: ["spring boot 4", "configuration properties", "java testing", "ai coding agents", "java-ai-cluster", "maven"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["spring.properties.migrator.fail", "spring boot 4.2 properties migrator", "spring boot properties migrator on-warning", "spring resources add-mappings renamed", "spring boot 4.2 migration config", "propertysource old key ignored", "spring boot config silent failure"]
updatedDate: 2026-10-30
faq:
  - question: "Does spring.properties.migrator.fail exist in Spring Boot 4.1?"
    answer: "It is introduced in the 4.2 line; the 4.2.0-RC1 release notes list it as new. I verified it on 4.2.0-RC1 only. If you are still on 4.1, the migrator reports the same findings but has no property to turn them into a failure, so the exit-code gate described here is not available yet."
  - question: "Why does on-error let my renamed key through?"
    answer: "Because the level comes from the metadata classification. A key with a documented replacement is a rename and reports at warning level; a key whose feature was removed reports at error level. on-error therefore stops only the second kind. Use on-warning during an upgrade."
  - question: "Should the migrator stay in the application permanently?"
    answer: "No. It is documented as an aid for the migration window and it rewrites configuration at runtime while present. Keep it in the upgrade branch or a temporary CI job, verify the removals and renames, then take it out. Plan for what replaces it, because the gate leaves with the module."
  - question: "How do I catch the @PropertySource case?"
    answer: "Not with this tool. Either read those files directly and compare the keys against the target release's metadata, or write a small test that binds the consuming object and asserts the value. In my lab, the @PropertySource file said false and the bound field was true, with nothing in the log — a binding assertion is the only thing that would have caught it."
  - question: "Is the migrator useful at all if it misses so much?"
    answer: "Yes, for the two categories it does cover: renamed keys under on-warning, and removed keys under either value. That covers most of what a generation upgrade breaks on. The four gaps are about what to check in addition, not a reason to skip the tool."
  - question: "Can I re-run these measurements myself?"
    answer: "Yes — that is why the fixture and its logs are public. Clone ai-kit-guides-verification-labs, enter boot42-migrator-lab, run bash verify.sh on JDK 17 or later, and you should get checks passed: 23 failed: 0. Change the parent version in pom.xml to repeat the matrix on whichever 4.2 build you actually deploy."
---

Spring Boot 4.2.0-RC1 gives the properties migrator a switch that can stop the application when it finds configuration problems. That is a real improvement over a log line nobody reads. It also has four specific gaps, and I measured all of them on 4.2.0-RC1. Some of these limits are documented; the consequences at runtime are not, and the exit codes below are from my own runs.

The short version: `spring.properties.migrator.fail` defaults to `never`, and `on-error` — the value most people will reach for — does not stop a single renamed key. Worse, keys loaded through `@PropertySource` are neither reported nor renamed, so the setting silently reverts to its default while the file still says otherwise.

Every measurement below comes from a lab project I built for this article and published, with its raw startup logs, at [`ai-kit-guides-verification-labs/boot42-migrator-lab`](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/boot42-migrator-lab). Environment: Amazon Corretto 17.0.19, Maven 3.9.11, `spring-boot-starter-webmvc` plus `spring-boot-properties-migrator` at 4.2.0-RC1, all runs with `--spring.main.web-application-type=none` so the process exits on its own. Exit codes and log excerpts are from those runs, not from the release notes. Release candidates change; re-run the table against the GA you actually deploy.

## What the switch is and where it fires

`spring-boot-properties-migrator` reads the configuration metadata shipped with Spring Boot, compares it against the property sources in your `Environment`, and reports keys that were renamed or removed. The [4.2 upgrading guide](https://docs.spring.io/spring-boot/4.2-SNAPSHOT/upgrading.html#upgrading.to-feature) is where the new property and its three values are actually defined; the [4.2.0-RC1 announcement](https://spring.io/blog/2026/10/23/spring-boot-4-2-0-RC1-available-now) and the [release notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2.0-RC1-Release-Notes) only announce the capability in one sentence.

The timing matters for how you use this. RC1 shipped on 2026-10-23 and 4.2 is not GA; the current general-availability line that same week was 4.1.2. So this is a property to test now and put into an upgrade gate when you land on 4.2, not something to add to a production parent tomorrow.

The property binds to an enum named `Fail` with three values, which the framework itself will print for you if you misspell one:

```
Action:
Update your application's configuration. The following values are valid:
    NEVER
    ON_ERROR
    ON_WARNING
```

That output came from passing `on-warn`. The startup failed with a bind error. This is worth noting early: the switch's own configuration fails loudly, while the problems it looks for fail quietly by default.

The check runs on [`ApplicationPreparedEvent`](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/context/event/ApplicationPreparedEvent.html). The stack trace names it directly:

```
at ...PropertiesMigrationListener.onApplicationPreparedEvent(PropertiesMigrationListener.java:62)
```

Two consequences follow from that timing. The environment is already assembled, so command-line arguments, environment variables, YAML, profile files and `spring.config.import` are all visible. But `@Configuration` classes have not been parsed yet — that happens during context refresh — so any property source they add is still absent when the migrator looks. The [upgrading guide](https://docs.spring.io/spring-boot/4.2-SNAPSHOT/upgrading.html#upgrading.to-feature) states this boundary in one line: properties added late to the environment, such as those from `@PropertySource`, are not taken into account. Gap 3 is what that boundary actually costs you.

## The behaviour table

Same jar, same classpath, only the arguments change. `renamed` means the key has a documented replacement; `removed` means the feature is gone.

| Key supplied | `fail` value | Exit | Reported | Startup stopped |
| --- | --- | ---: | --- | --- |
| none | default | 0 | – | – |
| renamed (`spring.resources.add-mappings`) | `never` (default) | 0 | yes | no |
| renamed | `on-error` | 0 | yes | **no** |
| renamed | `on-warning` | 1 | yes | yes |
| removed (`spring.banner.image.width`) | `never` | 0 | yes | no |
| removed | `on-error` | 1 | yes | yes |
| removed | `on-warning` | 1 | yes | yes |
| misspelled key (not in metadata) | `on-warning` | 0 | **nothing** | no |
| real key, no consumer on classpath | `on-warning` | 0 | **nothing** | no |
| renamed, from `@PropertySource` | `on-warning` | 0 | **nothing** | no |
| renamed, from `application-legacy.properties` | `on-warning` | 1 | yes | yes |
| renamed, from `spring.config.import` | `on-warning` | 1 | yes | yes |
| renamed, as `SPRING_RESOURCES_ADD_MAPPINGS` | `on-warning` | 1 | yes | yes |
| renamed, in a YAML config data file | `on-warning` | 1 | yes | yes |
| renamed + removed, mixed | `on-error` | 1 | yes | yes |

CI systems read exit codes, not log lines. Read the table that way and every gap below shows up as a run that exited 0 when it should have stopped.

## Gap 1: the default value is "say nothing"

Any run without the property behaves like `never`: a report is printed, the application starts, the exit code is 0. In the pipeline that upgrades a service, this is indistinguishable from a clean run, because nobody greps for the phrase "The use of configuration keys that have been renamed".

The migrator has always behaved this way. What changed in 4.2 is that you can now choose otherwise. Choosing requires a deliberate edit, and the module is meant to be temporary — the [external configuration reference](https://docs.spring.io/spring-boot/reference/features/external-config.html) and the [4.2 upgrading guide](https://docs.spring.io/spring-boot/4.2-SNAPSHOT/upgrading.html#upgrading.to-feature) both treat it as an aid that gets removed once the move is finished. So the window where the switch is available is exactly the window where it needs to be switched on, in CI, by someone who remembers.

## Gap 2: `on-error` passes every renamed key

This is the one that will catch people. The name suggests "make errors fail". In practice the level is decided by how the metadata classifies the key, not by how bad the consequence is.

A renamed key reports as:

```
The use of configuration keys that have been renamed was found in the environment:
	Key: spring.resources.add-mappings
		Replacement: spring.web.resources.add-mappings
```

That is a warning-level finding. With `fail=on-error` the process exits 0. A removed key reports differently — `Reason: Support for image banners has been removed.` — and that one does stop the process under `on-error`.

Renamed keys are not an edge case: Boot 2.4 moved `spring.resources.*` to `spring.web.resources.*`, and the same pattern repeats elsewhere. The stricter-sounding value therefore misses exactly the category a generation upgrade has to rename. If you set this property at all, set `on-warning`. The reason is visible in one line of the table: `on-warning` covers both, `on-error` covers one.

## Gap 3: `@PropertySource` is reported nowhere and renamed nowhere

The upgrading guide already says that properties added late to the environment, including those from `@PropertySource`, are not taken into account. What it does not say is what else is lost with them. I measured that consequence, and I nearly got the measurement wrong.

A class like this is still common in older services:

```java
@Configuration
@Profile("psource")
@PropertySource("classpath:legacy.properties")
public class LegacyPropertySourceConfig {
}
```

with `legacy.properties` containing `spring.resources.add-mappings=false`. Run it with `fail=on-warning`: exit code 0, no migration report at all. [`@PropertySource`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/annotation/PropertySource.html) is processed when the configuration class is parsed, which happens during context refresh — after `ApplicationPreparedEvent`. At the moment the migrator looks, that file has not been read into the environment yet. This part is documented behaviour, not a discovery. What the guide does not spell out is that the key is never renamed either: the module both reports and rewrites, so losing the check also loses the rewrite. A probe that prints what the environment resolved shows this:

```
PROBE old-name   spring.resources.add-mappings      = false
PROBE new-name   spring.web.resources.add-mappings  = null
PROBE bound      spring.web.resources.addMappings   = true
```

Compare the same key supplied on the command line, where the migrator does run first:

```
PROBE old-name   spring.resources.add-mappings      = false
PROBE new-name   spring.web.resources.add-mappings  = false
```

So the migrator is not only a reporter, it is also the mechanism that maps the old name onto the new one. When it runs too late, you lose both functions at once. The file says `false`, the bound value is `true`, and nothing anywhere in the log mentions the key. That is a silent behaviour change produced by the tool you added to prevent silent behaviour changes.

For contrast, the same old key placed in `application-legacy.properties`, or pulled in through `spring.config.import=classpath:imported.properties`, is reported and does stop the process. YAML works the same way. The difference is not the file format or the filename, it is whether the source is loaded as config data before the event.

The measured trap is worth stating separately, because it nearly invalidated my own run. I first activated a profile named `legacy` for the `@PropertySource` case and got a failure — but that profile also triggered `application-legacy.properties`, which is config data. The test proved nothing until the profile name for the `@PropertySource` class was changed to one with no matching profile file. If you build this check for your own service, make sure the profile you activate does not quietly load a second copy of the same key.

## Gap 4: keys the metadata does not know, and keys nothing claims

Two categories never appear in any report, at any `fail` level.

The first is the key that does not exist. I passed `spring.web.resource.add-mappings` — one `s` short of the real name — with `fail=on-warning`. Exit code 0, empty output, no mention anywhere. The migrator works from a list of known renames and removals. A made-up name matches nothing on that list, so there is nothing to compare it against. This matters more in an AI-assisted workflow than a hand-written one, because inventing a plausible property name is one of the common failure modes when a coding agent writes configuration. You can see the general shape of that in [why resolved dependencies are not configured dependencies](/blog/codex-spring-boot-4-dependencies-silent-failures/); the same mechanism applies to property names.

The second category is the key that exists but has nothing to bind it. `spring.datasource.hikari.maxLifetime` with no JDBC starter on the classpath: exit 0, no output, no warning. The key is valid, the metadata knows it, but no module claims it, so no component reads it. Metadata presence is not the same claim as binding, which is the point of the [YAML audit sequence](/blog/codex-spring-boot-4-yml-properties/) published earlier; the migrator simply cannot help with this class of problem.

## What I would put in the build

Given the four gaps, the switch is worth using, but only as one of three checks. This is the sequence that follows from the measurements:

1. Add `spring-boot-properties-migrator` with `runtime` scope, and set `spring.properties.migrator.fail=on-warning` in the upgrade branch. Not `on-error` — it passes renamed keys.
2. Grep the effective environment for `@PropertySource` usage and for properties files loaded that way. Nothing in the migrator output will tell you they exist. Those files have to be checked by reading them, or by asserting the bound values directly.
3. For the keys you care about, assert the bound object rather than the key. `spring.web.resources.add-mappings` is a string in the environment and a boolean on a bean; only the second one tells you what the application will do. The [migration walkthrough](/blog/claude-code-spring-boot-4-migration-walkthrough/) shows the same acceptance pattern for other property families.

Then remove the migrator. That last step is in the migration guide for a reason, and it has a side effect worth planning for: once the module is gone, the gate that stopped your build disappears with it. If you want the check to survive, keep it in a dedicated upgrade profile or a temporary CI job rather than in the shipped artifact.

The wider point is the one that shows up in every Spring Boot 4 investigation: the changes a compiler catches and the changes that only appear as different behaviour at runtime are two different problems. A renamed key is mechanical, and a tool can handle it. A key that is silently no longer read is a behavioural change wearing the same clothes, and no amount of metadata comparison finds it. The [migration overview](/blog/spring-boot-4-migration-ai-agents/) keeps the two lists separate for that reason.

If you are working through this with an agent, the useful instruction is not "fix the warnings". It is "make the process exit non-zero on the key we are migrating, and show me the run where it does" — a request whose result can be checked, rather than a claim that the migration is clean. The [hub page](/blog/ai-for-java-developers/) collects the other verification-first walkthroughs for this stack.

## Reproduce it, and what it does not prove

The code sits in a separate repository so that it stays inspectable after this page changes: [`github.com/zhoupeng20188/ai-kit-guides-verification-labs`](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs), directory `boot42-migrator-lab`. Clone it and run the script, and every number above comes out of that run:

```bash
git clone https://github.com/zhoupeng20188/ai-kit-guides-verification-labs
cd ai-kit-guides-verification-labs/boot42-migrator-lab
bash verify.sh
```

The script runs `clean package`, starts the same jar eighteen times — one case per JVM, since an exit code only means something when the process ends by itself — and compares each result against the recorded value. It prints one line per assertion and exits 0 only when all 23 match:

```
  checks passed: 23   failed: 0
  all cases match the recorded behaviour
```

Fifteen of the eighteen cases are the rows in the behaviour table. The other three are the misspelled enum value quoted higher up and the two probes in gap 3, which is what turns the probe output from a screenshot into something you can diff. `evidence/` in that directory holds the raw startup log for every case, with local paths replaced by placeholders and nothing else edited. `README.md` records the version matrix, the case list, and both traps described above.

The boundary is worth stating as plainly as the results:

- One JDK (17), one platform, one starter set. A different module combination changes which keys exist and which have consumers — which is gap 4 restated as a limitation of the fixture rather than of the tool.
- Release candidate only. Nothing here is a claim about 4.2.0 GA or about 4.1.x.
- No web server starts in any case, so no result measures request handling. The probe asserts the bound field, not the behaviour of the filter chain that consumes it.
- Two synthetic legacy keys. This is not an inventory of every renamed key in 4.2, and the counts say nothing about how many keys a real service carries.

That shape — one narrow question, a runnable fixture, a stated boundary — is the part that makes a claim checkable. If you ask an agent for a "thorough migration test", you usually get coverage. What you want instead is a case whose result you can predict before running it, and a log you are willing to publish.
