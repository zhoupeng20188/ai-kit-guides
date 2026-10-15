# X Thread Draft — using-ai-legacy-java-codebase (6-post, all ≤280 chars)

**Post 1** (~220 chars)
I inherited Java code older than some coworkers.

First AI task: "add a discount cap." Merged in 90s.

A partner channel started rejecting orders 2 days later.

The AI wrote fine code. It just had no idea what it stood on. 🧵

**Post 2** (~241 chars)
Costliest mistake: the multi-channel trap.

calculateFinalPrice() served 5 channels. I said "fix the partner price."

AI edited the shared method, fixed 1 caller, missed the other 4.

Fixed A, broke B–E. Learned it from an angry partner, not a test.

**Post 3** (~214 chars)
Greenfield coding = give AI freedom.

Legacy coding = fence it in.

You're not collaborating with a smart junior. You're supervising a fast, confident one who doesn't know the history and will wander off if you let it.

**Post 4** (~254 chars)
Rules don't live in prompts. They live in CLAUDE.md:

→ Use existing utils (no new deps)
→ Match surrounding style
→ List callers before touching shared logic
→ Never "simplify" unknown code

Good CLAUDE.md = your persistent "stop doing that" list.

**Post 5** (~200 chars)
And you still have to review. Hard.

Read every line like a stranger wrote it — because one did.

The AI is fast, confident, context-blind. You hold the business history.

The review is where you stay the boss.

**Post 6** (~169 chars)
Full writeup + the exact CLAUDE.md template I use on legacy Java:

👉 https://aikitguides.com/blog/using-ai-legacy-java-codebase

What's your worst AI-on-legacy horror story? 👇

---

## 发布建议
- 每条均 ≤280 字符（含换行/emoji 余量），可直接粘贴
- 节奏：单独发这篇当"人设锚点"，不要和别的线程同一天刷
- 最佳时段（X 全球受众）：北京时间 21:00-23:00 或 08:00-09:00（美东早通勤 + 欧洲上午）
- 发完后在评论区自己补一条："Full post + CLAUDE.md template here 👆" 再贴一次链接，提升曝光
- 想要中文版 / 加截图，告诉我
