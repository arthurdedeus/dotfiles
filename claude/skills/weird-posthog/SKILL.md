---
name: weird-posthog
description: Use when implementing a weird, unhinged, or deliberately fun idea inside the PostHog **app** repo (github.com/PostHog/posthog at ~/Code/posthog) — typically sourced from the #do-more-weird Slack channel (C04JN5NNMPF). Triggers on `/weird-posthog`, `/do-more-weird` referring to the app, ideas about Max personas (pirate, ye olde english, hedgehog squeaks), plan-name jokes, in-app easter eggs, leaderboards, treasure-map site maps, potential meters, AI-mode gags, or any "PostHoggy" request to ship something fun to the product itself. NOT for posthog.com (use posthog-do-more-weird) or for serious feature work.
---

# Implementing weird ideas in the PostHog app

## The job

Take one weird idea and ship a working, feature-flagged, draft PR against `github.com/PostHog/posthog` with the requester tagged as reviewer. They should be able to flip the flag locally, laugh, and merge — or reject — in under five minutes.

**Bar:** unhinged > polished. If you're hesitating because it feels silly, that's the signal to keep going. Joy is the deliverable.

## Three non-negotiables

1. **Feature flag everything.** No weird behavior reaches real users until somebody flips the flag. Default off, registered in `FEATURE_FLAGS`, gated end-to-end.
2. **Tag the requester as reviewer.** They proposed it; they ship it. Not you.
3. **Vertical slice, not framework.** One flag, one surface, one joke, one PR. Tiny diff. The joke either lands in the diff or it doesn't — there is no "phase 2".

Skipping any of these = not done.

## When to use this skill

- Idea forwarded from `#do-more-weird` targeting the product (not the marketing site)
- Request mentions Max personas/speaking modes, hedgehog gags, treasure maps, leaderboards, "potential meters", in-app easter eggs, plan-name jokes that live in the app UI
- "Make it weird", "ship something fun", "PostHoggy idea" framings aimed at the app
- A teammate names a person and says "their idea" — that's a sign you should tag them

## When NOT to use

- Marketing site changes → `posthog-do-more-weird`
- Docs / handbook / changelog → `posthog-docs-writer`
- Anything touching real billing math, auth, rate limits, capture pipeline guarantees, or migration of person/group data — the bit must not break invariants. Renaming labels: fine. Touching `posthog/auth.py`, `billing_v2/` math, `personhog_client/`, or ingestion: no.

## Repo essentials

- **Path:** `/Users/arthur/Code/posthog`. Clone from `github.com/PostHog/posthog` if missing.
- **Authoritative agent docs:** `~/Code/posthog/CLAUDE.md` and `CLAUDE.local.md`. Both are already loaded for you when working in this directory; they override anything in this skill if they conflict.
- **Stack:** Django (Python, `posthog/`) + Kea + React + TypeScript (`frontend/src/`). Products live under `products/`.
- **Env:** `flox activate -- bash -c "<command>"` for backend tooling. Never `flox activate` interactively (hangs).
- **Dev server:** `./bin/start` or `hogli start`. Frontend on `:8000` via webpack proxy.
- **Lint:** `ruff check . --fix && ruff format .` (Python); `pnpm --filter=@posthog/frontend format` (frontend).
- **Tests:** `hogli test <path>` — universal runner.
- **Typecheck:** `pnpm --filter=@posthog/frontend typescript:check` — but **don't run it immediately after editing Kea logic files**. Kea's typegen needs to run first (see `CLAUDE.local.md`).
- **API regen:** `hogli build:openapi` after serializer changes. If your weird idea touches a DRF serializer, invoke `/improving-drf-endpoints` and `/adopting-generated-api-types` skills.

## Feature-flag mechanics (verified against repo)

**Register the flag** in `frontend/src/lib/constants.tsx`, in the `FEATURE_FLAGS` object, with an owner comment:

```ts
// in FEATURE_FLAGS:
WEIRD_<UPPERCASE_SLUG>: 'weird-<kebab-slug>', // owner: @<requester-or-you>, weird idea — see PR #NNNN
```

**Frontend gating** — `useFeatureFlag` hook from `lib/hooks/useFeatureFlag`:

```tsx
import { useFeatureFlag } from 'lib/hooks/useFeatureFlag'
import { FEATURE_FLAGS } from 'lib/constants'

const isWeirdOn = useFeatureFlag(FEATURE_FLAGS.WEIRD_MAX_PIRATE)
return isWeirdOn ? <Yarr /> : <NormalThing />
```

For declarative gating use the existing `<FlaggedFeature>` component in `frontend/src/lib/components/FlaggedFeature.tsx`.

**Backend gating** — `posthoganalytics.feature_enabled(...)`:

```python
import posthoganalytics

if posthoganalytics.feature_enabled('weird-<slug>', str(user.distinct_id)):
    ...
```

