# PostHog MDX components

The live repository is authoritative. Read `contents/handbook/docs-and-wizard/mdx-and-components.mdx` and inspect current usage before adding a component.

## Common choices

- `ProductScreenshot`: app screenshots with the standard frame.
- `ProductVideo`: product recordings.
- `CalloutBox`: important information, action, or caution.
- `Steps` and `Step`: ordered procedures.
- `MultiLanguage`: equivalent code in several languages.
- `QuestLog`: guided getting-started pages.
- `Tab`: content variants.
- `PrivateLink`: internal links that must not render publicly.
- `TeamMember` and `SmallTeam`: handbook ownership references.

Do not add a component because it appears in this list. Confirm that it still exists and copy its current import and props.

## Selection rules

- Use plain Markdown before a custom component.
- Use one component for one clear purpose.
- Keep content readable in source.
- Add blank lines around Markdown nested inside JSX.
- Keep indentation consistent with nearby files.
- Give every image useful alt text.
- Do not embed secrets, private URLs, or customer data.

## Verification

1. Find recent examples in the same docs area.
2. Inspect the component definition when props are unclear.
3. Run `pnpm format:docs`.
4. Preview the changed page when layout or interaction changed.
