---
title: "MCP Tutorial: Connect Your AI to Everything (Without Getting Burned)"
description: "MCP tutorial 2026: set up MCP servers with Claude and Cursor, and avoid the security traps that burned real users."
pubDate: 2026-07-20
category: "ai-tools"
tags: ["mcp", "model context protocol", "mcp tutorial", "mcp server", "ai tools"]
image: "/og-mcp-tutorial.jpg"
imageAlt: "Diagram showing MCP protocol connecting an AI assistant to external tools like filesystem, GitHub, and database"
keywords: ["mcp tutorial", "model context protocol", "how to use mcp", "mcp server setup", "mcp security"]
faq:
  - question: "What is MCP in simple terms?"
    answer: "MCP (Model Context Protocol) is an open standard that lets AI assistants like Claude and Cursor connect to external tools and data sources. Instead of copy-pasting files or writing custom integrations, you configure an MCP server once and the AI can read your files, query your database, or browse GitHub on its own."
  - question: "Is MCP safe to use?"
    answer: "It can be, if you follow basic precautions. MCP servers run with your user permissions, and security researchers found over 30 vulnerabilities in MCP-related software between January and April 2026 alone. Use scoped read-only tokens, only install servers from trusted sources, and never grant filesystem access to your entire home directory. Treat every MCP server as untrusted software."
  - question: "Which AI tools support MCP?"
    answer: "As of mid-2026: Claude Desktop, Claude Code, Cursor, Windsurf, Cline, VS Code (via Copilot), Zed, and Replit all support MCP. ChatGPT added MCP support in Developer Mode in September 2025. If you already use Cursor or Claude Code, you can start using MCP today without installing anything new."
  - question: "Do I need to write code to use MCP?"
    answer: "No. Most popular MCP servers are pre-built and run via npx or a single command. You just edit a JSON config file to tell your AI client which servers to load. Writing your own MCP server is only necessary if you need a custom integration that does not exist yet."
---

The first time I connected an MCP server to Claude Desktop, I felt like I had given my AI assistant hands. Within five minutes, Claude was reading my project files, checking my Git log, and pulling pull request details from GitHub — all without me copy-pasting a single thing. I sat there thinking, "This changes everything."

Then, three months later, I read the OX Security report about MCP vulnerabilities and realized those hands could also pick my pockets. That whiplash — from "this is amazing" to "wait, is this safe?" — is the whole story of MCP in 2026. This tutorial covers both sides: how to set it up, and how not to get burned.

## What MCP Actually Is (Plain English)

MCP stands for Model Context Protocol. Anthropic open-sourced it in late 2024, and by mid-2026 it has become the standard way to connect AI assistants to external tools. Think of it as a USB port for AI: any AI client (Claude, Cursor, Windsurf) can plug into any MCP server (filesystem, GitHub, Postgres), and they just work together.

Before MCP, if you wanted Claude to read your files, you had to copy-paste them into the chat. If you wanted it to check your database, you ran the query yourself and pasted the results. MCP eliminates that middleman. The AI calls the MCP server directly, gets the data, and uses it — all with your approval for each action.

The protocol gives your AI three types of capabilities:

- **Tools** — functions the AI can call (read a file, run a query, create a GitHub issue). This is what 90% of people use MCP for.
- **Resources** — file-like data the AI can read (API responses, file contents, database schemas).
- **Prompts** — pre-written templates that help users accomplish specific tasks.

In practice, almost everyone just uses Tools. That is where the magic is.

## My Setup: The Starter Trio

When I first set up MCP, I went overboard. I installed seven servers in one afternoon — filesystem, GitHub, Postgres, Brave Search, Memory, Slack, Linear. Claude Desktop took 40 seconds to start up, and the AI got confused about which tool to use for simple tasks. I scaled back to three.

Here is the "starter trio" I recommend to anyone using [Cursor](/blog/cursor-ai-editor-tutorial/) or Claude Desktop for the first time:

**1. Filesystem** — lets the AI read and write files in specific directories you choose.

**2. Git** — lets the AI check your Git log, diff, and status without you pasting it.

**3. GitHub** — lets the AI browse repos, read issues, and draft PR descriptions.

