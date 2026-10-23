---
title: "Spring Boot 4 Dependencies: Resolved Does Not Mean Configured"
description: "Diagnose a Boot 4 dependency that resolves and compiles but does not activate its feature. Check integration modules, conditions, beans, and behavior."
pubDate: 2026-09-18
category: "spring-boot-4"
tags: ["openai codex", "spring boot 4", "maven", "dependency management", "ai coding agents", "java testing", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["spring boot 4 dependencies", "spring boot 4 starter renamed", "codex spring boot 4", "flyway core not running spring boot 4", "webclient builder bean not found spring boot 4", "spring boot 4 restclient builder", "spring boot 4 webmvctest package"]
updatedDate: 2026-10-23
---

Spring Boot 4 dependencies can resolve successfully while the integration you expected remains inactive. Diagnose the feature and its conditions rather than using a green build as proof that a suggested coordinate is correct.

This guide preserves the useful mechanism from AI-built dependency experiments. The original full transcripts were not retained, so the earlier “one correct answer out of twelve” and follow-up model success rates have been removed.

## Understand the layers

A third-party library supplies functionality. A Boot integration module supplies relevant configuration. A starter groups dependencies for a use case. These layers overlap, but their names are not interchangeable.

Spring's [modularization article](https://spring.io/blog/2025/10/28/modularizing-spring-boot/) explains the move to focused integration modules. A library can remain version-managed without bringing the auto-configuration that a feature previously received from a broader module.

Do not turn this into a ban on direct library dependencies. They can be intentional. The issue is whether the task requires Boot integration and whether the selected dependency graph supplies it.

## Worked investigation: migrations absent

Suppose the application has migration scripts and a datasource, but no migration ran. Check whether Flyway is invoked, not only whether `flyway-core` is on the classpath.

For a Boot-managed integration, inspect the target release's recommended dependency, for example:

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-flyway</artifactId>
</dependency>
```

This fragment assumes the project already manages the Boot dependency versions. Database-specific Flyway support and a suitable driver may also be needed. Adding the starter does not create credentials or make every database configuration valid.

Verify the migration through a fresh test database and a database with existing history. The [Flyway guide](/blog/flyway-checksum-mismatch-ai-agent/) explains why those are different tests.

## Inspect the actual dependency graph

Use the build's dependency tree and effective configuration. Identify the integration module, conflicting generations, exclusions, and the version selected after management.

```bash
./mvnw dependency:tree
./mvnw help:effective-pom
```

For a build importing only the BOM, check plugin configuration separately. Do not infer the full build behavior from dependency management.

A missing or changed starter may fail during model resolution or compilation. A valid but insufficient dependency can fail later during startup or behavior. Keep those categories separate in the diagnosis.

## Read conditions and inspect the expected bean

Spring's [auto-configuration reference](https://docs.spring.io/spring-boot/reference/using/auto-configuration.html) describes condition reporting. Use a local debug startup or an appropriately restricted diagnostic to understand why a configuration matched or did not match.

A bean-count check can help for a specific expected type, but “one bean” is not a universal success criterion. User configuration can intentionally replace auto-configuration, and some features expose several beans. Follow up with the behavior required by the task.

For a web-client builder, verify its configured behavior. For a migration, inspect applied versions. For a test annotation, compile and run the intended test using the correct test module.

## Check names against the target release

Consult the [Boot 4 migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) rather than applying a global coordinate substitution. Old names can be removed, deprecated bridges, or still valid libraries. Their status depends on the exact release and purpose.

Review the diff for added starters, removed modules, explicit versions overriding management, and changed test dependencies. A narrower coordinate can also remove configuration the application had implicitly depended on.

The [YAML guide](/blog/codex-spring-boot-4-yml-properties/) covers the corresponding binding question. Put the verification requirement in the [Boot 4 instruction template](/blog/spring-boot-4-agents-md-guide/) and use the [Java hub](/blog/ai-for-java-developers/) for related checks. The acceptance evidence is an active working feature, not a resolving artifact or an agent score.
