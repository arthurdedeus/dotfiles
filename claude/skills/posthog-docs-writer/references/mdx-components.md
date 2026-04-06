# PostHog MDX Components Reference

All components are globally available — no imports needed unless noted.

## Table of contents

1. [Images and media](#images-and-media)
2. [Code blocks](#code-blocks)
3. [Callout boxes](#callout-boxes)
4. [Page structure](#page-structure)
5. [Links and references](#links-and-references)
6. [Interactive elements](#interactive-elements)

## Images and media

### ProductScreenshot

Wraps screenshots with border and background to distinguish from page content. Use for all app screenshots.

```tsx
<ProductScreenshot
    imageLight="https://res.cloudinary.com/dmukukwp6/image/upload/..."
    imageDark="https://res.cloudinary.com/dmukukwp6/image/upload/..."
    alt="Description of what the screenshot shows"
    classes="rounded"
/>
```

- `imageDark` is optional — light image used for both modes if omitted.
- Pass `zoom={false}` to disable click-to-zoom (zooming is on by default).

### ProductVideo

Same pattern as screenshots but for video. Import video URLs at top of file.

```tsx
---
export const VideoLight = "https://res.cloudinary.com/dmukukwp6/video/upload/..."
export const VideoDark = "https://res.cloudinary.com/dmukukwp6/video/upload/..."
---

<ProductVideo
    videoLight={VideoLight}
    videoDark={VideoDark}
    classes="rounded"
/>
```

### ImageSlider

Carousel of images:

```html
<ImageSlider>
    ![alt](url1)
    ![alt](url2)
</ImageSlider>
```

### Caption

Add captions below images:

```tsx
<Caption>Caption text here</Caption>
```

## Code blocks

### Basic with syntax highlighting

Use language identifier after opening backticks:

````md
```python
posthog.capture("event_name", {"property": "value"})
```
````

Supported languages: html, css, js, jsx, ts, tsx, swift, dart, objectivec, node, elixir, go, java, php, ruby, python, c, cpp, bash/shell, json, xml, sql, graphql, markdown, mdx, yaml, git.

### MultiLanguage

Show code in multiple languages with tabs:

````md
<MultiLanguage>

```js
console.log('Hello')
```

```python
print('Hello')
```

</MultiLanguage>
````

Important: blank lines between snippets and around the component tags.

### File indicator

```md
```yaml file=values.yaml
cloud: 'aws'
```
```

Don't quote the filename.

### Code highlighting

- `// +` — green highlight (additions)
- `// -` — red highlight (removals)
- `// HIGHLIGHT` — yellow highlight (emphasis)

### Collapsed code blocks

Focus on specific lines of large files:

````md
```json file=config.json focusOnLines=4-14
{ full json here }
```
````

## Callout boxes

Three types — use sparingly for important information:

```tsx
<CalloutBox icon="IconInfo" title="Title text" type="fyi">
Content here. Markdown supported.
</CalloutBox>
```

Types:
- `fyi` — helpful but not critical information
- `action` — tasks developers should complete
- `caution` — potential for misconfiguration, data loss

Requires import at top of file:
```tsx
import { CalloutBox } from 'components/Docs/CalloutBox'
```

### Blockquote notes

For simpler callouts, use standard markdown blockquotes:

```md
> **Note:** Brief note here.
```

## Page structure

### QuestLog (getting-started pages only)

For setup/onboarding pages with a step-by-step quest structure:

```tsx
import { QuestLog, QuestLogItem } from 'components/Docs/QuestLog'

<QuestLog firstSpeechBubble="Let's get started!" lastSpeechBubble="You're all set!">

<QuestLogItem title="Step title" subtitle="Required" icon="IconCode">

Content in **markdown**.

</QuestLogItem>

</QuestLog>
```

Requires frontmatter: `hideRightSidebar: true` and `contentMaxWidthClass: max-w-5xl`.

### Steps (sequential instructions)

For how-to guides and tutorials:

```mdx
<Steps>

<Step title="Install the SDK" badge="required">
Content here.
</Step>

<Step title="Verify installation" badge="optional">
Content here.
</Step>

</Steps>
```

Add `showStepsToc: true` to frontmatter for a steps-only table of contents.

### Tabs

For content variants (install methods, languages, etc.):

```tsx
import Tab from 'components/Tab'

<Tab.Group tabs={['Web', 'iOS', 'Android']}>
    <Tab.List>
        <Tab>Web</Tab>
        <Tab>iOS</Tab>
        <Tab>Android</Tab>
    </Tab.List>
    <Tab.Panels>
        <Tab.Panel>Web content</Tab.Panel>
        <Tab.Panel>iOS content</Tab.Panel>
        <Tab.Panel>Android content</Tab.Panel>
    </Tab.Panels>
</Tab.Group>
```

### Collapsible sections

```html
<details>
<summary>Question or title</summary>

Answer or hidden content.

</details>
```

## Links and references

### TeamMember

Mention a team member (links to their profile):

```tsx
<TeamMember name="Cory Watilo" />        // text only
<TeamMember name="Cory Watilo" photo />   // with photo
```

### SmallTeam

Mention a small team:

```tsx
<SmallTeam slug="brand" />               // with mini crest
<SmallTeam slug="brand" noMiniCrest />    // inline text only
```

### Private links

For links to internal/confidential resources:

```tsx
<PrivateLink url="https://private-url">click here</PrivateLink>
```

### OSButton

Styled button links:

```tsx
import OSButton from 'components/OSButton'

<OSButton variant="primary" asLink to="/docs/path">
    Button text
</OSButton>
```

For external links add `external`:

```tsx
<OSButton variant="primary" asLink to="https://app.posthog.com/..." external>
    Open in PostHog
</OSButton>
```

## Interactive elements

### AskMax (PostHog AI on docs)

Opens PostHog AI chat in docs context:

```tsx
<AskMax
    title="Need help?"
    quickQuestions={[
        'How do I set up feature flags?',
        'Why are my events not showing?',
    ]}
/>
```

### MaxCTA (link to PostHog AI in app)

Pre-loaded question linking to PostHog AI:

```tsx
<MaxCTA question="What's my churn rate?" />
```

### AskAIInput

Inline AI input field (for troubleshooting pages):

```tsx
<AskAIInput placeholder="Type your question and hit enter..." />
```

### ArrayCTA

Simple call-to-action block. Use on high-intent pages (comparisons):

```tsx
<ArrayCTA />
```

### ProductChangelog

Auto-renders changelog for a product:

```tsx
import { ProductChangelog } from 'components/Docs/ProductChangelog'

<ProductChangelog product="Customer Analytics" />
```

## Beta/alpha warning snippets

Create a shared snippet file (e.g., `_snippets/product-beta-warning.mdx`) and import it at the top of each page:

```tsx
import BetaWarning from './_snippets/product-beta-warning.mdx'

<BetaWarning />
```

The snippet itself uses a CalloutBox:

```tsx
import { CalloutBox } from 'components/Docs/CalloutBox'

<CalloutBox icon="IconInfo" title="[Product] is in beta" type="fyi">
Brief description of beta status and any limitations.
</CalloutBox>
```

## MDX gotchas

- Avoid indenting by more than 2 spaces — Gatsby's parser gets confused.
- Every JSX tag with inner markdown needs a blank line after opening tag and before closing tag.
- Empty lines must be truly empty (no spaces).
- Different snippets can't share the same filename and import alias.
- Run `yarn format:docs` to auto-fix common formatting issues.
