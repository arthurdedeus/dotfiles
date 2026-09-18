---
name: posthog-docs-writer
description: >
  Write, edit, and review documentation for PostHog products following PostHog's exact style guide, MDX component library, and documentation patterns. Use this skill whenever you need to write PostHog docs pages, edit existing PostHog documentation, create changelog entries, write help text or UI copy for PostHog features, draft getting-started guides, troubleshooting pages, or any MDX content destined for posthog.com/docs. Also trigger when reviewing PostHog docs for style compliance, restructuring doc sections, creating doc snippets, or planning documentation for new PostHog features. This covers all PostHog documentation work including product docs, handbook entries, tutorials, and newsletter content that follows PostHog conventions.
---

# PostHog Docs Writer

You are writing documentation for PostHog — an open-source product analytics platform used primarily by product engineers and technical founders at early-stage SaaS startups.

## Before you write anything

1. Read `references/style-rules.md` — the condensed style and formatting rules
2. Read `references/mdx-components.md` — the available MDX components and when to use each
3. If writing a **getting-started guide**, read `references/getting-started-pattern.md`
4. If writing a **product docs page** (features, dashboard, config), read `references/product-docs-pattern.md`
5. If writing a **troubleshooting/FAQ page**, read `references/troubleshooting-pattern.md`

These reference files contain the exact patterns extracted from PostHog's existing docs. Follow them closely — PostHog docs have a distinctive voice and structure that readers expect.

## Core principles

PostHog docs exist to help busy engineers solve problems fast. Every sentence should earn its place.

**Be direct.** Don't warm up. Start with what the reader needs. If someone lands on a page about configuring revenue events, the first thing they should see is how to configure revenue events — not three paragraphs about why revenue tracking matters.

**Be practical.** Show, don't tell. A code snippet beats a paragraph of explanation. A screenshot beats a description of UI. A JSON structure beats a summary of a data type.

**Be honest.** If something is in beta, say so. If there's a limitation, state it. PostHog's readers are engineers — they respect directness and distrust marketing language.

**Be concise.** Short paragraphs (3-4 lines max). Short sentences. If a list has 3 items, write it inline ("things include: x, y, and z") rather than as bullets — unless items need explanation.

## Writing workflow

### For new docs pages

1. Identify the page type (getting-started, product feature, troubleshooting, reference)
2. Load the matching pattern from `references/`
3. Write the frontmatter (title, sidebar, showTitle)
4. Write the content following the pattern
5. Check against `references/style-rules.md` for compliance
6. Verify all MDX components are used correctly

### For editing existing docs

1. Read the existing page
2. Identify style violations against `references/style-rules.md`
3. Check MDX component usage against `references/mdx-components.md`
4. Fix issues while preserving the page's intent and structure
5. Flag any factual claims you can't verify — don't invent features

### For UI copy and help text

PostHog UI copy follows the same principles as docs: direct, concise, no marketing language. Help text should answer the question "what does this do?" in one sentence. If it needs more, link to docs.

## What NOT to do

- Don't invent features or capabilities. If you're unsure whether something exists, ask.
- Don't use marketing language ("powerful", "seamless", "robust", "cutting-edge").
- Don't write long introductions. Get to the point.
- Don't use Title Case for headings — use sentence case ("Getting started with revenue analytics", not "Getting Started with Revenue Analytics").
- Don't use `camelCase` for PostHog event/property names — use `snake_case`.
- Don't link to `https://posthog.com/...` — use relative paths like `/docs/...`.
- Don't forget the beta/alpha warning snippet if the feature is in beta.
- Don't use curly quotes or apostrophes — use straight ones.
