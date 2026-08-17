---
title: "Claude Code + GitHub Actions for Spring Boot: Auto-Review PRs (2026)"
description: "How I wired Claude Code into GitHub Actions to auto-review Spring Boot PRs and fix failing CI builds — the real YAML, OAuth setup, and cost traps I hit."
pubDate: 2026-08-17
category: "ai-tools"
tags: ["claude code", "github actions", "spring boot", "ai coding", "ci/cd", "java-ai-cluster"]
image: "/og-claude-code-github-actions-spring-boot.jpg"
imageAlt: "GitHub Actions workflow running Claude Code to review a Spring Boot pull request, with an automated review comment posted on the PR"
keywords: ["claude code github actions spring boot", "claude code github actions", "claude code action spring boot", "automated pr review spring boot", "github actions claude code ci"]
faq:
  - question: "Can Claude Code run inside GitHub Actions for a Spring Boot project?"
    answer: "Yes. The official anthropics/claude-code-action@v1 runs the full Claude Code runtime headless inside a runner. On a Spring Boot repo it can open a PR, read the diff, post a review comment, or even fix a failing build and push the change back. It is a different setup from running Claude Code in your terminal, which I covered in my local workflow post."
  - question: "What is the difference between the Claude Code Action and using Claude Code locally?"
    answer: "Locally, Claude Code is an interactive agent on your machine that you drive prompt by prompt. In GitHub Actions it runs headless, triggered by CI events (a PR opens, a build fails), with no human at the keyboard. It posts results as PR comments or commits. Same model underneath, completely different execution model, and different guardrails."
  - question: "How much does the Claude Code GitHub Action cost?"
    answer: "Two billing paths: ANTHROPIC_API_KEY bills per token on your API account, while CLAUDE_CODE_OAUTH_TOKEN counts against your Claude Pro or Max plan. On Sonnet 5 a medium Spring Boot PR review runs roughly $0.50 to $2 depending on diff size. I pin Sonnet 5 in CI for cost and only reach for Opus 5 on gnarly multi-file fixes. Watch the first week of billing before scaling to every repo."
  - question: "Is it safe to let Claude Code commit from GitHub Actions?"
    answer: "Only with narrow permissions and hard limits. I grant contents: write plus a max-turns cap, never let it auto-merge, and I review the commit before it goes anywhere near main. An agent that can both edit and push is one bad loop away from a rough afternoon, so the push to main stays manual and the destructive commands stay blocked."
---

I use Claude Code on Spring Boot every day from my terminal. That setup, and the CLAUDE.md that makes it behave, is something I already wrote about. The thing that changed my week was moving that same agent out of my laptop and into GitHub Actions, so it reviews every pull request and patches a red build without me waking up to a broken main branch. This is the Claude Code GitHub Actions Spring Boot setup I actually run, including the parts that bit me.

This is not a "fully autonomous dev team" pitch. It is a specific, bounded use: let Claude read the diff on each PR and tell me what is wrong, and let it fix the build when CI goes red. Two workflows, a token, and a couple of traps I learned the expensive way.

## Why I moved Claude Code from my terminal into CI

The terminal agent is great when I am at the keyboard and can read the diff five seconds later. It is useless at 2am when a teammate merges a PR that breaks the integration test, or when three PRs open while I am in a meeting and nobody gets a second opinion before approving.

What I wanted was consistency, not magic. A reviewer that looks at every PR with the same eye, never gets tired, and never skips the test check because it is late. GitHub Actions is the natural place for that because it already sees every PR and every build result. Claude Code is the natural agent because it can actually run `./mvnw test` and read its own failure instead of guessing from a log snippet.

So the goal was narrow: PR review on every change, and auto-fix on CI failure. Everything else stays with a human.

## The one command that gets you 80% there

If you have the Claude Code CLI installed, the fastest start is one command inside the repo:

```bash
claude /install-github-app
```

It installs the Anthropic GitHub App, writes a `claude.yml` (interactive, triggered by `@claude` in comments) and a `claude-code-review.yml` (auto-review) into `.github/workflows/`, and sets the secret for you. For most people that is enough to start.

Here is the trap I hit, and it cost me a day of confusion. The auto-installed review workflow ships with `pull-requests: read`. That means Claude can read the PR but is not allowed to post a comment. The run went green, no error, and I saw nothing on the PR for two days. I thought the action was just quiet. It was silently blocked. Change that permission to `write` or the review never appears. I now write the workflow by hand so I never inherit that default again, and because I want the token choice and model pin to be explicit.

For auth you have two options. `ANTHROPIC_API_KEY` bills per token on your API account. `CLAUDE_CODE_OAUTH_TOKEN` counts against a Claude Pro or Max plan instead, generated with `claude setup-token` (needs claude-code-action v1.0.44+). I use the OAuth token because I already pay for Max, but I keep a close eye on it, which I get to below.

## Workflow 1: automated PR review on every Spring Boot PR

This is the workflow I actually keep. It reviews every opened or updated PR and posts one terse comment with `file:line` pointers.

