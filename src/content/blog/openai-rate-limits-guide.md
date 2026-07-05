---
title: "OpenAI Rate Limits: How Much API Can You Afford?"
description: "Confused by TPM, RPM, and 5 different OpenAI tiers? Here's how rate limits actually work, what your real budget is, and how to check it right now."
pubDate: 2026-07-03
category: "chatgpt"
tags: ["openai rate limits", "openai api quota", "chatgpt api tpm rpm", "api tier system", "openai developer guide"]
image: "/og-openai-rate-limits-guide.jpg"
imageAlt: "OpenAI API rate limits dashboard showing TPM and RPM values across different tier levels"
keywords: ["openai rate limits", "openai api quota calculator", "openai tpm rpm", "openai tier system 2026", "chatgpt api limits"]
---

A few months ago I spent two hours debugging a "rate limit" error on a side project, only to discover the problem wasn't rate limiting at all — I had burned through my credits three days earlier and OpenAI was just politely telling me I was broke.

That's the dirty secret of OpenAI's rate limit docs: they make it sound like 429 is always about throttling, but there are actually **two completely different 429 errors** with the same status code, and they have totally different fixes. Mix them up and you'll waste an evening like I did.

This guide breaks down the real OpenAI rate limit system as of mid-2026: the 4 dimensions that actually matter (most docs only mention 2), the 5-tier system that determines your budget, and the exact way to check what your limit actually is right now. No fluff, no hand-waving. Just the stuff I wish someone had told me six months ago.

If you just want the quick fix for a 429 error, check out my [ChatGPT API 429 fix guide](/blog/chatgpt-api-429-fix) first. This article is more about understanding the system so you can stop hitting the limit in the first place.

## The 4 Dimensions of OpenAI Rate Limits (Not 2)

Every OpenAI doc mentions RPM and TPM. That's two dimensions. But OpenAI actually enforces **four**, and the other two will bite you the moment you go from a toy script to anything resembling a real workload.

Here's what each one means in plain English:

### RPM — Requests Per Minute

The simplest one. How many API calls you can make in any rolling 60-second window. This is the limit people hit first when they write a `for` loop that fires off 100 requests in a row.

The default limits (as of May 2026) are roughly:
- **Tier 1, GPT-5.4**: ~500 RPM
- **Tier 5, GPT-5.5**: ~15,000 RPM

Most people never come close to hitting TPM before they hit RPM on small requests. I personally never hit RPM on anything I built until I started doing batch processing for a customer support project.

### TPM — Tokens Per Minute

This is the one that actually matters for serious work. TPM is the total input + output tokens you can process per minute across all requests.

Why does it matter more than RPM? Because a single request to GPT-5.5 with 100k context can eat 5-10% of your entire Tier 1 TPM budget by itself. RPM will happily let you fire that request, but the API will reject it because you've blown your token budget.

Indicative numbers:
- **Tier 1, GPT-5.4**: ~500,000 TPM
- **Tier 5, GPT-5.5**: tens of millions of TPM

If you do a lot of long-context work — summarizing documents, RAG pipelines, code review of big files — TPM is what you'll hit first. Guaranteed.

### RPD — Requests Per Day

This is the one nobody talks about, and it's mostly enforced on free-tier accounts and certain older model snapshots. RPD is a hard daily cap on total API calls.

For Tier 1+ accounts on most modern models, RPD is effectively unlimited. But if you're on a free trial or using an older snapshot (like `gpt-4-turbo-2024-04-09`), you might hit this without warning.

I hit RPD once on a `gpt-3.5-turbo-instruct` call I forgot I was using. The error message was identical to a regular 429. Took me an embarrassing 20 minutes to figure out what was happening.

### TPD — Tokens Per Day

The fourth dimension, and the rarest to hit. TPD is a daily token cap, applied on some models. Mostly relevant on free trials and lower-tier model snapshots.

If you see a 429 at midnight and your code worked fine all day, you might be hitting TPD. Check the error message body — it tells you which dimension you hit.

## The 5-Tier System (and Why You Can't Skip Tiers)

OpenAI's rate limits scale with your cumulative spend. This is the part that confuses people the most, because there's a hard waiting period you can't bypass.

Here's the tier structure as of mid-2026:

| Tier | Qualification | Limits (indicative) |
|------|---------------|---------------------|
| **Free** | New account, no payment | Very low, model-dependent |
| **Tier 1** | $5 paid total | 500 RPM / 500K TPM (GPT-5.4) |
| **Tier 2** | $50 paid + 7 days since first payment | Higher RPM/TPM |
| **Tier 3** | $100 paid + 7 days | Significantly higher |
| **Tier 4** | $250 paid + 14 days | Near-Tier 5 levels |
| **Tier 5** | $1,000 paid + 30 days | 15K RPM / 10M+ TPM (GPT-5.5) |

