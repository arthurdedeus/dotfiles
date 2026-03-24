---
name: write-snapshot-test
description: Generate visual regression tests (Storybook stories) for PostHog components
---

# Write Snapshot Test for PostHog Component

Generate a Storybook story file with visual regression testing for a given component.

## Required Context

When using this command, provide:
1. **Component name and path** - e.g., "LemonButton in lib/lemon-ui/LemonButton"
2. **Component props/interface** - The TypeScript interface or props definition
3. **Key states to test** - Different variants, loading states, error states, etc.

## Before You Start

Before writing any new stories, check if snapshot coverage already exists:

1. **Search for existing stories** — `grep -r 'ComponentName' --include='*.stories.tsx'` in the relevant directory and neighboring directories
2. **Search for existing snapshots** — check `frontend/__snapshots__/` for files matching the component or scene name (snapshots follow `{story-id}--{theme}.png` naming)
3. **If a story already covers the needed state** (e.g., an empty state story exists and you only changed text in the component it renders), no new story is needed. The existing story will automatically pick up the change, and **CI will regenerate the snapshot PNGs**. Inform the user and stop.

## Implementation Instructions

### File Structure
- Stories go in the same directory as the component: `ComponentName.stories.tsx`
- Import pattern: `import { Meta, StoryObj } from '@storybook/react'`

### Story Template Structure

```typescript
import { Meta, StoryObj } from '@storybook/react'
import { ComponentName } from './ComponentName'

const meta: Meta<typeof ComponentName> = {
    title: 'Category/ComponentName', // Use proper categorization
    component: ComponentName,
    tags: ['autodocs'], // Include for component documentation
    parameters: {
        // Configure visual test behavior
        testOptions: {
            // Wait for loaders to disappear (default: true)
            waitForLoadersToDisappear: true,
            // Wait for specific selectors
            waitForSelector: '.specific-element',
            // Multiple selectors
            waitForSelector: ['.element1', '.element2'],
            // Allow broken images (default: false)
            allowImagesWithoutWidth: false,
            // Include navigation in fullscreen stories (default: false)
            includeNavigationInSnapshot: false,
            // Browsers to test (default: ['chromium'])
            snapshotBrowsers: ['chromium', 'webkit'],
            // Custom viewport size
            viewport: { width: 1280, height: 720 },
            // Skip iframe loading wait
            skipIframeWait: false,
        }
    },
}
export default meta

type Story = StoryObj<typeof ComponentName>

// Basic story
export const Default: Story = {
    args: {
        // Component props
    },
}

// Multiple variants showcase
export const AllVariants: Story = () => {
    return (
        <div className="deprecated-space-y-2">
            {/* Render multiple states */}
        </div>
    )
}
```

### Component Categories
Use these standard categories in the title:
- `'Lemon UI/ComponentName'` - For lemon-ui components
- `'Components/ComponentName'` - For lib/components
- `'Scenes/ComponentName'` - For scene-specific components
- `'Insights/ComponentName'` - For insights-related components
- `'Data/ComponentName'` - For data visualization components

### Test Options Configuration

#### Wait Strategies
```typescript
testOptions: {
    // Default: waits for these selectors to be hidden
    // '.Spinner', '.LemonSkeleton', '.LemonTableLoader', '.Toastify__toast',
    // '[aria-busy="true"]', '.SessionRecordingPlayer--buffering',
    // '.Lettermark--unknown', '[data-attr="loading-bar"]'
    waitForLoadersToDisappear: true,

    // Wait for specific element(s) to appear
    waitForSelector: '[data-attr="data-table"]',
    // Or multiple elements
    waitForSelector: ['[data-attr="chart"]', '.PayGateMini'],
}
```

#### Special Cases
```typescript
// For components with async data
testOptions: {
    waitForSelector: '[data-attr="data-loaded"]',
}

// For components with intentionally broken images
testOptions: {
    allowImagesWithoutWidth: true,
}

// For fullscreen layouts that should include navigation
parameters: {
    layout: 'fullscreen',
    testOptions: {
        includeNavigationInSnapshot: true,
    }
}

// For components with external iframes
testOptions: {
    skipIframeWait: true,
}
```

### Common Patterns

#### Testing Multiple States
```typescript
const statuses = ['default', 'alt', 'danger'] as const
const types = ['primary', 'secondary', 'tertiary'] as const

export const AllVariants: Story = () => {
    return (
        <div className="deprecated-space-y-2">
            {types.map((type) => (
                <div key={type}>
                    <h5>type={type}</h5>
                    <div className="flex gap-2">
                        {statuses.map((status) => (
                            <Component
                                key={status}
                                type={type}
                                status={status}
                            >
                                {status}
                            </Component>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    )
}
```

