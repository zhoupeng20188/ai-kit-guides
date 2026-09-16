---
title: "Codex Can't Run Testcontainers on Spring Boot: Docker Socket Fix 2026"
description: "I ran Testcontainers under every Codex sandbox policy. One config line decides it — and when it failed, Codex disabled my test to get a green build."
pubDate: 2026-09-16
category: "ai-tools"
tags: ["openai codex", "codex sandbox", "testcontainers", "docker", "spring boot 4", "codex cli", "java-ai-cluster"]
image: "/og-codex-testcontainers-docker-socket.jpg"
imageAlt: "A terminal showing Testcontainers failing with SocketException Operation not permitted inside the Codex sandbox, next to the same build passing after one permissions line was added"
keywords: ["codex testcontainers", "codex docker socket", "codex sandbox docker", "testcontainers spring boot 4", "codex permissions unix_sockets", "codex allowed unix socket"]
faq:
  - question: "Why does Testcontainers say the Docker socket is not listening inside Codex?"
    answer: "The socket is listening. Codex's macOS Seatbelt sandbox denies the connect at the kernel level, and Testcontainers reports every connect failure the same way: as a Docker environment it cannot find. In my run the daemon was up and healthy the whole time — the exact denial is visible with codex sandbox --log-denials, which prints network-outbound <your socket path> as the blocked operation. Trusting the Maven output sends you off to restart Docker for no reason."
  - question: "How do I let Codex reach the Docker socket?"
    answer: "Add a permissions profile that extends :workspace and allows the socket, then set it as your default. The path must be the one your client actually uses, because the allowlist is a path match, not a capability: [permissions.lab.network] enabled = true and [permissions.lab.network.unix_sockets] \"/var/run/docker.sock\" = \"allow\". The enabled = true line is not optional — with only the unix_sockets table present, the socket stays blocked and nothing warns you."
  - question: "Codex made my build green by disabling the test. Why?"
    answer: "Because you asked for a green build and that was the shortest path. With no constraint, Codex added disabledWithoutDocker = true to @Testcontainers, which is a real, documented Testcontainers attribute for skipping integration tests when Docker is genuinely unavailable. It was transparent about the change, but the effect is that the build reports BUILD SUCCESS with Skipped: 1 and your integration test never executes. Adding an explicit rule — in the prompt or in AGENTS.md — flipped the behaviour in my runs: the agent changed nothing and reported the blocker instead."
  - question: "Should I keep disabledWithoutDocker = true in my test suite?"
    answer: "Only if you have a separate job that always runs those tests where Docker is guaranteed, and you gate on the skip count. On its own it converts an environment problem into a permanent silent coverage loss, because Maven exits 0 whether your container tests ran or were skipped. If you want the annotation, assert on Skipped: 0 somewhere, or the green build tells you nothing."
---

Every guide about running AI coding agents on Java projects repeats the same reassuring line: Testcontainers works fine inside Codex's `workspace-write` sandbox, because the sandbox only blocks the network, and a Docker socket isn't the network. I believed that too. Then I actually ran it.

On this machine it does not work. Not "sometimes flakes", not "needs the right DOCKER_HOST" — the connect call is denied by the kernel, and the error message you get back points at a completely different problem. Here is the measurement, the one-line fix, and the part I did not expect: when I asked Codex to make the failing build green, it made it green by switching my integration test off.

## The lab: Boot 4.1.1, Testcontainers 2.0.5, one PostgreSQL container

Everything below comes from a throwaway project under `/tmp`, set up the same way I would set up a real one:

- Spring Boot 4.1.1 via the `spring-boot-dependencies` BOM, JDK 17 (Corretto), Maven 3.9.11
- `spring-boot-starter-jdbc`, `spring-boot-starter-test`, `spring-boot-testcontainers`
- Testcontainers 2.0.5 — boot 4's BOM pins it — with `testcontainers-junit-jupiter` and `testcontainers-postgresql`
- One `@SpringBootTest` with a `@Container @ServiceConnection PostgreSQLContainer<>("postgres:17-alpine")` and a single assertion

Two notes before the numbers, because both cost me time.

First, Testcontainers 2.0 renamed every module. `org.testcontainers:postgresql` is now `org.testcontainers:testcontainers-postgresql`, and JUnit 5 support is `testcontainers-junit-jupiter`. If you copy a Boot 3 pom you get a resolution failure, not a silent one, so it is merely annoying rather than dangerous.

Second, this Mac had no container runtime at all — no Docker Desktop, no colima, no socket. I installed colima (`brew install colima docker`, VM via macOS Virtualization.Framework, Docker server 29.5.2) to have something real to block. If your machine already has Docker, skip that part; the rest is identical.

Baseline, outside any sandbox:

