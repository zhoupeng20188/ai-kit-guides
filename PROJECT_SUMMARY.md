# AI Kit Guides — 项目总结文档

> 项目路径：`/Users/forever/github/ai-kit-guides`  
> GitHub 仓库：`https://github.com/zhoupeng20188/ai-kit-guides`  
> 目标域名：`https://aikitguides.com`  
> 构建时间：2026-06-27

---

## 1. 项目背景与目标

原中文博客因 Google AdSense 单价低（约 $0.01）且内容杂乱，决定转型为专注 AI 工具的英文博客，以获取更高 CPC 广告收入和更清晰的受众定位。

**目标定位**：为英语用户（尤其是北美、欧洲）提供 AI 工具教程、诚实对比和新手友好指南。

**核心关键词方向**：
- `ChatGPT tutorial`
- `Claude vs ChatGPT`
- `prompt engineering`
- `Midjourney guide`
- `best AI tools`

---

## 2. 技术栈

| 层级 | 技术 |
|---|---|
| 框架 | [Astro](https://astro.build/) 5.8.0 |
| 样式 | Tailwind CSS 4.0 + `@tailwindcss/typography` |
| 构建输出 | 静态站点（SSG） |
| 部署目标 | Cloudflare Pages |
| CI/CD | GitHub Actions（自动构建部署） |
| 内容格式 | Markdown + Astro Content Collections |
| 类型安全 | TypeScript 5.8 |

---

## 3. 已完成功能

### 3.1 页面与路由

| 页面 | 路径 | 说明 |
|---|---|---|
| 首页 | `/` | Hero、分类导航、最新文章、CTA |
| 博客列表 | `/blog/` | 全部文章列表 |
| 文章详情 | `/blog/{slug}/` | Markdown 渲染、TOC、相关文章 |
| 分类首页 | `/categories/` | 全部分类 |
| 分类页 | `/categories/{category}/` | 某分类下的文章 |
| 关于 | `/about/` | 站点介绍 |
| 联系 | `/contact/` | 联系方式 |
| 隐私政策 | `/privacy-policy/` | AdSense 合规 |
| RSS | `/rss.xml` | 文章订阅 |
| 404 | `/404` | 404 页面 |

### 3.2 组件系统

- `BaseSEO.astro` — 全站 SEO 元标签 + 结构化数据
- `Header.astro` — 响应式导航
- `Footer.astro` — 页脚导航
- `ArticleCard.astro` — 文章卡片
- `ArticleList.astro` — 文章列表
- `TableOfContents.astro` — 目录（TOC）
- `RelatedPosts.astro` — 相关文章推荐
- `InContentAd.astro` — 内容内广告位
- `AdScript.astro` — AdSense 脚本注入

### 3.3 内容系统

- 使用 Astro Content Collections + Zod schema 校验
- frontmatter 字段：`title`、`description`、`pubDate`、`updatedDate`、`category`、`tags`、`author`、`featured`、`image`、`imageAlt`、`faq`
- 已发布 5 篇种子文章（约 8000 字）

---

## 4. 内容文章列表

| 文件 | 标题 | 分类 | 关键词 |
|---|---|---|---|
| `chatgpt-beginners-guide-2026.md` | ChatGPT Beginner's Guide 2026 | ChatGPT | chatgpt, openai, beginners, tutorial |
| `claude-vs-chatgpt-2026.md` | Claude 4.7 vs GPT-5.5: Which AI Assistant Is Better in 2026? | LLM | claude, chatgpt, gpt-5.5, claude-4.7, comparison |
| `prompt-engineering-techniques.md` | Prompt Engineering Techniques That Actually Work in 2026 | Prompt Engineering | prompt-engineering, chatgpt, claude, techniques |
| `midjourney-complete-guide.md` | Midjourney Complete Guide for Beginners (2026) | AI Art | midjourney, ai-art, tutorial, image-generation |
| `best-ai-tools-2026.md` | Best AI Tools for Productivity in 2026 | AI Tools | ai-tools, productivity, comparison, reviews |

---

## 5. SEO 优化清单

### 5.1 基础 SEO

- [x] `<title>` 和 `<meta name="description">` 每个页面唯一
- [x] `<link rel="canonical">` 规范链接
- [x] `<meta name="robots" content="index,follow,max-image-preview:large">`
- [x] `<meta name="keywords">`（文章页自动生成）
- [x] 响应式 `<meta name="viewport">`
- [x] `robots.txt`（含 sitemap 引用和 Host 指令）
- [x] `sitemap-index.xml`（Astro 自动生成）

### 5.2 Open Graph / Twitter Card

- [x] `og:title`、`og:description`、`og:image`、`og:url`、`og:type`
- [x] `og:image:alt`、`article:section`、`article:tag`
- [x] `twitter:card`、`twitter:title`、`twitter:description`、`twitter:image`
- [x] 默认 OG 图片 `/og-default.png`
- [x] 每篇文章专属 OG 图片 `/og-{slug}.png`

### 5.3 结构化数据（JSON-LD）

- [x] **Organization** — 全站输出（name、url、logo、email、sameAs）
- [x] **WebSite** — 首页输出
- [x] **Article** — 文章页输出（含 author、publisher、image）
- [x] **BreadcrumbList** — 文章页输出（Home → Blog → Category → Article）
- [x] **FAQPage** — 文章页输出（若 frontmatter 含 `faq`）

### 5.4 PWA / 浏览器增强

- [x] `/site.webmanifest`
- [x] `/favicon.svg`
- [x] `/icon-192x192.png`
- [x] `/icon-512x512.png`
- [x] `/apple-touch-icon.png`
- [x] `<meta name="theme-color">`

---

## 6. Google AdSense 集成

当前状态：**已集成，但设置为未启用**（等 AdSense 审核通过后再打开）。

### 6.1 配置位置

```ts
// src/config/site.ts
export const ADSENSE = {
  client: "ca-pub-0000000000000000", // 审核通过后替换为真实 Publisher ID
  enabled: false,                    // 审核通过后改为 true
  slot: {
    inContent: "1111111111",
    sidebar: "2222222222",
    header:  "3333333333",
  },
};
```

### 6.2 已预留广告位

| 位置 | 页面 |
|---|---|
| 顶部广告 | 文章详情页（标题下方） |
| 底部广告 | 文章详情页（正文下方） |
| 侧边栏广告 | 文章详情页（目录下方，仅大屏） |
| Hero 下方广告 | 首页 |
| 文章列表下方广告 | 首页 |

### 6.3 合规文件

- [x] `/privacy-policy/` 页面（含隐私政策、Cookie、数据使用说明）
- [x] `/ads.txt`（已预留，需替换为真实 Publisher ID）

---

## 7. 项目结构

```
ai-kit-guides/
├── .github/workflows/deploy.yml    # CI/CD 部署到 Cloudflare Pages
├── public/                         # 静态资源
│   ├── robots.txt
│   ├── ads.txt
│   ├── site.webmanifest
│   ├── favicon.svg
│   ├── icon-192x192.png
│   ├── icon-512x512.png
│   ├── apple-touch-icon.png
│   ├── og-default.png
│   ├── og-{slug}.png
│   └── rss-styles.xsl
├── scripts/
│   └── generate-og-images.mjs      # 自动生成 OG 图片脚本
├── src/
│   ├── components/                 # UI 组件
│   ├── layouts/                    # 页面布局
│   ├── pages/                      # 路由页面
│   ├── content/blog/               # Markdown 文章
│   ├── config/site.ts              # 站点核心配置
│   ├── content.config.ts           # 内容集合 schema
│   ├── styles/global.css           # 全局样式
│   └── utils/                      # 工具函数
├── astro.config.mjs
├── package.json
├── tsconfig.json
├── README.md
├── PUSH_GUIDE.md                   # Git 推送指南
└── PROJECT_SUMMARY.md              # 本文档
```

---

## 8. 部署流程

### 8.1 本地开发

```bash
cd /Users/forever/github/ai-kit-guides
npm run dev
# 打开 http://localhost:4321
```

### 8.2 构建

```bash
npm run build
# 输出到 dist/ 目录
```

### 8.3 推送代码

```bash
git add -A
git commit -m "update: ..."
git push -u origin main
```

### 8.4 Cloudflare Pages 部署

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/) → Pages
2. Create a project → Connect to Git
3. 选择仓库 `zhoupeng20188/ai-kit-guides`
4. 构建设置：
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
   - **Node Version**: `22`