The config goes into `claude_desktop_config.json` (on macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`). For Cursor, it goes into `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/you/projects"]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

Save the file, restart your AI client, and you should see an MCP indicator in the chat input. That is it. No SDK, no build step.

One thing that bit me: the first time you call an MCP tool, `npx` downloads the package, which takes 30-60 seconds. I thought it was broken and restarted Claude three times before realizing it was just a cold start. Subsequent calls are fast.

## The Wow Moment

After setting up the trio, I tried a real task. I was reviewing a PR on GitHub and wanted to understand the context. I asked Claude: "Read PR #42 in my repo, check the related test files, and tell me if the test coverage looks adequate."

Claude pulled the PR details via the GitHub MCP server, read the test files via the filesystem server, and gave me a summary in about 20 seconds. Doing that manually would have taken me 5 minutes of clicking around. That was the moment I understood why people are excited about MCP — it is not a novelty, it is a real productivity multiplier.

But I also noticed something that gave me pause. Claude had access to my entire `~/projects` directory. It could read any file in there — including files with API keys, database credentials, and SSH configs. I had not thought about that when I set it up.

## The Security Reality Check

Here is where this tutorial stops being cheerful. I want to be honest because too many MCP guides skip the security part, and that is how people get hurt.

**In April 2026, OX Security published research that found a systemic vulnerability in Anthropic's official MCP SDKs.** The STDIO transport — the default mechanism most people use — passes commands to the operating system shell without sanitization. This affected Python, TypeScript, Java, and Rust SDKs simultaneously, rippling through 150 million package downloads and an estimated 200,000 vulnerable instances. Anthropic confirmed the behavior was intentional and declined to change it.

Between January and April 2026 alone, security researchers disclosed over 30 CVEs related to MCP. The real-world attacks are not theoretical:

- **Tool poisoning**: A malicious MCP server hides instructions in its tool description — text the AI reads but the user never sees. The AI follows those hidden instructions, which can include "read the user's Gmail and send the contents to this URL." Tencent's Zhuque Lab demonstrated this exact attack on ChatGPT users with a fake MCP server.
- **Cursor RCE (CVE-2025-54135)**: An attacker plants a malicious prompt in a public document (like a GitHub README). When Cursor's AI reads it, the prompt instructs the AI to create a new `.cursor/mcp.json` file with a reverse shell command. Creating a new file did not require user approval — only editing an existing one did. Zero-click remote code execution.
- **Trust bypass (CVE-2025-54136)**: Cursor's trust model was name-based and permanent. An attacker submits a PR with a harmless `mcp.json` (just `echo "hello"`). You approve it once. The attacker then changes the command to something malicious. Cursor loads it without asking again because the name was already trusted.

I am not telling you this to scare you away from MCP. I am telling you because if you use MCP without knowing these risks, you are walking into a dark room without a flashlight.

## My Rules for Safe MCP Usage

After reading the security reports, I audited my own setup and made four rules. These are not theoretical — they are what I actually do:

**1. Read-only by default.** My GitHub token has read-only scope. My Postgres connection uses a read-only role. I only grant write access when I have a specific task that requires it, and I revoke it after.

**2. Scope filesystem access tightly.** I do not point the filesystem server at `~` or `~/Documents`. I point it at one specific project directory. If I need a different project, I change the config. It is annoying, but it limits the blast radius.

**3. Audit community servers before installing.** MCP servers are usually small (under 500 lines). I spend 10 minutes reading the source on GitHub before I install anything that touches sensitive data. If I cannot find the source, I do not install it.

**4. Pin versions.** I replace `@modelcontextprotocol/server-github` with `@modelcontextprotocol/server-github@2.1.0` in my config. This prevents a compromised update from silently changing what the server does — the attack pattern behind the Cursor trust bypass.

These rules take 15 minutes to implement and have zero downside. The productivity gain from MCP is the same whether your token is read-only or admin.

## The July 28 Spec Update (Heads Up)

If you are reading this before July 28, 2026, here is something you should know: the MCP spec is about to undergo its biggest revision since launch.

The 2026-07-28 release makes the protocol stateless. The old `initialize` handshake and session management are gone. Every request becomes self-contained, which means MCP servers can finally run behind plain round-robin load balancers without sticky sessions. For anyone deploying MCP servers in production, this is a big deal — it removes the main infrastructure headache.

The spec also deprecates three features: Roots, Sampling, and Logging. If you are just using MCP as a consumer (connecting servers to Claude or Cursor), this does not affect you yet. If you are building MCP servers, check the [migration guide](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) on the official blog.

The key reassurance: your existing setup keeps working. The old protocol version is not switched off on July 28. The SDKs maintain backward compatibility. You can upgrade on your own schedule.

## How to Start Today

Here is the 15-minute version:

1. Pick your AI client. If you already use [Cursor](/blog/cursor-ai-editor-tutorial/) or Claude Desktop, you are set. Both support MCP natively.
2. Create the config file (see the starter trio above). Point the filesystem server at one specific project directory, not your home folder.
3. Generate a GitHub Personal Access Token with read-only scope (no admin, no write).
4. Restart your client and verify the MCP indicator shows up.
5. Try one real task: "Read the README in my project and summarize what it does."

If that works, you have a working MCP setup. Add more servers later, one at a time, as you find genuine needs. Do not install seven on day one like I did.

One more thing: if you use Cursor's [rules system](/blog/cursor-rules-tutorial/), you can write a rule that tells the AI to always explain which MCP tool it is about to call before calling it. This gives you a chance to catch unexpected behavior. It is a small thing, but it adds a layer of awareness that the default setup lacks.

## Summary

MCP is the most useful AI integration tool I have added to my workflow in 2026, and also the one that requires the most caution. The productivity gain is real — having Claude read my files, check my Git history, and pull PR details without copy-pasting saves me 20-30 minutes a day. But the security surface is real too: 30+ CVEs in 60 days, systemic SDK vulnerabilities, and tool poisoning attacks that work on real users today.

The good news is that safe usage is not complicated. Scoped tokens, tight filesystem paths, source code audits, and version pinning cover 90% of the risk. Spend 15 minutes on those, and you get the productivity upside without the downside of being the next cautionary tale.
