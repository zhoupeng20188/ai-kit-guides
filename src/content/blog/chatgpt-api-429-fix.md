---
title: "OpenAI API 429: Diagnose Before You Retry"
description: "Separate temporary throttling from exhausted credits, spend limits, and gateway errors. Includes an offline Python classifier and a recovery checklist."
pubDate: 2026-06-28
updatedDate: 2026-10-23
category: "ai-api-limits"
tags: ["openai api", "error 429", "rate limit", "python", "troubleshooting"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
featured: true
faq:
  - question: "Should I retry every OpenAI API 429?"
    answer: "No. Temporary throttling can justify bounded retries. Exhausted credits, spend caps, and usage limits require account action. Inspect the response body before choosing a recovery action."
  - question: "Does a new API key increase my limits?"
    answer: "A new key does not create a new organization or project rate-limit pool. Check the limits applying to the organization, project, and model used by the request."
  - question: "Is this a live API benchmark?"
    answer: "No. The Python example classifies synthetic responses offline. It does not make API requests or measure provider throughput."
---

An HTTP `429` tells you that a request was rejected, but it does not identify the recovery action. Waiting can help with temporary throttling. It cannot replenish credits or change an account limit.

This guide combines the earlier general 429 and error-variation articles. It covers **OpenAI API responses**, not message limits in the ChatGPT app. The examples below are synthetic fixtures, not captured production responses or a throughput benchmark.

## Capture the response before changing the retry loop

Keep the HTTP status, `error.type`, `error.code`, request ID, and relevant response headers. Also record the configured API hostname, endpoint, model, and project. Remove credentials and customer content before sharing the record.

For example, this deliberately simplified fixture represents a billing failure:

```json
{
  "error": {
    "type": "insufficient_quota",
    "code": "credit_balance_exhausted",
    "message": "Example: prepaid balance is exhausted."
  }
}
```

A retry loop cannot repair that condition. Conversely, a temporary request-rate rejection calls for a different response. OpenAI's [error-code reference](https://developers.openai.com/api/docs/guides/error-codes) distinguishes exhausted credits, spend and usage limits, temporary rate limits, and `slow_down` errors. It also documents temporary model overload as `503` with `server_is_overloaded`.

The practical branches are:

- **Account action:** check the account or project identified by the failed request.
- **Temporary pressure:** reduce traffic and use a bounded retry policy.
- **Unknown response:** inspect the service that generated it before assigning a meaning.

## A classifier you can run without an API key

Save this block as `classify_error.py` and run `python3 classify_error.py`. It uses only Python's standard library. The assertions exercise synthetic examples; they do not establish which errors your account will receive.

```python
ACCOUNT_CODES = {
    "insufficient_quota",
    "credit_balance_exhausted",
    "organization_spend_limit_exceeded",
    "project_spend_limit_exceeded",
    "organization_usage_limit_exceeded",
}


def classify_error(status, body):
    if not isinstance(body, dict):
        return "INSPECT"
    error = body.get("error")
    if not isinstance(error, dict):
        return "INSPECT"

    code = str(error.get("code") or "")
    kind = str(error.get("type") or "")
    if status == 429:
        if code in ACCOUNT_CODES or kind == "insufficient_quota":
            return "ACCOUNT_ACTION"
        if code in {"rate_limit_exceeded", "slow_down"}:
            return "RETRY_WITH_BACKOFF"
        if not code and kind == "rate_limit_exceeded":
            return "RETRY_WITH_BACKOFF"
    if status == 503 and code == "server_is_overloaded":
        return "RETRY_WITH_BACKOFF"
    return "INSPECT"


if __name__ == "__main__":
    fixtures = [
        (429, {"error": {"code": "rate_limit_exceeded"}},
         "RETRY_WITH_BACKOFF"),
        (429, {"error": {"code": "slow_down"}},
         "RETRY_WITH_BACKOFF"),
        (429, {"error": {"type": "insufficient_quota"}},
         "ACCOUNT_ACTION"),
        (429, {"error": {"code": "project_spend_limit_exceeded"}},
         "ACCOUNT_ACTION"),
        (503, {"error": {"code": "server_is_overloaded"}},
         "RETRY_WITH_BACKOFF"),
        (429, {"error": {"code": 429001}}, "INSPECT"),
        (429, {"error": "unexpected shape"}, "INSPECT"),
        (400, {"error": {"code": "rate_limit_exceeded"}}, "INSPECT"),
    ]
    for status, body, expected in fixtures:
        assert classify_error(status, body) == expected
    print(f"{len(fixtures)} synthetic fixtures passed")
```

The conservative `INSPECT` result is intentional. A message containing “cooling down” or “method not allowed” is insufficient evidence to label it an OpenAI rate limit. Neither is an agent log entry such as `request_retry:68` or `max_check_attempts`. Identify the SDK, agent, or gateway that produced the text.

For a provider-specific numeric code, use the [429001 gateway guide](/blog/openai-429001-error-code-fix/). Do not add it to the OpenAI classifier merely because its digits begin with `429`.

## Apply the recovery action

For `ACCOUNT_ACTION`, stop automatic retries for that failed work item. Check credits, spend controls, and approved usage limits in the account associated with the request. Keep the work item pending so it can resume after the account issue is resolved.

For `RETRY_WITH_BACKOFF`, lower concurrency first. Treat a supplied `Retry-After` delay as a minimum; otherwise use exponential backoff with jitter. Limit both attempts and elapsed time. If the required wait exceeds the job's deadline, defer the job instead of retrying early. These recovery rules are described in OpenAI's [rate-limit guide](https://developers.openai.com/api/docs/guides/rate-limits).

Choose one owner for retries. The [Python SDK documentation](https://developers.openai.com/api/reference/python#retries) describes automatic retries and the `max_retries` option. If an application implements its own classifier and retry loop, configure the SDK accordingly; otherwise an outer loop can multiply the number of attempts. The classifier above does not itself send requests, sleep, or disable SDK retries.

For `INSPECT`, retain a sanitized error sample and consult the endpoint's documentation. Do not turn an unknown response into an unlimited retry.

## Keep a batch job recoverable

Retry handling and job recovery solve different problems. A worker can use correct backoff and still lose hours of work if results live only in memory.

Assign each input a stable job ID, save successful results as they arrive, and keep failed items in a separate queue. On restart, select pending IDs rather than replaying every input. If a request timed out after submission, check whether a result already exists before resending it. Streaming requests need particular care once output has been consumed.

A useful verification sequence for your own worker is:

1. Inject a temporary rate error and confirm the retry budget is bounded.
2. Inject an exhausted-credit response and confirm it stops retrying.
3. Terminate the process after a saved result and confirm restart skips it.
4. Inject an unknown gateway response and confirm its details remain available for diagnosis.

These are acceptance checks to run against your implementation, not claims about a test performed for this article.

## Reduce the pressure that caused the rejection

Use the [capacity-planning guide](/blog/openai-rate-limits-guide/) to estimate request and token demand. Shorter prompts, smaller output budgets, and a queue may address different bottlenecks; none should be applied blindly.

Changing keys does not change the limit pool. Changing models only helps if the destination has suitable capacity and still meets the task's quality requirements. For asynchronous workloads, evaluate the provider's batch interface separately rather than assuming that putting more items into a synchronous prompt changes its token limit.

**Correction, October 23, 2026:** Earlier versions included unsupported account-limit numbers, personal throughput anecdotes without attached records, and claims that gateway or agent log strings were OpenAI internal errors. Those claims have been removed. The diagnostic examples are explicitly synthetic, and unknown codes remain unknown until their source is identified.
