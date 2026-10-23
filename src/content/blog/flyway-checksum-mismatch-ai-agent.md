---
title: "Flyway Checksum Mismatch: Restore History Before Repair"
description: "Diagnose edited migrations, preserve applied SQL, and distinguish Flyway metadata repair from a real schema correction before changing a database."
pubDate: 2026-09-14
category: "spring-boot-4"
tags: ["flyway", "flyway migration", "flyway checksum mismatch", "spring boot 4", "ai coding agent", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["flyway checksum mismatch", "flyway migration checksum mismatch", "spring boot 4 flyway", "ai agent flyway migration", "flyway repair"]
updatedDate: 2026-10-23
---

A Flyway checksum mismatch usually means the migration available to Flyway differs from the migration recorded in that database's history. The first question is which file and database are being compared. Running `repair` immediately can remove the warning while leaving a schema difference unresolved.

This walkthrough uses an illustrative versioned-migration scenario. It is not a report of agent trials or a production incident. The migration identifier and schema-history table name below are examples; your configuration can change both.

## Establish which history you are repairing

Record the target host, database, schema, migration locations, Flyway version, and active application profile without publishing credentials. Use the same environment when comparing validation results. A command configured by a Maven plugin may target something different from the application started by Spring Boot.

Inspect the reported migration version and the corresponding history row. With the default table name, this read-only query can help:

```sql
SELECT installed_rank, version, description, script, checksum, success
FROM flyway_schema_history
ORDER BY installed_rank;
```

Check the configured schema before using it. Save the relevant history and deployment revision, then compare the current SQL against the artifact originally deployed. A Git copy is useful only if it really matches the deployed artifact; the latest main branch is not automatically authoritative.

## An example of divergent databases

Suppose an applied `V2__add_status.sql` originally added a nullable column. An agent later edits that same file to add `NOT NULL` and a default.

An existing database still has the earlier column definition and original checksum. A new database executes the edited file and gets the new definition. A successful fresh-database test therefore cannot prove the upgrade path works. See Flyway's [validation documentation](https://documentation.red-gate.com/fd/validate-277578898.html) for the checks Flyway performs against migration history.

For this scenario, restore the applied V2 file to its deployed content **and** create a new versioned migration for the intended change. Merely adding V3 while leaving V2 modified does not resolve V2's validation mismatch. Restoring V2 alone removes the mismatch but also leaves the requested schema change unimplemented.

The new migration must handle existing data. If a column will become non-nullable, decide how to backfill nulls before applying the constraint. The SQL and locking implications depend on the database, table size, and application compatibility requirements. Have the agent explain those assumptions before writing the migration.

## What repair actually changes

Flyway's [repair reference](https://documentation.red-gate.com/flyway/reference/commands/repair) describes changes to its schema-history metadata, including alignment with available migration files. Repair does not execute the missing schema change. It can also affect failed or missing migration records, so using the correct migration locations matters.

There are legitimate repair cases, but first establish that the database state and intended migration history agree. Keep a record of the reason, history before and after, and the exact target. Do not use an agent's suggestion to run repair as evidence that this investigation has occurred.

## Test both installation and upgrade

Use two disposable databases of the actual database engine:

1. Install the complete migration chain into an empty database.
2. Install the previous released chain, load representative existing data, then apply the proposed upgrade.
3. Compare required columns, constraints, indexes, data transformations, and application behavior.
4. Run validation against both outcomes and retain the reports.

These tests answer different questions. Neither replaces a deployment plan for a shared database. [Testcontainers setup](/blog/codex-testcontainers-docker-socket-spring-boot/) can help provision the disposable engine, provided tests actually execute.

If Flyway never runs after a Boot upgrade, investigate application integration separately: effective dependencies, auto-configuration conditions, configuration, and startup logs. An absent migration run is not a checksum error. The [Boot 4 dependency guide](/blog/codex-spring-boot-4-dependencies-silent-failures/) covers that distinction.

## Give agents a verifiable boundary

Tell the agent to preserve applied versioned migrations, propose new versions, and report which upgrade tests ran. Enforce historical-file review in CI against a known release baseline, allowing explicitly reviewed exceptions. [CI review gates](/blog/ai-code-ci-gates-archunit-spotless/) are more useful than assuming any agent always respects a paragraph of instructions.
