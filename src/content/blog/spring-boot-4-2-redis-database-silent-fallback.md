---
title: "Spring Boot 4.2 Redis: Why database=5 Really Meant db0 (2026)"
description: "On Spring Boot 4.1.2, spring.data.redis.database=5 binds correctly, but master/replica connections are built for db0. I ran 12 cases against 4.2.0-RC2."
pubDate: 2026-11-09
category: "spring-boot-4"
tags: ["spring boot 4", "redis", "configuration properties", "ai coding agents", "java-ai-cluster", "maven"]
image: "/og-spring-boot-4-2-redis-database.jpg"
imageAlt: "Spring Boot 4.2 Redis database mismatch: config says db5, connection factory uses db0"
keywords: ["spring boot 4.2 redis database", "spring.data.redis.database ignored", "masterreplica.nodes database 0", "spring boot 4.2 redis cache empty", "spring.data.redis.url database", "redis CLIENT INFO db", "spring boot 4.1.2 vs 4.2.0-RC2"]
updatedDate: 2026-11-09
faq:
  - question: "Does Spring Boot 4.2 GA include the Redis master/replica database fix?"
    answer: "I measured 4.2.0-RC2, published on November 6, 2026. The 4.2 GA had not shipped when I ran the lab. The fix is listed in the RC2 release notes, so it is expected in GA, but re-run the probe against the exact build you deploy before relying on these numbers."
  - question: "Was spring.data.redis.database ignored for every Redis topology?"
    answer: "No. Only when spring.data.redis.masterreplica.nodes was set. Standalone and Sentinel already applied the configured database. My standalone control returned database 5 on both 4.1.2 and 4.2.0-RC2, which is what isolates the problem to the master/replica assembly branch."
  - question: "Does spring.data.redis.url switch the topology to standalone when masterreplica.nodes is present?"
    answer: "No. In all four URL cases the connection factory was still RedisStaticMasterReplicaConfiguration. The URL only supplies the database value that the RC2 fix now applies; it does not replace the node list."
  - question: "Why did Spring Boot not log a warning about the ignored database?"
    answer: "There is no check for 'a bound value that a downstream component forgot to use'. The property binds successfully, the context refreshes, and Lettuce connects lazily. My two silent-case checks confirmed that no warning or error line mentioned a database at all."
  - question: "What should I do before upgrading a master/replica app to 4.2?"
    answer: "Find out which database the running connection actually uses, not which one the file declares. Ask Redis with CLIENT INFO and read the db= field, or assert the connection factory's configured database in a test. Then either keep the intended database and plan for existing keys in db0, or set the value to 0 explicitly."
  - question: "Can I reproduce these results myself?"
    answer: "Yes. The probe source and twelve sanitized logs are in the boot42-redis-database-lab directory of my verification repository. On JDK 17 or later, bash verify.sh builds both parents and prints checks passed: 44 failed: 0. No Redis server or Docker is needed."
---

I was reviewing a service before moving it from Spring Boot 4.1.2 to the 4.2 line, and this was the whole Redis section of its configuration:

```yaml
spring:
  data:
    redis:
      masterreplica:
        nodes: redis-a.internal:6379,redis-b.internal:6379
      database: 5
```

Ask which Redis database that application writes to, and every static source agrees on five. The key is spelled correctly. It binds to the integer `5`. The IDE shows no yellow line. A tool asked to summarise the configuration will report `database: 5`, because that is what the file says and the file is all it can see.

On Spring Boot 4.1.2, the connection factory was built for database `0`.

There was no crash and no warning. The application started, the Redis client was created lazily, the process exited zero, and not one log line mentioned a database. I found the mismatch only after I stopped asking what the configuration says and started asking what the connection was built with. Those are different questions, and the space between them is where a whole family of upgrade problems lives.

## What the release notes already say

I want to be precise about attribution, because it would be easy to present the paragraphs above as a discovery. They are not.