5. 保存并部署
6. 在 Pages 设置中绑定自定义域名 `aikitguides.com`

---

## 9. 后续待办事项

### 9.1 上线前必须完成

- [ ] 将代码推送到 GitHub
- [ ] 部署到 Cloudflare Pages
- [ ] 在 Cloudflare 中绑定域名 `aikitguides.com`
- [ ] 配置 DNS 解析（域名服务商指向 Cloudflare Pages）
- [ ] 申请 Google AdSense 账号
- [ ] 替换 `src/config/site.ts` 中的真实 AdSense Publisher ID
- [ ] 更新 `public/ads.txt` 中的 Publisher ID
- [ ] 将 `ADSENSE.enabled` 改为 `true`
- [ ] 添加 Google Search Console 验证文件

### 9.2 内容扩展

- [ ] 持续发布文章，目标上线前 15-20 篇
- [ ] 覆盖高 CPC 长尾关键词（如 `best AI writing tools`、`Jasper AI review`、`Copy.ai vs ChatGPT`）
- [ ] 添加更多对比类、评测类、教程类文章
- [ ] 为文章添加真实截图/演示图

### 9.3 SEO 进一步升级

- [ ] 压缩 OG 图片（当前默认图约 500KB，建议压缩到 100KB 以内）
- [ ] 提交 sitemap 到 Google Search Console
- [ ] 设置 Google Analytics 4
- [ ] 增加分类页描述
- [ ] 在文章正文中增加内链

### 9.4 功能增强

- [ ] 添加站内搜索
- [ ] 添加邮件订阅表单（Newsletter）
- [ ] 添加评论系统（如 Giscus）
- [ ] 多语言支持（后续可考虑西班牙语等）

---

## 10. 关键配置说明

### 10.1 站点配置 `src/config/site.ts`

```ts
export const SITE = {
  name: "AI Kit Guides",
  tagline: "Honest AI tool tutorials, comparisons, and beginner-friendly guides.",
  url: "https://aikitguides.com",
  email: "foreverzhy1252@gmail.com",
  defaultOgImage: "/og-default.png",
  // ...
};
```

### 10.2 Astro 配置 `astro.config.mjs`

```js
export default defineConfig({
  site: "https://aikitguides.com",
  integrations: [sitemap(), tailwind()],
  output: "static",
});
```

### 10.3 文章 Frontmatter 示例

```yaml
---
title: "Your Article Title"
description: "Brief SEO description under 160 characters."
pubDate: 2026-06-27
category: "ai-tools"
tags: ["ai-tools", "tutorial"]
image: "/og-your-article.png"
imageAlt: "Descriptive alt text for the OG image"
featured: false
---
```

---

## 11. 联系与维护

- **项目维护者**：foreverzhy1252@gmail.com
- **GitHub**：https://github.com/zhoupeng20188/ai-kit-guides
- **RSS**：https://aikitguides.com/rss.xml

---

*文档最后更新：2026-06-27*
