---
title: "OpenAI 429001 Error: What It Means and How I Fixed It"
description: "Got a 429001 error from the OpenAI API or a Chinese model gateway? Here's what the 429001 subcode means and the exact backoff code I used to fix it."
pubDate: 2026-07-29
category: "llm"
tags: ["openai 429001", "429001 error", "rate limit", "api gateway error", "glm", "minimax"]
image: "/og-openai-429001-error-code-fix.jpg"
imageAlt: "Terminal showing a 429001 rate limit error response from an OpenAI-compatible API gateway"
keywords: ["openai 429001 error", "429001 rate limit fix", "api gateway 429 subcode"]
faq:
  - question: "Is 429001 an official OpenAI error code?"
    answer: "No. OpenAI returns a plain HTTP 429 with an error type like rate_limit_error. 429001 is a subcode used by OpenAI-compatible gateways and Chinese cloud providers (Tencent Cloud is the canonical example) that append a numeric code to the 429 status."
  - question: "What is the difference between 429001 and 429006?"
    answer: "429001 means you exceeded the gateway's rate threshold. 429006 means the upstream model service is busy or at capacity. 429006 usually needs a longer backoff because the problem is on the provider side, not your request rate."
  - question: "Does this apply if I call OpenAI directly?"
    answer: "If you only ever see a plain '429' with no subcode, you are talking to OpenAI directly. In that case 429001 does not apply and you should follow the general ChatGPT 429 fix. The 429001 subcode appears when a gateway sits between you and the model."
  - question: "Will retrying immediately fix a 429001 error?"
    answer: "No. Instant retries usually make it worse because the gateway may throttle your key harder. Use exponential backoff with jitter and respect any Retry-After header the gateway returns."
---

Last month I was running a LangChain batch job that called a GLM-5.2 endpoint through an OpenAI-compatible gateway. About 4,000 requests in, the whole thing died. But the error was not the plain `429` I had seen a dozen times before. It was `429001`.

I did what anyone does: I searched "openai 429001" and found almost nothing useful. Every guide treats 429 as one generic thing, and none of them mentioned a subcode. It took me a couple of frustrating hours to figure out that `429001` is a completely different animal from a normal OpenAI 429. This article is the explanation I wish I had that night.

## What 429001 Actually Is (and Why It's Not a Normal 429)

Here is the part that confused me the most. When you call OpenAI directly and get rate limited, you get an HTTP 429 and a JSON body that looks roughly like this:

```json
{
  "error": {
    "type": "rate_limit_error",
    "code": "rate_limit_reached",
    "message": "Rate limit reached for requests"
  }
}
```

That is a plain 429. The status code is the only signal, and the `code` field is a string like `rate_limit_reached`.

A `429001` is different. It is an HTTP 429 **plus a three-digit provider subcode**. You see it when you are NOT talking to OpenAI directly. You are behind a gateway, a proxy, or a Chinese cloud provider that wraps the upstream model (OpenAI, or a domestic model like GLM-5.2 or MiniMax M3) and returns its own numeric error codes. Tencent Cloud's API is the canonical example. In their docs, `429001` maps to `CodeRateLimitExceeded` with the note "request rate exceeded the current model threshold."

So the first thing to understand: if you are seeing `429001`, you are almost certainly behind a gateway. That changes the fix, because the gateway may not pass through OpenAI's `Retry-After` header, and it may rate-limit at its own layer (per-key, account-level) rather than at the upstream.

## The Full 429xxx Family (Save This Table)

Once I knew `429001` was a subcode, I dug into the provider docs and found the whole family. If you are seeing any of these, this table tells you what actually happened:

| Subcode | Name | What it means |
|---------|------|---------------|
| 429001 | CodeRateLimitExceeded | Request rate exceeded the current model threshold |
| 429002 | CodeRPMLimitExceeded | You exceeded requests-per-minute |
| 429003 | CodeTPMLimitExceeded | You exceeded tokens-per-minute |
| 429004 | CodeTPDLimitExceeded | You exceeded tokens-per-day |
| 429005 | CodeConcurrencyLimitExceeded | Too many concurrent requests |
| 429006 | CodeUpstreamRateLimitExceeded | The upstream model is busy or at capacity |

The two that matter most for day-to-day work are `429001` (the generic "slow down" code) and `429006` (the upstream is overloaded). They need different handling, which I'll get to in a second.

One honest caveat: not every gateway uses this exact numbering. Some proxies invent their own subcodes, and some just return a plain 429 with a weird message. The table above is the Tencent Cloud scheme, which is the most common one I have run into when calling Chinese models through an OpenAI-compatible endpoint. If your gateway's docs disagree, trust your gateway.

## How I Reproduced It (My Actual Setup)

