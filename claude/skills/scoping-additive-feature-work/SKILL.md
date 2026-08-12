---
name: scoping-additive-feature-work
description: Scope a large feature, RFC, or GitHub issue into a parent issue and ordered sub-issues that deliver user value through additive vertical slices. Use when asked to plan a feature, define an MVP or minimal valuable feature, break work into GitHub issues, map blockers and dependencies, audit an existing issue before implementation, or add user-story-based UI test instructions to a delivery plan.
---
# Scoping additive feature work
## Purpose
Turn an idea, RFC, or oversized issue into an evidence-based delivery plan.

The plan must:

- Deliver a minimal working feature as soon as possible.
- Describe the ideal end state before selecting the first release.
- Work backward from that end state to the smallest valuable version.
- Move forward through additive vertical slices.
- Connect every slice to a user story.
- Show implementation order and blockers.
- Include UI test setup, steps, and expected results.

This skill produces a plan. It does not implement code or create GitHub issues without explicit approval.
## Core tenets
### 1. Deliver value before groundwork
The first implementation step must produce the smallest usable end-to-end behavior.

Do not default to a sequence such as:

1. Add models.
2. Add services.
3. Add an API.
4. Add the interface.

That sequence delivers no user value until the last step.

Prefer one vertical slice:

1. Let a user create and view the simplest valid record through the interface.

The slice can contain a model, service, endpoint, and interface. Keep each layer as small as the user story permits.

A slice can use more than one PR when review safety requires it. Keep those PRs under one user-story issue. Land them close together behind a feature flag.
### 2. Use a parent issue and sub-issues for large work
Use one parent issue when the feature needs multiple independently testable user outcomes.

Use GitHub sub-issues for the work units. Do not rely only on a markdown checklist. Use GitHub's native issue dependencies for real execution constraints: **blocked by** identifies prerequisites, and **blocking** identifies downstream work. Sub-issue hierarchy expresses decomposition; issue dependencies express delivery order. Use both when both relationships exist.

The hierarchy must show:

- The ideal end state.
- The minimal valuable release.
- Ordered increments.
- Dependencies and blockers.
- Release gates.

Keep a small feature in one issue when splitting it would only create coordination overhead.
### 3. Make order and blockers explicit
Every sub-issue must state:

- What blocks it.
- What it blocks.
- Whether it can run in parallel.
- What user-visible state exists when it closes.

Do not hide dependencies in prose. Include a dependency table or graph during planning. After the user approves GitHub mutation and the issues exist, also create the native GitHub dependency relationships. The GitHub **Relationships** data is the source of truth; the table and graph explain it for readers.
### 4. Connect each step to a parent user story
Each sub-issue must quote or reference the parent user story that it implements.

Use this form:

> As a `<persona>`, I can `<action>`, so that `<outcome>`.

The issue must explain what part of that story becomes possible after the issue closes.
### 5. Make increments additive
Each slice should preserve prior behavior and add one coherent capability.

Prefer:

- New nullable fields before required fields.
- New tables before destructive table changes.
- New routes before removing old routes.
- Feature flags before irreversible cutovers.
- Read-compatible deployments before backfills.
- Idempotent imports before final migrations.
- Reconciliation before source deletion.

Avoid temporary architectures that the next slice immediately replaces.
### 6. Scope from the end to the beginning
First describe the ideal user experience without limiting it to the current architecture.

Then remove capabilities one at a time. Stop at the smallest version that still solves a real user problem. That version is the minimal valuable feature.

Finally, reverse the sequence into implementation order. The result must start with the minimal valuable feature and grow toward the ideal state.
## Definitions
### Ideal end state
The complete user experience that the team wants when the feature is mature.

It includes the main workflow, permissions, integrations, migration, reporting, failure behavior, and operational support.
### Minimal valuable feature
The smallest end-to-end version that a real user can use to complete one meaningful story.

It is not a backend foundation, a mock interface, or a disconnected API.
### Vertical slice
A thin implementation through every necessary layer. It ends in observable user behavior.
### Additive increment
A slice that keeps the previous slice working while adding a new capability.
## Workflow
### Step 0: Confirm the task and output
Ask what the user wants if the request is ambiguous:

- A discovery audit.
- A delivery plan.
- GitHub issue bodies.
- Actual issue creation.
- Implementation.

