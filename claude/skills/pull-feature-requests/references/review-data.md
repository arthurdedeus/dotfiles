# Review data format

The renderer accepts one JSON object.
Use ISO 8601 timestamps for the time window.
Slack message timestamps remain Slack timestamp strings.

```json
{
  "title": "Customer analytics request review",
  "channel": {
    "id": "C0123456789",
    "name": "#project-customer-analytics",
    "workspace_url": "https://posthog.slack.com"
  },
  "window": {
    "start": "2026-08-01T00:00:00-07:00",
    "end": "2026-09-03T23:59:59-07:00",
    "timezone": "US/Pacific"
  },
  "requests": [
    {
      "id": "stable-request-id",
      "area": "Accounts and navigation",
      "name": "Search accounts by user email",
      "description": "Find an account from a user email address.",
      "requesters": ["Example Person"],
      "message_ts": "1788273840.214909",
      "thread_ts": null,
      "completed": false,
      "completion_message_ts": null,
      "completion_thread_ts": null,
      "existing": true,
      "related_name": "Search accounts by user email",
      "related_url": "https://us.posthog.com/project/2/customer_analytics/feature-requests/example",
      "match_confidence": "high"
    }
  ]
}
```

## Field rules

### Top level

- `title`: Page title. Optional.
- `channel.id`: Required Slack channel ID.
- `channel.name`: Display name. Optional.
- `channel.workspace_url`: Slack workspace origin. Required for generated links.
- `window.start`: Inclusive start.
- `window.end`: Inclusive end.
- `window.timezone`: Timezone used to resolve the boundaries.
- `requests`: Request rows.

### Request

- `id`: Stable and unique. Derive it from the source message timestamp and request name.
- `area`: A short grouping such as `Accounts and navigation` or `Workflows`.
- `name`: Concise request name.
- `description`: One direct sentence describing the outcome.
- `requesters`: All people who made the same ask.
- `message_ts`: Timestamp of the exact message containing the ask.
- `thread_ts`: Parent timestamp when the ask is a reply. Use `null` for a top-level ask.
- `completed`: Completion decision based on later Slack evidence.
- `completion_message_ts`: Exact later message confirming completion. Use `null` when absent.
- `completion_thread_ts`: Parent timestamp when the completion evidence is a reply.
- `existing`: Whether a semantic feature request match exists.
- `related_name`: Existing feature request name, or the proposed new name without `[NEW]`.
- `related_url`: Existing PostHog URL. Use an empty string for a new request.
- `match_confidence`: `high`, `moderate`, or `low`.

## Multiple source messages

When duplicates are merged, keep the strongest source in `message_ts` and list every requester.
Explain additional sources in the description only when they add a distinct requirement.
Do not replace a reply permalink with its thread parent.

## Completion links

A completion link supports the `Completed` decision.
Do not use a pull request link as completion evidence unless a later Slack message says the change is live.

## Private data

Keep review JSON and rendered HTML outside public repositories.
Descriptions should summarize the requested outcome without copying customer data, private operational details, or long quotations.
