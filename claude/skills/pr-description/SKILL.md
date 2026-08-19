---
name: pr-description
description: Write a pull request body from the current branch using the repository's live template and authoring rules.
argument-hint: "[base-branch]"
---

# Pull request description

## Gather evidence

1. Detect the repository's default base unless the user supplied one.
2. Read the branch name, commits, status, diff, and diff stat against that base.
3. Read `.github/pull_request_template.md` from the current revision.
4. Load the repository's PR-writing skill when present.
5. Find linked issues from verified branch or commit references. Do not infer issue numbers.
6. Record only tests and browser checks that ran in this session.

## Write the body

Use the live template as the source of truth. Preserve its required comments, checkboxes, and agent instructions.

- Make the body stand alone for a reviewer who opens no files.
- Lead with the user-visible problem and result.
- Size the explanation to the change.
- Explain important design choices, not a file-by-file diff.
- Name test evidence and untested areas accurately.
- Keep public text free of customer data and private operational details.
- Use the current agent identity. Do not hardcode an agent name.
- Preserve the template's autonomy and attribution rules.
- Follow current title rules if the user also requests a title.

For PostHog, read `.agents/skills/writing-pr-descriptions/SKILL.md` when available. It overrides personal style details.

## Linked issues

Add a closing reference only when the branch, commits, or user supplies a verified issue:

```markdown
Closes https://github.com/<owner>/<repo>/issues/<number>
```

Do not add a placeholder beyond the template's own comment.

## Output

Return only the completed template inside one `markdown` code fence. Do not claim tests, screenshots, or manual verification that did not occur.
