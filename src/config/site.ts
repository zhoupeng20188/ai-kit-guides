export const SITE = {
  name: "AI Kit Guides",
  shortName: "AI Kit",
  description:
    "AI tool tutorials, honest comparisons, and beginner-friendly guides. Helping you find and master the best AI tools — ChatGPT, Midjourney, Claude, and more.",
  url: "https://aikitguides.com",
  author: "AI Kit Guides Team",
  email: "foreverzhy1252@gmail.com",
  locale: "en_US",
  lang: "en",
  twitter: "", // No Twitter account
  defaultOgImage: "/og-default.jpg",
  nav: [
    { label: "Home", href: "/" },
    { label: "Blog", href: "/blog" },
    { label: "Categories", href: "/categories" },
    { label: "About", href: "/about" },
  ],
  social: {
    github: "https://github.com/zhoupeng20188/ai-kit-guides",
    rss: "/rss.xml",
  },
};

export const ADSENSE = {
  client: "ca-pub-0000000000000000", // Replace with your AdSense publisher ID
  enabled: false, // Set to true after AdSense approval
  slot: {
    inContent: "1111111111",
    sidebar: "2222222222",
    header: "3333333333",
  },
};

export const CATEGORIES = [
  {
    slug: "chatgpt",
    name: "ChatGPT",
    description: "Guides and tutorials for OpenAI ChatGPT — from basics to advanced prompting.",
    icon: "chat",
  },
  {
    slug: "ai-tools",
    name: "AI Tools",
    description: "Reviews and comparisons of the best AI tools available in 2026.",
    icon: "tools",
  },
  {
    slug: "prompt-engineering",
    name: "Prompt Engineering",
    description: "Master the art of writing effective AI prompts for better results.",
    icon: "prompt",
  },
  {
    slug: "ai-art",
    name: "AI Art & Design",
    description: "Create stunning visuals with Midjourney, DALL-E, and other AI art tools.",
    icon: "art",
  },
  {
    slug: "llm",
    name: "Large Language Models",
    description: "Deep dives into GPT, Claude, Gemini, and the future of language AI.",
    icon: "brain",
  },
];

export function getCategoryBySlug(slug: string) {
  return CATEGORIES.find((c) => c.slug === slug);
}