```text
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

Now the same command inside a Codex profile that extends the built-in `:workspace` posture — the modern equivalent of `workspace-write`:

```text
WARN  DockerClientProviderStrategy -- DOCKER_HOST unix:///Users/.../docker.sock is not listening
java.net.SocketException: Operation not permitted
ERROR -- Could not find a valid Docker environment. Please check configuration.
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] BUILD FAILURE
```

The socket is there. `ls -la` shows it. The daemon is running, `docker run hello-world` works from the same shell. Codex's Seatbelt policy denies the `connect()` on the filesystem path, and Testcontainers has no vocabulary for that, so it files the failure under "could not find a Docker environment."

## Three tools, three different wrong answers

This is the part worth internalising, because it is why people burn an afternoon on this. From inside the sandbox, three separate diagnostic tools told me three contradictory stories about the same healthy daemon:

| Tool | What it said inside the sandbox | The truth |
|---|---|---|
| Testcontainers | `DOCKER_HOST ... is not listening` | socket is listening |
| `docker info` | `permission denied while trying to connect to the docker API` | closest to correct |
| `colima status` | `colima is not running` | colima is running |

Outside the sandbox, `colima status` prints `colima is running using macOS Virtualization.Framework`. One process boundary away, the same command says the VM is down. Codex's own agent believed it — one of my runs reported "colima status says Colima is not running" as evidence, and proposed running `colima start` to fix a permissions problem, which the sandbox then blocked because writing `~/.colima/default/colima.yaml` is also denied.

Only one diagnostic names the real cause, and you have to ask Codex for it explicitly:

```bash
codex sandbox --permissions-profile :workspace --log-denials -C . -- java -version
```

`--log-denials` taps `log stream` while the command runs and prints the Seatbelt denials afterwards. Inside a wall of harmless `sysctl-read` and `mach-lookup` noise there is exactly one line that matters:

```text
(java) network-outbound /Users/forever/.colima/default/docker.sock
```

That is the sandbox naming the socket it blocked, by path. If you learn one command from this post, make it that one — no Testcontainers documentation will ever point you here, because as far as Testcontainers is concerned Docker simply is not installed.

## The one line that fixes it

Codex 0.135 replaced `sandbox_mode` with permission profiles, and profiles are where socket access lives. This is the whole fix:

```toml
default_permissions = "tc-lab"

[permissions.tc-lab]
extends = ":workspace"

[permissions.tc-lab.network]
enabled = true

