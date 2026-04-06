# Troubleshooting and FAQ Page Pattern

Troubleshooting pages answer common questions and help users debug issues.

## When to use this pattern

- FAQ pages for a product
- Troubleshooting guides
- "Common questions" pages
- Pages titled "[Product] troubleshooting and FAQs"

## Anatomy

### Frontmatter

```yaml
---
title: [Product] troubleshooting and FAQs
sidebar: Docs
showTitle: true
---
```

### Standard structure

```
1. Beta warning import + render (if applicable)
2. Brief intro line: "Have a question not covered here? [Let us know](http://app.posthog.com/home#supportModal)."
3. PostHog AI input (optional but recommended)
4. Questions as ## headings
5. Each answer: direct answer first, then details, code if needed
```

### PostHog AI integration

Add at the top for self-serve troubleshooting:

```tsx
<AskAIInput placeholder="Type your question and hit enter..." />
```

Or use the AskMax component with pre-loaded questions:

```tsx
<AskMax
    title="Have a question?"
    quickQuestions={[
        'Why is my data not showing?',
        'How do I configure X?',
    ]}
/>
```

### Question format

Use `##` headings phrased as questions:

```md
## How are active users calculated?

A user is considered active if they triggered at least one activity event in the period:

- **DAU**: Users with at least one event in the past day
- **WAU**: Users with at least one event in the past 7 days
- **MAU**: Users with at least one event in the past 30 days
```

### Answer format

1. **Direct answer first** — one sentence if possible
2. **Details** — how it works, edge cases, configuration
3. **Code snippet** — if the answer involves implementation
4. **Link to full docs** — if the answer needs more depth than fits here

**Good:**
> ## Can I use customer analytics with groups?
> 
> Yes. Customer profiles work with both persons and groups. This is useful for B2B products where you want to track company-level activity.
> 
> See [B2B mode](/docs/customer-analytics/b2b-mode) to learn more.

**Bad:**
> ## Can I use customer analytics with groups?
>
> Groups are a powerful feature in PostHog that allow you to... [three paragraphs of context before answering the question]

### Debugging-style questions

For questions about "why isn't X working", use a numbered checklist:

```md
## Why isn't my revenue appearing in the dashboard?

A few common issues to check:

1. **Check the Revenue tab in Data management**: Verify your events are being captured in the [Revenue tab](https://app.posthog.com/data-management/revenue).
2. **Make sure tracking is enabled**: Legacy sources have tracking disabled by default.
3. **Check your filters**: The dashboard filters may be excluding your data.
```

### Technical FAQ questions

For questions about how something works internally (currency conversion, calculations):

```md
## How do you convert revenue in different currencies?

PostHog automatically converts revenue into your chosen reporting currency. Exchange rate data comes from [Open Exchange Rates](https://openexchangerates.org/), updated hourly with daily granularity.
```

Follow with a code example if users can interact with the feature programmatically:

```sql
SELECT convertCurrency('CAD', 'USD', amount, _toDate(timestamp))
FROM events
WHERE event = 'purchase'
```

### "Is X supported?" questions

Be direct about limitations:

```md
## Can I use custom currency conversion data?

No. PostHog uses exchange rates from Open Exchange Rates. If you need custom rates, [create a feature request](https://github.com/PostHog/posthog/issues/new).
```

### Grouping related questions

If the page has many questions, group them loosely by theme but don't add explicit section groupings unless there are 10+ questions. The `##` headings serve as natural scan points.

For pages with 10+ questions, consider adding informal grouping with a brief `###` subsection header.

## Common mistakes

- Not answering the question in the first sentence. The heading IS the question — answer it immediately.
- Writing answers that are too long. If an answer needs more than a few paragraphs, it probably deserves its own docs page. Write a short answer here and link to the full page.
- Asking rhetorical questions in answers. The user already has a question — don't give them more questions.
- Forgetting the support link at the top. Users who don't find their answer need a clear escape hatch.