**Create the flag in PostHog itself via the PostHog MCP** (`mcp__posthog__exec`, `feature-flag` domain) so the reviewer doesn't have to. Target the user's active project (US cloud, project `🎉 PostHog App + Website` / id `2` unless the user is scoped elsewhere — confirm from MCP context if unsure).

Create it with:
- Key: matches the string value you used in `FEATURE_FLAGS` exactly (e.g. `weird-max-pirate`)
- Name: short human-readable label, e.g. "Weird: Max pirate speaking mode"
- Description: one line — the idea + a link to the PR (you can patch the URL in after the PR exists)
- **Rollout: 0% / disabled.** Default off everywhere. The reviewer enables it for themselves.
- Tag with `weird` if the MCP supports tags

If the PostHog MCP isn't available in the current session, fall back to "flag registered in code only; reviewer will create it in PostHog" and call that out explicitly in the PR body. Don't block on this.

## Workflow

1. **Pick the funniest interpretation that fits in one PR.** Don't ask the user to clarify unless the idea is literally undefined. Your PR description states your interpretation; the requester can comment.
2. **Identify the requester.** Look in the prompt for a name/handle ("Cory's idea", "from @benlea"). That's your reviewer. If only a first name is given, search the repo's `CODEOWNERS` or recent PR authors for a likely GitHub login. If genuinely unidentifiable, leave reviewer tagging for the user to do at the end.
3. **Branch from latest master:**
   ```bash
   cd ~/Code/posthog && git fetch origin && git checkout master && git pull && git checkout -b weird/<slug>
   ```
4. **Find the surface.** For UI ideas, locate the smallest existing component you can wrap or branch from. For Max-persona ideas, look in `products/max_ai/`. For sidebar/nav additions, `frontend/src/layout/`. For mascot bits, search `HedgehogBuddy`. Mimic adjacent patterns — don't invent new ones.
5. **Add the flag** to `FEATURE_FLAGS` first. Reference it from the new code path.
6. **Create the flag in PostHog via MCP.** Use `mcp__posthog__exec` with the `feature-flag` domain to create the flag in the user's active project at 0% rollout / disabled. Key must match the string in `FEATURE_FLAGS`. If MCP is unavailable, skip and note it in the PR body — don't block.
7. **Implement the slice.** Edit existing files when possible. Keep the diff readable in two minutes. If you find yourself splitting into multiple files, you're over-building.
8. **Run it.** `./bin/start`, then open the affected URL in Claude in Chrome MCP. Flip the flag locally — either via the toolbar, by overriding via the PostHog MCP on your own user, or stub the hook in dev. Confirm the joke visually lands. **Type-checks pass ≠ joke works.**
9. **Capture a GIF** for any visual change using `mcp__claude-in-chrome__gif_creator`. Visual diffs without a GIF in the PR get punted.
10. **Lint + targeted tests.** `pnpm --filter=@posthog/frontend format`, `ruff check . --fix`. Run `hogli test <touched_paths>` for the files you actually changed.
11. **Commit.** Conventional commits, lowercase, no period, <72 chars, scope required:
    ```
    feat(max): add pirate speaking mode behind weird-max-pirate flag
    ```
    Use `feat` for new behavior, `chore` for label-only changes. One commit per PR if possible.
12. **Push and open a draft PR** with `gh pr create --draft --base master`. Body uses the repo's PR template (read `.github/pull_request_template.md`):
    - **Problem:** restate the weird idea + credit the requester ("Idea from @handle in #do-more-weird")
    - **Changes:** the slice you shipped, with the flag name + a link to the PostHog flag you created via MCP (or a note that MCP was unavailable and the flag needs manual creation). Include the GIF here.
    - **How did you test this code?:** declare you're an agent and list the automated tests/checks you actually ran. Do not claim manual testing you didn't do.
    - **Publish to changelog?:** `no` — it's flagged and off by default.
    - **🤖 Agent context:** tools/agent used, interpretation chosen, what you tried/rejected. Paraphrase user intent; never paste prompts verbatim.
13. **Patch the flag's description in PostHog** (via MCP) with the PR URL now that it exists, so anyone landing on the flag in PostHog can find the code.
14. **Add the requester as reviewer:** `gh pr edit <PR#> --add-reviewer <github-username>`. If you couldn't identify them, surface this back to the user so they can do it.
15. **Report back** with the PR URL, the flag link in PostHog, and one line on how to flip it locally.

## Don't push until done

The repo's CI burns runner credits on every push. Batch local commits; push once when the PR is actually ready (visual check passed, lint passed, tests for changed files pass).

## Idea → smallest-slice mapping (illustrative, not exhaustive)

