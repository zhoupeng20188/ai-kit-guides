---
title: "Cursor Rules Tutorial: Scope Instructions and Check Activation"
description: "Write focused Cursor project rules, choose activation deliberately, and test whether the right guidance was supplied without treating it as enforcement."
pubDate: 2026-07-15
category: "ai-coding-agents"
tags: ["cursor rules", "cursorrules", "cursor ai", "ai coding tools", "cursor tutorial"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["cursor rules tutorial", "cursorrules", ".cursor/rules", "cursor project rules 2026", "cursor mdc rules"]
updatedDate: 2026-10-23
---

Cursor rules provide reusable instructions for a project or task. Their value comes from relevant context and checkable requirements, not from the amount of text in the file.

This tutorial uses illustrative `.mdc` files. Earlier claims about guaranteed compliance, measured error reduction, and the legacy `.cursorrules` file being universally ignored have been removed.

## Read the installed product's rule modes

Use the current [Cursor Rules reference](https://cursor.com/docs/rules) to check supported formats and activation behavior. Interface labels and rule discovery evolve, so verify what your version actually loads.

Keep global conventions short. Use scoped rules for instructions that apply only to a language, path, or task. A repository-wide rule about Java packages is irrelevant to an unrelated documentation edit and consumes attention without helping.

## Start with one small project rule

An illustrative `.cursor/rules/java-tests.mdc`:

```markdown
---
description: Java test review and execution requirements
globs: "**/src/test/java/**/*.java"
alwaysApply: false
---

- Match the repository's test engine and naming configuration.
- Assert the specified result, including important boundaries and rejected input.
- Do not weaken an assertion merely to obtain a passing build.
- Run the focused test and report execution and skipped counts.
- Keep helpers and generated output distinct from intended test classes.
```

Match the glob against real files in your repository. Confirm the rule appears in the relevant context when selecting or editing a matching file. A rule that is not loaded cannot affect the task, and a loaded rule can still be misunderstood.

## Write observable conventions

“Write clean code” is hard to assess. “Use the existing mapper; preserve the response contract” identifies a concrete review question. “Do not add dependencies” may be too broad for a task whose purpose is to add an integration. Scope it to the intended change and require justification when the build changes.

For Spring, do not turn a project preference into a framework law. Request DTO validation does not replace service invariants, and constructor injection does not prove the chosen bean is available in every profile.

## Check interactions and conflicts

Review root, path-specific, user, and task instructions together. Avoid maintaining two contradictory copies of the same build command. Keep a reference to longer documentation when the task needs it, and verify the reference path exists.

Do not delete an existing legacy rule file solely because an article says it is ignored. Consult your version's migration guidance, compare contents, and move the guidance deliberately if required.

## Trial the rule on a representative edit

Use a small disposable change. Ask the agent to identify the applicable instruction and required verification. Inspect the resulting patch for the intended convention and an unrelated counterexample.

For a test rule, confirm the assertion observes the behavior and the test actually executes. The [JUnit guide](/blog/ai-junit-tests/) and [Surefire guide](/blog/ai-junit-tests-not-running-spring-boot-4/) provide concrete checks. A passing answer about the rule is weaker evidence than the correct patch and test result.

## Keep hard controls executable

Rules guide behavior. Permissions, architecture checks, branch protection, and tests provide different forms of enforcement. Do not treat a sentence in an instruction file as protection against all reads or writes.

If the assistant repeatedly misses a rule, investigate activation, ambiguity, context, and whether the requirement is observable. Add an executable check where the constraint matters. The [CI gate guide](/blog/ai-code-ci-gates-archunit-spotless/) covers that next step.

Use the [codebase guide](/blog/cursor-codebase-spring-boot/) for retrieval problems and the [Spring Boot workflow](/blog/cursor-spring-boot/) for an end-to-end task. A useful ruleset stays small enough to review and specific enough to test.
