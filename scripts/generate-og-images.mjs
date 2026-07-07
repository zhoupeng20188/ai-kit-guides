import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

const articles = [
  {
    slug: "chatgpt-beginners-guide-2026",
    title: "ChatGPT for Beginners",
    subtitle: "A Complete Guide to Getting Started in 2026",
  },
  {
    slug: "claude-vs-chatgpt-2026",
    title: "Claude 4.7 vs GPT-5.5",
    subtitle: "Which AI Assistant Is Better in 2026?",
  },
  {
    slug: "prompt-engineering-techniques",
    title: "Prompt Engineering",
    subtitle: "10 Proven Methods for Better AI Results",
  },
  {
    slug: "midjourney-complete-guide",
    title: "Midjourney Complete Guide",
    subtitle: "Create Stunning AI Art from Text",
  },
  {
    slug: "best-ai-tools-2026",
    title: "10 Best AI Tools for Productivity",
    subtitle: "Tested and Ranked in 2026",
  },
  {
    slug: "harness-engineering",
    title: "Harness Engineering",
    subtitle: "What Prompt Engineering Couldn't Solve",
  },
];

const publicDir = path.resolve(import.meta.dirname, "../public");

const template = (title, subtitle) => `<svg width="1200" height="630" viewBox="0 0 1200 630" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f0f9ff"/>
      <stop offset="100%" style="stop-color:#e0f2fe"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0ea5e9"/>
      <stop offset="100%" style="stop-color:#06b6d4"/>
    </linearGradient>
  </defs>

  <rect width="1200" height="630" fill="url(#bg)"/>

  <circle cx="1000" cy="120" r="180" fill="#e0f2fe" opacity="0.6"/>
  <circle cx="150" cy="520" r="140" fill="#dbeafe" opacity="0.5"/>
  <rect x="850" y="350" width="200" height="200" rx="24" fill="#bae6fd" opacity="0.3" transform="rotate(12 950 450)"/>

  <g transform="translate(80, 80)">
    <rect width="56" height="56" rx="14" fill="url(#accent)"/>
    <path d="M18 18h8v20h-8zM30 18h8v20h-8z" fill="white" opacity="0.9"/>
    <circle cx="22" cy="42" r="4" fill="white"/>
    <circle cx="34" cy="42" r="4" fill="white" opacity="0.6"/>
  </g>

  <text x="80" y="300" font-family="Inter, ui-sans-serif, system-ui, sans-serif" font-size="64" font-weight="800" fill="#0f172a" letter-spacing="-0.02em">
    ${title}
  </text>

  <text x="80" y="380" font-family="Inter, ui-sans-serif, system-ui, sans-serif" font-size="34" font-weight="500" fill="#334155">
    ${subtitle}
  </text>

  <text x="80" y="560" font-family="JetBrains Mono, ui-monospace, monospace" font-size="22" font-weight="500" fill="#0ea5e9">
    aikitguides.com
  </text>
</svg>`;

for (const { slug, title, subtitle } of articles) {
  const svgPath = path.join(publicDir, `og-${slug}.svg`);
  const jpgPath = path.join(publicDir, `og-${slug}.jpg`);

  fs.writeFileSync(svgPath, template(title, subtitle));
  execSync(`sips -s format jpeg "${svgPath}" --out "${jpgPath}"`);
  fs.unlinkSync(svgPath);
  console.log(`Generated ${jpgPath}`);
}

console.log("Done!");