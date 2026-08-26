---
title: "Filesystem MCP Server + Claude Code for Spring Boot (2026)"
description: "How I wired the Filesystem MCP server into Claude Code for Spring Boot: scoped directories, a --read-only guardrail, and the generated-code traps I hit."
pubDate: 2026-08-26
category: "ai-tools"
tags: ["claude code", "mcp", "filesystem mcp", "spring boot", "java ai tools", "java-ai-cluster"]
image: "/og-mcp-filesystem-claude-code-java.jpg"
imageAlt: "Terminal showing a Spring Boot project's .mcp.json next to Claude Code, with the filesystem MCP server scoped to the src directory"
keywords: ["filesystem mcp server claude code", "claude code mcp spring boot", "mcp filesystem java", "claude code spring boot setup", "filesystem mcp server", "spring boot ai coding"]
faq:
  - question: "Doesn't Claude Code already read and write files? Why add the Filesystem MCP?"
    answer: "It does, and for solo Spring Boot work the built-in Read/Write tools are usually enough. I reach for the Filesystem MCP when I want a separate, tighter boundary: a read-only scope so Claude can browse the codebase but cannot touch anything, a per-module scope so a subagent only sees one slice of a monorepo, or a setup I can commit to the repo so the whole team gets the same guardrails. It is a control surface, not a replacement for the built-in tools."
  - question: "Is the Filesystem MCP server safe to point at a Java project?"
    answer: "Yes, if you scope it. The server only touches the directories you pass as absolute paths on the command line and it validates symlinks to stop path traversal. The single most useful safety switch is --read-only, which disables write, edit, create, and move tools so Claude can read your Spring Boot code but cannot change it. The standard server has no delete tool at all, so the real risk is an accidental overwrite, not a deletion. I keep generated output like target/ and build/ outside the allowed scope entirely."
  - question: "Can the Filesystem MCP server delete my files?"
    answer: "The official @modelcontextprotocol/server-filesystem implementation does not expose a delete tool. It can write, edit, create directories, and move files, so an overwrite is possible, but there is no direct 'delete everything' switch. Combined with --read-only for everyday browsing and a git diff review before any commit, the blast radius stays small. If you need deletion, you are better off running it as an explicit shell command you can see and approve."
---

I'll be honest up front: for the first few months of using Claude Code on my Spring Boot work, I never touched MCP. Claude Code already reads and writes files through its built-in tools, and that covered what I needed. The Filesystem MCP server earned its place only after I wanted a *tighter, separate* boundary than "give the agent the whole project." This is the setup I landed on, what `--read-only` actually buys you, and the ways it quietly wasted an afternoon.

## Why I Added It at All

The built-in file tools in Claude Code are convenient but blunt. When you start a session, Claude can read and edit anywhere in the repo you've opened. For a single-developer side project that's fine. For a multi-module Spring Boot monorepo with generated code, tests, and config scattered across a dozen folders, "anywhere" is more access than I want to hand over by default.

The Filesystem MCP server, the official `@modelcontextprotocol/server-filesystem` package, gives me a clean second boundary. Instead of trusting the session-wide file access, I point a scoped server at exactly the directories I want Claude to see. The server can't escape those paths, it validates symlinks, and with one flag it becomes read-only. That's a different shape of safety than "just be careful," and it's why I bother.

If you want the broader Claude Code baseline first, I wrote about [Claude Code on Spring Boot](/blog/claude-code-spring-boot/) and the deeper "teach the agent your codebase" angle in [making Claude Code remember a Spring Boot project](/blog/claude-code-remember-spring-boot/). This article is the file-access layer underneath those.

## The Setup That Actually Worked

Claude Code reads MCP servers from a `.mcp.json` file at your project root. Commit it and the whole team gets the same servers. The minimal filesystem entry looks like this:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/absolute/path/to/your/project/src",
        "/absolute/path/to/your/project/pom.xml"
      ]
    }
  }
}
```

Each path after the package name is an *allowed root*. The server rejects anything outside them. Use absolute paths every time — relative paths resolve against the process working directory when Claude Code spawns the server, which is not always your repo root, and that mismatch produces confusing "path not allowed" errors.

You can also add it from the CLI without touching a file:

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /abs/path/to/src
```

Either way, restart the session and run `/mcp` inside Claude Code. You should see `filesystem` listed with its tools: `read_file`, `list_directory`, `directory_tree`, `search_files`, `get_file_info`, and the write side — `write_file`, `edit_file`, `create_directory`, `move_file`.

## The `--read-only` Guardrail

This is the part I wish I'd set up on day one. The server accepts a `--read-only` flag that disables every write tool. Point it at your source and Claude can browse, search, and read to its heart's content, but it physically cannot modify a file through that server.

```json
"args": [
  "-y",
  "@modelcontextprotocol/server-filesystem",
  "--read-only",
  "/abs/path/to/project/src"
]
```

For day-to-day "help me understand this bean wiring" or "find every place we call this service" work, I run read-only. I only drop the flag for a narrow, deliberate task where I actually want edits, and even then I scope to the single module I'm touching. After a refactor I run a `git diff` before committing anything, which has saved me more than once.