Do not mutate GitHub during discovery. Get explicit approval before creating or editing issues.
### Step 1: Audit the current state
Read the parent issue, comments, linked RFCs, and related code.

Check source claims instead of repeating them. When data is available, verify:

- Totals and arithmetic.
- Missing keys versus empty values.
- Distinct values and malformed values.
- Link and identifier formats.
- Duplicate and many-to-many relationships.
- Existing account or tenant matches.
- Mutable source behavior.

When code is available, verify:

- Model constraints.
- Team or tenant scoping.
- Access controls.
- Existing routes and interfaces.
- Webhook routing.
- Migration state.
- Whether reusable primitives fit the user story.

Record the code revision and data snapshot time. Distinguish:

- **Fact:** Verified in data or code.
- **Decision:** Product behavior the team approved.
- **Assumption:** A temporary belief that needs confirmation.
- **Open question:** A missing decision that blocks a slice.

Do not treat an existing primitive as the correct design only because it exists.
### Step 2: State the ideal end state
Write the end state as user outcomes, not components.

Cover:

- Who uses the feature.
- What starts the workflow.
- What the user creates, reads, updates, or removes.
- How related entities connect.
- How users find and organize records.
- What integrations automate.
- What historical data moves.
- What reports users need.
- What viewers and editors can do.
- What happens when dependencies fail.
- How operators detect and recover from failure.

Write one parent user story for the main outcome. Add supporting stories for materially different personas or workflows.
### Step 3: Work backward to the minimal valuable feature
Start with the ideal end state. Remove one capability at a time.

For each removal, ask:

1. Can the user still complete a meaningful story?
2. Can the team safely release this state?
3. Will this design support the removed capability later?
4. Does this state avoid throwaway work?

Stop when another removal would make the feature useless or misleading.

Common features to defer when the first story does not require them:

- Advanced filtering.
- External integrations.
- Bulk migration.
- Voting or scoring.
- Reporting dashboards.
- Notifications.
- Automated deduplication.
- Custom fields.

Do not defer access control, tenant isolation, basic error handling, or data integrity.
### Step 4: Build the forward sequence as vertical slices
Reverse the backward path. The first slice is the minimal valuable feature.

For each slice, write:

- The parent user story.
- The new user-visible capability.
- The smallest required data and API changes.
- The interface change.
- The compatibility strategy.
- The test journey.
- The dependency on prior slices.

Use this test:

> If this issue closes and all later issues disappear, can a user complete the stated story?

If the answer is no, the issue is probably horizontal groundwork. Merge it into the first slice that exposes the behavior.

Allow a technical-only issue only when at least one condition is true:

- It removes a material delivery risk before a vertical slice.
- It performs a production operation that cannot live in a product PR.
- It adds shared infrastructure with more than one immediate consumer.
- It is an independently reversible migration or security change.

A technical-only issue must name the user-facing slice it enables. It must not create a long chain of groundwork issues.
### Step 5: Check that every slice compounds
For each adjacent pair, answer:

- What remains unchanged?
- What new capability appears?
- Does the new schema remain compatible with the old application version?
- Can the feature flag disable the new capability without data loss?
- Does the next slice extend the same user workflow?
- Can the team stop after this slice and still support users?

Rework any step that replaces the previous interface, discards imported data, or changes core semantics without a transition.
### Step 6: Map dependencies and parallel work
Create an ordered table:

| Order | Issue | Parent user story | User value when complete | Blocked by | Blocks | Can run in parallel |
|---|---|---|---|---|---|---|

Then create a dependency graph when there are more than four issues.

Dependencies must follow real constraints. Do not serialize work only by team boundaries.

After the first vertical slice, common parallel tracks are:

- A second product workflow.
- Migration preparation.
- An integration.
- Analytics exposure.

Each parallel track must start from a released or stable contract.

#### Materialize dependencies in GitHub
During discovery, produce a proposed edge list without mutating GitHub:

```text
<blocked issue> is blocked by <blocking issue>
```

After the user explicitly approves issue creation or editing:

1. Create all new issues and retain their issue numbers or URLs.
2. Apply dependencies in a second pass so every endpoint exists.
3. Add each relationship from the blocked issue:

```bash
gh issue edit <blocked-issue> --add-blocked-by <blocking-issue>
```

Use `--add-blocking` only when editing from the blocker's perspective. Both flags accept issue numbers or URLs, including comma-separated values:

```bash
gh issue edit 123 --add-blocked-by 120,121 --add-blocking 130
```

When creating an issue whose related issues already exist, use the native creation flags:

```bash
gh issue create --title "..." --body-file issue.md --blocked-by 120,121 --blocking 130
```

Verify every relationship after writing it:

```bash
gh issue view <issue> --json blockedBy,blocking
```

If the installed GitHub CLI lacks dependency flags, use the REST issue-dependencies endpoints through `gh api`. The REST POST body requires the blocking issue's database `id`, not its issue number:

```bash
blocker_id="$(gh api repos/<owner>/<repo>/issues/<blocking-number> --jq '.id')"
gh api -X POST \
  repos/<owner>/<repo>/issues/<blocked-number>/dependencies/blocked_by \
  -F "issue_id=$blocker_id"
```

Creating dependencies requires sufficient issue permissions. Do not silently fall back to prose-only dependencies. Report unsupported permissions or tooling, and leave the exact proposed edges for a human to apply.

Do not create a native dependency merely because one issue is listed earlier. Add it only when the blocked issue cannot safely or meaningfully complete before the blocker. Check for cycles before writing relationships.
### Step 7: Write the parent issue
Use this structure:

```markdown
# <Feature name>
## Goal
The user problem and desired outcome.
## Ideal end state
The complete user experience.
## Parent user stories
- As a ..., I can ..., so that ...
## Minimal valuable feature
The first releasable end-to-end behavior.
## Scope
Included behavior.
## Non-goals
Explicitly deferred behavior.
## Verified current state
Facts from code and data, with revision and snapshot date.
## Decisions
Approved product and technical decisions.
## Open questions
Only unresolved questions. Mark blockers.
## Delivery sequence
| Order | Sub-issue | User story | User value | Blocked by |
|---|---|---|---|---|
## Dependency graph
A Mermaid graph or a concise text graph. When issues have been created, this graph must mirror their native GitHub blocked-by relationships.
## Native GitHub dependency status
State whether relationships were created and verified, only proposed pending approval, or could not be applied because of permissions or tooling.
## Release gates
Migration, access, testing, observability, and rollback requirements.
```

The parent issue owns the outcome. Do not copy every implementation detail into it.
### Step 8: Write each sub-issue
Use this structure:

```markdown
# <Area>: <User-visible outcome>
## Parent
- Parent issue: #...
- Delivery step: <number>
## Parent user story
> As a ..., I can ..., so that ...
## Outcome of this step
What becomes possible when this issue closes.
## Starting state
What the previous step already provides.
## Scope
- The smallest work required for this outcome.
## Out of scope
- Later additive capabilities.
## Additive design
How this step preserves previous behavior and supports later steps.
## Acceptance criteria
- [ ] Observable user behavior.
- [ ] Access and tenant isolation.
- [ ] Error and empty states.
- [ ] Compatibility or migration behavior.
## Test setup
Personas, permissions, feature flags, test records, accounts, and integrations.
## UI testing
### User journey: <name>
1. Open ...
2. Select ...
3. Enter ...
4. Save ...

Expected result:

- The user can ...
- The interface shows ...
- Refreshing preserves ...
## Automated tests
Unit, service, API, integration, and browser tests required by this slice.
## Dependencies
- Blocked by: #... or None
- Blocks: #... or None
- Can run in parallel with: #... or None
- Native GitHub relationships: Applied and verified | Proposed pending approval | Not applicable
## Rollout and production verification
Feature flag, migration, observability, verification, and rollback steps.
```

Give each issue one directly responsible owner when the team is ready to assign work.
### Step 9: Write UI tests as user journeys
Every user-facing slice needs manual interface instructions.

The instructions must include:

- **Persona:** Viewer, editor, account owner, administrator, or another real role.
- **Starting state:** Existing records, permissions, feature flags, and integrations.
- **Steps:** Actions through the interface. Do not replace them with API or database calls.
- **Expected result:** Visible results after each meaningful action.
- **Persistence check:** Refresh or reopen the page.
- **Navigation check:** Direct URL, back navigation, and preserved filters when applicable.
- **Permission check:** What an unauthorized user sees and cannot do.
- **Failure check:** What happens when a save or integration fails.
- **Cleanup:** How to identify and remove test records.

Write tests around stories, not components. “The modal renders” is not a user journey. “An editor creates a request and finds it after refresh” is a user journey.

