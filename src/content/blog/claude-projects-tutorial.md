---
title: "Claude Projects: How I Organized 50+ AI Chats"
description: "Claude Projects changed how I use AI. Here's how to set it up, what actually works, and the limitations nobody tells you about. Updated for Claude 4.7 in 2026."
pubDate: 2026-06-28
category: "llm"
tags: ["claude projects", "claude 4.7 tutorial", "ai workflow", "claude tips", "ai organization"]
image: "/og-claude-projects-tutorial.jpg"
imageAlt: "Claude Projects interface showing project sidebar with uploaded files and custom instructions"
keywords: ["claude projects tutorial", "claude 4.7 projects", "organize ai workflow", "claude custom instructions"]
---

I used to have 40+ separate ChatGPT and Claude conversations, all doing slightly different versions of the same task. One thread was helping me write blog posts. Another was reviewing my code. A third was summarizing research papers. And because Claude (and ChatGPT) doesn't remember anything between conversations, I was pasting the same context — my writing style, my codebase structure, my project goals — into every new thread like an idiot.

Then Claude Projects launched, and I realized I'd been doing it wrong for months.

If you've never used Projects, here's the simplest way to think about it: it's a dedicated workspace where Claude remembers your files, your instructions, and your conversation history — across *every* conversation in that project. No more pasting the same context 15 times.

Here's how I set it up, what actually works, and the limitations that annoyed me enough to write this.

## Setting Up Your First Project (It's Easier Than You Think)

Getting started takes about three minutes. Here's what I wish someone had told me before I created six messy projects and had to merge them.

**Step 1: Create the project**

In Claude.ai, click the "+" next to "Projects" in the left sidebar. Give it a name. I named my first one "AI Kit Guides Blog" — specific names are better than vague ones like "Work" or "Writing."

**Step 2: Write project instructions**

This is the part that matters most. Project instructions are like a permanent system prompt that Claude uses for every conversation in this project. I spent 20 minutes writing mine and it saved me hours of repeating myself.

Here's what I put in my "AI Kit Guides Blog" project instructions (you can steal this):

```
You're helping me write blog posts for AI Kit Guides, a site about practical AI tool tutorials.

My writing style:
- Conversational, first-person ("I", "my experience")
- Include real examples and mistakes I've made
- No corporate speak, no "in today's rapidly evolving landscape"
- Keep paragraphs short (2-3 sentences max)

My audience: beginners who want practical steps, not theory.

Always:
- Ask if you're unsure about my opinion on something
- Suggest internal links to other posts when relevant
- Keep posts between 1,000-2,500 words
```

The difference was immediate. Before Projects, I'd start every Claude conversation with "Okay, I'm writing a blog post, here's my style..." Now Claude just knows. It's like the difference between explaining your job to a new coworker every day vs. having a coworker who's been there for six months.

**Step 3: Upload your files**

This is the killer feature. You can upload files to a Project, and Claude can reference them in *any* conversation in that project. I uploaded:

