---
title: "Codex Cannot Run Maven: Diagnose JDK, Cache, and Network Access"
description: "Compare the same Maven command inside and outside Codex, then separate JDK errors, filesystem denials, repository configuration, and network failures."
pubDate: 2026-09-07
category: "ai-coding-agents"
tags: ["openai codex", "codex sandbox", "codex approval modes", "maven", "spring boot", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["codex maven", "codex sandbox maven", "codex full auto maven", "codex approval modes", "openai codex spring boot", "codex unknown host"]
updatedDate: 2026-10-23
---

When Codex cannot run Maven but a terminal can, compare the same command in the two environments. The difference may be JDK selection, working directory, cache permissions, network policy, proxy settings, or repository credentials.

This guide replaces a historical configuration scorecard and retired approval recommendations. One local sandbox failure does not establish that nested sandboxing always fails or that unrestricted access is the required fix.

## Establish the actual runtime

Run diagnostics in the environment where the failure occurs:

```bash
codex --version
codex --help
java -version
./mvnw -version
```

The wrapper can select a different runtime from the one expected by an IDE. A Java 8 process cannot build a Java 17 application; that failure is not a network problem. Record `JAVA_HOME` and the wrapper output without printing secret-bearing environment variables.

If a specific JDK is required, select its real installation for the build process. Do not copy an absolute path from someone else's computer.

## Classify the earliest failure

| Observation | Next investigation |
|---|---|
| Unsupported release or class-file version | JDK and compiler/toolchain configuration |
| Cannot write a local-repository path | Filesystem policy and cache location |
| Unknown host | DNS, network policy, proxy, and repository hostname |
| HTTP authentication error | Repository credentials and mirror configuration |
| TLS error | Certificate chain, proxy, and runtime trust store |
| Sandbox initialization fails before commands | Host/runtime sandbox support and logs |

An error message narrows the search; it rarely proves a unique cause. `Unknown host` is not by itself proof that a particular sandbox flag blocked DNS.

## Control the dependency cache deliberately

A warm cache can make an offline build pass while a clean machine fails. A cold cache can expose network or write requirements that a previous run hid.

When diagnosing, use a disposable cache in a known writable location and record it. Maven's `-Dmaven.repo.local=...` changes its local repository; it does not grant network access or repair authentication. Do not delete the user's existing cache just to create a clean comparison.

Also check the wrapper distribution download. The build may need network access before Maven itself starts.

## Inspect policy without conflating its parts

Approval settings control when actions require approval. Filesystem and network policy control what the process can access. An approval does not necessarily remove a sandbox restriction.

Use the [current Codex approvals and security documentation](https://learn.chatgpt.com/docs/agent-approvals-security) together with the installed CLI's help. Supported policy names and configuration keys change. The old `suggest`, `auto-edit`, `untrusted`, and historical `--full-auto` explanations are not reliable current configuration guidance.

Grant only the access the build requires in an environment where that access is appropriate. A dependency download needs repository access; it does not establish a need to expose every local file or service.

## Compare one variable at a time

Keep project revision, working directory, command, JDK, and cache state constant. Change only the suspected policy or environment input, then preserve the result.

If sandbox initialization fails before even a harmless command can run, investigate the runtime and host constraints. Avoid asserting a permanent platform limitation from one version's failure. Keep the version and actual error in the incident record.

## Keep application failures separate

After environment setup works, run the application tests. Do not turn a blocked build into a green result by skipping tests or editing business logic. Report unresolved access or credential requirements.

The [Docker socket guide](/blog/codex-testcontainers-docker-socket-spring-boot/) covers container access, the [CI guide](/blog/codex-ci-spring-boot-green-build/) covers independent acceptance, and the [Codex workflow](/blog/codex-spring-boot/) covers task setup. Use the [Java hub](/blog/ai-for-java-developers/) to locate related checks.
