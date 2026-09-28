---
title: "Codex Upgraded My Spring Boot 4 YAML. 3 Tools, 3 Blind Spots (2026)"
description: "Codex migrated 8 keys in my application.yml to Spring Boot 4.1.1. The 3 it missed still worked. Here are the three tools I used to find what actually broke."
pubDate: 2026-09-28
category: "ai-tools"
tags: ["openai codex", "spring boot 4", "configuration properties", "maven", "ai coding agents", "java testing", "java-ai-cluster"]
image: "/og-codex-boot4-yml.jpg"
imageAlt: "A table of application.yml keys after a Spring Boot 4 migration, with one key marked not bound and three diagnostics each showing a blind spot"
keywords: ["spring boot 4 application.yml ignored", "spring boot 4 properties migrator", "codex spring boot 4 migration", "spring boot 4 configuration metadata", "management endpoint enabled vs access boot 4", "spring boot 4 datasource hikari ignored", "jackson 3 write dates as timestamps boot 4 fails", "spring boot 4 yaml silent failure"]
faq:
  - question: "Does Spring Boot 4 silently ignore old configuration keys?"
    answer: "Mostly no, and that surprised me. I put a Spring Boot 3.5.8 application.yml with 17 keys on Spring Boot 4.1.1 and changed nothing else. Before that I had to delete one key because it stopped the app from starting at all. Of the remaining keys, every single one still took effect, including management.endpoint.health.enabled and management.endpoint.env.enabled, which no longer appear anywhere in Boot 4's configuration metadata. Migration guides describe the old keys as silently ignored. On 4.1.1 they are not ignored; they are invisible-but-working, which is its own kind of problem."
  - question: "Why did my datasource properties stop working after upgrading to Spring Boot 4?"
    answer: "Because Spring Boot 4 moved configuration metadata into per-module jars, so whether a property exists now depends on your dependencies. In the lab project, spring.datasource.hikari.maxLifetime was advertised by 2,936 properties on Boot 3.5.8 with no JDBC starter anywhere. On 4.1.1 without a JDBC starter there were 1,161 properties on the classpath and that key had nobody to bind to. Add spring-boot-starter-jdbc back and the count goes to 1,415 and the key is claimed again. Same YAML file, one dependency apart, no log line either way."
  - question: "Do I need spring-boot-properties-migrator?"
    answer: "For a Boot 3 to Boot 4 migration, yes — it is the only thing that reports anything, and nothing adds it for you. No starter pulls it in, so an AI agent doing your upgrade will not add it unless you say so. It prints two kinds of report: WARN for keys it temporarily remapped (logging.file.max-size to logging.logback.rollingpolicy.max-file-size) and ERROR for keys it cannot remap because the replacement has a different type (spring.main.show-banner to spring.main.banner-mode, because boolean does not become Banner.Mode). Neither one fails the build, and it says nothing at all about keys that have vanished from metadata."
  - question: "How do I check what Spring Boot actually bound from my application.yml?"
    answer: "The actuator's configprops endpoint is the only real source of truth, because it reports the values bound onto @ConfigurationProperties beans rather than what might get bound. You have to enable it explicitly, which is awkward when management.endpoints.enabled-by-default is false: run with --management.endpoints.web.exposure.include=configprops --management.endpoint.configprops.enabled=true. Watch for map-based properties that swallow anything you give them — my keys turned up under datatype.datetime.WRITE_DATES_AS_TIMESTAMPS while json.write stayed empty, so a wrong key look like it went somewhere."
  - question: "Which Spring Boot 4 property change will actually break my build?"
    answer: "The Jackson ones. spring.jackson.serialization.write-dates-as-timestamps is fine on Boot 3.5.8 and stops the app dead on 4.1.1 with 'failed to convert java.lang.String to tools.jackson.databind.SerializationFeature (caused by No enum constant SerializationFeature.write-dates-as-timestamps)'. Jackson 3 turned those map values into typed enum keys, so the kebab-case name is now parsed as an enum constant name. That one is loud, which is a relief: after a day of quiet failures it was nice to see something refuse to start."
---

