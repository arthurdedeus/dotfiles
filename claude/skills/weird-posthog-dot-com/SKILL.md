---
name: weird-posthog-dot-com
description: Use when implementing a weird/unhinged idea for posthog.com (the public marketing site at github.com/PostHog/posthog.com) — typically sourced from the #do-more-weird Slack channel (C04JN5NNMPF) or framed as easter eggs, novelty variants, themed takeovers, hidden routes, feature-flagged alt experiences, AI gags, or self-aware product jokes. Triggers include "weird idea", "do more weird", "easter egg on the website", "new DPA reading style", "themed posthog.com", "AI mode on the site", or any request to ship something deliberately fun on the marketing site.
---

# posthog.com: implementing weird ideas

## Overview

PostHog's public site is a playground. The `#do-more-weird` channel is where teammates dump unhinged ideas — easter eggs, novelty variants of real features, themed takeovers, fake-but-functional AI gags, self-aware product jokes. Your job: turn one of those ideas into a PR that's **shippable in one go** — working code, CI green, copy in PostHog voice, joke landed.

**The Iron Law: lean unhinged.** When given options, pick the funniest one. The bar isn't "is this acceptable corporate output?" — it's "does the team laugh and want to ship it?" Cory Watilo's reaction to PR #16827 was *"think it might be time to add review requirements lol"*, and Eli's reply was *"that wouldn't be very unc of us"*. That's the target temperature. Stay unc.

## When to use

- Idea posted in `#do-more-weird` / forwarded from there
- Request mentions a specific weird pattern: easter egg URL, DPA reading style, AI gag, killed-product revival, themed-day takeover, feature-flagged alt homepage
- "Make it unhinged" / "do something fun" framings targeting posthog.com
- Self-aware bits about PostHog culture (Max, jAImes, hedgehogs, sunsetted products)

## When NOT to use

- Changes to the PostHog **app** (product analytics) — different repo, different culture
- Serious docs writing — use the `posthog-docs-writer` skill
- Marketing campaigns with launch coordination — those go through normal review
- Anything that touches billing, legal, or signup flows for real — novelty variants of legal docs are fine *as long as* the existing "preview only — generate the real one at app.posthog.com/legal" disclaimer is preserved

## Repo facts (verified)

- **Path on Arthur's laptop:** `/Users/arthur/Code/posthog.com`
- **Stack:** Gatsby 4. Read `AGENTS.md` at the repo root — it's the source of truth and supersedes anything below if they conflict
- **Package manager:** `pnpm` only. Never `npm`
- **Dev server:** `pnpm start` → `http://localhost:8001`. Needs `NODE_OPTIONS='--max_old_space_size=16384'` (16 GB)
- **Reset when broken:** `pnpm clean && mkdir .cache && pnpm i && pnpm start`
- **Format:** `pnpm format`
- **Architecture:** desktop-OS UI paradigm — pages open as draggable, resizable windows via `<Editor />`, `<Reader />`, `<Presentation />`, `<Explorer />`, `<Inbox />`, `<Wizard />`, `<MediaPlayer />`. New pages should use one of these app templates. See `agents/apps.md`
- **Components:** use OS-prefixed wrappers (`OSButton`, `OSTable`, …) from `components/RadixUI/` rather than raw Radix
- **Responsiveness:** Tailwind `@container` queries (windows resize) — never media queries
- **Tailwind colors:** project tokens only, no stock Tailwind colors
- **Redirects:** moving/renaming a page → add redirect in `vercel.json`

## Workflow

