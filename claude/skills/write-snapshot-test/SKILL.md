---
name: write-snapshot-test
description: Add or update a PostHog Storybook story for visual regression coverage.
---

# Write a visual regression story

PostHog now uses Visual Review with `frontend/snapshots.yml`. Do not use the retired committed-PNG workflow.

## 1. Check existing coverage

Search for nearby `*.stories.tsx` files and stories that already render the changed state.

If an existing story covers it, update that story only when setup or stability needs a change. Do not add duplicate coverage.

## 2. Read current conventions

Before editing, read:

- The nearest recent stories for the same scene or component.
- `common/storybook/package.json`.
- Relevant parts of `.github/workflows/ci-storybook.yml`.
- Repository skills for Storybook flags or Visual Review, when applicable.

Copy current local patterns. Do not rely on a fixed title taxonomy or old template.

## 3. Build a deterministic story

- Place the story beside the component or in the area's existing story location.
- Use current CSF types such as `Meta` and `StoryObj`.
- Prefer typed `args` for simple components.
- Use `render` for stateful scenes or grouped states.
- Reuse current decorators, fixtures, and `useStorybookMocks` patterns.
- Freeze dates, identifiers, and network responses that affect pixels.
- Cover one meaningful visual state per story.
- Add `testOptions.waitForSelector` only for a stable readiness signal.
- Set `waitForLoadersToDisappear: false` only when the loader is the intended state.
- Use `tags: ['test-skip']` only with a stated reason.

Do not add `autodocs`, browser matrices, timeouts, or custom viewports by habit. Match nearby stories and the behavior under test.

## 4. Verify

Start Storybook when local inspection helps:

```bash
pnpm --filter=@posthog/storybook start
```

Run the focused checks available for the changed area. Confirm that the story settles without live data or timing races.

## 5. Let Visual Review own baselines

CI captures temporary images and compares them through Visual Review. After human approval, the bot updates `frontend/snapshots.yml`.

Do not:

- Commit generated snapshot PNGs.
- Edit `frontend/snapshots.yml` by hand.
- Run an old local PNG update command as the normal workflow.
- Approve a visual change without checking the rendered difference.

Report the story changed, states covered, local checks, and the expected Visual Review step.
