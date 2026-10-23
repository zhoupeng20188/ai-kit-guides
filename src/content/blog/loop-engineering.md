---
title: "Agent Loop Engineering: Stop, Verify, and Recover"
description: "Build a bounded coding-agent loop with observable state, independent verification, repeat detection, and explicit stops for problems it cannot repair."
pubDate: 2026-07-14
category: "ai-coding-agents"
tags: ["loop engineering", "ai agents", "ai coding", "agent workflow", "peter steinberger"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["loop engineering", "peter steinberger", "ai agent loops", "agentic workflow 2026", "self-running ai agents"]
updatedDate: 2026-10-23
---

A coding agent often works in a cycle: inspect a failure, choose a change, run a check, and decide whether to continue. This guide calls the design of that cycle **loop engineering**. The term describes a useful implementation problem rather than a universal product architecture.

A better loop does not simply allow more attempts. It preserves enough state to recognize progress, avoid repeating the same unsuccessful action, and stop when the next decision needs information or authority the agent lacks. The surrounding permissions, tools, and CI belong to the [agent harness](/blog/harness-engineering/).

## Define what one attempt means

For an illustrative Java compilation task, one attempt might inspect the current compiler error, edit within an agreed module, and run a targeted compiler check. The input state includes the source revision and current failure. The result includes changed files, the command, its exit status, and the next failure if any.

Do not confuse an individual command with completion of the task. Compilation may be one gate before tests and runtime behavior. If the task concerns another user's data, a compiler result does not establish authorization; the [security example](/blog/claude-code-insecure-api-spring-boot/) needs negative tests.

## Use explicit stop conditions

| Observation | Appropriate next step |
| --- | --- |
| Verification passed | Stop only after the task's complete acceptance checks pass |
| New actionable code failure | Continue within the remaining budget |
| Identical failure after an ineffective change | Reconsider the hypothesis instead of repeating the edit |
| Dependency endpoint unavailable | Diagnose access; bounded retry only when appropriate |
| Credentials or business policy missing | Report the missing input and stop dependent work |
| Unexpected files or failing baseline | Preserve evidence and review the scope |

For a network outage, repeated code changes are usually the wrong response. For an authentication error, retrying the same key is not recovery. The [API 429 guide](/blog/chatgpt-api-429-fix/) further distinguishes temporary rate limits from quota problems.

## A small executable control example

This pure Python example demonstrates repeat detection and a fixed attempt budget. It does not call a model or execute shell commands. `step` and `verify` are supplied functions, so their own timeout and permission controls remain the caller's responsibility.

```python
def run_loop(state, step, verify, max_attempts=3):
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    seen = set()
    for attempt in range(1, max_attempts + 1):
        result = verify(state)
        if result["passed"]:
            return {"status": "passed", "state": state}
        fingerprint = result["fingerprint"]
        if fingerprint in seen:
            return {"status": "repeated_failure", "state": state}
        seen.add(fingerprint)
        if result.get("blocked"):
            return {"status": "blocked", "state": state}
        state = step(state, result)
    final = verify(state)
    status = "passed" if final["passed"] else "budget_exhausted"
    return {"status": status, "state": state}
```

The final verification is intentional: the last allowed edit still needs checking. A production orchestrator also needs cancellation, wall-clock limits, crash recovery, and structured error handling. Framework execution limits, such as those described in [LangChain's agent documentation](https://docs.langchain.com/oss/python/langchain/agents), are useful controls but do not replace task-specific completion checks.

Fingerprint a normalized failure together with the relevant verification context. Hashing an entire noisy log can miss repeats because timestamps change. Grouping only by an exception name can stop too early when distinct causes produce the same exception. Keep both the fingerprint and the original report for inspection.

## Make retries safe to resume

Before a state-changing external action, consider what happens if it succeeds but the response is lost. Repeating a migration, email, or purchase can duplicate effects. Use supported idempotency mechanisms and durable state where appropriate; an in-memory loop counter does not provide either. The [transactional email guide](/blog/claude-code-after-commit-email-loss/) explains a related failure boundary.

Store the last completed step and verification evidence. On resumption, inspect actual state before replaying an action. Report which check passed and which work remains blocked. A finite loop that ends with an accurate incomplete result is more useful than one that reaches its budget and declares success.
