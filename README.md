# AI Kit Guides

> Honest reviews, step-by-step tutorials, and head-to-head comparisons of ChatGPT, Claude, Midjourney, and dozens more AI tools — written for real people, not AI experts.

🌐 **Live site:** [https://aikitguides.com](https://aikitguides.com)

![AI Kit Guides homepage](https://aikitguides.com/screenshot-home.png)

---

## About

AI Kit Guides is a personal blog by **Peng Zhou**, a senior Java engineer who has been actively using AI tools since early 2023. The site covers practical guides, real-world comparisons, and tested workflows for the most popular AI tools of 2026.

## Tech Stack

- **Framework:** Astro 7
- **Styling:** Tailwind CSS 4
- **Language:** TypeScript
- **Content:** Markdown-based content collections
- **Deployment:** Cloudflare Pages (native Git integration)
- **Domain:** [aikitguides.com](https://aikitguides.com)

## Getting Started

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── config/         # Site configuration
├── content/        # Blog articles (Markdown)
│   └── blog/
├── layouts/        # Page layouts
├── pages/          # Route pages
│   ├── blog/       # Blog routes
│   └── categories/ # Category routes
├── styles/         # Global styles
└── utils/          # Utility functions
```

## Writing Articles

1. Create a new `.md` file in `src/content/blog/`
2. Use the frontmatter schema from `src/content.config.ts`
3. Run `npm run dev` to preview
4. The project-level `ai-kit-guides-article-skill` enforces the writing conventions

## Deployment

This site is deployed via Cloudflare Pages (native Git integration):

1. Connect your GitHub repository to Cloudflare Pages
2. Build command: `npm run build`
3. Output directory: `dist`
4. Add custom domain `aikitguides.com` in Cloudflare Pages settings
5. Push to `main` triggers automatic deployment

## License

MIT
