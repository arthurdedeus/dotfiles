---
name: customer-analytics-weekly-update
description: Use when Arthur wants a weekly shipped-work update for the customer analytics product, summarizing his merged PostHog PRs for the week and drafting it to the customer-analytics Slack channel
argument-hint: [since-date] [until-date] [channel]
---

Build a "what shipped this week" update for the **customer analytics** product from Arthur's merged PostHog PRs (Monday through today), then draft it to Slack for him to send.

**Arguments:**

- `<since-date>` — (optional) `YYYY-MM-DD` start of the window. Defaults to the **Monday of the current week**.
- `<until-date>` — (optional) `YYYY-MM-DD` end of the window. Defaults to **today**.
- `<channel>` — (optional) target Slack channel. Defaults to **#project-customer-analytics** (`C08GGECGJF4`).

The author is always `arthurdedeus` and the repo is always `PostHog/posthog`.

## Steps

### Step 1: Compute the date window

The window MUST default to Monday-of-this-week through today. Do not eyeball it — compute it:

```bash
SINCE="${1:-$(date -v-mon +%Y-%m-%d)}"   # most recent Monday (today if it's Monday)
UNTIL="${2:-$(date +%Y-%m-%d)}"          # today
echo "window: $SINCE .. $UNTIL"
```

`date -v-mon` is BSD/macOS syntax and resolves to the current week's Monday. If a `since-date` argument was passed, use it verbatim instead.

### Step 2: Fetch the week's merged PRs (with bodies)

One command pulls titles **and** bodies, so no follow-up fetches are needed:

```bash
gh search prs \
  --author arthurdedeus \
  --repo PostHog/posthog \
  --merged \
  "merged:$SINCE..$UNTIL" \
  --limit 50 \
  --sort updated \
  --json number,title,url,closedAt,labels,body
```

Notes:
- `gh search prs` does **not** support a `mergedAt` JSON field — use `closedAt` (equal to merge time for merged PRs).
- The `merged:$SINCE..$UNTIL` qualifier filters server-side, so the result is already scoped to the week.

### Step 3: Filter to customer analytics, then curate

**Net (include candidates):** Keep PRs whose title carries a customer-analytics scope prefix — `feat(customer-analytics):`, `fix(customer-analytics):`, `refactor(customer-analytics):`, `chore(customer-analytics):`. This scope is the reliable signal. Also keep any PR clearly about the product (accounts list, account tabs, overview tiles, tags/Segments/Vitally, usage tab) even if the scope prefix is missing.

**Then curate (drop the noise).** Not every scoped PR belongs in a team update. Apply judgment and DROP:

| Drop | Why |
|------|-----|
| Flaky-test / snapshot stabilization (e.g. "stabilize flaky accounts row-expansion snapshots") | Not shippable work the team cares about |
| Pure internal refactors with no user-visible effect (e.g. "collapse id/external_id into the name column tuple") | Invisible to the audience |
| CI / chore / dependency bumps | Noise |
| Anything outside customer analytics (revenue-analytics, hogql infra, stripe-mock, jokerhog, RFCs) | Different product |

When unsure whether something is worth highlighting, lean on the manual gold-standard example below: it kept features and data/consistency wins, and silently dropped test and plumbing PRs.

Print a one-line trace so the user can see what was kept vs dropped:

```
[ca-update] window 2026-06-01..2026-06-05 — 12 scoped PRs, kept 8, dropped 4 (2 test, 2 refactor)
```

### Step 4: Mine PR bodies for detail

The value of the update is in the sub-bullets, which usually aren't in the title. Read each kept PR's `body` and pull out:
- The user-facing capability (what someone can now do)
- Caveats and "for now" notes (e.g. "Persisted in localStorage for now, will build persistent storage later")
- Follow-ups the team should know (e.g. "will run a backfill to add the missing data")
- People to credit — `cc @Name` — when the body or context implies collaboration
- Whether screenshots exist (note `(screenshots)` so Arthur knows to attach them)

Do **not** invent detail. If the body is thin, keep the line to one sentence rather than padding it.

### Step 5: Group thematically and write the update

Group the kept PRs into a few themed sections. The natural groups (from past updates) are **Features** and **Data consistency**, but let the actual work drive the headers — add or rename sections if the week's content calls for it. Within a section, lead each item with the capability name, then indent sub-bullets for detail.