```yaml
name: Claude PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened]
permissions:
  contents: read
  pull-requests: write
jobs:
  review:
    if: github.actor != 'dependabot[bot]'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          model: sonnet
          max-turns: 15
          prompt: |
            Review this Spring Boot PR diff against the base branch.
            Check transaction boundaries, N+1 queries, missing tests,
            Bean Validation placement, and whether it compiles.
            Be terse. Post one review comment with file:line pointers.
          post-comment: true
```

Two details that are not optional in my experience.

First, `fetch-depth: 0`. My first version used the default shallow checkout, and the review commented on the entire codebase instead of just the changes, because Claude only had the PR head and no base to diff against. Full history fixed it. The extra checkout time is seconds; the wrong-review noise was hours.

Second, `model: sonnet`. As of August 2026 Claude Code's default model is Opus 5, which is the stronger model for hard refactors. But for a high-volume PR review that runs on every push, Sonnet 5 is the right call: it is good enough to catch transaction and test gaps, and it is far cheaper per run. I reserve Opus 5 for the few PRs that are genuinely large or architectural.

The `max-turns: 15` cap matters too. Without it the agent can loop on a confusing diff and burn tokens exploring. Fifteen turns is plenty to read the diff and write one comment.

## Workflow 2: let it fix the failing build in CI

The second workflow fires only when the build fails, checks out the branch, reads the failure, and pushes a fix if the build goes green. This is where the value is real, because a red build used to sit until I noticed it.

```yaml
name: Claude Fix CI
on:
  workflow_run:
    workflows: ["Build"]
    types: [completed]
jobs:
  fix:
    if: github.event.workflow_run.conclusion == 'failure'
    permissions:
      contents: write
      pull-requests: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_branch }}
          fetch-depth: 0
      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          model: sonnet
          max-turns: 20
          prompt: |
            The Build workflow failed. Read the failure log, find the
            broken test or compile error, fix it, run ./mvnw -q test,
            and only commit if the build is green. Do not touch
            unrelated files.
```

I lean on this hard for the boring failures: a test that broke because of a renamed field, a missing import after a merge, a flaky assertion with an obvious cause. Claude reads the log, fixes the one file, runs the build, and only commits on green. For anything that touches the database migration or a public API, I would rather do it myself, and the prompt's "do not touch unrelated files" line keeps the diff small enough to review in thirty seconds.

If you want the agent to write the tests in the first place, that is a different muscle. I have a separate post on [getting AI-written JUnit tests to actually be worth something](/blog/ai-junit-tests/) because a green build is only as good as the assertions behind it.

## The cost traps I hit

This is the part nobody warns you about until the bill shows up.

The OAuth token is not free. It draws from your Max usage budget, and if you point auto-review at five repos, the same token is also what your local Claude Code session uses. I turned on auto-review across four repos on a Monday and by Wednesday my local sessions were getting throttled because the CI runs had eaten the weekly allowance. The fix was simple: I moved the high-volume repos to `ANTHROPIC_API_KEY` billing and kept OAuth only on the one repo I work in daily. Lesson learned, and it only cost me a frustrated afternoon.

Sonnet 5 promo pricing of $2 per million input and $10 per million output is scheduled to revert to $3/$15 on September 1, 2026. If you are budgeting CI across many repos, model that now. For my scale, a medium Spring Boot PR review lands around $0.50 to $2 on Sonnet 5, and a team running fifty PRs a month is usually in single-digit dollars. That is cheap insurance against a broken main branch, but it is not zero, and it is not the OAuth "free" that some setup guides imply.

The other trap is runaway loops. An agent that cannot solve a flaky test will happily retry, re-read, and re-edit until the token budget is gone. The `max-turns` cap is the only thing standing between you and a $20 review of a test that was broken by design. Keep it tight.

## What I still don't let it do

I am deliberately conservative here, because an agent with write access is a different risk class from one in my terminal.

I do not let it auto-merge. Ever. It can post a review and it can push a fix to a branch, but merging to main is a human decision. A green build means it compiles and the tests it wrote pass, not that the change is correct or wanted.

I do not let it touch database migrations or Kubernetes manifests in CI. Those have blast radius beyond the repo, and I want a person who understands the rollback story to own them. The prompt scope keeps it to application code.

I still read the diff. The PR review comment is a starting point, not a verdict. When Claude flags a transaction boundary or a missing `@Transactional`, I go look, because it is right often enough to trust but wrong often enough to verify. The full map of what AI code review misses on Java is its own topic, and it applies just as much to an agent in CI as to one on my laptop.

## Summary

Putting Claude Code into GitHub Actions for a Spring Boot project is a small change with an outsized payoff, as long as you keep it bounded. Install with `claude /install-github-app` but rewrite the workflow by hand so the review permission is `write`, set `fetch-depth: 0` so it diffs against the base, pin `model: sonnet` for cost, and cap `max-turns` so it cannot loop. Use OAuth if you already pay for Max, but watch the budget across repos, and switch busy repos to API-key billing before they throttle your local sessions. Let it review every PR and patch red builds, but keep the merge and the migrations with a human.

If you want the bigger picture of how I use AI across Java and Spring Boot, every tool and every failure mode is in my [AI for Java Developers guide](/blog/ai-for-java-developers/). The terminal workflow I started from is [here](/blog/claude-code-spring-boot/).
