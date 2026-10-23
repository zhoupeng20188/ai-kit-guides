---
title: "AFTER_COMMIT Is Not Durable Delivery: A Spring Outbox Checklist"
description: "Separate transaction timing from notification durability. Design an outbox with retries, idempotency, crash recovery, and failure-path verification."
pubDate: 2026-10-21
category: "java-ai-tools"
tags: ["claude code", "spring boot", "ai coding", "transactional events", "outbox pattern", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["claude code spring boot", "transactional event listener", "after commit notification lost", "spring boot outbox pattern", "ai generated code silent failure", "spring events transaction"]
updatedDate: 2026-10-23
---

`@TransactionalEventListener(AFTER_COMMIT)` controls when a listener runs relative to a transaction. It does not by itself durably record an obligation to notify an external service.

This article explains a failure scenario reconstructed from an AI-built lab. It is not a customer incident or a comparative model benchmark. Original full project and raw outputs were not retained, so historical millisecond timings and model-performance claims have been removed.

## Establish what the annotation guarantees

Spring's [transaction-bound event documentation](https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html) describes listener phases. With the usual default behavior, an event published without a transaction does not invoke a transactional listener unless fallback execution is enabled.

That fallback concerns the absence of a transaction. It is not a retry setting and does not force a rolled-back test transaction to commit. The previous article blurred those mechanisms.

## Model a failure after the order commits

Suppose an order transaction commits, then a listener calls a notification provider. If the call fails and the application only logs the exception, the order may exist while no durable record says that notification remains pending.

The HTTP outcome depends on the listener, exception handling, asynchronous execution, and request path. Do not claim that every AFTER_COMMIT failure returns 200 or that every exception is swallowed. Inspect the actual implementation.

Likewise, adding `@Async` changes execution timing and failure handling; it does not create a durable queue.

## Write the obligation in the order transaction

An outbox design records the order and notification intent atomically in the same database transaction. A separate relay delivers pending events afterward.

An illustrative event record needs an immutable event ID, aggregate ID, payload or reference, creation time, delivery state, attempt count, and next-attempt time. The schema and indexes depend on the workload. A minimal teaching sketch is:

```text
transaction:
  persist order
  persist outbox(event_id, order_id, payload, status=PENDING)
commit

relay:
  claim eligible pending event
  deliver using event_id as an idempotency key where supported
  record outcome and schedule retry or mark completed
```

This is a design sketch, not complete relay code. Publishing an outbox row without defining claiming, crash recovery, and duplicate delivery leaves important behavior unspecified.

## Handle the send-versus-acknowledge gap

The provider can accept a message and the relay can crash before marking the event sent. After restart, the relay may send it again. A durable outbox therefore does not automatically provide exactly-once external delivery.

Use a stable event ID, provider idempotency where supported, or consumer deduplication. Define what happens when a request times out after submission and the caller cannot tell whether it succeeded.

For multiple relay workers, define claiming or leasing so they do not normally process the same event concurrently. Recover expired claims after a worker failure. Keep retries bounded or observable through a failure state and operational process.

## Test stored state and recovery

A mock assertion that the gateway was called once establishes an interaction, not durable recovery. Verify:

1. Successful order commit records an outbox event.
2. Rollback leaves neither the order change nor the event.
3. Provider failure retains a retryable obligation.
4. Restart recovers pending work.
5. Provider success followed by relay failure does not create an uncontrolled duplicate.
6. Exhausted retries remain visible for intervention.

Choose a transaction setup that actually commits when testing an AFTER_COMMIT listener. A default rollback test can hide the callback entirely. If writing more data from a post-commit callback, inspect the transaction semantics rather than assuming the completed transaction will commit those writes.

## Review the guarantee, not just the annotation

Ask what persistent state remains if the process stops at each boundary. Keep latency, delivery, and order-acceptance requirements separate. The correct annotation can coexist with a missing recovery contract.

Use the [Java review guide](/blog/ai-code-review-java/), [JUnit guide](/blog/ai-junit-tests/), and [CI contract guide](/blog/codex-ci-spring-boot-green-build/) for verification discipline. The [Java hub](/blog/ai-for-java-developers/) connects this case to other behavior that a green build alone does not establish.
