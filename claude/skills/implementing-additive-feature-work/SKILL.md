---
name: implementing-additive-feature-work
description: Implement a parent issue or sub-issue produced by the scoping-additive-feature-work process. Use when coding an ordered feature slice, continuing a multi-issue feature plan, delivering a minimal end-to-end user story, checking blockers, preserving prior slices, running user-story-based UI tests, preparing a focused pull request, or verifying an additive release in production.
---
# Implementing additive feature work
## Purpose
Deliver one scoped user story as a working, additive vertical slice.

The implementation must:

- Start only when its real blockers are complete.
- Preserve the behavior from prior slices.
- Produce observable user value in the current slice.
- Implement only the layers needed by the user story.
- Follow the parent issue's decisions and non-goals.
- Run automated tests and the documented UI journey.
- Remain safe to deploy, disable, retry, and roll back.
- Leave the next planned slice easier to add.

This skill consumes plans created with `scoping-additive-feature-work`. Use that skill first when no approved parent issue and ordered slice exist.
## Core tenets
### 1. Implement the user story, not a technical layer
The unit of delivery is the sub-issue's user outcome.

Do not stop after adding a model, service, endpoint, or component when the issue promises an end-to-end action. Add the smallest necessary part of each layer until the user can complete the story.

Do not add speculative fields, abstractions, endpoints, or interface controls for later slices.
### 2. Preserve every completed slice
Treat the previous slice as a supported product.

The new slice must keep its:

- Routes and links.
- API contracts.
- Stored data.
- Permissions.
- User journeys.
- Automated tests.
- Rollback path.

Run the prior slice's UI journey before and after the change.
### 3. Follow the dependency order
Do not start a blocked issue because its code looks independent.

A blocker is complete only when the required contract exists on the target branch. An open pull request is not a completed blocker unless the team explicitly coordinates a stack.

When stacking is approved, state the base branch, dependency, merge order, and rebase plan in every pull request.
### 4. Keep the change additive
Prefer expansion over replacement:

- Add nullable schema before enforcing required values.
- Add optional API fields before changing existing fields.
- Add new behavior behind a stable interface.
- Keep old readers compatible during migrations.
- Make imports and event handling idempotent.
- Keep rollback from deleting new data.
- Defer destructive cleanup to a later issue.
### 5. Test through the interface as a user
Automated tests are necessary but do not replace the documented UI journey.

Use the issue's persona, setup, steps, and expected results. Perform the journey with browser tools when available. If browser tools are unavailable, say so. Do not claim that manual UI testing passed.
### 6. Keep the pull request aligned with one slice
A pull request should make the current user story work. It should not quietly implement later sub-issues.

When safe review requires several pull requests, keep them under one user-story issue. Land them close together behind a feature flag. Do not mark the issue complete until the full story works.
## Inputs
Before coding, obtain:

- The parent issue.
- The current sub-issue.
- The parent user story referenced by the sub-issue.
- The ordered delivery plan and dependency graph.
- The current target branch.
- Prior pull requests or commits for completed slices.
- Repository instructions and local context files.
- Test setup and UI test instructions.
- Rollout and production-verification requirements.

If one of these is missing, recover it from GitHub or the repository. Ask the user only when the missing information changes product behavior.
## Workflow
### Step 0: Identify the exact slice
Write a short implementation contract before changing code:

```markdown
Current issue: #...
Parent issue: #...
Parent user story: As a ..., I can ..., so that ...
Starting state: What completed slices already provide.
Outcome: What becomes possible after this issue.
Out of scope: Capabilities assigned to later issues.
Blocked by: #... or None
Blocks: #... or None
```

If the issue describes multiple unrelated user outcomes, stop and propose a split. Do not make an oversized pull request to match an oversized issue.
### Step 1: Verify readiness
Check each blocker against the target branch.

For every blocker, verify:

- The pull request merged or the required commit exists.
- The documented schema or API contract matches the code.
- Its migrations exist in the target history.
- Its feature flag state is known.
- Its user journey still works when practical.

Also check whether another pull request already implements the current issue. Continue that work instead of opening a duplicate.

Stop when a required blocker is missing. Report the blocker and the first safe action.
### Step 2: Reconcile the issue with reality
Read the affected code, tests, recent changes, and repository instructions.

Compare the issue with the actual system:

- Are file paths and symbols current?
- Did a prior slice change the contract?
- Does the data have the expected shape?
- Do existing primitives still fit the story?
- Are permissions and tenant boundaries understood?
- Is the documented UI route available?

Classify discrepancies:

- **Blocking:** The story or data contract is wrong. Stop and update the plan.
- **In-scope:** The discrepancy must be fixed for this story to work.
- **Follow-up:** Record it without widening the current slice.

Do not silently reinterpret an approved product decision.
### Step 3: Map acceptance criteria to evidence
Create a verification table:

| Acceptance criterion | Implementation area | Automated test | UI step | Production check |
|---|---|---|---|---|

Every criterion needs at least one form of evidence. User-visible behavior needs a UI step. Access, data integrity, and business rules need automated tests.

Add missing test setup before implementation. Use stable test names and data that a reviewer can reproduce.
### Step 4: Design the thinnest vertical path
Trace the user's action through the system:

1. Entry point or route.
2. Interface action.
3. Client state and request.
4. API boundary.
5. Service or domain rule.
6. Persistence or external effect.
7. Response and visible result.
8. Refresh or return path.

Implement only what this path requires.

For the first slice, prefer one simple happy path with honest empty, permission, and failure states. Do not build advanced configuration before the basic action works.

For later slices, extend the same path. Do not create a parallel workflow unless the parent plan requires it.
### Step 5: Plan additive compatibility
Before editing, answer:

- Can the old application read the new schema?
- Can the new application read old rows?
- Can old clients ignore new API fields?
- Can the feature flag turn off the new interface without deleting data?
- Can a retry create duplicates?
- Can events arrive twice or out of order?
- Can rollback leave the database in a valid state?

Use an expand, migrate, contract sequence when a destructive change is eventually necessary:

1. **Expand:** Add backward-compatible schema and behavior.
2. **Migrate:** Backfill or dual-write with reconciliation.
3. **Contract:** Remove obsolete behavior in a later issue after verification.

Do not combine contract cleanup with the slice that first introduces the replacement.
### Step 6: Establish a baseline
Run the smallest relevant tests before changing code.

Include:

- The nearest unit or service tests.
- The affected API or frontend tests.
- The prior slice's regression tests.
- Repository-specific validation for migrations or generated files.

Record existing failures. Do not attribute them to the new change.

When practical, perform the prior UI journey once before implementation. Save the starting behavior.
### Step 7: Implement the walking skeleton
Build the happy path through every required layer.

Recommended order inside the working branch:

1. Add the minimal domain rule and persistence.
2. Add the narrow service and API operation.
3. Add the interface entry point and action.
4. Display the saved result.
5. Confirm refresh or return behavior.

This is an implementation order inside one slice. It is not a reason to open several horizontal issues.

Keep the feature hidden behind the planned flag until the end-to-end path works.
### Step 8: Add required safeguards
After the happy path works, implement only the safeguards required by the issue:

- Tenant and object access checks.
- Input validation.
- Empty and loading states.
- Save and external-service errors.
- Duplicate prevention.
- Retry and idempotency behavior.
- Audit or status history.
- Accessible controls and keyboard behavior.
- Useful user-facing error messages.

Do not use error handling to hide corrupted state. Surface actionable failures and preserve user input.
### Step 9: Add observability with the feature
Instrument the user story, not implementation details.

Consider:

- A product event for the completed user action.
- Error tracking for failed saves or external calls.
- Structured logs with stable identifiers.
- Metrics for migration, webhook, queue, or sync health.
- Feature-flag exposure when rollout analysis needs it.

Do not add sensitive quotes, tokens, URLs, or customer data to logs or analytics.

Use the relevant instrumentation skill when the repository needs a new PostHog integration, product event, feature flag, error tracking, logs, or LLM tracing.
### Step 10: Run automated verification
Run focused tests first. Then widen to the repository's required checks.

At minimum, cover:

- Business rules and status transitions.
- Team or tenant isolation.
- Viewer and editor permissions.
- API validation and compatibility.
- Frontend interaction and state restoration.
- Duplicate and retry behavior.
- Migration safety when schema changes.
- Regression behavior from prior slices.

Regenerate checked-in clients, schemas, snapshots, or migrations when repository rules require it. Review generated diffs before including them.

