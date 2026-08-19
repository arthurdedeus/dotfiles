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

Keep customer analytics work with a user-visible, data-quality, or operational effect worth sharing.

Drop:

- Flake and snapshot stabilization.
- Internal refactors without an observable effect.
- Dependency and CI chores.
- Work for another product.

Show a trace with the window, candidate count, kept count, and drop reasons.

## 4. Remove repeats

Read:

`~/.claude/state/customer-analytics-weekly-update/last-update.md`

Drop capabilities already announced in the prior weekly update. Ad-hoc messages during the week do not count as the weekly record.

If the file is missing, inspect the latest weekly roundup in the channel.

## 5. Add verified detail

Use pull request bodies to extract:

- The capability shipped.
- Material caveats.
- Follow-up work already stated.
- People credited by the source.

Do not invent detail or mention feature-flag gating in the internal roundup.

## 6. Match requesters

Read the channel from seven days before the report window through today.

Tag a requester only when they asked for the exact shipped capability.

- High confidence: include the resolved `<@USER_ID>` mention.
- Lower confidence: list it separately in the preview.
- Never infer a Slack identity from a display name.

## 7. Write the update

Use Arthur's terse, capability-first voice.

- Group work by useful themes.
- Use standard Markdown for the Slack draft tool.
- Use `**bold**`, `-` bullets, and four-space nested bullets.
- Use real `<@USER_ID>` mentions only when a notification is intended.
- State caveats plainly.
- Cut marketing language, LLM stock phrases, and em dashes.

Do not add screenshot placeholders.

## 8. Preview and draft

Show:

1. The kept and dropped trace.
2. Included pull request links.
3. The full rendered update.
4. Included requester tags.
5. Possible low-confidence tags.

Wait for approval. Then create a Slack draft in the resolved channel with the available Slack tool.

Never send it. Arthur sends the draft.

After draft creation, save the exact update text to:

`~/.claude/state/customer-analytics-weekly-update/last-update.md`

## Optional visual proof

If Arthur asks for visuals, use `ui-testing-proof`. Record read-only production walkthroughs and avoid customer mutations.

Cover every highlighted surface or report the missing item. Flag visible customer data before sharing any artifact.