#### Testing with Mock Data
```typescript
import { mswDecorator } from '~/mocks/browser'
import { useStorybookMocks } from '.storybook/useStorybookMocks'

const meta: Meta = {
    decorators: [
        mswDecorator({
            get: {
                '/api/endpoint': { data: 'mocked' },
            },
        }),
    ],
}

// Or in a story
export const WithData: Story = {
    decorators: [
        mswDecorator({
            get: {
                '/api/endpoint': mockData,
            },
        }),
    ],
}
```

#### Testing Loading States
```typescript
export const Loading: Story = {
    args: {
        loading: true,
    },
    parameters: {
        testOptions: {
            waitForLoadersToDisappear: false, // Don't wait for loaders since we want to test them
        },
    },
}
```

### Layout Options
```typescript
parameters: {
    layout: 'padded',    // Default: adds padding around component
    layout: 'centered',  // Centers component in viewport
    layout: 'fullscreen', // Full viewport, no padding
}
```

### Testing Forms and Interactions
```typescript
export const FormStates: Story = {
    render: () => {
        return (
            <div className="deprecated-space-y-4">
                <Component state="default" />
                <Component state="focused" />
                <Component state="error" message="Validation error" />
                <Component state="success" message="Saved!" />
                <Component state="disabled" disabled />
            </div>
        )
    },
}
```

### Important Notes

1. **Automatic theme testing** - Both light and dark themes are captured automatically, no need to specify
2. **Snapshots location** - Stored in `frontend/__snapshots__/` with naming: `{story-id}--{theme}.png`
3. **Browser testing** - Default is Chromium only, add Webkit for critical components
4. **Timeouts** - Tests have a 25s timeout, with 10s for Playwright operations
5. **Comparison method** - Uses SSIM (structural similarity) with 1% threshold, not pixel-perfect
6. **Retries** - Tests retry 2 times on failure
7. **CI behavior** - In CI, tests also wait for network idle state
8. **Existing coverage may suffice** — If you changed text, styles, or markup in a component that an existing story already renders, no new story is needed. The existing story picks up the change automatically and CI will regenerate the snapshots

### Snapshot Generation

**Snapshots are generated in CI (GitHub Actions), not locally.** Do not attempt to run snapshot update commands locally — the Docker-based toolchain requires a full environment that may not be available in worktrees or dev setups.

Your job is to create or modify the `.stories.tsx` file. Once pushed, CI will:
1. Build Storybook
2. Render each story in Chromium
3. Generate/update the `.png` snapshots in `frontend/__snapshots__/`
4. Commit updated snapshots automatically

If you need to debug a story locally, you can run Storybook directly:
```bash
pnpm --filter=@posthog/storybook storybook
```

### Skip Testing
Add tag to skip visual tests:
```typescript
export const SkipVisualTest: Story = {
    tags: ['test-skip'],
    // ...
}
```

## Example Implementation

For a button component with multiple states:

```typescript
import { Meta, StoryObj } from '@storybook/react'
import { IconPlus } from '@posthog/icons'
import { MyButton, MyButtonProps } from './MyButton'

const meta: Meta<typeof MyButton> = {
    title: 'Lemon UI/MyButton',
    component: MyButton,
    tags: ['autodocs'],
}
export default meta

type Story = StoryObj<typeof MyButton>

const statuses: MyButtonProps['status'][] = ['default', 'primary', 'danger']
const sizes: MyButtonProps['size'][] = ['small', 'medium', 'large']

export const Default: Story = {
    args: {
        children: 'Click me',
        icon: <IconPlus />,
    },
}

export const AllVariants: Story = {
    render: () => (
        <div className="deprecated-space-y-4">
            {sizes.map((size) => (
                <div key={size}>
                    <h5>Size: {size}</h5>
                    <div className="flex gap-2 items-center">
                        {statuses.map((status) => (
                            <MyButton
                                key={status}
                                size={size}
                                status={status}
                                icon={<IconPlus />}
                            >
                                {status}
                            </MyButton>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    ),
}

export const Loading: Story = {
    args: {
        loading: true,
        children: 'Loading...',
    },
}

export const Disabled: Story = {
    args: {
        disabled: true,
        children: 'Disabled',
    },
}
```

## Checklist
When creating snapshot tests, ensure:
- [ ] Component renders correctly in both light and dark themes
- [ ] All significant visual states are covered
- [ ] Async content is handled with appropriate wait strategies
- [ ] Story follows PostHog's categorization conventions
- [ ] Props use TypeScript types for documentation
- [ ] Complex components have multiple focused stories
- [ ] Loading and error states are tested if applicable

## After completion

Assess how this skill performed:
- If the user had to provide significant guidance, corrections, or workarounds to get the task done, recommend running `/improve-skill` to capture those learnings. Explain briefly what could be improved.
- If the skill ran smoothly with minimal intervention, offer it as an option: "Would you like to run `/improve-skill` to refine this skill based on this session?"
