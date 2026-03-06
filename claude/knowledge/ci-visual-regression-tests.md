# Visual Regression Tests — Patterns & Architecture

## How the pipeline works

1. CI builds Storybook into a static bundle
2. `@storybook/test-runner` (Jest + Playwright) navigates to each story
3. Waits for readiness (loaders gone, selectors present, images loaded)
4. Takes screenshots via Playwright and compares against PNG baselines in `frontend/__snapshots__/`
5. First run creates baselines; subsequent runs do pixel-diff comparison

## Key files

- CI workflow: `.github/workflows/ci-storybook.yml`
- Test runner config: `common/storybook/.storybook/test-runner.ts`
- Snapshot directory: `frontend/__snapshots__/`
- Shard sequencer: `common/storybook/test-sequencer.js` (greedy bin-packing based on timing data)
- CSS that affects tests: `frontend/src/styles/base.scss` (search for `storybook-test-runner`)

## Sharding

- 16 Chromium shards + 4 WebKit shards = 20 parallel CI jobs
- Greedy bin-packing assigns longest-running stories first to lightest shard
- Timing data lives in `common/storybook/storybook-timings.json`
- New (unknown) stories distributed round-robin

## Screenshot targeting by layout mode

| Layout | `#storybook-root` CSS | Screenshot target |
|---|---|---|
| `padded` (default) | `display: inline-block` (shrink-to-fit) | `#storybook-root` |
| `fullscreen` | normal flow | `body, main` |
| `centered` | normal flow | `#storybook-root` |

The `inline-block` on padded layout is the source of a common failure pattern (see below).

## Browser behavior differences

- Snapshots taken on **Chromium only** by default (`snapshotBrowsers: ['chromium']`)
- WebKit runs tests but doesn't take snapshots unless overridden
- Chromium and WebKit resolve CSS edge cases differently — a test passing on WebKit but failing on Chromium is a strong signal of a CSS layout issue

## Timeouts

- Playwright action timeout: 10s (`PLAYWRIGHT_TIMEOUT_MS`)
- Jest test timeout: 25s (`JEST_TIMEOUT_MS`)
- Retries: 2 (`RETRY_TIMES`)

## Common failure pattern: "element is not visible" timeout

**Mechanism**: `padded` layout sets `#storybook-root { display: inline-block }`. If a child element uses `width: 100%`, the parent (shrink-to-fit) and child (percentage of parent) create a **circular CSS dependency**. Chromium resolves this as zero width, making the element invisible to Playwright. WebKit resolves it more forgivingly.

**Symptoms**:
- `locator.screenshot: Timeout ~10s`
- `element is not visible`
- `retrying scroll into view action`
- Each story takes exactly the timeout duration
- Passes on WebKit, fails only on Chromium

**Fix strategies** (pick one):
- Replace `width: '100%'` with explicit pixel width
- Set `testOptions: { snapshotTargetSelector: '.specific-element' }`
- Change to `layout: 'fullscreen'`

## Story parameters reference

```typescript
parameters: {
    layout: 'padded' | 'fullscreen' | 'centered',
    testOptions: {
        waitForSelector: string | string[],
        snapshotTargetSelector: string,
        snapshotBrowsers: SupportedBrowserName[],
        waitForLoadersToDisappear: boolean,  // default: true
        allowImagesWithoutWidth: boolean,
        includeNavigationInSnapshot: boolean, // fullscreen only
        viewport: { width: number, height: number },
        skipIframeWait: boolean,
    },
}
```

## Loader selectors (test waits for these to disappear)

`.Spinner`, `.LemonSkeleton`, `.LemonTableLoader`, `.Toastify__toast`, `[aria-busy="true"]`, `.SessionRecordingPlayer--buffering`, `.Lettermark--unknown`, `[data-attr="loading-bar"]`

## Running locally

```bash
# Debug mode (quick iteration, won't match CI exactly)
pnpm --filter=@posthog/frontend storybook          # Terminal 1
pnpm exec playwright install                        # once
pnpm --filter=@posthog/storybook test:visual:debug  # Terminal 2

# Reproduce a specific shard
pnpm --filter=@posthog/storybook test:visual:ci:verify --browsers chromium --shard 10/16

# Update snapshots via Docker (matches CI rendering)
pnpm --filter @posthog/storybook test:visual:update
```

## Investigation commands

```bash
# 1. Overview
gh pr checks

# 2. Failed job logs
gh run view <run-id> --log-failed 2>&1 | grep -E "(FAIL|PASS)" | head -30

# 3. Error signatures
gh run view <run-id> --log-failed 2>&1 | grep -E "(Timeout|snapshot|Error|missing)" | head -20

# 4. Cross-browser comparison
gh run view <run-id> --log 2>&1 | grep -E "(PASS|FAIL).*<StoryName>"
```
