---
name: fix-types
description: Run typechecking and fix type errors with minimal, sensible changes. Use when you need to check for or fix TypeScript type errors after code changes.
args: "[frontend|backend|both] — which type checker to run (default: both)"
---

Run type checkers on the PostHog codebase and fix any errors found.

## Argument parsing

Parse the optional argument from `$ARGUMENTS`:
- `frontend` — run TypeScript typechecking only
- `backend` — run mypy only
- `both` (or no argument) — run both TypeScript and mypy

## Frontend typechecking

Skip this section if the argument is `backend`.

### Step F1: Run typechecking

```bash
flox activate -- bash -c 'export NODE_OPTIONS="--max-old-space-size=16384" && pnpm --filter=@posthog/frontend typescript:check'
```

Capture the full output. If no errors, report success and move on (or stop if only running frontend).

### Step F1.5: Triage

Before attempting fixes, scan the error list for patterns that need external action:

- **Kea typegen staleness** — If most errors are "Property X does not exist on type" where the type originates from a `*LogicType.ts` file, the generated types are stale. Tell the user to run kea typegen first, then re-run the typecheck. Do not attempt to fix these by editing source files.
- **Monorepo module resolution** — If errors are `TS2307: Cannot find module 'X'` in a product workspace (`products/*/frontend/`), check whether the module is a missing `peerDependencies` entry in that product's `package.json`. Compare with a sibling product that successfully imports the same module. This needs a `package.json` change, not a code change.

If either pattern accounts for the majority of errors, stop and report the root cause to the user rather than proceeding to fix individual errors.

### Step F2: Parse errors

Group errors by file. For each error, note:
- File path and line number
- The error code (e.g. TS2322, TS2345)
- The type mismatch: what was expected vs what was provided

### Step F3: Fix errors

Apply fixes with **minimal impact** — prefer the simplest change that resolves the error.

#### Fix priority (try in order)

1. **Narrow a type annotation** — if a variable/constant is typed too broadly for where it's used, narrow it at the declaration site
2. **Add a type assertion at the usage site** — if narrowing the declaration would break other consumers (e.g. contravariance with callbacks), use `as` at the single call site that needs the narrower type
3. **Add a missing import or type argument** — sometimes the fix is just supplying a generic parameter or importing a type
4. **Fix the actual logic** — if the types reveal a genuine bug (wrong property access, missing null check), fix the code

#### Rules

- Never use `any` or `@ts-ignore` to suppress errors
- Never widen a type to fix a narrowing error — go the other direction
- Watch for **contravariance traps**: if a generic interface has callback properties like `(node: Q) => void`, then `Interface<Narrow>` is NOT a subtype of `Interface<Wide>`. In this case, keep the declaration as the wide type and cast at the specific usage site
- When a type assertion (`as`) is needed, cast at the **narrowest scope** possible (the single expression that needs it), not at the declaration
- If a fix would require significant refactoring or architectural changes, stop and ask the user before proceeding
- **JSON fixture imports widen types** — JSON imports infer `null` (not `undefined`) and widen string literals to `string`. In mock/test files, use `as unknown as T` to bridge the gap. This is expected at test boundaries and not a code smell.
- **Monorepo "Cannot find module"** — In pnpm strict mode, each workspace package resolves only its own declared dependencies. A `TS2307` error in `products/*/frontend/` often needs a `peerDependencies` addition to that product's `package.json`, not a code change.

### Step F4: Verify

Re-run the typecheck command from Step F1 to confirm all errors are resolved.
If new errors appear from your fixes, repeat from Step F2.

## Backend typechecking

Skip this section if the argument is `frontend`.

### Step B1: Run mypy

```bash
flox activate -- bash -c 'TEST=1 mypy . | mypy-baseline filter'
```

This uses `mypy-baseline` to filter out known/accepted errors — only new errors are shown. Capture the full output. If no errors, report success and move on (or stop if only running backend).

### Step B1.5: Triage

Before attempting fixes, scan the error list for patterns:

- **Import errors from missing stubs** — If errors are `import-untyped` or `no-any-unimported`, these typically need a stub package (`types-*`) added to `pyproject.toml`, not a code change.
- **Django model field errors** — If errors relate to Django model field types (e.g., `has incompatible type "CharField[...]"`), check if the issue is a missing plugin override in `pyproject.toml` `[tool.mypy]` before editing source.

If a pattern accounts for the majority of errors, report the root cause to the user rather than fixing individual errors.

### Step B2: Parse errors

Group errors by file. For each error, note:
- File path and line number
- The error code (e.g. `[assignment]`, `[arg-type]`, `[return-value]`)
- The type mismatch: what was expected vs what was provided

### Step B3: Fix errors

Apply fixes with **minimal impact** — prefer the simplest change that resolves the error.

#### Fix priority (try in order)

1. **Add or narrow a type annotation** — if a variable/parameter is untyped or too broad, annotate it at the declaration
2. **Add a `None` check or assertion** — if mypy reports a possible-`None` access, add an appropriate guard
3. **Add a missing import or generic parameter** — sometimes the fix is importing a type or supplying a `TypeVar`
4. **Fix the actual logic** — if the types reveal a genuine bug, fix the code
5. **Use `cast()`** — as a last resort for complex generic situations, use `typing.cast()` at the narrowest scope

#### Rules

- Never use `type: ignore` to suppress errors unless absolutely unavoidable (e.g., known mypy bug)
- If `type: ignore` is truly needed, always include the error code: `# type: ignore[specific-code]`
- Never widen a return type to fix a caller error — fix the caller
- For Django QuerySet/Manager methods, check the django-stubs documentation before "fixing" what may be a stubs limitation
- If a fix would require significant refactoring, stop and ask the user before proceeding

### Step B4: Verify

Re-run the mypy command from Step B1 to confirm all errors are resolved.
If new errors appear from your fixes, repeat from Step B2.

## After completion

Assess how this skill performed:
- If the user had to provide significant guidance, corrections, or workarounds to get the task done, recommend running `/improve-skill` to capture those learnings. Explain briefly what could be improved.
- If the skill ran smoothly with minimal intervention, offer it as an option: "Would you like to run `/improve-skill` to refine this skill based on this session?"
