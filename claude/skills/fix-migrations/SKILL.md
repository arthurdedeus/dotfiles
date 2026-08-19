---
name: fix-migrations
description: Resolve PostHog Django migration numbering conflicts with the repository's migration tools.
argument-hint: "[app-label]"
---

# Fix migration conflicts

Do not use a custom rename script. PostHog uses `django-linear-migrations` and the `rebase_migration` management command.

## Workflow

1. Read the repository's `.agents/skills/django-migrations/SKILL.md` and linked migration guides.
2. Check the current Git operation and unmerged files.
3. Detect the target app from conflicting `*/migrations/` paths.
4. If more than one app is involved, handle each app separately.
5. Fetch the current base branch before choosing new numbers.
6. Run the repository command from its root:

```bash
python manage.py rebase_migration <app-label>
```

Use `flox activate -- bash -c 'python manage.py rebase_migration <app-label>'` when the local environment requires Flox.

7. Review every renamed migration, dependency change, and `max_migration.txt` update.
8. Confirm that only branch-owned, unmerged migrations changed.
9. Stage the affected migration directory when resolving an active Git conflict.
10. Validate:

```bash
python manage.py makemigrations --check
python manage.py showmigrations <app-label>
```

Run migration-specific tests required by the repository instructions.

## Guardrails

- Never rename or delete a migration already merged into the base branch.
- Never rewrite migration operations to solve a numbering conflict.
- Never edit dependencies with a broad text replacement.
- Never assume the app label from its directory name. Check `apps.py` or the migration metadata.
- Stop if two branches changed the same migration's operations or intent. That is not a numbering conflict.
- Preserve unrelated working-tree changes.

Report the old and new names, dependency updates, validation commands, and any unresolved conflict.