I gave Codex one job: move this project from Spring Boot 3.5.8 to 4.1.1, dependencies and configuration, and prove it still runs. It did that in three minutes. Rename-type work is the part [Codex is genuinely good at](/blog/codex-spring-boot/) on a JVM project, which is exactly why I stopped auditing it — right up until this run. It edited the pom, renamed five property keys in `application.yml`, deleted one it decided I did not need, and reported BUILD SUCCESS with the app started.

Then I did what I always do now, which is refuse to believe any of it until I have measured it myself. I wrote a ~120-line auditor that answers one question: of every key in `application.yml`, which ones does anything on this classpath actually claim? The answer changed what I think this migration is about.

This is one Codex run, so treat the migration behaviour as a case study. Everything else below is deterministic and reproducible on any machine — a version bump with the YAML left byte-for-byte untouched.

## The honest ledger

The starting file had 17 keys. Eight of them need attention in Boot 4. Here is what happened to each, verified by me afterwards rather than read out of the agent's summary:

| Boot 3 key | What Codex did | Verdict |
|---|---|---|
| `spring.main.show-banner` | → `spring.main.banner-mode: off` | correct |
| `logging.file.max-size` | → `logging.logback.rollingpolicy.max-file-size` | correct |
| `logging.file.total-size-cap` | → `logging.logback.rollingpolicy.total-size-cap` | correct |
| `logging.file.clean-history-on-start` | → `logging.logback.rollingpolicy.clean-history-on-start` | correct |
| `server.max-http-header-size` | → `server.max-http-request-header-size` | correct |
| `management.endpoints.enabled-by-default` | left alone | still worked |
| `management.endpoint.health.enabled` | left alone | still worked |
| `management.endpoint.env.enabled` | left alone | still worked |

Five right, three missed, zero failures. It also deleted `spring.datasource.hikari.maxLifetime` with the explanation that "no datasource stack exists in this app", and rewrote my Jackson key into `spring.jackson.datatype.datetime.write-dates-as-timestamps`, a path I have never seen in any guide.

I expected the three misses to be my article. They weren't, and here is the proof:

```text
management.endpoints.enabled-by-default: false   # pretend every endpoint is off
management.endpoint.health.enabled: true         # except health
management.endpoint.env.enabled: true            # and env

GET /actuator/health -> 200
GET /actuator/env    -> 200
GET /actuator/beans  -> 404
```

`beans` returns 404, so the blanket switch is definitely still binding. `health` and `env` return 200, so their per-endpoint overrides are definitely still binding too. **Both of those keys are marked "supported" nowhere in Spring Boot 4.1.1's configuration metadata.** They work perfectly. The framework pulled this quiet switch on me — the opposite of the [loud 403 an AI agent trips over in the same upgrade](/blog/codex-spring-boot-4-403-fix/), where at least the failure announces itself.

So the migration guides that tell you old keys "will be ignored silently" are wrong on 4.1.1. Something more interesting is true.

## The number nobody publishes: your metadata shrank by 60%

My auditor counts every property advertised by every `spring-configuration-metadata.json` on the classpath:

- Boot 3.5.8: **2,936** properties known
- Boot 4.1.1 after the migration: **1,161**

That 60% drop is not missing configuration. It is Boot 4's modularisation doing exactly what it set out to do: the giant `spring-boot-autoconfigure` jar was split into focused per-technology modules, and each module carries only its own metadata. Configuration metadata now travels with the jar that owns it.

Which means the set of properties your tooling can see is a function of your dependency tree. This is the same structural shift behind [the dependency additions that built green and wired nothing](/blog/codex-spring-boot-4-dependencies-silent-failures/) — there it was auto-configuration classes missing from the classpath, here it is their property definitions. Same cause, different symptom, and this one reaches into your IDE. Those yellow squiggles under an unrecognised key come from that metadata. Get 60% less of it and you get 60% less of the safety net, and no notification that the net moved.

## Tool 1: properties-migrator, and the three things it cannot say

`spring-boot-properties-migrator` is the only thing in the whole toolchain that talks about your configuration at all. It is also a dependency you must add yourself. No starter brings it. An agent doing your upgrade will not add it, because nothing told the agent it exists, and the official guidance is to **remove it again once you are done** — so the safety equipment for the most dangerous part of a major upgrade is deliberately temporary and deliberately absent by default.

