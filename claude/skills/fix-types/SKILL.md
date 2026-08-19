---
name: fix-types
description: Run PostHog frontend and backend type checks and fix new errors with minimal, behavior-preserving changes.
argument-hint: "[frontend|backend|both]"
---

# Fix type errors

Default to `both`. Use `frontend` or `backend` when requested.

## Frontend

Run:

```bash
flox activate -- bash -c 'export NODE_OPTIONS="--max-old-space-size=16384" && pnpm --filter=@posthog/frontend typescript:check'
```

If errors involve generated `*LogicType.ts` files, run typegen before editing source:

```bash
pnpm --filter=@posthog/frontend typegen:write
```

Then rerun the type check and group remaining errors by file and code.

Fix the cause at the narrowest useful scope:

1. Correct wrong logic or missing null handling.
2. Add or narrow an annotation.
3. Add a missing import, dependency, or generic argument.
4. Use a local assertion only when a verified runtime invariant exceeds the type system.

Do not use `any`, `@ts-ignore`, or a broad cast to hide an error. Do not edit generated files by hand.

For `TS2307` inside a workspace package, check that package's declared dependencies before changing code.

## Backend

Run:

```bash
flox activate -- bash -c 'TEST=1 mypy . | mypy-baseline filter'
```

Group new errors by file and code. Prefer:

1. Correct logic or add a missing `None` guard.
2. Add or narrow an annotation.
3. Add a missing import or generic argument.
4. Use `typing.cast()` at the smallest scope when the runtime type is verified.

Use `# type: ignore[code]` only for a confirmed checker or stubs limitation. Explain why in the code when the reason is not obvious.

## Verification

Rerun each selected checker after editing. Review the diff for runtime behavior changes and accidental generated-file churn.

Report:

- Commands run.
- Root causes fixed.
- Remaining errors.
- Checks that could not run.
