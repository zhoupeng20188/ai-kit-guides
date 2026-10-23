---
title: "Codex and Testcontainers: Diagnose Docker Socket Access"
description: "Check the active Docker endpoint inside the agent environment, separate daemon availability from permissions, and verify integration tests actually execute."
pubDate: 2026-09-16
category: "java-testing-ci"
tags: ["openai codex", "codex sandbox", "testcontainers", "docker", "spring boot 4", "codex cli", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["codex testcontainers", "codex docker socket", "codex sandbox docker", "testcontainers spring boot 4", "codex permissions unix_sockets", "codex allowed unix socket"]
updatedDate: 2026-10-23
---

A Testcontainers failure inside Codex can be an environment-access failure rather than a broken test. The daemon, socket path, client configuration, network, and sandbox policy all participate.

This article reconstructs the diagnostic mechanism from AI-built lab notes. It does not retain the original full transcripts and does not present a model-run score as evidence. Configuration must match your installed CLI and container runtime.

## Identify the endpoint in use

Start with the [Testcontainers runtime requirements](https://java.testcontainers.org/supported_docker_environment/). Record the Docker context, endpoint, runtime, and relevant client configuration in both the working terminal and the agent environment.

```bash
docker context show
docker context ls
docker info
```

A successful host command does not prove the same process inside a sandbox can connect. A Unix socket is also not automatically outside all network controls. Check the actual endpoint rather than copying `/var/run/docker.sock` when your runtime uses a different path.

## Separate daemon state from access

A message saying a socket is unavailable can reflect a stopped daemon, a wrong path, missing permissions, a denied connect operation, or a mismatch between Docker CLI and Java configuration.

Compare the earliest exception and the exact path. Use version-supported sandbox diagnostics for a harmless connection check. Preserve denial logs when available. Do not label every message from a tool as false merely because it differs from another tool's summary.

## Grant access deliberately

Consult [Codex security guidance](https://learn.chatgpt.com/docs/agent-approvals-security) and the installed configuration reference. Network enablement, Unix-socket allowlists, filesystem access, and approval policies can be separate controls; do not assume one historical spelling works on every version.

Access to a container daemon can grant powerful operations independently of workspace write restrictions. A workspace-scoped file policy does not make Docker access harmless. Use an appropriately isolated runtime and the access required by the task.

## Check Testcontainers-specific configuration

Make sure Java uses the intended Docker endpoint. For alternative runtimes, follow the documented environment requirements and socket overrides for that setup. A value that worked for one Colima or Docker Desktop installation may be wrong on another machine.

Use dependency versions and module names selected by the project. A major Testcontainers upgrade can change artifacts or APIs, so do not combine that migration with socket diagnosis unless it is required.

## Detect a green skip

The [JUnit integration reference](https://java.testcontainers.org/test_framework_integration/junit_5/) documents Testcontainers test behavior. A suite configured to disable tests without Docker can produce a successful build without exercising the database.

Inspect fresh reports for the expected integration suite, executed cases, and skips. A grep for zero skips is insufficient: undiscovered tests can be absent from the report entirely. Conversely, an explicitly authorized skip may be legitimate; keep the acceptance requirement visible.

Do not add `disabledWithoutDocker = true` merely to satisfy a request to make the integration build green. If Docker is required and unavailable, report the blocker.

## Verify after the environment is repaired

Confirm that a container actually starts, the test connects to its database, assertions observe real state, and cleanup occurs as intended. Record the runtime and command with the result. A changed configuration without an executed test is still an unverified hypothesis.

Use the [Surefire guide](/blog/ai-junit-tests-not-running-spring-boot-4/) for discovery, [Maven diagnostics](/blog/codex-sandbox-maven-spring-boot/) for dependency access, and the [CI contract guide](/blog/codex-ci-spring-boot-green-build/) for final acceptance. The [Java hub](/blog/ai-for-java-developers/) connects the related workflow.