Do not report “tests pass” without naming the commands and results.
### Step 11: Perform the UI journey
Use the issue's **Test setup** and **UI testing** sections.

When the user asks to run the UI tests autonomously or provide proof that the implemented journey works or fails, load the `ui-testing-proof` skill and follow it. Use Browser Use for inspection and assertions, Pagecast for recording the actual run, explicit PASS/FAIL/BLOCKED criteria, and screenshots, GIFs, videos, or artifacts as evidence. The issue's documented setup, steps, and expected results remain the source of truth.

For each journey:

1. Prepare the named persona and permissions.
2. Enable the documented feature flag.
3. Create the stated test records and integrations.
4. Follow the interface steps exactly.
5. Compare each result with the expected result.
6. Refresh or reopen the page.
7. Test direct navigation and back navigation when relevant.
8. Repeat the permission case with the restricted persona.
9. Exercise one documented failure path.
10. Clean up test records.

Record:

- Environment and project.
- Browser or browser tool.
- Actual result for each step.
- Screenshots or recordings when the interface changed materially.
- Any step that was not run.

A screenshot proves appearance. It does not prove the full journey. Record the actions and persistence check too.
### Step 12: Review the diff against the slice
Read the complete diff before publishing.

Ask:

- Does every changed file support the current story?
- Did later-slice work enter the pull request?
- Is dead or hidden code left without an immediate consumer?
- Are new abstractions justified by more than one current use?
- Are migrations additive and safe?
- Are permissions enforced on the server?
- Are error messages concise and actionable?
- Are analytics and logs free of sensitive data?
- Did prior behavior remain intact?

Remove unrelated cleanup. Create follow-up issues for valid discoveries outside the current story.
### Step 13: Prepare the pull request
Use one branch for the current slice unless the user approved a stack.

Follow repository publishing instructions. When signed commits are required, use the approved signed-commit tool. Do not substitute an unsigned local commit.

Use this pull request body:

```markdown
## Summary
What user-visible behavior this adds.
## Parent user story
> As a ..., I can ..., so that ...
## Additive change
What prior behavior remains and what this slice adds.
## UI testing
- Test setup
- Steps performed
- Actual results
- Screenshots or recording
- Steps not performed
## Automated tests
- `<command>` — passed
## Migration and compatibility
Schema, backfill, API, flag, and rollback notes.
## Rollout and production verification
How to enable, observe, verify, and disable the slice.

Closes #...
Parent: #...
Blocked by: #... or None
Blocks: #... or None
```

Open a draft pull request when the change still needs review or external checks. Link the parent and sub-issue.
### Step 14: Verify the deployed slice
After deployment, perform the production verification from the issue.

Verify as a user where safe:

- The feature is reachable for the intended audience.
- The main action succeeds.
- The result persists.
- Prior slice behavior still works.
- Permissions remain correct.
- Error rates, logs, and metrics are healthy.
- Migration or synchronization counts reconcile.

Use test or internal records. Do not modify customer data for verification.

If verification fails:

1. Disable the feature when the flag supports it.
2. Preserve data.
3. Record the exact failed step.
4. Fix forward or follow the rollback plan.
5. Repeat the full journey.
### Step 15: Close the loop in GitHub
When the slice passes production verification:

- Record the verification result on the sub-issue.
- Close the sub-issue.
- Update the parent delivery table.
- Mark newly unblocked issues ready.
- Confirm that the next slice's starting state matches reality.
- Add follow-up issues for deferred discoveries.

Do not mark later user stories complete because their groundwork landed in this pull request.
## Handling scope changes
### A blocking discovery
Stop implementation when new evidence invalidates:

- The parent user story.
- Field ownership.
- A status transition.
- Tenant routing.
- Migration identity.
- Security boundaries.
- The additive sequence.

Update the parent decision and affected sub-issues before continuing.
### An in-scope defect
Fix a defect in prior behavior when it prevents the current story or makes the additive change unsafe. Explain the fix in the pull request.
### A useful follow-up
Create or propose a follow-up when the discovery does not block the story. Do not widen the current issue.
### A later-slice capability
Do not implement it early only because the current code makes it convenient. Preserve the extension point without shipping unused behavior.
## Migration rules
When the slice changes data:

- Use a stable source identity.
- Make writes idempotent.
- Preserve unresolved relationships.
- Distinguish missing values from empty values.
- Normalize malformed values explicitly.
- Keep dry-run and real-run logic identical where possible.
- Emit reconciliation counts.
- Retry safely after partial failure.
- Keep a rollback or disable path.
- Test representative source fixtures.
- Inspect migrated records through the interface.

Do not delete the source or obsolete columns in the same slice that first consumes migrated data.
## Integration rules
When the slice adds an external integration:

- Validate links or identifiers before saving.
- Route events to every correct tenant.
- Authenticate at the shared boundary.
- Reject stale events.
- Deduplicate repeated events.
- Define manual override behavior.
- Expose sync state and actionable errors.
- Add reconciliation for missed events.
- Test the external action and visible product result.

Do not couple a new integration to unrelated product settings only because an existing handler does so.
## UI implementation rules
- Preserve direct links and browser navigation.
- Preserve search, filters, and ordering in the URL when applicable.
- Show loading, empty, no-results, permission, and error states.
- Keep unsaved input after a failed save.
- Prevent duplicate submissions.
- Make destructive actions explicit and reversible when planned.
- Use existing design-system components and patterns.
- Keep server enforcement behind hidden or disabled controls.
- Test the restricted persona, not only the editor.
- Verify persistence after refresh.
## Definition of done
A slice is done only when all statements are true.
### User value
- The parent user story works end to end for this slice.
- The user can reach, complete, and revisit the action.
- The interface communicates errors and permissions.
### Scope
- The change implements the current sub-issue.
- Later capabilities remain out of scope.
- New discoveries have follow-up issues when needed.
### Additivity
- Prior journeys still work.
- Schema and API changes are backward compatible.
- The feature can be disabled without data loss.
- Retries and repeated events do not duplicate effects.
### Verification
- Focused and required automated tests pass.
- The documented UI journey ran, or the report states why it could not run.
- Migration, permissions, failure, and regression cases have evidence.
### Delivery
- The pull request links the parent and sub-issue.
- The pull request states the user story and UI results.
- Rollout and rollback steps are clear.
- Production verification has an owner.

Do not close the issue before the complete user-visible outcome exists.
## Common anti-patterns
### Groundwork-only completion
A model or endpoint lands, and the issue closes before users can act.

**Fix:** Keep the issue open or merge the work into the vertical slice.
### Scope hitchhiking
A later feature enters the pull request because nearby code was already open.

**Fix:** Preserve an extension point and move the behavior to its planned issue.
### Hidden breaking change
A new client and server deploy together, but old workers or clients cannot read the new data.

**Fix:** Use additive contracts and an expand, migrate, contract sequence.
### Automated-test substitution
The agent runs component tests and reports the UI journey as complete.

**Fix:** Perform the documented interface steps or state that manual testing was not run.
### Screenshot substitution
The pull request contains a screenshot but no interaction or persistence evidence.

**Fix:** Record the full journey and refresh check.
### Premature cleanup
The slice removes the old field, route, or source before the replacement is verified.

**Fix:** Move cleanup to a later contract issue.
### Silent plan divergence
The code reveals that the issue is wrong, so the implementation chooses new behavior without approval.

**Fix:** Stop, record the evidence, and update the product decision.
### Dependency theater
Issues are serialized by backend, API, and frontend labels rather than real constraints.

**Fix:** Deliver one vertical slice and parallelize only after a stable contract exists.
## Completion report
End an implementation run with:

- Current issue and parent issue.
- User story delivered.
- Pull request and signed commit.
- Automated test commands and results.
- UI journey result and evidence.
- Additive compatibility notes.
- Production-verification plan or result.
- Newly unblocked issue.
- Follow-up issues or remaining blockers.

Use concise, direct language. Do not claim tests, UI checks, deployment, or production verification that did not occur.
## Related skills
- `scoping-additive-feature-work`: Use when the parent plan or vertical slices need creation or revision.
- `ui-testing-proof`: Use to execute documented UI journeys autonomously and provide validated visual PASS/FAIL proof.
- `writing-simplified-technical-english`: Use for issue updates, pull request text, test instructions, and user-facing errors.
- `instrument-feature-flags`: Use when the slice needs a controlled rollout.
- `instrument-product-analytics`: Use when the slice adds a meaningful user action.
- `instrument-error-tracking`: Use when the slice adds a new failure path.
- `instrument-logs`: Use when operators need structured runtime evidence.
