---
title: "Codex Can't Run Maven on Spring Boot: Unknown Host Sandbox Fix (2026)"
description: "I ran one Spring Boot build under every Codex sandbox policy. Default failed, full-auto failed on a cold repo, only one setting let Maven download."
pubDate: 2026-09-07
category: "ai-tools"
tags: ["openai codex", "codex sandbox", "codex approval modes", "maven", "spring boot", "java-ai-cluster"]
image: "/og-codex-sandbox-maven-spring-boot.jpg"
imageAlt: "A terminal showing Maven failing with Unknown host maven.aliyun.com next to the Codex CLI header reading sandbox workspace-write with network access enabled"
keywords: ["codex maven", "codex sandbox maven", "codex full auto maven", "codex approval modes", "openai codex spring boot", "codex unknown host"]
faq:
  - question: "Why does Codex fail with Unknown host when running Maven?"
    answer: "Codex sandbox policies block network access by default. codex exec with no flags runs read-only with no network at all, and --full-auto writes files inside the workspace but still blocks outbound connections, so Maven cannot reach your repository mirror and every dependency resolution dies with Unknown host. The fix that keeps file isolation is -s workspace-write plus -c 'sandbox_workspace_write.network_access=true', which turns network on while the filesystem stays locked to your project directory."
  - question: "What is the difference between Codex approval modes and sandbox modes?"
    answer: "They are two independent axes. The approval policy decides whether Codex asks you before running a command; the sandbox mode decides what that command can touch. --full-auto is just a shortcut for the workspace-write sandbox plus approve-on-failure. Because the axes are independent, --add-dir can grant write access to a directory without granting any network, which is why adding your Maven repository directory alone does not fix a cold-cache build — the build dies on DNS, not on permissions."
  - question: "Does --full-auto work for Java projects?"
    answer: "Yes, with two conditions. Your local Maven repository must already contain every dependency the build needs, because --full-auto has no network to download anything new. And the project must compile on whatever JDK Codex inherits from your shell. In my experiment the warm-cache build passed under --full-auto once I pinned JAVA_HOME to JDK 17; the moment Maven needed one new artifact, the sandbox blocked it."
  - question: "How do I stop Codex from using the wrong JDK version?"
    answer: "Pin the JDK inside the build command itself, for example JAVA_HOME=/path/to/jdk-17 mvn -B test, and put that exact command in AGENTS.md as your definition of done. In my run, Codex inherited JAVA_HOME pointing at Corretto 8 from the login shell, and a Spring Boot 4 project using records failed with five syntax errors before any sandbox issue could even appear. My exported JAVA_HOME never made it into Codex's shell."
---

## I handed Codex a Maven build and watched it fail five different ways

After my last experiment, where an agent obeyed my CI rules so literally that it reverted a gate fix, I wanted to give OpenAI's Codex a bigger job: not just editing code, but actually building and testing a Spring Boot project on its own — the thing you need working before you even think about [a Codex-specific AGENTS.md](/blog/codex-agents-md-spring-boot/).

So I set up the simplest possible version of that job. One Maven project. One command: `mvn -B test`. One instruction: run it, tell me if it passes.

Five runs later, I had watched it fail five different ways — a filesystem permission error, a DNS failure, the same DNS failure again after I "fixed" permissions, and a compile error that had nothing to do with the sandbox at all. Only two settings made the build pass, and the one I now use daily was not `--full-auto` and definitely not the full-access mode everyone warns you about.

If you have ever run `codex exec` on a Java project and watched Maven die with `Unknown host` while your own terminal builds the same project fine, this is the full map of why.

## The lab: one project, one command, seven configurations

The project is the same little order service I used before: four layers, one controller, in-memory storage, Spring Boot 4.1.1 on Java 17, four tests, plus an ArchUnit ruleset that runs during the test phase. Green baseline, committed, reproducible.

The tool was codex-cli 0.135.0. One honest environment note: my local config defaults to a model called `gpt-6-astra`, which this CLI version is too old to use — the API rejects it and asks for an upgrade. I explicitly passed `-m gpt-5.5` for every run so all seven runs used the same model. If your default model works on your CLI version, nothing else in this article changes.

Two knobs I controlled so the results mean what they claim:

- **Warm vs cold Maven repository.** My real `~/.m2` has every dependency cached, which would let the build pass with no network at all and hide the sandbox behavior. To simulate a fresh machine or a CI runner, I pointed Maven at an empty repository with `-Dmaven.repo.local`. That forces real downloads and makes the network question unavoidable. This trick is worth stealing even outside this experiment — it is how you test whether a build is hermetic.
- **Proxy.** My network only reaches the Maven mirror (my settings.xml points Central at maven.aliyun.com) through a local proxy, so I pinned it in `MAVEN_OPTS`. That way, when a run failed with a network error, I knew it was the sandbox blocking traffic, not a missing proxy setting.

