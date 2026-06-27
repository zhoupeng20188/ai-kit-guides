# AI Kit Guides

AI tool tutorials, honest comparisons, and beginner-friendly guides. Built with Astro 5 + Tailwind CSS 4.

## Tech Stack

- **Framework:** Astro 7
- **Styling:** Tailwind CSS 4
- **Language:** TypeScript
- **Deployment:** Cloudflare Pages
- **Content:** Markdown-based content collections

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

## Deployment

This site is designed for Cloudflare Pages:

1. Connect your GitHub repository to Cloudflare Pages
2. Build command: `npm run build`
3. Output directory: `dist`
4. Add custom domain in Cloudflare Pages settings

## License

MIT
