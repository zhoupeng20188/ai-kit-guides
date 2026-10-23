---
title: "Filesystem MCP with Claude Code: Scope Paths and Verify Access"
description: "Configure a filesystem MCP server for a small Java workspace, verify allowed directories, and avoid assuming an unsupported flag creates read-only access."
pubDate: 2026-08-26
category: "ai-coding-agents"
tags: ["claude code", "mcp", "filesystem mcp", "spring boot", "java ai tools", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["filesystem mcp server claude code", "claude code mcp spring boot", "mcp filesystem java", "claude code spring boot setup", "filesystem mcp server", "spring boot ai coding"]
updatedDate: 2026-10-23
---

A filesystem MCP server adds another path through which an assistant can access files. Use it when that extra integration serves a concrete task, not merely because the assistant already has file tools.

The earlier article recommended an unverified `--read-only` option and supplied a file path where the reference server expects allowed directories. Those examples have been removed. This guide follows the [reference server README](https://raw.githubusercontent.com/modelcontextprotocol/servers/main/src/filesystem/README.md) and keeps directory scope separate from read-only enforcement.

## Choose a disposable scope first

Create a small workspace containing a harmless Java file and a note. Keep credentials, production configuration, and unrelated repositories outside it. Start with that directory rather than your home folder.

The reference server accepts allowed directories as positional arguments. A client configuration might look like this:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/absolute/path/to/mcp-demo"
      ]
    }
  }
}
```

This is a configuration template. Replace the path, check the installed package version, and use your client's supported configuration mechanism. A floating package invocation can change over time; pin a reviewed version when reproducibility matters.

## Verify connection and directory access

Inspect the registered server and tool list using the client's diagnostics. Confirm that reading the harmless file succeeds and that attempting to read a harmless file outside the allowed directory is rejected.

Do not infer success only from a process starting. A server can launch with a wrong path, expose unexpected tools, or negotiate a different protocol version from the one assumed by an old tutorial. Keep connection errors and tool-call errors distinct.

## Directory scope is not read-only access

The reference server exposes write-capable operations. A directory allowlist does not turn those operations into reads. Do not add an undocumented `--read-only` flag and assume writes are impossible.

For a read-only requirement, use a server configuration that explicitly supports it, a verified client tool policy, and/or OS-level read-only mounts or permissions. Then attempt an innocuous write in a disposable copy and confirm denial. Merely omitting write tools from an “allow” list can still leave an interactive approval path depending on the client.

Other tools matter too. A shell command or a built-in file tool may reach data independently of MCP. Test the complete set of available capabilities before claiming an access boundary.

## Apply it to a Java review task

Ask the assistant to summarize a controller and its service using only the intended paths. Check every path it cites. For a multi-module project, supply the relevant module deliberately instead of granting access to every repository by default.

If the task requires a build, determine which tool executes the command and which permissions it uses. The MCP directory allowlist does not establish the JDK, Maven network access, or Docker availability of that command.

Use the [Claude Code workflow](/blog/claude-code-spring-boot/) for task setup, the [memory guide](/blog/claude-code-remember-spring-boot/) for stable instructions, and the [Maven diagnostics](/blog/codex-sandbox-maven-spring-boot/) for environment failures.

## Keep the evidence and limitations visible

Record server version, client version, allowed paths, exposed tools, a successful read, and an out-of-scope denial. These are configuration checks, not a guarantee against every malicious tool response or privilege path.

The [MCP overview](/blog/mcp-model-context-protocol-tutorial/) explains the protocol components. The [Java hub](/blog/ai-for-java-developers/) connects this setup to review and verification tasks. A useful integration has a demonstrated access boundary, not an invented flag.
