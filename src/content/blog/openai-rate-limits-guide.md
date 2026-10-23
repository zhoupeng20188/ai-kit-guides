---
title: "OpenAI Rate Limits: Plan Request and Token Capacity"
description: "Estimate request and token demand, pace shared workers, and use account limits and response headers without relying on outdated tier tables."
pubDate: 2026-07-03
updatedDate: 2026-10-23
category: "ai-api-limits"
tags: ["openai rate limits", "capacity planning", "tpm", "rpm", "queues"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
---

A retry loop helps after a rejection. Capacity planning helps a worker avoid sending work faster than its available budget. This article focuses on that second problem; for an active error, start with the [429 diagnostic guide](/blog/chatgpt-api-429-fix/).

The calculations here use invented workload numbers so you can reproduce the arithmetic. They are not published OpenAI account allowances or measured throughput.

## Find the limits for the actual request

Check the organization, project, model, and endpoint your application uses. OpenAI's [rate-limit documentation](https://developers.openai.com/api/docs/guides/rate-limits) describes request, token, image, and some audio limits, organization and project scopes, and model families with shared pools. Account limits and response headers are the relevant inputs; copying another account's tier table is unreliable.

Record the applicable limits beside the worker configuration. If multiple services use the same pool, include their traffic in the estimate. Creating another key for a worker does not give that worker an independent organization allowance.

Distinguish a rate budget from money available to spend. A larger request allowance does not replenish credits, and a higher account balance does not guarantee the request rate your application wants.

## Work an example before adding workers

Suppose a fictional workload has these inputs:

| Input | Example value |
|---|---:|
| Request ceiling | 60 requests per minute |
| Token ceiling | 120,000 tokens per minute |
| Planning allowance per job | 3,000 tokens |
| Target utilization | 75% |
| Average request duration | 8 seconds |

The token budget permits `120,000 / 3,000 = 40` jobs per minute. The request budget permits 60. The smaller value is 40; a 75% operating target gives **30 jobs per minute**.

At an eight-second average duration, 30 starts per minute correspond to roughly `30 × 8 / 60 = 4` concurrent requests in steady state. Four workers are a starting estimate, not a throughput guarantee. Variable request sizes and latency can change it.

Use a conservative token allowance based on representative inputs and the configured output budget. Provider rate accounting need not equal the final tokens shown on an invoice. Check the endpoint's rules instead of treating this planning estimate as an exact rate-limit counter.

## Spread starts across time

Thirty jobs per minute means roughly one start every two seconds in this example. Launching all thirty together at the top of a minute creates a different traffic pattern.

A queue should control when requests begin. A concurrency limit should control how many remain in flight. Use both: a semaphore alone allows fast responses to create a burst of new requests; a start-rate limiter alone allows slow requests to accumulate.

One implementation check is to log the start timestamp and job ID for each request, then inspect the busiest short interval. An acceptable average over a minute can hide an undesirable burst within that minute.

For several worker processes, coordinate admission through shared state or allocate explicit budgets to each worker. Otherwise each process may schedule as if it owns the entire pool.

## Use headers as feedback

When the service supplies request/token remaining and reset headers, capture them with the response timestamp. A sample describes one response at one point in time. Other workers can consume capacity before the next call.

Use that feedback to slow admission when capacity is low. Keep a margin for latency, variable token sizes, and competing traffic. A missing header should lead to conservative pacing, not an assumption that capacity is unlimited.

Separate the metrics that answer different questions:

- Queue age shows how long users wait before work starts.
- Successful jobs per minute shows useful throughput.
- Rate rejections show pressure at the provider boundary.
- Attempts per completed job shows retry amplification.
- Token use per completed job helps explain workload changes.

A lower error count is not automatically an improvement if the queue is growing without bound. Compare completion rate and queue age together.

## Decide when to change the workload

For a token bottleneck, test smaller inputs, retrieval of relevant sections, or a lower output allowance. Check result quality after each change. For a request bottleneck, consider whether small independent items can be processed together while preserving a stable ID for each result.

For work that can finish later, evaluate [OpenAI's Batch API](https://developers.openai.com/api/docs/guides/batch). Batch has its own queue constraints and processing workflow; grouping items into an ordinary synchronous prompt is a separate technique.

If a shared pool remains too small, review the account's available limit options. Do not buy credits solely on the assumption that a particular historical tier number or waiting period will apply.

## A fallback needs its own acceptance criteria

Routing to another model or provider changes more than capacity. Before enabling fallback, compare output format, tool-call behavior, quality, latency, cost, and data-handling requirements. Check whether the target actually has a separate limit pool.

Test a rejected primary request and verify that the fallback produces a usable result once. Also test a failed fallback. A gateway that retries repeatedly and then returns an incompatible response has only moved the failure.

**Correction, October 23, 2026:** The previous version presented an outdated five-tier table, fixed model allowances, and unsupported claims about account upgrades as general rules. This revision replaces them with an explicit worked example and links to the current account-limit documentation.