The 7-day and 30-day waiting periods are hard floors. You can spend $10,000 on day one and **still wait the calendar days** before advancing. This is intentional — OpenAI uses the waiting period as a fraud check before giving out higher limits.

The frustrating part: tier advancement is automatic when you meet both criteria. There's no support ticket that speeds this up. If you're stuck at Tier 1 for two weeks and you've spent $200, you just have to wait for the time-based requirement to elapse.

A few strategies that work:

1. **Top up in larger increments.** A single $1,000 top-up counts the same as 200 $5 top-ups for tier qualification, but with way less platform friction.
2. **Avoid hitting zero balance.** If you start bouncing 429 `insufficient_quota` errors, your account looks unstable. Set up auto-recharge.
3. **Concentrate spend in one org.** Tier qualification is per-organization, not per-account. Spreading $1,000 across three orgs leaves all three stuck at Tier 3 or lower.
4. **Don't ask support to manually upgrade you.** OpenAI doesn't process manual tier upgrade requests for standard models. Your account manager can do it for enterprise contracts, but otherwise it's automatic.

## How to Check Your Real Limits Right Now

The fastest way to check your current limits is the response headers on any API call. Every successful response includes them. Most people don't notice because they're not errors.

Look for these headers on any chat completion call:

```
x-ratelimit-limit-requests: 500
x-ratelimit-limit-tokens: 500000
x-ratelimit-remaining-requests: 487
x-ratelimit-remaining-tokens: 423511
x-ratelimit-reset-requests: 38s
x-ratelimit-reset-tokens: 52s
```

These tell you your live budget in real time. I check them constantly when I'm building anything that does more than 10 requests in a session.

You can also see them in the platform UI under Settings → Limits, which shows the ceiling (not the live remaining). The response headers are more useful for real-time decisions.

There's also a third place: the 429 error response body. When you hit a limit, the body tells you exactly which dimension you hit and what your current usage is:

```json
{
  "error": {
    "message": "Rate limit reached for gpt-5.4 in organization org-xxx on tokens per min. Limit: 500000 / min. Current: 487234 / min.",
    "type": "rate_limit_exceeded",
    "code": "rate_limit_exceeded"
  }
}
```

Read that message carefully. If it says "tokens per min" you're hitting TPM. If it says "requests per min" you're hitting RPM. If it says "insufficient_quota" you're broke. Different problems, different fixes.

## The `insufficient_quota` Trap (Different Problem, Same Status Code)

This is the mistake I made the night I lost two hours. Both `rate_limit_exceeded` and `insufficient_quota` return HTTP 429. Same status code. Completely different problems.

- `rate_limit_exceeded`: "Wait a moment and try again. You have budget but you're using it too fast."
- `insufficient_quota`: "You're out of credits. Retrying won't help. Add money to your account."

The fix for `insufficient_quota` is to top up your account, not to back off and retry. I added a 60-second sleep to my script before realizing I was just delaying the inevitable.

How to tell them apart: check the `error.code` field in the response body. If it's `insufficient_quota`, your retry logic should bail immediately. If it's `rate_limit_exceeded`, retry with exponential backoff. Mixing these up will cost you hours of debugging like it did me.

## Estimating Tokens Before You Send (the Proactive Fix)

The cleanest way to avoid 429s is to slow yourself down before OpenAI does. Before each request, estimate the token count and check it against a local token bucket sized to your TPM.

For Python, use `tiktoken` to count input tokens, then add your `max_completion_tokens` setting to get the worst case:

```python
import tiktoken

def estimate_tokens(messages, model="gpt-5.4", max_output=1000):
    enc = tiktoken.encoding_for_model(model)
    input_tokens = sum(len(enc.encode(m["content"])) for m in messages)
    return input_tokens + max_output
```

If your estimated tokens would push you over your TPM budget, sleep until the window resets. The response headers tell you exactly when that is.

A single-process token bucket is fine for one script. If you have multiple processes or services all hitting the same OpenAI account, you need a shared bucket in Redis or a gateway. Otherwise each process thinks it has the full quota and they collectively blow past the limit.

## When You Outgrow the Limits: The Gateway Pattern

Past about 100 RPS sustained, in-process throttling stops being enough. The right architecture is multi-provider: OpenAI as primary, Azure OpenAI as secondary mirror (same models, separate rate-limit pool), and Bedrock or Vertex as tertiary.

