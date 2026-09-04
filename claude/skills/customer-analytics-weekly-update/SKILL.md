---
name: customer-analytics-weekly-update
description: Draft Arthur's weekly customer analytics shipped-work update from merged PostHog pull requests.
argument-hint: "[since-date] [until-date] [channel]"
---

# Customer analytics weekly update

Draft only. Never send the Slack message.

Defaults:

- Window: Monday of the current week through today.
- Repository: `PostHog/posthog`.
- Author: `arthurdedeus`.
- Channel: `#project-customer-analytics` (`C08GGECGJF4`).

## 1. Compute the window

Use supplied dates verbatim. Otherwise use a cross-platform date calculation:

```bash
python3 - <<'PY'
from datetime import date, timedelta
end = date.today()
start = end - timedelta(days=end.weekday())
print(start, end)
PY
```

## 2. Fetch merged pull requests

```bash
gh search prs \
  --author arthurdedeus \
  --repo PostHog/posthog \
  --merged \
  "merged:<since>..<until>" \
  --limit 50 \
  --json number,title,url,closedAt,labels,body
```

## 3. Curate

The audience is CSMs, TAMs, sales, and support. Not engineers.

Keep work a GTM reader can notice: something they can now see, click, or rely on.

Drop:

- Flake and snapshot stabilization.
- Internal refactors without an observable effect.
- Dependency and CI chores.
- Work for another product.
- Reliability, telemetry, and instrumentation work with no visible surface. Fold it into the visible bullet it supports, or cut it.
- Sync and pipeline repair work, even when a named person was blocked by the failure. A status
  field that now reports the truth is not a capability.
- Fixes to internal tooling and settings cleanup that no reader in the channel uses.

Landing four themes a reader acts on beats landing nine they scroll past.

Show a trace with the window, candidate count, kept count, and drop reasons.

## 4. Remove repeats

Read:

`~/.claude/state/customer-analytics-weekly-update/last-update.md`

Drop capabilities already announced in the prior weekly update. Ad-hoc messages during the week do not count as the weekly record.

If the file is missing, inspect the latest weekly roundup in the channel.

## 5. Add verified detail

Use pull request bodies to extract:

- The capability shipped.
- Caveats that change what a reader should do.
- Follow-up work already stated.
- People credited by the source.

Do not invent detail or mention feature-flag gating in the internal roundup.

Leave out mechanism. A PR body explains how a thing works because a reviewer needs that. This
reader does not. Cut region splits, transports, schedule times, ID matching, access checks,
debouncing, retries, phase counts, and workflow topology.

Keep a caveat only when a reader would do something different knowing it. "Gong summaries are
not included" is a limit on what they will find and can go. "The global schedule starts paused"
is an operator detail and cannot.

## 6. Match requesters

Read the channel from seven days before the report window through today.

Tag everyone with a stake in the shipped capability, not only the person who phrased it best.

Tag when someone:

- Asked for the capability.
- Asked for an adjacent slice of it.
- Reported the bug or gap it closes.
- Sent a customer or a thread that motivated it.

Under-tagging is the common failure. A theme with one tag usually means the channel was not
read closely enough. Several tags on one theme is normal and correct.

- Resolve every mention to a real `<@USER_ID>`.
- Never infer a Slack identity from a display name.
- List genuinely uncertain matches separately in the preview instead of dropping them silently.
- Ask Arthur for tags on any theme the channel gave no requester for. He tracks stakeholders from
  DMs and other channels that this read cannot see.

## 7. Write the update

Use Arthur's terse, capability-first voice.

Structure: one message. A short intro line, then the themes separated by blank lines. Do not
split the update across several messages, and do not put `---` separators between themes.

Per theme:

- Bold theme name, then the requester tags on the same line.
- One line naming the capability.
- At most three nested bullets under it. Two levels of nesting, never three.
- Cut a bullet a GTM reader cannot act on.
- Prefix a theme with `[WIP]` when the surface shipped unfinished.
- For a permission or guardrail change, name the control the reader now sees, not the
  consequence. "A delete confirmation modal was added" beats "deleting removes stored values
  permanently".
- Say `hard-delete` when the record is destroyed, so it reads apart from ending or unassigning.

Add a PS with the next action when a feature needs the reader to set something up.

- Use standard Markdown for the Slack draft tool.
- Use `**bold**`, `-` bullets, and four-space nested bullets.
- Use real `<@USER_ID>` mentions only when a notification is intended.
- Cut marketing language, LLM stock phrases, and em dashes.

Name the capability, do not sell it. "Decide which accounts stay tracked" beats "Which accounts
stay tracked is now decided in Customer analytics, not Vitally". Drop comparisons to the tool
being replaced, and drop claims about how much better a surface now is.

Do not add screenshot placeholders.

## 8. Preview and draft

Show:

1. The kept and dropped trace.
2. Included pull request links.
3. The full rendered update.
4. Included requester tags.
5. Possible low-confidence tags.

Wait for approval. Then create a Slack draft in the resolved channel with the available Slack tool.

Slack allows one attached draft per channel, and the update is one message, so the draft is the
message. The Slack tool cannot delete or edit a draft, so redrafting leaves the earlier draft in
place. Confirm the text before drafting, and say which draft ID is current.

Never send it. Arthur sends the draft.

After draft creation, save the exact update text to:

`~/.claude/state/customer-analytics-weekly-update/last-update.md`

## Optional visual proof

If Arthur asks for visuals, use `ui-testing-proof`. Record read-only production walkthroughs and avoid customer mutations.

Cover every highlighted surface or report the missing item. Flag visible customer data before sharing any artifact.
