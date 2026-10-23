export const SITE = {
  name: "AI Kit Guides",
  shortName: "AI Kit",
  description:
    "AI-assisted Java and Spring Boot guides, with runnable case studies, source references, and inspectable verification records.",
  url: "https://aikitguides.com",
  author: "Peng Zhou",
  email: "foreverzhy1252@gmail.com",
  locale: "en_US",
  lang: "en",
  twitter: "", // No Twitter account
  defaultOgImage: "/og-default.jpg",
  nav: [
    { label: "Home", href: "/" },
    { label: "Blog", href: "/blog/" },
    { label: "Categories", href: "/categories/" },
    { label: "About", href: "/about/" },
  ],
  social: {
    github: "https://github.com/zhoupeng20188/ai-kit-guides",
    rss: "/rss.xml",
  },
};

export const ANALYTICS = {
  ga4Id: "G-FN0G78042G",
};

export const ADSENSE = {
  client: "ca-pub-2558991461210670",
  enabled: true,
  slot: {
    inContent: "",
    sidebar: "",
    header: "",
  },
};

export const CATEGORIES = [
  {
    slug: "ai-coding-agents",
    name: "AI Coding Agents",
    description:
      "Hands-on guides for Claude Code, OpenAI Codex, Cursor and GitHub Copilot — setup, sandboxing, MCP servers, subagents and hooks.",
    icon: "agent",
  },
  {
    slug: "spring-boot-4",
    name: "Spring Boot 4 Migration",
    description:
      "Upgrading to Spring Boot 4 and Spring Framework 7: Jakarta EE 11, Security 7, Jackson 3, and the silent behaviour changes tests catch first.",
    icon: "spring",
  },
  {
    slug: "java-testing-ci",
    name: "Testing & CI",
    description:
      "JUnit 6, Maven and Gradle builds, ArchUnit, Spotless, Testcontainers and CI gates — and why AI-generated code can pass CI while running zero tests.",
    icon: "test",
  },
  {
    slug: "java-ai-tools",
    name: "AI on Real Code",
    description:
      "Pointing AI at an actual codebase: code review, legacy refactoring, LangChain agents, and the MCP filesystem server.",
    icon: "java",
  },
  {
    slug: "ai-api-limits",
    name: "AI API & Errors",
    description:
      "Fixing OpenAI and ChatGPT API errors: 429 rate limits, the 429001 gateway code, quota tiers, and retry strategy that holds up.",
    icon: "api",
  },
  {
    slug: "ai-models-basics",
    name: "AI Models & Basics",
    description:
      "Model comparisons, prompt technique, and hallucination control — the fundamentals, in plain language and without the hype.",
    icon: "brain",
  },
];

export function getCategoryBySlug(slug: string) {
  return CATEGORIES.find((c) => c.slug === slug);
}