Then I ran the same prompt under every sandbox configuration Codex offers. Here is the full result table before we walk through it:

| Run | Codex configuration | Maven repo | Result | Actual failure |
|---|---|---|---|---|
| 1 | `codex exec` (defaults) | cold, outside workspace | ❌ | `Operation not permitted` — read-only sandbox |
| 2 | `--full-auto` | cold, inside workspace | ❌ | `Unknown host maven.aliyun.com` — no network |
| 3 | `--full-auto --add-dir <repo-dir>` | cold, outside workspace | ❌ | Same `Unknown host` — writes granted, network still off |
| 4 | `--full-auto` | warm `~/.m2` | ❌ | Wrong JDK — it picked up Corretto 8 |
| 5 | `--full-auto` + pinned `JAVA_HOME` | warm `~/.m2` | ✅ | 4 tests, 0 failures |
| 6 | `--sandbox danger-full-access` | cold, inside workspace | ✅ | 4 tests, 0 failures |
| 7 | `workspace-write` + network on | cold, inside workspace | ✅ | 4 tests, 0 failures |

Runs 5 and 7 both pass, but they are not equivalent — run 7 keeps the filesystem locked to the project while run 6 removes all isolation. That difference is the whole point of this article.

## First, two axes people keep confusing

Codex separates two decisions that most tools merge into one:

- **Approval policy** — does Codex ask you before it runs something? Values include `untrusted` (ask about anything not on a safe list), `on-failure` (run it, only ask when it fails), `on-request` (the model decides when to ask), and `never`.
- **Sandbox mode** — what can the command touch? `read-only` (no file writes, no network), `workspace-write` (writes inside the workspace only, network off by default), and `danger-full-access` (everything).

`--full-auto` is just a shortcut that combines one setting from each axis: the `workspace-write` sandbox plus `on-failure` approvals. That is why it feels confusing in practice — you flipped one flag but you are actually standing on two axes at once, and the build can fail on either one.

If you only remember one sentence from this article: **approval decides whether you get asked; sandbox decides whether the command can succeed.** A prompt-perfect agent with the wrong sandbox mode cannot run your build no matter how politely you ask it.

## Run 1: the default is read-only, and Maven never stood a chance

Plain `codex exec` with no flags prints its own configuration at startup, and this is what it said:

```
approval: never
sandbox: read-only
```

Read that twice. The non-interactive mode that everyone uses for scripting and CI defaults to a sandbox where the agent **cannot write a single file and cannot touch the network**. It is not conservative — it is inert. For "analyze this code and tell me things" that is a sensible default. For "run my build" it is a wall.

The failure was immediate and very concrete. Maven tried to create the local repository directory I pointed it at, and the filesystem refused:

```
java.nio.file.FileSystemException: /tmp/cold-m2/org: Operation not permitted
```

One detail worth noticing: the failure came from `/tmp`, not the project. `read-only` really means read-only everywhere. The agent reported this honestly — "the build failed before tests could run" — but no amount of re-prompting would have helped, because the constraint was never information, it was capability.

## Run 2: --full-auto grants writes, then cuts the network

This is the setting everyone uses, so expectations were high. `--full-auto` means `workspace-write`: the agent can edit files inside the project and run commands, asking only when a command fails.

I put the cold Maven repository **inside the workspace** this time (`./local-m2`), so writes were fully permitted. Compilation started, dependency resolution began, and then:

```
Unknown host maven.aliyun.com: nodename nor servname provided, or not known
```

That is the sandbox network cutoff talking. `workspace-write` blocks outbound connections by default, and DNS resolution is part of that. The build died before it produced a single class file.

Here is what makes this trap so good at catching people: the same `mvn -B test` succeeds in your own terminal seconds earlier, because your terminal has network. The agent sits in the same directory, runs the same command, and gets a different result. If you have never heard of the sandbox network default, this looks exactly like a broken DNS, a VPN glitch, or Maven being Maven — and you will waste an evening on the wrong suspect.

## Run 3: --add-dir fixes the permission, not the network

My next guess was the intuitive one: the repo directory is outside the workspace, so grant access to it explicitly with `--add-dir`. This is exactly what the flag exists for, and it worked — the `Operation not permitted` from run 1 was gone, the directory was writable.

And the build failed with the identical `Unknown host`.

This run is the cleanest demonstration of the two-axes point. `--add-dir` lives on the filesystem axis only. It extends *where the agent may write*; it does not touch *what the agent may reach*. Permissions were necessary but nowhere near sufficient, because the cold-repo build needs one thing `--add-dir` does not sell: packets.

