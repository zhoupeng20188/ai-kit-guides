---
title: "429001 Errors: Identify the Gateway Before Retrying"
description: "Trace a 429001 response to its provider, distinguish Tencent TokenHub codes from OpenAI errors, and preserve the evidence needed for a useful fix."
pubDate: 2026-07-29
updatedDate: 2026-10-23
category: "ai-api-limits"
tags: ["429001", "api gateway", "tokenhub", "troubleshooting"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
faq:
  - question: "Is 429001 a standard OpenAI API error code?"
    answer: "It is not listed in the linked OpenAI error-code reference. Tencent TokenHub documents 429001 in its own code scheme. Identify your endpoint and provider before applying that mapping."
  - question: "Does a plain 429 prove I am calling OpenAI directly?"
    answer: "No. A gateway can also return an ordinary HTTP 429. Inspect the configured base URL and request path to identify the service."
  - question: "What is the difference between 429001 and 429006?"
    answer: "In Tencent TokenHub's documented scheme, 429001 refers to a model request-rate threshold and 429006 to upstream capacity pressure. Other services may use different mappings."
---

`429001` is an application error code, not an HTTP status. HTTP status codes have three digits. A service can return HTTP `429` and place `429001` in a JSON field, but the field's meaning belongs to that service.

The first diagnostic step is therefore to identify the service. An OpenAI-compatible request format does not make every response an OpenAI response.

## Establish which endpoint answered

Inspect the application's configured base URL, the failing request's hostname and path, and any proxy or gateway in between. A plain HTTP `429` does not prove a direct connection to OpenAI; a proxy can pass through or generate that same status.

Check the configuration actually loaded by the failing process. A shell variable, SDK option, deployment secret, or LangChain client configuration can point a worker somewhere different from the endpoint used in a manual test.

Create a short incident record:

```text
Timestamp: <UTC timestamp of the failed request>
API hostname and path: <no credentials or secret query parameters>
HTTP status: <actual three-digit response status>
Application code: <value from the response body>
Request ID: <provider request ID, if present>
Provider / gateway: <confirmed service, or unknown>
Model: <requested model or deployment ID>
```

This is a template, not a record of a request made for this article. Keep a sanitized response body alongside it; never include an authorization header.

## A documented mapping: Tencent TokenHub

Tencent's [TokenHub API error reference](https://www.tencentcloud.com/document/product/1300/82348) defines the following codes for that service:

| Code | Meaning in TokenHub's scheme |
|---|---|
| `429001` | Model request-rate threshold exceeded |
| `429002` | Requests-per-minute limit exceeded |
| `429003` | Tokens-per-minute limit exceeded |
| `429004` | Tokens-per-day limit exceeded |
| `429005` | Concurrency limit exceeded |
| `429006` | Upstream model busy or at capacity |

The same reference describes an `error` object with optional source and upstream details. Rate-limit codes may be strings or integers. Normalize the value before comparing it:

```python
def gateway_code(body):
    if not isinstance(body, dict):
        return None
    error = body.get("error")
    if not isinstance(error, dict):
        return None
    value = error.get("code")
    return None if value is None else str(value)


assert gateway_code({"error": {"code": 429001}}) == "429001"
assert gateway_code({"error": {"code": "429001"}}) == "429001"
assert gateway_code({"error": None}) is None
```

These assertions use synthetic input. They verify normalization, not the behavior of a live gateway.

Only apply the table after confirming TokenHub or another service explicitly documenting the same mapping. For a different gateway, use that gateway's reference. OpenAI's [API error guide](https://developers.openai.com/api/docs/guides/error-codes) is a separate source; it does not establish the meaning of this numeric family.

## Match the change to the failing layer

For a confirmed request-rate limit, reduce the pace at which new requests start. For a token limit, inspect request size and output allowance. For a concurrency limit, reduce simultaneous in-flight calls. For upstream pressure, use the provider's documented retry guidance and check the incident status if the condition persists.

Preserve any supplied `Retry-After` header and consult the provider's documented interpretation. Bound both retry attempts and total wait time. A server delay longer than the job's deadline is a reason to defer work, not to ignore the delay.

If failures persist even after traffic is reduced, inspect the account and service configuration. A failed first request alone does not prove exhausted credits: it can also reflect shared traffic or provider pressure. Use account information and the actual error fields to establish the cause.

Do not infer that a key has been penalized merely because the next response has a different code. Do not assume that creating more keys expands an account-wide limit pool.

## Keep gateway failures distinct in application logs

Preserve the gateway code and, when supplied, its upstream code and status as separate fields. Replacing them all with `OpenAI rate limit` discards the information needed to locate the failure.

When escalating an incident, include the request ID, timestamp, endpoint, and sanitized error. State what you changed and whether the result differed. “Reduced workers from eight to three; the same code persists” is a useful observation. “The provider banned my key” needs additional evidence.

For direct OpenAI error classification, continue with the [429 diagnostic guide](/blog/chatgpt-api-429-fix/). For planning worker demand, use the [capacity guide](/blog/openai-rate-limits-guide/).

**Correction, October 23, 2026:** Earlier versions treated this code family as universal, inferred direct OpenAI access from a plain 429, and presented unsupported batch-run and throughput anecdotes. The mappings here are now explicitly scoped to TokenHub, and the parsing examples are synthetic.