- My `site.ts` config file (so Claude understands my blog's structure)
- Three example blog posts I'd written (so it learns my style from real examples)
- A list of all my post ideas (so it can suggest what to write next)

The file upload has a 50MB total limit per project, which sounds small until you realize that's about 40,000 pages of text. I've never come close to hitting it.

## What Actually Works (and What Doesn't)

I've been using Projects for about four months now. Here's the honest breakdown.

### ✅ What works really well

**1. Style consistency across posts.** Before Projects, my posts had inconsistent tone because each conversation started fresh. Now Claude knows my style from the project instructions, and my last five posts have had way more consistent voice. A reader actually emailed me to say the posts "feel like they're written by the same person" — which, yeah, they are, but it wasn't always obvious.

**2. Referencing old decisions.** I can say "remember that SEO strategy we discussed last week?" and Claude actually remembers it because it's in the same Project. This was impossible before — I'd have to dig up the old conversation link and paste chunks of it.

**3. Code + writing in the same place.** I have a project for this blog where I keep both my content plans and my Astro code snippets. Claude can reference both and help me with either. I asked it to "write a component that displays related posts" and it knew what my site structure looked like because I'd uploaded my code files.

### ❌ What doesn't work (or is annoying)

**1. Projects don't share across each other.** If you have a "Writing" project and a "Coding" project, Claude can't reference files from one while working in the other. I get why — isolation is good — but it means I end up duplicating some files across projects. Not a huge deal, but mildly annoying.

**2. The file search is hit-or-miss.** Claude sometimes "forgets" to look at an uploaded file unless you explicitly ask it to. I've had conversations where I reference something in an uploaded file and Claude gives a generic answer, and then I say "check the file I uploaded" and suddenly it's precise. You have to nudge it sometimes.

**3. No version control for project instructions.** If you change your project instructions, there's no history. I learned this after I overwrote my carefully crafted instructions with a shorter version and couldn't get the old version back. Now I keep a copy of my project instructions in a local text file. Dumb, but necessary.

**4. Projects aren't available via API (yet).** If you're using the Claude API, Projects don't exist there. It's only in the web interface. For my use case (writing blog posts) this doesn't matter, but if you're building an app on top of Claude, Projects won't help you.

## A Real Example: How I Use Projects for This Blog

Let me show you exactly how I set up my main project, because the abstract advice only gets you so far.

**Project name:** AI Kit Guides

**Project instructions (the full version):**

```
You're helping me write and maintain AI Kit Guides (aikitguides.com), a blog about practical AI tool tutorials.

Writing style:
- First-person, conversational ("I tried X", "In my experience")
- Include specific details: numbers, time spent, real errors encountered
- No AI clichés: skip "in today's rapidly evolving AI landscape"
- Short paragraphs (2-3 sentences)
- Use subheadings every 200-300 words

SEO rules:
- Target low-competition long-tail keywords
- Include 2-3 internal links per post (see list below)
- Title under 60 characters, description 150-160 characters
- First 100 words must contain the target keyword

Existing posts (for internal linking):
- ChatGPT beginner's guide: /blog/chatgpt-beginners-guide-2026
- Claude vs ChatGPT comparison: /blog/claude-vs-chatgpt-2026
- Midjourney guide: /blog/midjourney-complete-guide
- Best AI tools 2026: /blog/best-ai-tools-2026
- Prompt engineering: /blog/prompt-engineering-techniques
- ChatGPT API 429 fix: /blog/chatgpt-api-429-fix

Technical context:
- Site built with Astro + Tailwind CSS + TypeScript
- Posts are Markdown in src/content/blog/
- Config in src/config/site.ts
- Deploy via Cloudflare Pages (git push to main triggers deploy)
```

Having all of this in the project instructions means I can open a new conversation and just say "write a post about Claude Projects" and Claude knows the style, the SEO rules, the existing posts to link to, and even the technical context. It's genuinely useful in a way that "ChatGPT but with longer memory" isn't.

I also keep a `ideas.md` file uploaded to the project — just a running list of post ideas, ranked by priority. When I finish a post, I ask Claude "what should I write next?" and it looks at the list and gives me a take based on what's working for the site.

##Projects vs. Custom Instructions (ChatGPT's Version)

Since people always ask: Claude Projects is basically ChatGPT's "Custom Instructions" but with file uploads and persistent memory across conversations.

| Feature | Claude Projects | ChatGPT Custom Instructions |
|---|---|---|
| Persistent across conversations | ✅ Yes | ⚠️ Only within same thread |
| File uploads | ✅ Up to 50MB | ❌ No |
| Conversation history visible | ✅ Across all project chats | ❌ No |
| API access | ❌ Not yet | ✅ Yes (via system prompt) |

I use both, but for different things. ChatGPT (via API) is better for automated tasks. Claude Projects is better for ongoing creative work where context matters. If you want a deeper comparison, I wrote a whole post on [Claude vs. ChatGPT](/blog/claude-vs-chatgpt-2026) that covers this and a lot more.

## FAQ

### Can I share a Project with someone else?

Not directly. There's no "invite collaborator" button. But you can export your project instructions and files and they can import them into their own project. It's manual, but it works. I do this with a friend who helps me edit posts — I export the project instructions as text, he pastes them into his own project, and now we're both working with the same context.

### Do Projects cost extra?

No. Projects are included in all Claude plans, including Free. The Free plan has some limitations on file upload size and the amount of content you can store in project instructions, but for most individual users it's fine. I'm on the Pro plan mostly for the higher message limits, not for Projects-specific features.

### Can Claude see my project files when I start a new conversation?

Yes, that's the point. Every conversation in a project starts with access to the project instructions and all uploaded files. You don't need to re-upload anything. That said, Claude sometimes needs a nudge — if you reference something in a file and Claude gives a generic answer, say "check the [filename] file I uploaded" and it'll look.

### Is there a limit to how much text I can put in project instructions?

Claude recommends keeping project instructions under 2,000 words, but I've pushed it to about 3,500 and it still works fine. Past that, Claude starts ignoring parts of the instructions. If you have a lot to say, put it in an uploaded file instead — Claude reads those more reliably.

## Wrapping Up

Claude Projects isn't a revolution, but it's a genuine quality-of-life improvement if you use Claude regularly. The combination of persistent instructions, file uploads, and cross-conversation memory eliminates a lot of the friction that made AI assistants feel disposable.

My advice: start with one project. Pick something you do repeatedly — writing, coding, research — and spend 20 minutes setting up proper instructions. Don't overthink it. You can always refine the instructions later. The fact that I wasted months *not* using Projects still annoys me, so maybe don't make the same mistake.

If you're deciding between Claude and ChatGPT for your workflow, I put together a [list of the best AI tools for 2026](/blog/best-ai-tools-2026) that includes both (and some others worth looking at). And if you want to get better at prompting Claude within Projects, the [prompt engineering techniques](/blog/prompt-engineering-techniques) guide has some Claude-specific tips toward the end.
