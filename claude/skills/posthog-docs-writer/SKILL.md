---
name: posthog-docs-writer
description: Write or review PostHog docs, handbook pages, tutorials, changelogs, MDX, and UI copy.
---

# PostHog docs writer

Write for busy product engineers. Lead with the action or answer they need.

## Load current guidance

For work in `posthog.com`, read these repository files before drafting:

- `contents/handbook/docs-and-wizard/docs-style-guide.mdx`
- `contents/handbook/content/posthog-style-guide.md`
- `contents/handbook/docs-and-wizard/mdx-and-components.mdx`
- The closest recent page of the same type.

Use this skill's bundled references only when the live repository guidance is unavailable. The repository is authoritative when they differ.

## Workflow

1. Identify the page type and audience.
2. Verify product behavior in current docs or code.
3. Read nearby pages for structure and component usage.
4. Draft the shortest complete answer.
5. Check links, code, MDX, headings, and frontmatter.
6. Run `pnpm format:docs` for changed docs files.
7. Report any claim that remains unverified.

## Style

- Start with the task, result, or limitation.
- Use sentence-case headings and American English.
- Prefer short paragraphs, concrete examples, and tested code.
- Use relative links for PostHog pages.
- Bold visible UI labels.
- Use exact event, property, API, and code names.
- State beta status and known limits.
- Cut marketing claims, long introductions, and repeated summaries.

## Safety

Do not invent features, settings, URLs, or component APIs. Inspect the current repository before using an MDX component.

For UI copy, answer “what does this do?” in one sentence. Link to docs when the interface cannot hold the full explanation.
