# AI Kit Guides

> Practical AI and Java development guides with source references and verifiable examples.

🌐 **Live site:** [https://aikitguides.com](https://aikitguides.com)

![AI Kit Guides homepage](https://aikitguides.com/screenshot-home.png)

---

## About

AI Kit Guides is a personal blog by **Peng Zhou**, a Java engineer. It covers AI coding tools, Java testing, Spring Boot migration, and AI API troubleshooting. Articles distinguish documented features, illustrative procedures, and executed examples.

## Tech Stack

- **Framework:** Astro 7
- **Styling:** Tailwind CSS 4
- **Language:** TypeScript
- **Content:** Markdown-based content collections
- **Deployment:** Cloudflare Pages (native Git integration)
- **Domain:** [aikitguides.com](https://aikitguides.com)

## Getting Started

```bash
# Use Node.js 22.12+ (this review used 22.23.2)
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
4. Follow [editorial standards](docs/editorial-standards.md); do not invent firsthand experience or measurements
5. Keep runnable artifacts and verification records when claiming an executed result

The [October 2026 audit](docs/adsense-content-audit-2026-10-23.md) covers every article and the supplied Search Console export. The [Java verification example](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/java-verification) is published with its source and sanitized evidence.

The [Boot 3.5 to 4 case study](examples/boot4-verification-lab/README.md) adds two pinned application profiles, real HTTP and MockMvc checks, H2 history exercises, and sanitized evidence. Run `python3 examples/boot4-verification-lab/verify.py` with JDK 17 selected; package a verified snapshot with `python3 scripts/package_boot4_lab.py`.

## Deployment

This site is deployed via Cloudflare Pages (native Git integration):

1. Connect your GitHub repository to Cloudflare Pages
2. Build command: `npm run build`
3. Output directory: `dist`
4. Add custom domain `aikitguides.com` in Cloudflare Pages settings
5. Push to `main` triggers automatic deployment

## License

MIT
