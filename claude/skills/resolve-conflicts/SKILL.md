---
name: resolve-conflicts
description: Resolve conflicts from a rebase, merge, cherry-pick, or revert without guessing about intent.
argument-hint: "[--abort|--continue]"
---

# Resolve Git conflicts

Use structural tools for mechanical conflicts. Ask when both sides changed behavior with different intent.

## 1. Detect the operation

Run:

```bash
~/.claude/skills/resolve-conflicts/scripts/conflict-status.sh
git diff --name-only --diff-filter=U
```

The status script returns `context`, `progress`, and `branch`.

- `--abort`: abort the active operation and report the resulting branch.
- `--continue`: run the matching continue command without editing.
- No active operation: report that there is nothing to resolve.
- Active operation with conflicts: continue below.

Do not run `--continue` with unresolved files unless the user explicitly requested it.

## 2. Check for already-landed work

When most replayed commits conflict, test whether the base already contains the branch through a squash merge.

Compare branch files and behavior with the target base. Do not trust `git cherry` alone after squash merges.

If most work already landed, stop. Show which commits remain unique and propose:

1. Abort the current operation.
2. Create a fresh branch from the base.
3. Cherry-pick only the unique commits in order.

Get confirmation before switching strategies.

## 3. Categorize files

Run:

```bash
~/.claude/skills/resolve-conflicts/scripts/categorize-conflicts.sh
```

Report lockfiles, generated files, migrations, structurally mergeable files, and other files.

## 4. Resolve mechanical files

### Lockfiles

Resolve dependency manifests first. Choose one lockfile side only as a temporary seed, then regenerate with the repository's package manager.

Prefer lockfile-only commands when available. Review churn before staging. Do not hand-edit lockfile conflict markers.

### Generated files

Resolve their source files, run the repository generator, inspect the output, then stage it.

Never hand-merge generated clients, schemas, or snapshots.

### Migration files

Use `fix-migrations` for numbering and dependency conflicts. If migration operations differ in intent, stop and ask.

### Structurally mergeable files

Run:

```bash
mergiraf solve -c <file>
```

Then inspect remaining markers, duplicate declarations, dead references, and changed behavior. Do not trust an empty displayed base without checking Git's stages:

```bash
git ls-files -u <file>
git show :1:<file>
git show :2:<file>
git show :3:<file>
```

## 5. Resolve semantic conflicts

For each remaining hunk:

1. Read the base, ours, and theirs.
2. Identify each side's intent.
3. Keep both changes when they are independent.
4. Auto-resolve only exact duplicates or a clearly superseded mechanical change.
5. Ask when behavior, data, API, or product intent differs.

Remember that ours and theirs reverse meaning during a rebase. Describe branches or commits, not only those labels.

After editing, search for conflict markers and run focused tests before staging.

## 6. Continue

When all conflicts are resolved:

1. Remove only backup files created by the merge tool during this operation.
2. Regenerate any lockfiles or generated files.
3. Review staged changes.
4. Run the matching command:

| Operation | Command |
| --- | --- |
| Rebase | `git rebase --continue` |
| Merge | `git commit --no-edit` |
| Cherry-pick | `git cherry-pick --continue` |
| Revert | `git revert --continue` |

If another rebase step conflicts, repeat the workflow.

Report auto-resolved files, user-decided files, regenerated artifacts, tests, and remaining risk.
