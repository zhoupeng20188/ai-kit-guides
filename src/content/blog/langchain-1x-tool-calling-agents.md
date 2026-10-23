---
title: "LangChain Tool Calling: A Bounded Agent with a Local Fixture"
description: "Build a small LangChain agent using a deterministic tool, configure a compatible provider explicitly, and inspect tool results without inventing live data."
pubDate: 2026-07-27
category: "java-ai-tools"
tags: ["langchain", "langchain 1.x", "tool calling", "langchain agents", "glm", "minimax", "openai compatible endpoint"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["langchain 1.x tool calling", "langchain agent glm", "langchain minimax", "langchain openai compatible endpoint", "create_agent langchain", "bind_tools langchain"]
updatedDate: 2026-10-23
---

LangChain tool calling connects a model request to code that the application executes. OpenAI-compatible HTTP syntax does not guarantee that every provider supports the same tool schema or returns identical messages.

This example uses a deterministic parcel-status fixture, avoiding invented financial quotes. It replaces snippets with undefined variables and an unlimited manual loop. It has not been run against a paid provider for this article.

## Record the dependency and provider versions

Use an isolated Python environment, install the packages required by your selected integration, and keep the resolved versions. The [LangChain agent documentation](https://docs.langchain.com/oss/python/langchain/agents) describes `create_agent`; the [tools guide](https://docs.langchain.com/oss/python/langchain/tools) describes typed tool inputs and results.

For an OpenAI-compatible endpoint, check its own documentation for base URL, model identifier, authentication, and tool support. Do not assume a GLM or MiniMax model label from an old article is still available on your account.

## Define a complete harmless tool

```python
from langchain_core.tools import tool

@tool
def parcel_status(reference: str) -> str:
    """Look up a parcel in a fixed teaching fixture; this is not live tracking."""
    states = {"DEMO-1": "packed", "DEMO-2": "dispatched"}
    return states.get(reference, "unknown reference")

assert parcel_status.invoke({"reference": "DEMO-1"}) == "packed"
assert parcel_status.invoke({"reference": "missing"}) == "unknown reference"
```

Run those assertions before involving a model. They check the fixture and tool wrapper, not model tool-selection quality.

## Configure the model explicitly

The following continuation uses `langchain-openai`. Set environment variables to the provider and model you intend to call. `OpenAI` protocol compatibility is an integration choice, not a claim that OpenAI operates the endpoint.

```python
import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

model = ChatOpenAI(
    model=os.environ["LLM_MODEL"],
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.environ["LLM_BASE_URL"],
    max_retries=0,
    timeout=30,
)
agent = create_agent(model=model, tools=[parcel_status])
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Check parcel DEMO-1 using the tool."}]},
    config={"recursion_limit": 20},
)
for message in result["messages"]:
    print(message)
```

This block makes a paid or metered network request when run with real credentials. It is an integration template, not evidence of a successful call to a particular provider. Keep keys outside source files and avoid logging secret-bearing responses.

## Inspect the exchange

Check whether the model issued a tool call, whether its arguments matched the schema, whether the tool executed, and whether the final answer reflects the result. A fluent answer saying “dispatched” is wrong for `DEMO-1`, even if it sounds plausible.

In a manual implementation, preserve tool-call IDs and return the corresponding tool-result message. Calling a tool with an argument dictionary can be valid when you handle message construction yourself; the earlier claim that only passing the whole call object is ever valid was too broad.

## Bound failure and retries

An invocation limit is not a complete cost budget. Also set timeouts, provider retry policy, and application-level limits. Handle an unknown tool, invalid arguments, tool failure, and repeated identical calls. A tool that changes external state needs authorization and duplicate-action handling beyond this harmless lookup.

If a gateway returns an unfamiliar numeric error, consult the [gateway diagnostic guide](/blog/openai-429001-error-code-fix/). The [429 guide](/blog/chatgpt-api-429-fix/) separates account action from temporary pressure.

Use the [loop guide](/blog/loop-engineering/) for stopping conditions and the [MCP overview](/blog/mcp-model-context-protocol-tutorial/) when tools come from a separate server. A small deterministic fixture makes the integration easier to debug before adding real data or side effects.