The [Spring Boot 4.2.0-RC2 release notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2.0-RC2-Release-Notes) state it plainly in the upgrading section: previously, the database configured with `spring.data.redis.database` — or in `spring.data.redis.url` — was silently ignored when `spring.data.redis.masterreplica.nodes` was set, and the connection factory always used database 0. From RC2 onward it is applied, as it already was for standalone and Sentinel setups. The [RC2 announcement](https://spring.io/blog/2026/11/06/spring-boot-4-2-0-RC2-available-now) lists it among the two notable changes in the release.

The notes also go further than most release notes bother to. They warn that an application which sets a database together with master/replica nodes will now read from and write to that database instead of database 0, and they give the remedy: remove the property, remove the database segment from the URL, or set the value to `0` explicitly. [PR #52189](https://github.com/spring-projects/spring-boot/pull/52189) is the fix. Its own description records a check against a real Redis 8.6.2 master and replica: with `database=1`, a key written through the auto-configured `StringRedisTemplate` landed in database 0 before the change and in database 1 afterwards. There is also a [Chinese hands-on comparison](https://spring4all.com/archives/spring-boot-420-rc2-redis-masterreplica-database), published two days after RC2, that runs RC1 against RC2 with a real master and replica and verifies the key with `redis-cli -n`.

So the behaviour change, the consequence on upgrade day, the affected property spellings, and the fix are all documented. I found none of them. Claiming otherwise would be dishonest, and it would also make the useful part of this article harder to see.

The question I actually wanted to answer is narrower: what does this mismatch look like from inside the process, which configurations does it cover, and why does a tool that reads a repository have no chance of catching it? The published comparisons start from RC1, which is a release candidate almost nobody upgrades *from*. My starting point is 4.1.2, the stable line most teams would actually be on. I also wanted the URL spelling, which the hands-on comparison explicitly leaves out of its runs, and I wanted a measurement that does not require a running Redis server at all. That last constraint turned out to be the interesting one.

## Twelve runs, two pinned parents

I wrote one small Java probe and compiled the same source twice — once against `spring-boot-starter-parent:4.1.2`, once against `4.2.0-RC2`. Both builds use `spring-boot-starter-data-redis`, Amazon Corretto 17.0.19 and Maven 3.9.11. Redis configuration is passed entirely on the command line, one fresh JVM per case.

The probe injects the auto-configured `RedisConnectionFactory`, reads its `configuration` field reflectively, and calls `getDatabase()` on the resulting `RedisConfiguration`. Reflection keeps one source file compiling against two parents whose internal APIs differ. It also prints the raw values from the `Environment`, so each run reports two numbers: what the configuration says, and what the factory was built with.

```text
PROBE case=02-412-masterreplica-db5 boot=4.1.2
PROBE source.property.database=5 source.url=absent source.nodes=2
PROBE factory.type=RedisStaticMasterReplicaConfiguration factory.database=0
PROBE assert expected=0 result=PASS
```

No Redis server is contacted. Lettuce creates its client lazily during `afterPropertiesSet()`, so the context starts and closes without opening a socket. That is worth underlining: a green startup here proves nothing about reachability, and the missing socket is exactly why nobody notices the wrong number.

Here is the complete table. `Factory DB` is the value the connection factory would use when it eventually selects a database.

| Case | Boot | Configuration | Factory type | Factory DB |
| --- | --- | --- | --- | ---: |
| 01 | 4.1.2 | standalone, `database=5` | `RedisStandaloneConfiguration` | **5** |
| 02 | 4.1.2 | master/replica, `database=5` | `RedisStaticMasterReplicaConfiguration` | **0** |
| 03 | 4.1.2 | master/replica, `database=0` | `RedisStaticMasterReplicaConfiguration` | 0 |
| 04 | 4.1.2 | master/replica, `url=.../5` | `RedisStaticMasterReplicaConfiguration` | **0** |
| 05 | 4.1.2 | master/replica, `url=.../0` | `RedisStaticMasterReplicaConfiguration` | 0 |
| 06 | 4.1.2 | master/replica, no database | `RedisStaticMasterReplicaConfiguration` | 0 |
| 07 | 4.2.0-RC2 | standalone, `database=5` | `RedisStandaloneConfiguration` | **5** |
| 08 | 4.2.0-RC2 | master/replica, `database=5` | `RedisStaticMasterReplicaConfiguration` | **5** |
| 09 | 4.2.0-RC2 | master/replica, `database=0` | `RedisStaticMasterReplicaConfiguration` | 0 |
| 10 | 4.2.0-RC2 | master/replica, `url=.../5` | `RedisStaticMasterReplicaConfiguration` | **5** |
| 11 | 4.2.0-RC2 | master/replica, `url=.../0` | `RedisStaticMasterReplicaConfiguration` | 0 |
| 12 | 4.2.0-RC2 | master/replica, no database | `RedisStaticMasterReplicaConfiguration` | 0 |

Three things fall out of the table.

First, the standalone control returns `5` on **both** versions. The difference is not in Lettuce, not in the property binder, not in the JDK, and not in Redis itself. It is in the one branch that assembles a static master/replica configuration. That matters when you are deciding what to retest after an upgrade: a standalone development profile will never show you this bug, even on the affected version.

Second, cases 04 and 10 settle the URL question. With `spring.data.redis.url=redis://127.0.0.1:6379/5` *and* `masterreplica.nodes` set, the factory is still a `RedisStaticMasterReplicaConfiguration`. The URL does not switch the topology to standalone; it only supplies the database value that RC2 now applies. On 4.1.2 that value is discarded just as the property form is. So "we use the URL spelling" is not a workaround.

Third, cases 02 and 08 are the same configuration on two versions, and the only difference is the number the factory carries. Two of the 44 checks in the verification script are dedicated to confirming that neither run emits a warning or error line containing the word "database". Both pass. The upgrade changes behaviour without changing a single character of configuration, and without producing a line of output about it.

## The first run of this lab was wrong in every row

I should describe a mistake I made, because it has the same shape as the bug.

My first `application.properties` still contained `masterreplica.nodes` and `database=5` from an earlier spike. Every case then reported `source.property.database=5` and `RedisStaticMasterReplicaConfiguration` — including the standalone controls, which is impossible. All twelve rows were wrong in the same direction, and they were wrong quietly: the probe printed plausible output and exited zero. I only caught it because I had included a control whose answer I already knew.

The fix was to reduce the base file to four harmless lines, pass every Redis property on the command line, and force `clean package` on both builds. A stale `application.properties` under `target/<version>/classes` overrides the command line in exactly the same way a stale assumption overrides a configuration review. This is the second time a lab of mine has produced a uniformly wrong table because of a leftover file, so it is now a rule rather than a note: if a matrix has no control row, I do not trust the matrix.

## Why a repository-reading tool cannot see this

I did not run a coding agent as part of this lab, so I am not going to quote one or invent a success rate. The argument here is structural, and it follows from the table.

Everything a code-reading tool can reach sits on one side of the boundary: the YAML file, the bound `RedisProperties` object, an `/actuator/configprops` response, a grep for the key across the repository, the release notes. All of those say `5` in case 02. The only thing that says `0` is a runtime object assembled inside Spring Boot's auto-configuration, and it is invisible until you execute the application and inspect it. There is no diff to review. There is no compiler error, no deprecation warning, no metadata gap, and no failing test — because nobody wrote a test that asks the connection which database it intends to use.

That is the same split I measured in the [Spring Boot 4 YAML audit](/blog/codex-spring-boot-4-yml-properties/): a key can exist in metadata, bind cleanly, and still have no consumer on the classpath. It is also the same split as [resolved versus configured dependencies](/blog/codex-spring-boot-4-dependencies-silent-failures/), where the artifact is on the classpath but no auto-configuration ever activates it. In all three cases the failure is not a wrong value in a file. It is a value that never reaches the component that acts on it.

The practical consequence for AI-assisted upgrades is about the *instruction*, not the model. "Check the Redis configuration" is a request to read, and reading returns 5. "Show me the run where the connection reports which database it selected, and make the build fail if it is not 5" is a request for an artifact, and it returns 0. The first sounds like verification and is not. The second is verifiable because it can fail. That distinction is the whole reason I keep a [hub of verification-first walkthroughs](/blog/ai-for-java-developers/) rather than a list of useful prompts, and it is the same discipline behind the [Codex Spring Boot guide](/blog/codex-spring-boot/).

The [4.2 properties migrator](/blog/spring-boot-4-2-properties-migrator-silent-gaps/) is worth naming as a contrast. It is a genuine improvement: it can stop the process on renamed and removed keys. But it compares keys, not values that were assembled into objects. A correctly spelled, correctly bound, correctly documented `database=5` is not a key problem. No migrator will ever flag it.

## What changes on upgrade day

The release notes already say the important part: your application will now read from and write to the configured database instead of database 0, and nothing moves your existing keys for you.

What that looks like in practice is quieter than "the cache broke". Suppose the service has been running on 4.1.2 for a year with `database=5` in the file and all its keys in db0. After the upgrade, reads go to db5. Every lookup misses. The cache does its job — it falls through to the database and repopulates — so latency rises, no exception is thrown, and no alert fires if you were not watching hit rate. Meanwhile db0 still holds the old keys, and db5 starts accumulating new ones. Two logical databases now contain different versions of the same key space. If you roll back, you are back in db0 with the old values, which can look like the rollback fixed it.

None of that appears in the application log, because from Boot's point of view nothing went wrong. The property was always 5. Nothing was renamed, removed, or rejected. The only change is that a value which used to be dropped is now passed on.

This is why I think of it as a behaviour change wearing the clothes of a bug fix. A compiler catches a renamed class immediately. This kind of change is only visible as different behaviour at runtime, and the version bump is the trigger. It belongs on the same list as the security, persistence and JSON contracts in a migration plan, not in the "dependency updates" column.

## How I check before an upgrade

The check has to end at the connection, not the file. In order of how much I trust them:

1. **Ask the running connection.** Execute `CLIENT INFO` through the same `RedisConnection` the application uses and parse the `db=` field. The [Redis command reference](https://redis.io/docs/latest/commands/client-info/) documents the field. A `redis-cli` session you opened yourself is a different connection and does not prove anything about the application.
2. **Assert the assembled value.** If you cannot reach a Redis server from the test, inject the `RedisConnectionFactory` and assert the database on its `RedisConfiguration`. That is what my probe does. It is weaker than step 1 — it proves what the client was built with, not what a server received — but it needs no infrastructure and it fails loudly.
3. **Keep a control case.** A standalone profile with the same `database=5` should always report 5. If your matrix has no row whose answer you know in advance, a stale config file can make every row wrong in the same direction, as happened to me.
4. **Decide the value explicitly.** If you were relying on db0, set `spring.data.redis.database=0` (or remove the URL segment) before the upgrade. Do not leave a nonzero value in the file and assume it is inert. If you intended db5 all along, plan for the keys that are still in db0.
5. **Phrase agent instructions as runnable checks.** Ask for the command and its output, and require the check to fail when the answer is wrong. "Show me the run where the connection reports db5" is verifiable. "Make sure Redis is configured correctly" is not.

The official [4.2 reference documentation for connecting to Redis](https://docs.spring.io/spring-boot/4.2/reference/data/nosql.html) is where the topology options and the Jedis limitation live: master/replica connections are not supported by Jedis. That is useful context for the upgrade decision, but note that it does not describe the database application behaviour at all — the RC2 release notes are the authority for that.

## Reproduce it, and what it does not prove

The probe source, both pinned parents, the verification script and twelve sanitized startup logs live in the `boot42-redis-database-lab` directory of my [verification repository](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/boot42-redis-database-lab).

```bash
git clone https://github.com/zhoupeng20188/ai-kit-guides-verification-labs
cd ai-kit-guides-verification-labs/boot42-redis-database-lab
export JAVA_HOME=/path/to/your/jdk-17
bash verify.sh
```

The script builds the same source twice, starts twelve fresh JVMs, checks exit codes, the probe assertions, the factory type and the factory database, verifies that the two silent cases log nothing about a database, and writes sanitized logs. A clean run ends with:

```text
  checks passed: 44   failed: 0
  all cases match the recorded behaviour
```

The boundaries matter as much as the numbers. This lab never contacts a Redis server, never issues `SELECT`, never writes a key, and never runs `CLIENT INFO`. It proves what the connection factory was **constructed with**; the server-side confirmation comes from the upstream PR linked above. It does not measure cache hit rates or production behaviour, does not cover Sentinel, Cluster, or Jedis, and uses one JDK, one client and one pair of Boot versions. It does not benchmark any coding agent, and no agent was run to produce it. `4.2.0-RC2` is a release candidate — re-run the matrix against the GA you actually deploy.

If there is one habit worth taking from this, it is the one that caught my own broken first run: when a configuration value matters, find the object that acts on it and ask that object what it received. The file will always tell you what you meant. It will not always tell you what happened.
