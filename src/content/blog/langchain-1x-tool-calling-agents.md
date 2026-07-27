---
title: "LangChain 1.x Tool Calling & Agents: GLM + MiniMax via OpenAI Endpoint"
description: "How I wired LangChain tool calling and create_agent to GLM and MiniMax via the OpenAI-compatible endpoint — the bind_tools loop and the tool.invoke footgun."
pubDate: 2026-07-27
category: "ai-tools"
tags: ["langchain", "langchain 1.x", "tool calling", "langchain agents", "glm", "minimax", "openai compatible endpoint"]
image: "/og-langchain-1x-tool-calling.jpg"
imageAlt: "Wiring LangChain 1.x tool calling and agents to GLM and MiniMax through the OpenAI-compatible endpoint"
keywords: ["langchain 1.x tool calling", "langchain agent glm", "langchain minimax", "langchain openai compatible endpoint", "create_agent langchain", "bind_tools langchain"]
faq:
  - question: "Can I use this with OpenAI or Claude instead of GLM and MiniMax?"
    answer: "Yes. The tool-calling and agent code is identical — only the model name, base_url, and api_key change. Point model_provider at \"openai\" and set base_url to the vendor's OpenAI-compatible gateway, whether that vendor is OpenAI, Anthropic, GLM, MiniMax, Qwen, DeepSeek, or Moonshot."
  - question: "Do I need langgraph to build agents in LangChain 1.x?"
    answer: "No. create_agent ships in langchain.agents and handles the call-tool-loop-retry cycle on its own. langgraph is for when you need explicit, branching graph control (conditional edges, human-in-the-loop pauses, multi-agent handoffs) — overkill for a single tool-using agent."
  - question: "Why not just call the model API directly instead of LangChain?"
    answer: "You can, and for one isolated call it is simpler. LangChain earns its place when you compose pieces: a retriever feeding context, conversation memory, and one or more tools, all as reusable runnables. If you only need one model call, skip it; if you need a pipeline, the boilerplate it removes is real."
  - question: "Which is better for tool calling, GLM or MiniMax?"
    answer: "Both worked in my tests on real tool schemas. Tool-calling quality tracks the underlying model, so pick by price and latency for your case — the wiring is exactly the same. Always test edge cases (ambiguous arguments, missing fields) rather than assuming the model will fill them in."
---

I'm a Java engineer by day. When I want to validate an AI feature quickly, I reach for Python and LangChain — it is the fastest way to wire a model to tools and see whether an idea holds up. But nearly every LangChain tutorial I found assumed OpenAI or Claude, and none showed how to plug in **GLM** or **MiniMax**, the models I actually have API keys for. Most were also written against LangChain 0.1/0.2, so the snippets broke the moment I installed the current 1.x line.

This is the post I wish had existed: LangChain 1.2 (I verified on **1.2.15**), wiring tool calling and agents to GLM and MiniMax through their OpenAI-compatible endpoints, using code from a project I actually built.

## Why "1.x" matters more than you think

LangChain 1.0 shipped in 2025 and quietly changed two things that bite everyone copying old snippets:

1. The model entry point became `init_chat_model` (in `langchain.chat_models`), not hand-constructing `ChatOpenAI`.
2. The agent API became `create_agent` (in `langchain.agents`), replacing the old `create_react_agent` + `AgentExecutor` dance.

If you are on 1.x and following a 2023 blog post, you will fight import errors for an hour. **State your version.** Mine: `langchain==1.2.15`, `langchain-openai==1.1.12`, `langchain-community==0.4.1`, `langgraph==1.1.6`.

## One model factory for every provider

The trick that unblocks GLM and MiniMax: both expose an **OpenAI-compatible endpoint**. You tell LangChain the provider is `"openai"` and point `base_url` at their gateway. LangChain does not care that the model behind it is not GPT.

```python
# init_llm.py
from langchain.chat_models import init_chat_model

minimax_llm = init_chat_model(
    model="MiniMax-M2.5",
    model_provider="openai",
    api_key=MINIMAX_API_KEY,
    base_url=MINIMAX_BASE_URL,
)

glm_llm = init_chat_model(
    model="glm-4.7-flash",
    model_provider="openai",
    api_key=GLM_API_KEY,
    base_url=GLM_BASE_URL,
)
```

Two footguns here:

- **The model name is vendor-specific, not LangChain-specific.** `"glm-4.7-flash"` and `"MiniMax-M2.5"` are exactly what those vendors' endpoints expect. Copy a name from an OpenAI tutorial and it returns a 400.
- **People assume LangChain only "natively" supports OpenAI/Anthropic.** It does not — the OpenAI-compatible endpoint trick works for any vendor that speaks that protocol (GLM, MiniMax, Qwen, DeepSeek, Moonshot, and so on).

I keep both clients in one module so every demo imports `glm_llm` / `minimax_llm` instead of re-declaring keys in every file.

## Defining tools the way the model actually reads them

A tool in LangChain is just a function with the `@tool` decorator. The docstring is **not for you** — it becomes the tool description the model uses to decide *when* to call. Write it like an API spec.

