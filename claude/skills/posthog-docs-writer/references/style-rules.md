# PostHog docs style

Use the live handbook guides in `posthog.com` when available. This file is a fallback summary.

## Language

- Use American English and sentence-case headings.
- Put the answer or action first.
- Keep paragraphs short.
- Prefer active voice and concrete verbs.
- Use the Oxford comma.
- Use straight quotes in source files.
- Cut marketing language, throat-clearing, and unsupported claims.
- State beta status, limits, and uncertainty directly.

## Structure

- Use `##` for main sections and `###` for subsections.
- Match the structure of a recent page with the same purpose.
- Use numbered steps for ordered tasks.
- Use tables only when readers compare fields or options.
- Link to deeper material instead of repeating it.

## Links

- Use root-relative paths for PostHog website links.
- Link the first useful mention of a product concept.
- Use the current app URL pattern from nearby docs.
- Verify external links and use the repository's current external-link component.

## Code

- Use inline code for identifiers, events, properties, commands, and paths.
- Add a language to every code fence.
- Follow each language's naming conventions.
- Use PostHog magic placeholders only when the current docs support them.
- Test commands and examples when practical.

## UI

- Bold visible labels.
- Describe clicks in order.
- Use the exact current label and route.
- Add screenshots only when they clarify a task or state.
- Remove customer data and secrets from media.

## MDX

Inspect current component source or recent usage before adding a component. Do not trust a remembered prop name.

Run:

```bash
pnpm format:docs
```

Review the final diff after formatting.