1. **Read the idea AND the thread.** Replies often contain the actually unhinged version. Lean toward the most absurd implementable-in-one-PR option.
2. **Find prior art.** Before writing, search the repo for similar weird features:
   - `src/pages/dpa.tsx` — the canonical "novelty variant" reference (modes: `pretty`, `lawyer`, `fairytale`, `tswift`, plus the Gen-Z `zoomer` PR #16827). Mode is local React state, variants are gated with `mode === 'xxx' ? 'block' : 'hidden'`
   - `src/pages/baa.tsx` — sibling generator with the same pattern
   - `src/pages/trash/index.tsx` references a `website-easter-eggs` slug — check for the running list
   - Grep for `usePostHog` for feature-flag patterns
3. **Branch.** `git checkout -b weird/<short-slug>` from `master`.
4. **Implement.** Copy the closest existing pattern verbatim, then warp it. The DPA variants pattern handles ~90% of generator-style ideas.
5. **Test locally.** Start `pnpm start`, open in Claude in Chrome at the actual URL, click through the user flow. Don't claim "working" without a browser screenshot/render — type-checking ≠ feature-checking.
6. **Lint + format.** `pnpm format`. Vale prose lint and the spelling checker are strict on copy — if your weird word triggers them, add to `.vale/` or `.codespellignore` instead of weakening the joke.
7. **PR.** Draft PR. Use the repo's `.github/PULL_REQUEST_TEMPLATE.md` checklist. Tag for vibe-check, not approval.

## Reference patterns (not a taxonomy)

Weird ideas are random by design. **Don't force-fit the idea into a pre-baked shape** — read the idea, then look for the *closest existing thing in the codebase* and pull from it. The list below is just a few well-trodden patterns to anchor on when one of them genuinely fits. If nothing here fits, design fresh.

- **Novelty variant of an existing thing** — the canonical pattern. `src/pages/dpa.tsx` keeps a `mode` state and gates whole sections on `mode === 'xxx'`. Look at the `pretty` / `lawyer` / `fairytale` / `tswift` modes for tone and structure. Sibling: `src/pages/baa.tsx`.
- **Standalone hidden URL** — a new page in `src/pages/` with no nav link, no SEO, single frame. Whatever the joke is, deliver it without ceremony.
- **Feature-flagged alt experience** — `usePostHog()` is already used across the codebase (see `src/pages/dpa.tsx` for an instance). Gate the flag check as high in the tree as the bit demands.
- **Pull-from-history bit** — sunsetted pages are still in `git log --diff-filter=D --summary`. Resurrecting one is sometimes the funniest implementation.
- **Static "AI-generated" content** — usually funnier and shippable as a single PR. Reach for a real LLM call only when the bit collapses without it.

**Beyond that, invent.** A pixel-art floor scene, a date-gated themed takeover, a fake-fulfillment form, a chat-only navigation mode, a printable scroll — none of these have an existing template. Read the idea, sketch the smallest version that lands the joke, build it. The codebase is permissive; the joke is the constraint.

## Voice & copy

PostHog voice: self-aware, slightly self-deprecating, doesn't take itself seriously. Existing reference points:

- DPA fairytale mode: *"we don't recommend sending this version to the lawyers"*
- DPA lawyer label: *"Drab and dull - preferred by lawyers — Because lawyers hate fun but love Times New Roman"*
- Novelty disclaimer (mandatory on legal-doc variants): *"Sorry, our lawyers refuse to recognize this version as a binding…"* — the disclaimer IS part of the joke, don't omit it
- Style guide: `contents/handbook/content/posthog-style-guide.md`. Double quotes. Sentence case. American English. Oxford comma. Relative URLs for internal links

**The "preview only — generate the real one at app.posthog.com/legal" pattern is mandatory** for any novelty variant of a legal document. Keeps the bit safe.

## PostHog culture vocabulary (use freely)

| Term | Meaning |
|------|---------|
| **Max** | PostHog's AI character. Default mascot for AI gags |
| **jAImes / Jamse** | Running joke "AI co-CEO" persona — pure fiction, fair game |
| **Hedgehogs** | The mascot. Appears liberally; reach for `<Hedgehog />` and the hedgehog assets in `src/images/` |
| **DeskHog** | PostHog's ESP32 hardware mini-device. Referenced in hardware-adjacent ideas |
| **"Unc energy"** | Slack-native vibe descriptor — lean into it |
| **Killed products** | Product Tours, Helm support, etc. Self-aware sunsetting jokes are encouraged |
| **"Vibe-check"** | What PostHog does instead of LGTM. PRs are not approval-gated |

## PR conventions

Title: lowercase, descriptive of the joke, e.g. `add zoomer-speak reading style to /dpa`. Skip ceremony.

Body: use the repo's existing template, plus:
- One-line summary of the joke
- Link to the `#do-more-weird` Slack thread if you have it
- Who proposed it (credit the proposer)
- Screenshot or GIF for any visual change — non-negotiable for UI bits (use Claude in Chrome's `gif_creator`)
- Confirm template checklist items: read style guides, American English, relative URLs for internal links, checked the Vercel preview, added redirect to `vercel.json` if you moved a page

Reviewers:
- **Tag the proposer.** They get to laugh at their own idea.
- **Tag for vibe-check, not approval.** Cory Watilo for design vibes; `annamarie-d` and `joethreepwood` are typical vibe-check routers based on PR #16827.
- **Open as draft first**, undraft once CI passes and you've eyeballed the Vercel preview.

CI runs ~19 required checks (Analyze x3, CodeQL, Lint Markdown, Vale, Semgrep, Spelling, Wiz scanners, pinned-actions, Build & deploy preview). Run lint locally before push. If Vale/spelling rejects a weird word that's the whole point, add to `.vale/styles/Vocab/` or `.codespellignore` — don't weaken the copy.

## Common mistakes

- **Skeleton PR.** Empty page with "TODO: fill in the joke later". Don't open the PR until the bit lands. Tiny but complete > big but stubbed.
- **Playing it safe with copy.** Corporate-voiced "fun" ruins the joke. Match the existing weird variants for temperature.
- **Forgot the disclaimer.** For legal-doc variants, the "preview only" disclaimer is the bit's safety net. Keep it.
- **Used `npm`.** Repo is `pnpm`. Lockfile will conflict.
- **Used stock Tailwind colors or media queries.** Both forbidden by `AGENTS.md`. Use project tokens and `@container`.
- **Skipped the browser check.** Type-checking proves code compiles, not that the joke works. Open it in Claude in Chrome, click through, take the screenshot.
- **Touched `src/context/App.tsx`, `gatsby/` pipeline, or `src/navs/index.js` without asking.** `AGENTS.md` flags these as ask-first.
- **Gated for review.** PostHog doesn't require approval. Tag for vibe-check and ship.

## Red flags — STOP

| Thought | Reality |
|---------|---------|
| "I should play it safe with the copy" | No. Match `lawyer` / `fairytale` / `tswift` temperature |
| "Should I ask which of the three reply variants to pick?" | No. Pick the funniest implementable one. Ship |
| "I'll mark sections TODO and ship the skeleton" | No. Tiny + complete > skeleton |
| "The legal disclaimer is too jokey to keep" | Keep it. The disclaimer IS the joke's safety |
| "Maybe I should build the *real* feature behind the joke" | No. The joke IS the feature |
| "I'll skip the browser screenshot" | No. UI bits without screenshots get punted |
| "I should request reviews from N people" | No. Tag for vibe-check. Draft → undraft on green |
| "References to killed products are mean" | No. They're encouraged. Be self-aware |

## Real-world reference

PR #16827 (Gen Z DPA variant) is the canonical example: ~one file changed (`src/pages/dpa.tsx`), one new mode entry, one new gated block of rewritten copy, kept the standard disclaimer, draft PR, vibe-check ping to `annamarie-d`, all 19 CI checks green. That's the shape to aim for.