I added it to a project with the Boot 3 YAML untouched. Two reports came out:

```text
WARN  PropertiesMigrationListener : The use of configuration keys that have been renamed
  Key: logging.file.clean-history-on-start
    Replacement: logging.logback.rollingpolicy.clean-history-on-start
  Key: logging.file.max-size
    Replacement: logging.logback.rollingpolicy.max-file-size
  Key: logging.file.total-size-cap
    Replacement: logging.logback.rollingpolicy.total-size-cap
  Each configuration key has been temporarily mapped to its replacement for your convenience.

ERROR PropertiesMigrationListener : The use of configuration keys that are no longer supported
  Key: management.endpoints.enabled-by-default
    Reason: Replacement key 'management.endpoints.access.default' uses an incompatible target type
  Key: server.max-http-header-size
    Reason: Replacement key 'server.max-http-request-header-size' uses an incompatible target type
  Key: spring.main.show-banner
    Reason: Replacement key 'spring.main.banner-mode' uses an incompatible target type

Please refer to the release notes or reference guide for potential alternatives.
```

Six keys reported, and note what it did about each of them. The WARN group it quietly remaps, so your app behaves as though you had migrated. The ERROR group — three keys whose new form is a different type, because `boolean` does not become `Banner.Mode` — it explicitly **refuses** to migrate, reports at ERROR level, and then starts your application anyway. Nothing exits non-zero. If you grep your CI logs for failures you will not see it, because there wasn't one.

And it said nothing about `management.endpoint.health.enabled` or `management.endpoint.env.enabled`, because there is no deprecation record left to find. The migrator can only report keys Spring still knows about. Keys that were removed from metadata entirely fall off its radar while continuing to work, which is precisely backwards from what you want.

## Tool 2: configprops is the only source of truth

The actuator's `configprops` endpoint reports what was bound onto actual `@ConfigurationProperties` beans, not what might get bound. Enabling it when you have disabled endpoints by default requires overriding two things:

```bash
java -jar target/yml-lab.jar \
  --management.endpoints.web.exposure.include=configprops \
  --management.endpoint.configprops.enabled=true
```

Then read it. When I looked at the Jackson properties bean, this is what the same key had turned into:

```json
"datatype": { "datetime": { "WRITE_DATES_AS_TIMESTAMPS": "******" } },
"json":     { "read": {}, "write": {} },
"write":    {}
```

My value landed in `datatype.datetime`. The place it was supposed to land, `json.write`, is empty. Nothing was dropped, nothing warned, and nothing took effect where I intended it to. Map-based properties absorb whatever you hand them, which makes `configprops` honest but not self-explanatory: you have to already know where to look to notice anything is wrong.

## Tool 3: scanning the classpath metadata yourself

Since I could not trust the migrator to be complete and could not trust the IDE to be informed, I wrote the check directly. It flattens `application.yml` into dotted keys, reads every `spring-configuration-metadata.json` on the classpath, and sorts each key into three buckets — bound verbatim, suspect (only a parent prefix exists), and not claimed by anything:

```java
Set<String> declared = readDeclaredKeys();      // application.yml, flattened
Set<String> known    = readKnownProperties();   // every spring-configuration-metadata.json

for (String key : declared) {
    if (findExactOwner(key, known) != null)      claimed++;
    else if (findContainerOwner(key, known) != null) suspect++;
    else                                          dead++;
}
```

Two details matter if you write your own:

1. **Relax before you compare.** Drop `-` and `_` and lowercase, keep the dot hierarchy. Otherwise `maxLifetime` never matches the `max-lifetime` advertised in metadata and everything looks dead.
2. **Suspect does not mean broken.** `spring.jackson.serialization.write-dates-as-timestamps` is only "suspect" even on Boot 3.5.8 where it demonstrably works, because those are map-based entries that accept arbitrary children. My three-stage output exists because a two-stage bound/dead split produced a lie.

Its headline result across 17 keys was one genuinely unclaimed key, and that was the interesting one.

## The one key that really died depended on my POM, not on Spring

`spring.datasource.hikari.maxLifetime` came back as **not claimed by anything**. Not deprecated. Not renamed. Just unclaimed, in a project with no JDBC starter.