For a technical-only issue with no independent interface:

- State that no direct UI journey exists.
- Link to the next user-facing issue.
- Name the journey that will exercise this work.
- Keep automated verification in the technical issue.

Do not invent a fake interface test for infrastructure.
### Step 10: Cover migration and integrations from the user perspective
A migration plan must include:

- Canonical source selection.
- Stable identity and idempotency.
- Field normalization.
- Duplicate behavior.
- Unresolved relation handling.
- Dry-run counts.
- Final delta or write freeze.
- Reconciliation.
- Rollback.
- A UI journey that samples migrated records.

An integration plan must include:

- Link validation.
- Tenant routing.
- Event ordering and deduplication.
- Manual override behavior.
- Failure visibility.
- Reconciliation for missed events.
- A UI journey that changes the external resource and observes the product result.
### Step 11: Apply the quality gate
Do not present the plan as ready until all answers are yes.
#### Value
- Does the first implementation issue deliver a working user story?
- Can the team release it without later issues?
- Does each later issue add visible or operational value?
#### Sequence
- Is the order explicit?
- Are blockers explicit?
- Can independent work run in parallel?
- Is there a dependency cycle?
- When issues were created or edited, do native GitHub blocked-by relationships match the dependency table and graph?
#### Additivity
- Does each slice preserve prior behavior?
- Are schema and API changes backward compatible?
- Can migrations retry safely?
- Can rollout stop after any slice?
#### Product clarity
- Does every issue reference a parent user story?
- Are field ownership and status transitions decided?
- Are non-goals explicit?
- Are unresolved blockers separated from implementation details?
#### Testing
- Does every user-facing issue include test setup and UI steps?
- Do expected results describe visible behavior?
- Are permissions, persistence, errors, and navigation covered?
- Do technical-only issues name the downstream UI journey?
#### Operations
- Are access control and tenant isolation included from the first slice?
- Are migration reconciliation and rollback defined?
- Are integration failures visible and recoverable?
- Is production verification assigned?

If any answer is no, revise the slices before writing or creating issues.
## Slicing heuristics
### Good slice boundaries
Prefer slices such as:

- Create and view the simplest record.
- Edit, archive, and find records.
- Connect a record to an existing account.
- Import existing records into the working interface.
- Connect an external system and synchronize one state.
- Add reports that drill into the working list.

Each slice completes a user or operator story.
### Bad slice boundaries
Avoid separate issues such as:

- Create database tables.
- Add serializers.
- Add endpoints.
- Build components.
- Wire components to endpoints.

These are implementation tasks inside a vertical-slice issue unless they meet the technical-only exception.
### Keep the first release honest
Do not call a technical foundation an MVP.

The minimal valuable feature must let a real user:

1. Reach the feature.
2. Complete one meaningful action.
3. See the saved result.
4. Return later and find it.
5. Understand errors and permissions.
## Example: reverse-scoping a tracker
Ideal end state:

- Users create requests.
- Users connect accounts and evidence.
- Existing records migrate.
- GitHub updates status.
- Product managers filter and report on requests.

Work backward:

1. Remove reporting. Users can still manage requests.
2. Remove GitHub sync. Users can still update status manually.
3. Remove migration. Users can still create new requests.
4. Remove account evidence. Users can still record requests, but the account-level goal is lost.
5. Keep create, list, detail, and one account link. This is the minimal valuable feature.

Forward slices:

1. Create, list, and inspect an account-linked request end to end.
2. Add multiple account evidence, editing, archiving, search, and filters.
3. Import historical records into the same interface.
4. Add normalized GitHub links and status synchronization.
5. Add reports that drill into the request list.

This sequence delivers value in the first slice. Each later slice extends the same model and workflow.
## Output style
Use concise, direct language.

- One meaning per term.
- One user outcome per issue.
- Short sentences.
- Tables for order and blockers.
- Lists for test steps.
- Exact counts and dates when evidence supports them.
- No speculative implementation detail presented as a decision.

End with:

- The minimal valuable feature.
- The ordered issue list.
- The dependency graph.
- The first issue that can start now.
- The decisions that still block implementation.
## Related skills
- `writing-simplified-technical-english`: Use to keep issue bodies, test instructions, and reports unambiguous.
- `working-with-skills`: Use when publishing or updating this skill in the PostHog skills store.