I want to be specific about my setup, because the fix only makes sense in context. I was running a LangChain 1.x pipeline that wrapped a GLM-5.2 endpoint exposed through an OpenAI-compatible gateway. The job was a batch of roughly 5,000 calls, fired with 8 concurrent workers.

At around 4,000 requests, I started getting `429001` in bursts. My first instinct, like an idiot, was to retry immediately. That made it worse. Within a minute the gateway started returning `429006` as well, which I now understand meant it had flagged my key as "aggressive" and was throttling the upstream harder.

The mistake was assuming the gateway behaved like raw OpenAI. It does not. A gateway almost always has its own per-key RPM that is lower than the upstream model's limit, because the gateway is multiplexing many customers onto shared upstream capacity. So even if your code is "within OpenAI's limits," the gateway can still slam you with `429001`.

## The Fix — Exponential Backoff That Reads the Subcode

The working fix was a retry wrapper that does three things the naive version did not: it parses the subcode, it respects `Retry-After` if present, and it treats `429006` with a longer base wait. Here is the Python version I ended up with:

```python
import time
import random
import requests

def call_with_backoff(url, headers, payload, max_retries=6):
    base_wait = 2  # seconds
    for attempt in range(max_retries):
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 429:
            return resp
        # Try to read the gateway's subcode and Retry-After
        subcode = None
        try:
            subcode = resp.json().get("error", {}).get("code")
        except Exception:
            pass
        retry_after = resp.headers.get("Retry-After")
        if retry_after:
            wait = float(retry_after)
        else:
            # 429006 (upstream busy) needs a longer floor
            floor = 8 if subcode == "429006" else base_wait
            wait = floor * (2 ** attempt) + random.uniform(0, 1)
        print(f"429{subcode or ''} on attempt {attempt}, sleeping {wait:.1f}s")
        time.sleep(wait)
    raise RuntimeError("Exhausted retries after 429001/429006")
```

The jitter (`random.uniform(0, 1)`) matters more than people think. Without it, if you have 8 workers all hitting the limit at once, they all back off for the exact same duration and then all fire again simultaneously. That is how you create a self-inflicted thundering herd. A little randomness spreads them out.

I hand-rolled it instead of pulling in the `backoff` library because the gateway's subcode lives in the JSON body, not in an exception type, so a generic decorator did not catch it cleanly. If your gateway raises proper exceptions, the `backoff` library is fine too.

If you are doing this inside LangChain, the same logic goes in a custom `RunnableRetry` or a wrapper around your `ChatOpenAI`-compatible client. The point is not the framework, it is reading the subcode before you decide how long to wait.

## Three Changes That Actually Cut My 429001 Rate

After the backoff was in place, three more changes dropped my error rate from "constant" to "rare":

**Lower concurrency.** I went from 8 workers to 3. This was the single biggest win. The gateway's per-key RPM was the real bottleneck, not my upstream quota.

**Check the gateway dashboard, not your assumptions.** The gateway showed my effective RPM limit was about a third of what I expected. I had been sizing my worker pool off OpenAI's published numbers, which was wrong for the gateway layer.

**Spread across keys if the gateway allows it.** Some gateways give each API key its own limit. Splitting the batch across two or three keys (where permitted) tripled my real throughput without tripping `429001`.

One thing that did NOT help: cramming more into a single request to "reduce call count." That just pushed me into `429003` (TPM) instead. There is no free lunch; you are trading one limit for another.

## When 429001 Is Really a Quota Problem

Most `429001` errors are rate problems you can back off from. But there is a version that backoff will never fix: when you see it on the very first request of a brand-new key, or it persists even at one request per minute, it is usually an account quota or billing issue at the gateway, not a rate limit. The dashboard will tell you. Retrying just burns what little capacity you have.

I hit this once when a gateway wallet ran out of prepaid credits. No amount of backoff helped because the limit was "zero until you top up." Check billing before you blame your code.

## Summary

If you remember nothing else: `429001` is a gateway subcode, not a native OpenAI error. When you see it, you are behind a proxy or Chinese cloud provider that wraps the model. Read the subcode, back off with jitter, respect `Retry-After`, and lower your concurrency before you assume the upstream is the problem.

If you are calling OpenAI directly and only ever see a plain `429` with no subcode, this whole subcode thing does not apply to you. Head to the [general ChatGPT 429 fix](/blog/chatgpt-api-429-fix) instead. And if you want the bigger picture on how the limits are structured, the [OpenAI rate limits guide](/blog/openai-rate-limits-guide) is worth a read. For the LangChain-side setup that got me into this mess in the first place, I wrote up the [LangChain 1.x tool calling approach](/blog/langchain-1x-tool-calling-agents) separately.
