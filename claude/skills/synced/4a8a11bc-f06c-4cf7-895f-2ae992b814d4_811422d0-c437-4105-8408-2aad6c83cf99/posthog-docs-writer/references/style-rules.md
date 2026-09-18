# PostHog Style Rules

Condensed reference for writing PostHog docs. When in doubt, be shorter and more direct.

## Table of contents

1. [Language and formatting](#language-and-formatting)
2. [Headings and structure](#headings-and-structure)
3. [Links](#links)
4. [Code and technical content](#code-and-technical-content)
5. [Images and media](#images-and-media)
6. [UI references](#ui-references)
7. [Terminology](#terminology)
8. [Frontmatter](#frontmatter)

## Language and formatting

- **American English** for spelling, grammar, dates, and times.
- **Sentence case** for all headings: "Getting started with revenue analytics", not "Getting Started With Revenue Analytics".
- **Oxford comma**: "bananas, apples, and oranges".
- **Straight quotes and apostrophes** — no curly/smart quotes.
- **British-style en dashes** with spaces: "Don't post it – just wait." (not em dashes without spaces).
- **"Enable"** not "allow" when PostHog gives users capability. "Allow" = permit. "Enable" = provide the means.
- **"Open source"** without hyphen in general use. Hyphenated ("open-source") only before a noun: "the open-source community."
- **Short paragraphs**: 3-4 lines maximum. Break up walls of text.
- **Bullet points**: add blank lines between long bullet items in markdown for readability. Short lists (3 items) can be written inline as prose.
- **No hedging**: don't say "it depends" or "it's complicated." Have an opinion, give an example, or do more research.
- **No marketing language**: never use "powerful", "seamless", "robust", "cutting-edge", "comprehensive", "best-in-class". Describe what it does, not how great it is.

## Headings and structure

- Use headings to break up content for scannability.
- Put the most important information first in every section.
- Use `##` for main sections, `###` for subsections. Avoid going deeper than `####`.
- Headings should describe what the section covers, not be clever or vague.

## Links

- **Internal links**: use relative paths with absolute paths from root. `/docs/product-analytics/insights` not `https://posthog.com/docs/product-analytics/insights`.
- **Wikipedia-style linking**: first mention of a PostHog term or feature on a page should link to its docs page.
- **PostHog app links**: use `https://us.posthog.com/${path}` (remove `project/2/` so it redirects properly). EU users are redirected automatically.
- **External links**: use the `<Link>` component with `external` attribute to open in new tab with icon.

## Code and technical content

- Use backticks for inline code: `posthog.capture()`.
- Use triple backticks with language identifier for code blocks.
- **snake_case** for PostHog event and property names: `user_signed_up`, not `userSignedUp`.
- Follow each language's own conventions in code samples (camelCase for JS, snake_case for Python, etc.).
- Use magic placeholders in code: `<ph_project_api_key>`, `<ph_client_api_host>`, etc. These auto-replace for logged-in users.
- Use `<MultiLanguage>` component for code in multiple languages.
- Use `// +` (green), `// -` (red), `// HIGHLIGHT` (yellow) comments for code highlighting.

## Images and media

- Upload to Cloudinary, use the URL provided.
- Use `<ProductScreenshot>` component for app screenshots (adds border/background). Provide `imageLight` and optionally `imageDark` props.
- Use `<ProductVideo>` component for app screen recordings.
- Screenshot tips: 1000-1400px width, DPR 3, focus on main element, no user data visible.
- Don't upload animated GIFs — use MP4 screen recordings instead.
- For YouTube embeds: use `-nocookie` URL variant, add `allowfullscreen`.

## UI references

- **Bold** button, tab, and navigation names: click **+ New insight**.
- **Chronological order** for UI steps: "Under **Settings** > **User**, click **Set up 2FA**."
- Use `>` for long menu hierarchies: "**Settings** > **Product analytics** > **Correlation analysis exclusions**."
- Hyperlink to the correct PostHog app location when possible.

## Terminology

- **PostHog**: default reference to the product (cloud). Most users are on cloud.
- **PostHog Cloud**: only when explicitly differentiating from self-hosted.
- **Self-hosted PostHog** or **hobby deployments**: for self-hosted installations.
- Capitalize product names as proper nouns when referencing the PostHog product: "Session Replay". Lowercase for generic industry terms: "product analytics."
- Capitalize acronyms: "URLs" not "urls". Define uncommon ones on first use.

## Frontmatter

Standard docs page frontmatter:

```yaml
---
title: Page title in sentence case
sidebar: Docs
showTitle: true
---
```

For getting-started pages with quest log layout:

```yaml
---
title: Getting started with [product]
hideRightSidebar: true
contentMaxWidthClass: max-w-5xl
---
```

For changelog pages:

```yaml
---
title: [Product] changelog
hideRightSidebar: true
---
```