| Idea shape | Smallest shippable slice |
|---|---|
| Max speaking mode (pirate, ye olde english, hedgehog squeaks) | One flag. In Max's system-prompt assembly (`products/max_ai/`), append a persona instruction when the flag is on for the requester. |
| 11labs-voice MCP response | One flag. New optional MCP response transform that, when flag + env-var key are set, POSTs the response text to 11labs and returns an audio URL. Fallback to text when key missing. |
| Potential meter / surface-area indicator | One flag. New sidebar widget that reads a hardcoded "used features" list (real telemetry later). Tooltip: "you've explored X% of PostHog". |
| Treasure-map site map (Max-as-pirate) | One flag. New route `/treasure-map`. Static SVG with feature pins; trail rendered from a stub "visited" array. Hedgehog asset wearing pirate hat. |
| Rename paid plans to "cheaper" / "more expensive" | One flag. Map plan-label dictionary in the billing-page React component to the new strings when flag is on. **Do not touch billing math.** |
| Token-usage leaderboard | One flag. New admin/instance page that embeds an existing PostHog insight via `<InsightCard>`. Insight ID hardcoded. |
| AI got jokes | One flag. Append "end every Max response with a hedgehog-themed dad joke" to Max's system prompt when flag is on. |
| `/karen mode` | One flag. Persona variant in the same Max system-prompt switch as pirate mode. |

The pattern repeats: **one flag, one file (mostly), one joke, draft PR, ship.**

## Voice and copy

- Sentence case for buttons, labels, tabs. American English. Oxford comma.
- Product names use sentence case: "Product analytics", not "Product Analytics".
- Lean into PostHog vocabulary: Max (the AI character), hedgehogs (the mascot — there's a `<HedgehogBuddy>` component), Hog (the language). Self-aware jokes about PostHog's own pricing/usage are encouraged.
- Use `<Link>` not `<a>` for internal nav.
- Tailwind utility classes only, no inline styles.

## Public-repo guardrails

This repo is open source. Commit messages, PR titles, and PR descriptions are public. Do not include:

- Internal Slack thread URLs, customer names, private incident details, unreleased roadmap
- Quoted user prompts (paraphrase intent in the Agent context section)
- Operational scale anecdotes ("our 12M rows")

Crediting a teammate by GitHub handle is fine — that's public attribution.

## Red flags — stop and reset

| Thought | Reality |
|---|---|
| "I'll skip the feature flag, it's harmless" | Non-negotiable #1. Add the flag. |
| "I'll merge it myself once CI is green" | Non-negotiable #2. The requester ships it. |
| "Let me build a proper framework for weird ideas" | Non-negotiable #3. One file, one flag, one joke. |
| "I should ask three clarifying questions first" | No. Pick the funniest interpretation. Ship. The PR is the conversation. |
| "Tone it down so it doesn't seem unprofessional" | No. Match the energy of the original idea. |
| "Type-check passed, calling it done" | No. Open it in a real browser, flip the flag, see the joke. |
| "I'll push after each commit to watch CI" | No. Push once, when actually ready. |
| "I'll paste the user's prompt into the PR for context" | No. Paraphrase in Agent context. |
| "I'll backfill telemetry/real data later in the same PR" | No. Stub data is fine for v0. Split out the real data PR. |

## Common mistakes

- **Empty/skeleton PR.** "TODO: fill in the joke" gets ignored. The diff *is* the joke.
- **Forgot to register the flag in `FEATURE_FLAGS`.** The hook returns undefined and the gate is permanently off (or worse, behaves oddly in dev).
- **Touched generated files.** Anything under `frontend/src/generated/core/` or `products/*/frontend/generated/` is auto-generated. Change the serializer and run `hogli build:openapi` instead.
- **Skipped the `## 🤖 Agent context` section.** The repo's PR template requires it for agent-authored PRs.
- **Capitalized the commit message or added a period.** Repo enforces lowercase conventional commits, no trailing period.
- **External API call without env-var fallback.** If the bit calls 11labs / OpenAI / anything paid, gate it on `os.environ.get('FOO_KEY')` and fall back gracefully when missing.
- **Touched person/group ORM directly.** Use `personhog_client` helpers (see `CLAUDE.md`). Almost no weird idea actually needs this — if you find yourself reaching for it, scope down.

## Definition of done

- [ ] Idea interpreted, smallest slice chosen
- [ ] Branch `weird/<slug>` off latest master
- [ ] Flag added in `FEATURE_FLAGS` with owner comment, default off
- [ ] Flag created in PostHog itself via `mcp__posthog__exec` (feature-flag domain), 0% rollout, in the user's active project — OR explicit fallback note in PR if MCP unavailable
- [ ] All new behavior gated behind the flag (frontend + backend if applicable)
- [ ] Dev server started, joke verified visually in Claude in Chrome with flag ON
- [ ] GIF captured for any visual change
- [ ] Lint + format pass; targeted tests for changed files pass
- [ ] Conventional-commit message (lowercase, scoped, no period)
- [ ] Draft PR opened against `master`; PR body uses repo template, includes Agent context section, credits requester, links the PostHog flag, includes GIF
- [ ] Flag description in PostHog patched with PR URL after PR is open
- [ ] Requester added as reviewer (or surfaced to user if unidentifiable)
- [ ] Pushed once (not after every commit)
- [ ] Reported back with PR URL + PostHog flag link + how to flip it