One thing worth knowing: the standard server has **no delete tool**. It can overwrite via `write_file` and `edit_file`, and it can move files, but there's no "rm -rf" switch. So the real risk is an accidental overwrite, not a mass deletion. Combined with `--read-only` for browsing and a diff review before commit, the blast radius stays small.

## Stopping the Permission Prompts

The first time I ran it, Claude paused to ask for approval on every single read. That gets old fast on a Spring Boot project where a single question can trigger a dozen file lookups. You can pre-approve the read-only tools in `.claude/settings.json` so browsing stays silent:

```json
{
  "permissions": {
    "allow": [
      "mcp__filesystem__read_file",
      "mcp__filesystem__list_directory",
      "mcp__filesystem__directory_tree",
      "mcp__filesystem__search_files"
    ]
  }
}
```

The tool name is `mcp__` plus the server name from your `.mcp.json`, plus the tool name, separated by double underscores. Run `/mcp` to see the exact identifiers your server exposes and match them. I only pre-approve the read tools here — the moment I add `write_file` or `edit_file` to that allow list, I've rebuilt the exact footgun I used `--read-only` to avoid, so I leave writes on the interactive prompt where I can see them.

## A Read-Only Session in Practice

To make the boundary concrete, here's a session I ran last week. I scoped the server to `src` on read-only, then asked: "Map how a POST to `/api/orders` flows from the controller through the service to the repository, and tell me which class validates the request body." Claude used `directory_tree` to see the package layout, `read_file` on the three layers, and `search_files` to find the `@Validated` annotation. It came back with a correct call graph and even flagged that the DTO validation lived in the wrong layer — all without writing a single byte. That's the sweet spot: deep read access, zero write risk, and a `git status` that stayed clean the entire time.

The contrast is what sold me. Before the scoped server, the same question would have Claude pawing through `target/classes` and the `.gradle` cache, and I'd be one careless "yes" away from an edit I didn't intend. Now the read-only scope is the default posture, and editing is an explicit, reviewed step-up.

## Spring Boot Specifics That Bit Me

A vanilla Spring Boot project has a lot of files you do *not* want an agent reading or writing. Maven dumps compiled classes into `target/`, Gradle into `build/`, and both pull dependency trees into `node_modules` or `.gradle` caches. If you point the filesystem server at the repo root, Claude will happily slurp thousands of generated `.class` files into context, your responses get worse, and you've paid for tokens describing bytecode nobody asked about.

My fix is to scope the allowed directory to `src` plus the build file, and leave `target/`, `build/`, and `.git` out of the root list entirely. The server does not respect `.gitignore`, so "out of scope" is the only reliable exclusion:

```json
"args": [
  "-y",
  "@modelcontextprotocol/server-filesystem",
  "--read-only",
  "/abs/path/to/project/src",
  "/abs/path/to/project/pom.xml"
]
```

For a multi-module Maven project (`module-api`, `module-service`, `module-web`), I'll often scope to the one module I'm actively working in. That keeps the directory tree small and stops Claude from "helpfully" editing a sibling module's code when my task was only about one. When I do want cross-module edits, I widen the scope deliberately and review the diff.

## The Traps I Hit

**Trap 1: whole-repo scope blew up the context.** My first config pointed at the project root. Claude read `target/classes`, generated `*.properties`, and a 4 MB `node_modules` index. The next answer was vague and slow. Scoping to `src` fixed it in one edit.

**Trap 2: a refactor overwrote a config file.** Without `--read-only`, I asked Claude to "clean up the configs" during a rename. It rewrote `application.yml` with a version that looked right but dropped two profiles. I caught it in `git diff` before committing. Now browsing is always read-only and edits happen on a deliberately widened, reviewed scope.

**Trap 3: relative paths resolved wrong.** I used `./src` in the args, and depending on how Claude Code started the server, the working directory wasn't the repo root. Half my reads failed with "path not allowed." Absolute paths ended the problem.

**Trap 4: it doesn't know Maven from Gradle.** The server is build-tool-agnostic. Tell it to "add a dependency" and it'll happily edit `pom.xml` when your project is Gradle, or vice versa. I encode the build tool and the "never touch the build file unless I say so" rule in `CLAUDE.md` (see the [remember your Spring Boot project](/blog/claude-code-remember-spring-boot/) writeup), and that single line has prevented more confusion than any MCP flag.

## When I Don't Bother

Honesty check: for most solo editing, I still just use Claude Code's built-in file tools. The Filesystem MCP is overhead I skip unless one of these is true — I want a read-only browse boundary, I'm scoping a subagent to one module, or I'm setting up a repo-wide config the team should share. It also shines in CI or agent pipelines where you want to hand a non-interactive process a strictly limited file surface. If none of that applies, the built-in tools are simpler and just as capable.

## Summary

The Filesystem MCP server is not a replacement for Claude Code's file access — it's a finer-grained control surface. The setup that works for my Spring Boot projects: commit a `.mcp.json`, use absolute allowed paths, keep `target/` and `build/` out of scope, and default to `--read-only` with deliberate widening for real edits. Pair it with a solid `CLAUDE.md` so the agent knows your build tool and your "don't touch this" rules, and you get a setup that's both productive and hard to break. For the full Java+AI picture, start from the [Java + AI hub](/blog/ai-for-java-developers/).
