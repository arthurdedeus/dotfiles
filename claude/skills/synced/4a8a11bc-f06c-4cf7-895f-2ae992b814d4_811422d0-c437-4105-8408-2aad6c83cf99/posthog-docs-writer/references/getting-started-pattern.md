# Getting Started Page Pattern

Getting-started pages are the entry point for a product. They use the QuestLog component to walk users through setup in a guided, sequential way.

## When to use this pattern

- New product setup guides
- Onboarding flows that have multiple required/optional steps
- Pages titled "Getting started with [product]"

## Anatomy

Based on the revenue analytics and customer analytics getting-started pages:

### Frontmatter

```yaml
---
title: Getting started with [product name]
hideRightSidebar: true
contentMaxWidthClass: max-w-5xl
---
```

### Imports

```tsx
import { QuestLog, QuestLogItem } from 'components/Docs/QuestLog'
import OSButton from 'components/OSButton'
import BetaWarning from './_snippets/product-beta-warning.mdx'
```

### Structure

```
1. Beta warning (if applicable)
2. Brief intro paragraph (1-2 sentences max — what the product does and who it's for)
3. QuestLog with QuestLogItems
```

### QuestLog pattern

```tsx
<QuestLog firstSpeechBubble="Let's get started!" lastSpeechBubble="Closing encouragement!">

<QuestLogItem title="Action-oriented title" subtitle="Required" icon="IconCode">

Brief explanation of what this step does and why (2-3 sentences max).

Screenshot showing the relevant UI.

Any tips or details as short prose.

<OSButton variant="primary" asLink to="/docs/path-or-app-url" external>
    Call to action
</OSButton>

</QuestLogItem>

</QuestLog>
```

### QuestLogItem guidelines

- **title**: Start with a verb. "Configure your revenue source", "Define usage metrics", "Visit the dashboard".
- **subtitle**: Use "Required", "Recommended", or "Optional" to set expectations.
- **icon**: Pick from PostHog's icon library. Common choices: `IconCode`, `IconGraph`, `IconPeople`, `IconHandMoney`, `IconPiggyBank`, `IconTrends`.
- **Content**: Keep each item focused. One concept per item. Use screenshots to show what they'll see.
- **Button**: End each item with an OSButton linking to the relevant config page or docs page.

### Ordering

1. Required setup steps first (data source, core configuration)
2. Recommended enhancements second (connecting data, exploring features)  
3. Optional/informational items last (pricing, advanced features)

## Example: Customer Analytics getting-started

This page has 3 QuestLogItems:

1. **Configure dashboard events** (Required) — explains event configuration with screenshot and tips
2. **Define usage metrics** (Recommended) — links to usage metrics creation with screenshot
3. **Explore customer profiles** (Optional) — shows what profiles look like

## Example: Revenue Analytics getting-started

This page has 5 QuestLogItems:

1. **Configure your revenue data source** (Required) — data warehouse or events
2. **Choose your reporting currency** (Required) — currency configuration
3. **Visit the revenue analytics dashboard** (Recommended) — main dashboard
4. **Connect to customers** (Recommended) — customer linking
5. **Use for free** (informational) — pricing and free tier info

## Common mistakes

- Making the intro too long. One or two sentences is enough. The QuestLog IS the content.
- Putting too much detail inside each QuestLogItem. Link to dedicated docs pages for depth.
- Forgetting the OSButton at the end of each item. Users need a clear next action.
- Using vague subtitles. "Required" / "Recommended" / "Optional" are the standard options.
