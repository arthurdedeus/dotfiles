# Product Docs Page Pattern

Product docs pages explain specific features, dashboards, configurations, or concepts within a PostHog product.

## When to use this pattern

- Feature documentation (dashboard, configuration, specific capability)
- Concept explainers (what is MRR, how deferred revenue works)
- Integration/connection pages (connecting Stripe, linking customers)

## Anatomy

### Frontmatter

```yaml
---
title: Page title in sentence case
sidebar: Docs
showTitle: true
---
```

### Standard structure

```
1. Beta warning import + render (if applicable)
2. Opening paragraph (1-3 sentences — what this page covers, why it matters)
3. Main content sections (## headings)
4. Each section: explanation → screenshot → details
5. Cross-references to related pages at natural points
```

### Opening paragraph

Get straight to the point. No "In this guide, we'll walk you through..." preamble.

**Good:**
> The revenue analytics dashboard provides an overview of your revenue data. For the selected time range, it starts with the total revenue alongside how many paying customers you have and the average revenue for each.

**Bad:**
> Revenue is the lifeblood of any business. Understanding your revenue metrics is crucial for making informed decisions. In this comprehensive guide, we'll walk you through everything you need to know about the revenue analytics dashboard.

### Section structure

Each `##` section follows this pattern:

1. **What it is** (1-2 sentences)
2. **Screenshot** showing the UI (ProductScreenshot component)
3. **Details** as needed (how it's calculated, configuration options, edge cases)
4. **Cross-links** to related pages when relevant

### Tables for configuration options and field descriptions

Use tables when documenting fields, properties, or configuration options:

```md
| Field | Description | Example |
| --- | --- | --- |
| **Name** | The column title shown in lists | `API Calls` |
| **Interval** | Time period: 7, 30, or 90 days | `30` |
```

### Linking to the PostHog app

When referencing a settings page or UI location, link directly:

```md
You can configure this in the [revenue analytics settings](https://us.posthog.com/data-management/revenue).
```

### Cross-referencing other docs

Use Wikipedia-style links — first mention of a PostHog feature should link to its docs:

```md
PostHog automatically defers [revenue recognition](/docs/revenue-analytics/deferred-revenue) to match your accounting practices.
```

## Dashboard documentation pattern

For pages documenting a dashboard (like revenue analytics dashboard or customer analytics dashboard):

1. Brief intro paragraph
2. Screenshot of the full dashboard
3. One `##` section per metric/chart, each containing:
   - What the metric is (1-2 sentences)
   - How it's calculated (if non-obvious)
   - Screenshot of that specific chart
   - Any configuration or caveats
4. Filters/breakdowns section (if the dashboard supports them)

## Feature configuration pattern

For pages explaining how to configure something (like "Configure your dashboard"):

1. Brief intro
2. Screenshot of the configuration UI
3. One section per configuration field, explaining:
   - What it controls
   - What values to use
   - Tips for getting it right
4. Link to AI helper if available

## Integration/connection pattern

For pages about connecting external data (like Stripe, Zendesk):

1. Brief intro stating what gets connected and why
2. CalloutBox for users who already have the connection
3. Step-by-step setup (use Steps component if >3 steps)
4. "How is the data stored?" section
5. Related features section (deferred revenue, customer linking, etc.)

## Common mistakes

- Writing sections that are all explanation and no screenshots. Almost every section should have a visual.
- Burying the "how to do it" under "why you should do it". Action first, rationale second.
- Forgetting to link to the PostHog app where users actually do the thing.
- Using heading levels inconsistently. `##` for main sections, `###` for subsections within those.
- Repeating information that lives on another docs page. Link to it instead. Brief context is fine, but don't duplicate full explanations.
