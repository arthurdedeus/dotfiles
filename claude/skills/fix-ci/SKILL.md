---
name: fix-ci
description: Diagnose and fix CI failures on the current PR. Use when PR checks are failing and you need to investigate why, identify root causes, and apply fixes. Covers visual regression tests, backend/frontend tests, lint, type errors, migration checks, and more.
---

# Fix CI

Diagnose and fix failing CI checks on the current branch's PR.

## Step 1: Triage

```bash
gh pr checks
```

Categorize each failure:

| Category | Typical job names | Action |
|---|---|---|
| Visual regression | `Visual regression tests - chromium/webkit` | Delegate to `ci-doctor` agent |
| Backend tests | `Django tests`, `Product tests`, `Dagster tests` | Delegate to `ci-doctor` agent |
| Frontend tests | `Jest test (EE/FOSS)` | Delegate to `ci-doctor` agent |
| Node.js tests | `Node.js Tests` | Delegate to `ci-doctor` agent |
| Type errors | `Frontend typechecking` | Use `fix-types` skill |
| Lint | `Python code quality`, `Frontend formatting` | Run linters locally |
| Migrations | `Validate migrations and OpenAPI types` | Use `fix-migrations` skill |
| Semgrep | `semgrep-*` | Read violation, fix code |

## Step 2: Investigate

Extract the **run ID** from the check URL (the number after `/runs/`), then:

```bash
# Failed job logs only (fastest, most focused)
gh run view <run-id> --log-failed 2>&1 | grep -E "(FAIL|PASS|Error|error)" | head -30

# Specific error signatures
gh run view <run-id> --log-failed 2>&1 | grep -E "(Timeout|snapshot|assert|Error:|FAIL)" | head -30
```

For visual regression, compare browsers to isolate Chromium-specific issues:
```bash
gh run view <run-id> --log 2>&1 | grep -E "(PASS|FAIL).*<StoryName>" | head -10
```

## Step 3: Diagnose

Launch the `ci-doctor` agent with the failure category and the relevant log output.
It returns a structured diagnosis with root cause and recommended fix.

## Step 4: Fix

Apply fixes in dependency order when multiple checks fail:
1. Migrations
2. Type errors
3. Lint
4. Tests
5. Visual regression

## Rules

- Always start with `gh pr checks` for the current state
- Use `--log-failed` first (faster). Only `--log` when you need cross-browser or passing-job data
- For flaky tests (pass on retry), note them but don't fix unless they fail 3+ times consistently
- Never run `typecheck` or `typegen` — the user handles those
- Never commit or push — the user handles that
- For lint: `ruff check . --fix && ruff format .` (Python), `pnpm --filter=@posthog/frontend format` (frontend)

## After completion

Assess how this skill performed:
- If the user had to provide significant guidance, corrections, or workarounds to get the task done, recommend running `/improve-skill` to capture those learnings. Explain briefly what could be improved.
- If the skill ran smoothly with minimal intervention, offer it as an option: "Would you like to run `/improve-skill` to refine this skill based on this session?"
