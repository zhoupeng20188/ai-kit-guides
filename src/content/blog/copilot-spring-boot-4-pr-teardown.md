---
title: "Reviewing Copilot Spring Boot 4 PRs: Evidence and Gaps"
description: "Two public migration PRs illustrate how to separate proposed changes, reported build results, and the evidence needed to approve a Boot 4 upgrade."
pubDate: 2026-10-08
category: "spring-boot-4"
tags: ["github copilot", "spring boot 4", "copilot coding agent", "ai coding agents", "java-ai-cluster", "spring boot migration"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["copilot coding agent spring boot 4", "github copilot spring boot 4 migration", "spring boot 4 pr teardown", "ai agent missed boot 4 changes", "camunda copilot spring boot 4", "azure sdk spring boot 4 copilot"]
updatedDate: 2026-10-23
---

Two public Spring Boot 4 migration pull requests provide useful review material: [Camunda #42114](https://github.com/camunda/camunda/pull/42114) and [Azure SDK for Java #47195](https://github.com/Azure/azure-sdk-for-java/pull/47195). This is a source-based review. Their descriptions and current metadata were checked on October 23, 2026; neither repository was built for this article.

The distinction matters. A pull request description tells us what its author reports. A diff shows proposed code. CI output demonstrates what ran on a particular revision. None alone proves the behavior of an entire migrated application. The broader [Boot 4 migration guide](/blog/spring-boot-4-migration-ai-agents/) explains how to assemble that evidence.

## What the public records establish

Camunda's PR was merged on December 12, 2025. Its description reports an SDK client upgrade from Boot 3.5.8 to 4.0.0, additional health and Jackson modules, and related import changes. The API reports six changed files. That supports a concrete observation: the proposed upgrade included module changes alongside version changes. It does not establish that every downstream application was tested.

Azure's PR is closed without a merge. Its description reports changes to 68 POM files and unresolved compilation problems in auto-configuration, along with security integration work still requiring review. The overall PR contains 71 changed files. Those counts describe different things. Its self-reported build status is not an independently reproduced benchmark.

These are historical changes targeting different scopes and framework versions. They cannot establish a Copilot success rate or show that one repository's size caused its outcome. Check the linked records for later discussion and follow-up work.

## Read the diff as a set of hypotheses

Use the [official migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) to identify affected technologies, then ask what observable behavior each change should preserve:

| Change in a PR | Evidence to request |
| --- | --- |
| Parent or BOM upgrade | Effective dependency versions and compatibility checks for integrations |
| New technology module | A context test showing the required bean and configuration actually activate |
| Test engine upgrade | Reports naming executed tests, counts, failures, errors, and skips |
| Property relocation | A test of the configured value and resulting behavior |
| Security configuration | Requests covering authorized, unauthenticated, and forbidden cases |
| Nullability annotation change | The old contract, replacement annotation or documented decision, and affected callers |

A removed nullability annotation does not automatically remove a runtime check: many annotations describe static contracts. Likewise, a compilation failure does not tell you which runtime behavior needs testing. Review each change on its own semantics.

## Ask for a result, not a reassuring summary

For a Maven project with its verification plugins configured, capture the complete command and its exit status:

```bash
./mvnw -B clean verify > migration-verify.log 2>&1
status=$?
cat migration-verify.log
exit "$status"
```

Then inspect Surefire and Failsafe reports where applicable. A skipped test can be intentional; a missing test can be absent from the summary entirely. Compare expected critical cases with the reports, rather than interpreting any nonzero skip count as a defect. See [test discovery checks](/blog/ai-junit-tests-not-running-spring-boot-4/).

For configuration, verify both binding and the consumer's effect. An Actuator endpoint may help diagnosis, but it is not the only source of truth and should not expose secrets. A targeted assertion can be stronger evidence than a screenshot of configuration metadata. See [property migration checks](/blog/codex-spring-boot-4-yml-properties/).

## Make unresolved work visible

A useful PR handoff lists the revision tested, commands, report paths, checks not run, and the specific blocker. If the environment cannot fetch an artifact or start a database, request that check in an appropriate CI environment. Do not infer its result from compilation elsewhere.

The reviewer can ask an agent to create and run behavioral tests. Agents are not inherently unable to observe runtime behavior; the limitation is the feedback available in that task. [Repository instructions](/blog/spring-boot-4-agents-md-guide/) should require accurate reporting, while [CI gates](/blog/ai-code-ci-gates-archunit-spotless/) enforce the checks that matter independently of the summary.