If your mental model was "sandbox = a permissions system," run 3 is the correction. The network cutoff is not a missing permission you can grant with more directory flags — it is its own switch.

## The setting that actually works

Codex's sandbox has a configuration entry for exactly this case, and once I found it the fix was one flag:

```
codex exec -m gpt-5.5 \
  -s workspace-write \
  -c 'sandbox_workspace_write.network_access=true' \
  "Run this Maven build and report whether it passes: ..."
```

Cold repository inside the workspace, network on, filesystem still locked to the project. The build downloaded every dependency through the mirror, compiled, and finished:

```
BUILD SUCCESS — 4 tests run, 0 failures, 0 errors
```

This is the configuration I now consider the actual default for Java work: **workspace-write plus network, nothing more**. The agent keeps its blast radius — it can still only write inside the project — while Maven, Gradle, and wrapper downloads work the way they do in real life. A build tool that cannot reach a repository is not a safe build tool; it is a broken one.

Worth saying out loud: I verified this key is real by running Codex with `--strict-config`, which errors out on unknown configuration fields. If you mistype the key, `--strict-config` is how you find out instead of silently getting the default.

## Do you ever need danger-full-access?

For completeness I also ran the blunt instrument: `--sandbox danger-full-access`, which removes all filesystem and network restrictions. The cold-repo build passed, of course — unrestricted machines can download things.

But compare what each passing run actually bought:

| Passing run | File isolation | Network | Verdict |
|---|---|---|---|
| `--full-auto` + warm cache | ✅ workspace only | ❌ off | Works until you need one new dependency |
| `workspace-write` + network on | ✅ workspace only | ✅ on | The one I use now |
| `danger-full-access` | ❌ none | ✅ on | Only in a disposable container/VM |

The middle row dominates the bottom one for daily work. Full access exists for environments that are already isolated — a container, a VM, a throwaway CI runner — where the sandbox's job is done by something outside Codex. On a developer laptop, it is a sledgehammer that also smashes the guardrail you will want the day the model decides to `rm` something creative.

## The plot twist: the sandbox was never the only problem

One run in this experiment failed for a reason that had nothing to do with Codex's sandbox, and it is arguably the most Java-specific trap in the whole piece.

On the warm-cache run under `--full-auto`, Maven didn't fail on network or permissions — it failed with five compile errors in one file:

```
src/main/java/com/example/lab/domain/Order.java
error: 需要 class, interface 或 enum   (expected class, interface or enum)
```

Five errors, all in a file containing a Java `record`. Records need JDK 16+. The file was untouched and correct — the diff against the baseline was empty. What differed was the toolchain: inside Codex's shell, `mvn -version` reported:

```
Java version: 1.8.0_462, vendor: Amazon.com Inc.
```

I had exported `JAVA_HOME` to JDK 17 in the parent terminal. Codex did not inherit it — its shell picked up a different `JAVA_HOME` (Corretto 8) from the login environment, and Maven silently followed. The error message is the giveaway: the compiler isn't rejecting your code, it is reading `record` as an identifier because it is a Java 8 compiler.

This is exactly the failure mode I flagged in the [Spring Boot 4 migration piece](/blog/spring-boot-4-migration-ai-agents/): the build fails with an error that points at the wrong suspect. Nothing about `Unknown host` or `Operation not permitted` appears — the sandbox worked fine at this level — and the compiler blames your perfectly valid code.

The fix that stuck: pin the JDK **inside the command**, not in the shell:

```
JAVA_HOME=/path/to/amazon-corretto-17.jdk/Contents/Home mvn -B test
```

…and put that exact command in the project's AGENTS.md as the definition of done, so every tool and every teammate inherits it the same way. An exported variable is a hope; a command in AGENTS.md is a contract.

## The decision table I actually use now

After seven runs, my personal defaults for Codex on Java projects:

- **Local development, warm cache, no new dependencies expected:** `codex exec --full-auto`. Fast, and the sandbox is enough because nothing needs the network.
- **Anything that might download a dependency (new machine, CI, first build, version bumps):** `-s workspace-write -c 'sandbox_workspace_write.network_access=true'`. This is my new default. It is the least privilege that can still do the job.
- **`danger-full-access`:** only inside something disposable that isn't my laptop.

And one operational note for CI: `codex exec`'s read-only default means the common advice of "just run codex exec in your pipeline" produces an agent that cannot compile anything. If you are wiring this into GitHub Actions, the same sandbox decision applies there, just with the network question answered differently — I cover the Claude Code equivalent of that setup in [my GitHub Actions piece](/blog/claude-code-github-actions-spring-boot/), and the Codex version needs this exact flag.

