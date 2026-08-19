---
name: implement-issue
description: Implement one scoped GitHub issue as a complete, tested, deployable outcome without widening its scope.
argument-hint: "<issue-number-or-url>"
---

# Implement an issue

Deliver one issue outcome. Preserve existing behavior and earlier slices. Do not pull follow-up work into the current change.

If the issue lacks verified scope, use `scope-issue` before coding.

## Inputs

Find:

- Current issue and parent issue, when one exists.
- User story or operator outcome.
- Acceptance criteria and test setup.
- Dependencies and blockers.
- Target branch and prior related changes.
- Repository instructions and relevant skills.
- Rollout, rollback, and production checks.

Ask only when missing information changes product behavior or safety.

## Workflow

### 1. State the implementation contract

Write:

```markdown
Issue: #...
Parent: #... or None
Outcome: ...
Starting state: ...
In scope: ...
Out of scope: ...
Blocked by: ...
Evidence required: ...
```

If the issue contains unrelated outcomes, stop and propose a split.

### 2. Verify readiness

For every blocker, verify that the required commit, schema, API, migration, flag state, or external contract exists on the target branch.

An open pull request is not a completed blocker unless the team approved a stack.

For a stack, state the base, merge order, and restack plan.

Stop when a required blocker is absent.

### 3. Reconcile the issue with reality

Read affected code, tests, data shape, recent changes, and repository instructions.

Classify discrepancies:

- **Blocking:** invalidates the issue or contract. Stop and update the scope.
- **In scope:** must change for this issue to work safely.
- **Follow-up:** record without widening the issue.

Do not silently change an approved decision.

### 4. Map criteria to evidence

Create:

| Acceptance criterion | Code area | Automated test | UI or operator check | Production check |
| --- | --- | --- | --- | --- |

User-visible behavior needs interface evidence. Access, integrity, and business rules need automated tests.

Add missing test setup before implementation.

### 5. Design the smallest complete path

Trace only the path needed for the outcome:

1. Entry point or trigger.
2. User or operator action.
3. Client, API, or job boundary.
4. Domain rule.
5. Persistence or external effect.
6. Observable result.
7. Refresh, retry, or return path.

Do not add fields, abstractions, endpoints, or controls for later issues.

### 6. Plan compatibility

Before editing, answer:

- Can old code read the new schema?
- Can new code read old data?
- Can old clients ignore new fields?
- Can a flag disable the change without deleting data?
- Can retries or repeated events duplicate effects?
- Can rollback leave valid data?

Use expand, migrate, and contract phases for destructive changes. Put contract cleanup in a later issue.

### 7. Establish a baseline

Run the smallest relevant tests before editing. Include nearby regressions and repository checks for migrations or generated files.

Record existing failures. Do not attribute them to the new change.

Run the existing UI or operator journey first when practical.

### 8. Implement the walking skeleton

Build the simplest successful path through every required layer.

For user-facing work:

1. Add the minimal domain and persistence change.
2. Add the narrow service or API operation.
3. Add the interface entry and action.
4. Show the saved result.
5. Verify refresh or return behavior.

Keep unfinished behavior behind the planned flag.

### 9. Add required safeguards

Add only safeguards required by the issue:

- Tenant and object access.
- Input validation.
- Loading, empty, error, and permission states.
- Duplicate prevention and idempotency.
- Accessible controls.
- Actionable errors.

Enforce permissions on the server. Preserve user input after failed saves.

### 10. Add useful observability

Instrument the outcome and important failures. Use stable identifiers without customer data, tokens, or sensitive content.

Follow repository skills for analytics, flags, logs, and tracing when present.

### 11. Run automated tests

Run focused tests first, then required broader checks.

Cover relevant cases:

- Business rules and state transitions.
- Tenant isolation and permissions.
- API validation and compatibility.
- UI interaction and restored state.
- Duplicate and retry behavior.
- Migration safety.
- Existing behavior near the change.

Regenerate checked-in artifacts through repository commands. Review generated diffs.

Report exact commands and results.

### 12. Run the UI or operator journey

Follow the issue's persona, setup, steps, and expected results.

Use `ui-testing-proof` when the user requests autonomous browser testing or visual proof.

Verify:

- Main outcome.
- Refresh or retry behavior.
- Direct and back navigation when relevant.
- Restricted persona.
- One documented failure path.
- Cleanup.

Do not claim a journey passed when it did not run.

### 13. Review the complete diff

Remove files that do not support the issue.

Check:

- No follow-up behavior entered.
- No unused abstraction or hidden dead code remains.
- Migrations and APIs remain compatible.
- Server permissions exist.
- Logs and analytics contain no sensitive data.
- Existing behavior remains intact.

Create follow-up issues for valid discoveries outside scope.

### 14. Prepare the pull request

Follow repository publishing, stacking, signing, and template instructions.

The pull request states:

- Delivered outcome and linked issue.
- Important design choice.
- Existing behavior preserved.
- UI or operator evidence.
- Automated checks.
- Migration and compatibility notes.
- Rollout, rollback, and production verification.

Do not mark the issue complete until its full outcome works.

### 15. Verify production

After deployment, use safe internal or test records.

Verify reachability, the main outcome, persistence, permissions, existing behavior, health signals, and migration reconciliation.

If verification fails, disable the change when possible, preserve data, record the failed step, and follow the rollback plan.

### 16. Close the loop

After production verification:

- Record evidence on the issue.
- Close the issue.
- Update the parent when one exists.
- Mark newly unblocked work ready.
- Create follow-ups for deferred discoveries.

## Stop conditions

Stop and update the scope when evidence changes the outcome, field ownership, state model, tenant routing, migration identity, security boundary, or dependency order.

Fix an existing defect only when it blocks this issue or makes the change unsafe. Explain it in the pull request.

## Definition of done

The issue is done when:

- Its outcome works end to end.
- The user or operator can reach, complete, and verify it.
- Permissions and errors are clear.
- Existing behavior still works.
- Changes are backward compatible.
- Retries do not duplicate effects.
- Required automated tests pass.
- The UI or operator journey ran or is explicitly marked untested.
- Rollout, rollback, and production verification are assigned.

End with the issue, delivered outcome, pull request, tests, UI evidence, compatibility notes, production plan, newly unblocked work, and remaining blockers.