| Project state | Properties advertised | `hikari.maxLifetime` |
|---|---|---|
| Boot 3.5.8, no JDBC starter | 2,936 | claimed |
| Boot 4.1.1, no JDBC starter | 1,161 | **unclaimed** |
| Boot 4.1.1, + `spring-boot-starter-jdbc` | 1,415 | claimed |

Same YAML. One dependency apart. Add the starter and 254 properties reappear and the key has an owner again; remove it and the key becomes an inert string sitting in your configuration file, read by nobody, complained about by nobody. On Boot 3 it was claimed even without a JDBC starter because one enormous jar advertised everything whether or not it could bind it.

This is the failure mode that actually deserves to be called silent, and it is triggered by dependency edits — exactly what an agent does during an upgrade, and exactly what it cannot see the configuration consequences of. Codex removed my Hikari key for the opposite reason, deciding there was no datasource stack to configure. One of those moves is right and one leaves a dead key, and they are separated only by whether your starter list is truthful.

## The one that failed loudly was not the one I expected

`spring.jackson.serialization.write-dates-as-timestamps: true` works on 3.5.8 — I verified it by serialising a `LocalDateTime` and getting `[2026,9,28,10,30]`. On 4.1.1 it refuses to start:

```text
Reason: failed to convert java.lang.String to
        tools.jackson.databind.SerializationFeature
        (caused by java.lang.IllegalArgumentException:
         No enum constant SerializationFeature.write-dates-as-timestamps)

Action:
Update your application's configuration. The following values are valid:
    APPLY_JSON_INCLUDE_FOR_CONTAINERS
    CLOSE_CLOSEABLE
    WRITE_CHAR_ARRAYS_AS_JSON_ARRAYS
    ...
```

Jackson 3 made those map values typed enum keys, so your kebab-case name is now parsed as an enum constant name, and an unknown constant is a startup failure. Interestingly, the odd path Codex invented — `spring.jackson.datatype.datetime.write-dates-as-timestamps` —**does** work on 4.1.1; I fed it `true` and got `[2026,9,28,10,30]` back. It found something real that I would have dismissed as a hallucination, which is a fair summary of working with these things: I don't trust its answers, and I check them, and sometimes they're right for reasons neither of us could articulate.

So of everything in that file, the key that broke the build was the one I had mentally filed under "probably fine", and the keys I was worried about worked throughout. If you want more of this pattern — the boring-looking thing that turns out to be load-bearing — the [full migration overview](/blog/spring-boot-4-migration-ai-agents/) has the rest of the traps, and the [Java + AI hub](/blog/ai-for-java-developers/) collects every measurement in this series.

## What I do now

Three habits, in order of how much they bought me:

1. **Add the migrator during the upgrade and read its whole report.** Treat the ERROR block as work you must do by hand, because Boot just told you it cannot do it for you. Remove the dependency when you are done.
2. **Check `configprops` once per migration**, ideally with the old and new builds side by side, and diff what actually got bound rather than what you wrote.
3. **Audit keys against the classpath, not against documentation.** A property's existence is a dependency-tree fact now. Re-run the check after any dependency edit, not only after version bumps.

And the reciprocity lesson from this series holds: an `AGENTS.md` line telling the agent to add `spring-boot-properties-migrator` costs nothing and probably helps, but remember it only steers the agent towards evidence already in the repository. Evidence that lives in your jar files is not in the repository, which is why none of it reaches the model.

Every measurement here came out of the same instinct: the build was green, the startup log was clean, and I still went looking. The parallel cases — a [green CI build](/blog/codex-ci-spring-boot-green-build/) whose tests said nothing, and [dependencies that resolve and wire nothing](/blog/codex-spring-boot-4-dependencies-silent-failures/) — are the reason I don't accept "it builds" as an answer any more.

## The three diagnostics, side by side

| Tool | Sees | Misses |
|---|---|---|
| Compiler / Maven | nothing | everything |
| `properties-migrator` | keys with a deprecation record; splits into auto-remapped vs incompatible-type | keys removed from metadata; keys whose owning module is not on the classpath |
| Classpath metadata scan | every advertised property name | map-based children; keys that work but are no longer advertised |
| `configprops` | what was actually bound, with values | needs explicit enabling, and you must know where the value ended up |
