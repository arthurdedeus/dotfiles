# QA proof

Store one folder per criterion under `/tmp/qa-proofs/<AC-id>/` on the box.

Use descriptive names such as `AC3-filtered-list.png` or `AC7-api.md`.

## Visual proof

Capture the state after the action, with the relevant result visible.

For a multi-step flow, prefer a short recording or numbered screenshots. Do not assemble a GIF from arbitrary frames when it hides timing or interaction.

Confirm each requested filename exists. Rename timestamped fallback files before reporting them.

## API proof

Record:

- Method and path.
- Relevant request fields.
- Status.
- Decisive response fields.

Redact tokens, cookies, personal data, and private URLs.

## Database proof

Save the exact query and decisive rows. Use a safe read-only query unless mutation is part of the approved test.

For ORM-only behavior, save the shell snippet and output.

## Transfer

Copy proof files to:

`~/Downloads/qa-proofs/<branch>/`

Use `scp` through the Coder SSH host. Use base64 transfer only when ordinary copy fails.

## Publishing

Show the proof block before changing a pull request or issue unless posting was already approved.

For public-safe images in PostHog, use:

```bash
bin/hogli pr:upload-image <file>
```

Inspect the image first. Never upload customer data, secrets, internal URLs, or private operational details.

Use a compact table:

```markdown
| ID | Criterion | Result | Evidence |
| --- | --- | --- | --- |
| AC1 | <statement> | PASS | <artifact or transcript> |
```

Keep failed-then-fixed history visible. Link or embed the final evidence and name the fixing revision.

If upload is unavailable, state the local path without calling it downloadable.