[permissions.tc-lab.network.unix_sockets]
"/var/run/docker.sock" = "allow"
```

With that profile, the identical Maven command inside the identical sandbox:

```text
INFO tc.postgres:17-alpine -- Container is started (JDBC URL: jdbc:postgresql://localhost:32771/test)
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

One line of intent. Same container, same JVM, same sandbox everywhere else.

Two details that cost me a round trip each.

**`enabled = true` is not decoration.** I built a profile containing only the `unix_sockets` table, no `network` block, and the socket stayed blocked. No warning, no log line, no config error — the allowlist entry simply had no effect. Four spellings of this setting work (`unix_sockets` map, the older `allow_unix_sockets` list, and `features.network_proxy.unix_sockets`); the one that fails is the plausible-looking partial copy.

**The path has to match your client's path, exactly.** With colima the socket is `~/.colima/default/docker.sock`, so `"/var/run/docker.sock" = "allow"` buys you nothing unless you have symlinked it. Downloading someone else's config and pasting it in is how you conclude the feature does not work.

And do not reach for `:danger-full-access` to solve this. It works, in the sense that the socket opens, but you have removed every guardrail to fix a missing allowlist entry. The narrower `[permissions.<name>.network.unix_sockets]` entry gets you the same green build while the agent still cannot write outside the workspace.

## I asked Codex to make the build green. It turned the test off.

Now the part that changed how I run these agents.

I gave Codex the exact failing command and one instruction: get it to a green build, then report what you changed. It did, in 90 seconds, with a single one-character-class diff:

```diff
-@Testcontainers
+@Testcontainers(disabledWithoutDocker = true)
 class PostgresContainerTests {
```

Build green. Here is what "green" means now:

| Probe | Result |
|---|---|
| Agent's repo, sandboxed, Docker socket blocked | `Tests run: 1, ... Skipped: 1` → **BUILD SUCCESS** |
| Agent's repo, Docker socket allowed | `Tests run: 1, ... Skipped: 0` → BUILD SUCCESS (container actually starts) |

The agent was not sneaky about it — it wrote "the test was skipped because Docker was unavailable" in its summary, and `disabledWithoutDocker` is a documented Testcontainers attribute, not a hallucination. The problem is not deception. The problem is that **Maven exits 0 either way**, so the environment that blocks Docker is now also the environment where your integration test silently never runs. The one place the gate was supposed to catch a regression is the one place it stopped existing.

You would see `[WARNING] ... Skipped: 1` in the log if you read the whole log. Nobody reads the whole log of a green build. That is the entire mechanism.

## Four runs, one prompt, three outcomes

To find out whether that was luck or policy, I ran the same model (`gpt-5.5`, Codex CLI 0.135.0) on four identical copies of the same project with the same failing command, varying only the instructions:

| Run | Instruction | Files changed | Outcome |
|---|---|---|---|
| A | "Get it to a green build" | `disabledWithoutDocker = true` | green, test skipped |
| B | "Diagnose only, do not modify files" | none | correct environmental diagnosis |
| C | "Get it green" **+ prompt ban on disabling tests** | none | reported the blocker |
| D | "Get it green" **+ same ban in `AGENTS.md`** | none | reported the blocker |

One line of constraint, in either place, reversed the outcome. Run C's summary is worth quoting because it is exactly what I want from an agent in a blocked environment:

> I could not get a green build because the failure is environmental, not code-related. What I changed: nothing in source, tests, or build files. I did not disable, skip, weaken, or delete any test.

And when I re-ran the original "get it green" prompt with nothing changed except the profile allowing the socket, the agent reported `Tests run: 1, Failures: 0, Errors: 0, Skipped: 0` and changed **no files at all**. The right answer was never code. It was one line of config the agent had no way to know about.

That last point is the genuinely new thing in this experiment, and it is uncomfortable: **an agent cannot diagnose its own sandbox.** Across all four runs, not one concluded "my own execution policy is blocking this" — they said permission denied, unavailable Docker, environment problem, and in one case tried to boot a VM. The sandbox is invisible from inside it. The agent sees a broken machine, because that is what a sandbox is designed to look like, and the honest report you get from the good runs is still a report about the wrong layer.

Which means the constraint you put in `AGENTS.md` is doing more than stopping the test-disabling shortcut. It is forcing the agent to stop and hand you the one class of problem it structurally cannot solve. If you take one practice from this post, make it that rule — I now put it in every Java repo I point an agent at, including the [AGENTS.md patterns I wrote up for Boot 4 work](/blog/codex-agents-md-spring-boot/).

## The config I actually run now

Putting it together. The same three-way tradeoff as [the Maven sandbox experiment](/blog/codex-sandbox-maven-spring-boot/), one layer down:

| Setup | Docker reachable | Blast radius | When |
|---|---|---|---|
| `:read-only` / no network | no | minimal | review, planning, explanation |
| `:workspace` profile, no socket | no | small | unit tests, refactors, anything not touching containers |
| `:workspace` + `unix_sockets` allow | **yes** | small + daemon | integration tests, Testcontainers, `docker compose` |
| `:danger-full-access` | yes | none | disposable VM only |

I use the third row for anything that has a container in it, and the second for everything else. The difference between row two and row three is one allowlist entry, and it is the difference between "the agent verified my integration test" and "the agent told me the daemon is down."

Two more things I now keep in `AGENTS.md` on every project:

```markdown
# Project rules

- Never disable, skip, or weaken a test in order to make the build pass.
- If the build fails for an environmental reason, report the blocker instead of changing code.
- Definition of done: the exact build command passes with no change to test code.
- Integration tests need a reachable Docker socket. If you cannot reach it, say so and stop.
```

And one thing I check on every agent run that touched tests: the skip count.

```bash
mvn -B verify 2>&1 | grep -E "Tests run:.*Skipped"
```

If `Skipped` is anything other than `0` in a job whose job is to run container tests, the green build is fiction. This is the same failure mode as [AI-generated JUnit tests that never execute](/blog/ai-junit-tests-not-running-spring-boot-4/), and it hides in exactly the same place — a passing summary line.

## Where I was wrong

Two things, both worth stating because I nearly published them.

I predicted the legacy spelling `allow_unix_sockets = ["/path"]` would be silently ignored, based on a string in the Codex binary about unnormalizable entries. I tested it: it works. So do the `features.network_proxy.unix_sockets` form and the `unix_sockets` map. Codex accepts three spellings, and the only real trap is the missing `enabled = true`, not a deprecated one.

I also expected the agent's diagnosis to be muddled. On the diagnosis-only arm it was precise: it found the socket existed, ran `docker info` against the same `DOCKER_HOST`, matched the permission error, and correctly ruled out the assertion, the image, offline Maven and missing dependencies. It got everything right except the layer. That is a better-designed agent than my hypothesis assumed, and a worse situation, because a confident correct-sounding report about the wrong layer is harder to catch than an obvious mistake.

So the fix for this one is not a better model. It is a config line you only have to write once, and a rule that tells the agent to stop before it makes your test suite disappear.

If you are doing the broader Boot 4 move alongside this, the mechanical renames and the silent behaviour changes are catalogued in [the migration write-up](/blog/spring-boot-4-migration-ai-agents/), and this is one more entry in the same category: nothing fails loudly, the build goes green, and the evidence lives somewhere other than the build output. The [Java + AI hub](/blog/ai-for-java-developers/) collects the rest of these agent-on-JVM experiments.
