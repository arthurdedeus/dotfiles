# QA worker prompts

Use workers only when the harness supports isolated agents. Keep browser actions serialized in one browser session.

Every worker returns structured evidence, not a narrative.

## Browser criterion

Provide:

- Devbox app URL.
- Required test identity.
- Criterion ID and statement.
- Exact steps.
- Expected state after each meaningful action.
- Required screenshot or recording names.

Require this response:

```text
RESULT: PASS | FAIL | BLOCKED
EVIDENCE: <observed state versus expected state>
PROOF_FILES: <paths or none>
NOTES: <errors, uncertainty, or flakiness>
```

The browser worker must verify the signed-in identity when the criterion depends on it. It must not improvise another workflow when a required control is missing.

## Log watcher

Provide the box label, relevant services, endpoint names, and watch duration.

Require timestamps and exact error lines. Return `clean` when no relevant anomaly appears.

## API checker

Provide the criterion, request, authentication method, and expected status or payload.

Require a redacted Markdown transcript under the criterion proof directory.

## Database checker

Provide one read-only query and expected rows or values.

Require the query and output in a Markdown proof file.

Use a stronger reasoning model only when interpreting results. A known single query does not need one.

## Research worker

Ask for routes, components, endpoints, models, tests, and repository instructions touched by the branch.

Require `file:line` evidence and open questions. Do not ask the worker to design product behavior.