**Tone — match Arthur's voice exactly:**
- Terse, telegraphic, capability-first. Fragments are fine. No marketing prose, no "I'm excited to share".
- Casual and concrete. Reference real surfaces and links (`/organization/billing/usage`), inline `:thread:` pointers, `(more in :thread:)`, `(screenshots)`, `cc @Person`.
- Honest about state: surface the "for now" / "still figuring out" / "will run a backfill" caveats rather than hiding them.
- **No em-dashes.** Arthur never writes `—`. Where you'd reach for one, end the sentence with a period and start a new one, or use a comma. e.g. "Missing links show disabled. You can fill them in inline" — NOT "...show disabled — and you can...".
- **No LLM tells or jargon.** Avoid the giveaways: em-dashes, "you can now", "seamless(ly)", "leverage", "robust", "powerful", "unlock", "delve", and "no more X" clichés. Name UI by what the user sees ("edit button", not "gear button"). Write plainly and concretely like the example below.

## Message formatting (write STANDARD markdown — the Slack MCP converts it)

The update is delivered through the Slack MCP (`slack_send_message_draft`), which accepts **standard markdown** and renders it natively in Slack — including real nested bullet lists. Write plain markdown; do NOT write Slack mrkdwn (`*single asterisks*`, literal `•`/`◦` glyphs) — that was the source of the earlier paste/formatting problems.

- **Bold:** double asterisks `**like this**` (title line and section headers).
- **Italic:** `_like this_`.
- **Bullets:** `- ` at the line start.
- **Nested sub-bullets:** indent **four spaces** then `- `. The MCP renders a true nested list (Slack shows `•`, then `◦` for the child level).
- **Links:** `[label](https://url)` or a bare URL.
- **Mentions:** `cc @Name` passes through as plain text — it does NOT ping. To actually notify someone, resolve their ID with `slack_search_users` and use `<@USER_ID>`. Default to plain text unless Arthur asks for a real ping.
- Keep emoji minimal — only `:thread:` / `:ship:`-style markers if they add meaning. Don't decorate.

## Gold-standard example (Arthur's own update — standard markdown)

Mirror this structure, density, and voice:

```markdown
**Update on what was shipped this week:**

**Features**
- Accounts list supports displaying fields from arbitrary views (more in :thread:)
- Customizable overview tiles in accounts list
    - Persisted in localStorage for now, will build persistent storage along with saving multiple views
    - Useful links section (mentioned above). Will run a backfill to add the missing data
- Account users tab
    - Showing all active users from a given account, hyperlinked to their person profile
- Usage tab (cc @Phil DelGobbo)
    - Reproduction of the graph from /organization/billing/usage, showing per-product usage over time (screenshots)
    - URL-persisted state, so sharing your view's link reproduces it for whoever opens it

**Data consistency**
- Migrated the managed accounts (either by csm or ae) over to the product. Still figuring out the best way to pipe this data in automatically
- Tags column shows Segments from Vitally and is filterable
```

### Step 6: Preview, then draft to Slack

1. Show Arthur the full update **rendered** in chat, preceded by the kept/dropped trace from Step 3 and the list of included PR numbers + URLs, so he can spot-check coverage.
2. Ask him to approve or adjust. **Do not draft or send anything yet.**
3. On approval, create a Slack **draft** in **#project-customer-analytics** (`C08GGECGJF4`) via `slack_send_message_draft`, passing the update as standard markdown. Return the channel link so Arthur does the final send from Slack himself.
   - If a `<channel>` argument was given, resolve its ID with `slack_search_channels` first and draft there instead.
   - If the call returns `draft_already_exists`, tell Arthur to delete the existing draft for that channel in Slack, then retry. Do not work around it.

This skill **only drafts — it never sends.** Arthur presses Send in Slack. Do not claim work that isn't backed by a merged PR in the window.

## After completion

Assess how this skill performed:
- If the user had to correct the filtering, the grouping, the tone, or the Slack formatting, recommend running `/improve-skill` to capture the fix.
- If it ran smoothly, offer it: "Would you like to run `/improve-skill` to refine this skill based on this session?"