The trick is doing this transparently to your app code. You point your OpenAI client at a gateway URL instead of `api.openai.com`, configure fallback rules on the gateway (primary: `openai/gpt-5.4`, fallback: `azure/gpt-5.4`, trigger on 429/5xx/timeout), and the gateway handles the rest. Your app code doesn't change.

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-gateway.example.com/v1",
    api_key=os.environ["GATEWAY_API_KEY"],
)

# Same code as before, gateway handles fallback
response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[{"role": "user", "content": "Hello"}],
)
```

When the gateway handles this, a 429 becomes a logline instead of a failed call. The client sees a successful response. If you're seeing fallback fire more than 5% of the time, you have a real capacity problem and should advance tiers or split traffic.

I haven't moved to a gateway myself yet — I'm still on a single OpenAI account with Tier 3 limits. But the moment I scale my side project past 50 RPS, that's my next step.

## Common Gotchas That Cost Me Hours

A few things that tripped me up while building this:

1. **Retrying on 4xx errors that aren't 429.** A 400 (bad request) is permanent. Retrying wastes time and clutters logs. Same for 401 (auth) and 403 (forbidden).
2. **Fixed `time.sleep(5)` between retries.** Works for one client. Causes a thundering herd when many clients hit the limit at the same time. Use jittered exponential instead.
3. **Not capping retry count.** A retry loop with no maximum will block your request handler indefinitely on a sustained outage. Always set `stop_after_attempt(6)` or similar.
4. **Ignoring `retry-after-ms` on the 429 response.** This header is more accurate than any heuristic. It tells you exactly when you'll have enough budget to retry. Honor it on the first attempt.
5. **Per-process token bucket in a multi-process service.** Each process thinks it has the full quota. Combined, you blow past the limit. Use a shared bucket or gateway.
6. **Conflating `insufficient_quota` with `rate_limit_exceeded`.** Different problem, different fix. Check the error code.

## FAQ

### How do I check my current rate limits?

Three places. The platform UI at Settings → Limits shows your ceiling. The response headers (`x-ratelimit-limit-*`) on any successful call show your live remaining budget. The 429 error body shows your current usage and which dimension you hit.

### Can I ask OpenAI for higher limits?

Limits scale automatically with spend and tier. There's no manual override for standard models. For enterprise contracts, your account manager can negotiate. Otherwise, the only way up is to spend more and wait for the tier timer to elapse.

### Does prompt caching count against TPM?

Yes. Cached tokens still count as input tokens for TPM accounting (you pay less for them, but they consume budget). Plan capacity accordingly if you use caching heavily.

### Are batch API calls subject to the same rate limits?

No. Batch has its own queue limit, separate from synchronous RPM/TPM. Submitting a batch with 100,000 requests does not block your live traffic. This is one of the biggest wins for cost reduction — see my [ChatGPT API 429 fix guide](/blog/chatgpt-api-429-fix) for the full batch workflow.

### What's the difference between `rate_limit_exceeded` and `insufficient_quota`?

Both return HTTP 429. The first means "wait and try again, you'll succeed." The second means "you're out of credits, retrying won't help." Check the `error.code` field to tell them apart.

### Should I retry on 500 errors?

Yes, with backoff. 500s are typically transient — same retry policy as 429. Don't retry 400, 401, or 403. Those are permanent.

### How do I shape traffic so no single feature starves the others?

Per-feature budgets in a gateway. OpenAI doesn't natively offer sub-account limits. A gateway lets you set RPM/TPM caps per user, feature, or workspace.

## Summary

The key things to remember:

- **4 dimensions, not 2**: RPM, TPM, RPD, TPD. TPM is the one that matters for real work.
- **5 tiers, with a hard time floor**: You can't skip the waiting period. Spend and wait.
- **`insufficient_quota` ≠ `rate_limit_exceeded`**: Same 429 status, totally different fix. Check the error code.
- **Read the response headers**: They tell you your live budget in real time. Check them on every call, not just errors.
- **Estimate tokens before you send**: A local token bucket sized to your TPM prevents 429s before they happen.

If you take one thing away: stop using fixed `time.sleep(5)` retries. They cause thundering herd problems and are the #1 reason 429s cascade across a system. Use exponential backoff with jitter, and honor the `retry-after-ms` header when it's present.

For the full retry code with `tenacity` and `p-retry` examples, see my [ChatGPT API 429 fix guide](/blog/chatgpt-api-429-fix). And if you're just getting started with the OpenAI API in general, my [ChatGPT beginner's guide](/blog/chatgpt-beginners-guide-2026) covers the basics.