```python
from langchain_core.tools import tool

@tool
def get_stock_price(company: str, time: str = "today") -> str:
    """Get the stock price for a company on a given day.

    Args:
        company: the company name, e.g. "Apple"
        time: "today", "yesterday", or "month"
    """
    # ... mock lookup ...
    return f"{company} {time} price is {price}"
```

If the docstring is vague, the model guesses wrong about when to call — or never calls at all. This is the #1 reason "my tool isn't being invoked" questions exist.

## Manual tool calling: bind_tools + the while loop

Before you use an agent, understand what an agent *is*. The model never calls your function. It only emits *"I need to call get_stock_price with company=Apple"*. Something has to execute that, append the result, and call the model again. You can do that by hand:

```python
from langchain_core.messages import HumanMessage

llm_with_tools = glm_llm.bind_tools([get_stock_price, search_news])

messages = [HumanMessage(content="Apple's stock price and news today")]
while True:
    res = llm_with_tools.invoke(messages)
    messages.append(res)
    if not res.tool_calls:
        break
    for call in res.tool_calls:
        tool = {"get_stock_price": get_stock_price, "search_news": search_news}[call["name"]]
        result = tool.invoke(call)   # <-- pass the WHOLE tool_call object
        messages.append(result)
```

This is you reimplementing the agent loop. Full control, full visibility into every step.

## The footgun: tool.invoke(call), not tool.invoke(call["args"])

Notice `tool.invoke(call)` passes the **entire** `tool_call` object, not just `call["args"]`. I burned time on this. The `tool_call` carries `name`, `args`, **and** `id`. LangChain uses `id` to match the result back to the right call in the message history. Drop it and the model sees a tool result with no `tool_call_id` — and either errors or silently ignores it.

So: pass the object. Let LangChain slice out `args` for you.

## Debugging: what the model actually returns

Before the loop runs, it pays to see exactly what the model emitted. `res.tool_calls` is a list of dicts, each carrying `name`, `args`, and `id`:

```python
res = llm_with_tools.invoke([HumanMessage(content="Apple's price today")])
for call in res.tool_calls:
    print(call["name"], call["args"], call["id"])
# get_stock_price {'company': 'Apple', 'time': 'today'} call_abc123
```

When that list is empty, the model decided no tool was needed — almost always because the docstring was too vague or the question didn't actually match the tool. Print this once and you skip the "why isn't it calling anything?" spiral entirely.

## Common failure modes

- **Tool is never called.** The docstring is vague, or the model thinks it can answer from pretraining. Rewrite the docstring as an imperative, specific sentence.
- **400 on the model name.** You passed an OpenAI model id to a GLM endpoint. Use the vendor's exact model string (`glm-4.7-flash`, not `gpt-4o`).
- **Tool result is ignored.** You passed `call["args"]` instead of `call`, so `tool_call_id` is missing and the model can't associate the result with its request.
- **Agent loops forever.** A tool returns text that makes the model call the same tool again. In the manual loop, add a max-iteration cap; in `create_agent`, the built-in retry usually bounds it, but a misbehaving tool still needs fixing at the source.

## Letting create_agent own the loop

For prototypes, hand-rolling the loop is tedious. `create_agent` does it for you — including a retry mechanism if a tool throws:

```python
from langchain.agents import create_agent

agent = create_agent(model=glm_llm, tools=[get_stock_price, search_news])
result = agent.invoke({"messages": [HumanMessage(content="Apple's stock price and news today")]})
```

Internally it runs the same loop: call model → if tool calls, execute → feed results back → repeat, with retry on failure. About 10 lines instead of ~40.

## Manual loop vs create_agent: which to use

The model never calls tools. It only *asks*. The question is who runs the loop:

- **Manual `bind_tools` + `while`** — use when you must inspect or constrain each step. A tool call is still just text the model generated, and it can call the wrong tool or pass a bad argument; the manual loop is where you add logging, allow-lists, and a human checkpoint. The same caution applies to trusting any model output — see my notes on the [habits that catch AI mistakes](/ai-hallucination-tips).
- **`create_agent`** — use for prototypes and internal tools where speed beats control.

Either way, what you are building is a [harness](/harness-engineering): a structured environment of constraints and verification wrapped around the model, not just a prompt.

## Caveats from real use

- The snippets above use mock data. Production tools need real implementations **and** error handling — a tool that throws becomes an agent that spins.
- GLM and MiniMax tool-calling quality is good but not identical to GPT-4-class models. Test edge cases (ambiguous arguments, missing fields).
- 1.x is young. Pin versions. I keep a `uv.lock` so the environment reproduces exactly.
- Streaming tool calls and parallel tool execution are out of scope here, but both are supported — start from `bind_tools` and add from there.

## What I'd build next

If this is your first LangChain 1.x agent, the natural next step is giving it memory (multi-turn conversations) or wiring it to a retriever for RAG. Both compose with the same `bind_tools` / `create_agent` primitives — the model factory and tool definitions you wrote here carry over unchanged.
