---
name: scope-issue
description: Research and scope a GitHub issue, ticket, epic, or feature into a factual issue body or an ordered additive delivery plan.
argument-hint: "<issue-number-or-url-or-ask>"
---

# Scope an issue

Turn an issue or loose request into verified, reviewable GitHub scope.

Do not change GitHub until the user approves the drafts and issue structure.

## Choose the output

Confirm which output the user wants:

- **Factual scope:** document current behavior, gaps, constraints, decisions, and open questions in one issue.
- **Issue breakdown:** inventory a parent ticket and draft missing sub-issues.
- **Delivery plan:** define the ideal state, minimal valuable feature, and ordered additive slices.
- **GitHub update:** apply approved drafts, hierarchy, labels, projects, and dependencies.

Use factual scope when implementation choices remain open. Use delivery planning when the user asks for an implementation sequence.

## Shared evidence rules

1. Verify source claims before repeating them.
2. Cite code claims with `file:line` or another direct source.
3. State how an absence claim was checked.
4. Separate facts, decisions, proposals, assumptions, and open questions.
5. Do not claim frequency or typicality without data.
6. Treat user-approved decisions as settled.
7. Do not invent issue links, owners, labels, or dependencies.
8. Preserve useful tracking content already in an issue.

For a factual scope, do not recommend an implementation or encode one in an open question.

For a delivery plan, label recommendations as proposed scope. Explain the evidence and tradeoff behind each proposal.

## Workflow

### 1. Confirm the task

Resolve:

- Issue, parent ticket, or loose request.
- Repository.
- Audience and required depth.
- Factual scope or delivery planning.
- Draft only or approved GitHub mutation.

Ask only for missing information that changes the output.

### 2. Inventory existing work

Read the parent issue and current sub-issues:

```bash
gh issue view <issue> --repo <owner>/<repo> --json title,body,state,labels,comments,subIssues
```

If the CLI lacks `subIssues`, use the REST sub-issues endpoint through `gh api`.

Classify each requested item as:

- Existing issue.
- Already shipped.
- Needs new scope.
- Unclear.

Do not draft duplicates.

### 3. Research the current state

Read linked RFCs, code, tests, data, migrations, routes, permissions, and recent changes.

Verify relevant details, including:

- Counts, formats, duplicates, and missing values.
- Model constraints and tenant boundaries.
- Existing APIs and interfaces.
- Access controls.
- Migration and integration behavior.
- Whether the request's premise matches the mechanism.

Record the code revision and data snapshot time when they affect the findings.

Classify findings:

- **Fact:** verified in code or data.
- **Decision:** approved behavior.
- **Proposal:** recommended delivery choice.
- **Assumption:** belief needing confirmation.
- **Open question:** missing decision.

If evidence changes the original problem, explain the reframing before drafting.

## Factual scope mode

Use this mode for one issue when the implementation approach is undecided.

### Rules

- Describe what exists and what does not.
- State constraints as mechanisms, not commands.
- Keep recommendations and phasing out of the body.
- Phrase open questions without solution menus or hidden assumptions.
- Attribute literal requirements to their source.

### Suggested structure

```markdown
## Summary
## Background
## Verified current behavior
## Constraints
## Goal
## Decisions
## Open questions
## References
## Original tracking content
```

Adapt headings to the issue. Omit empty sections.

## Delivery planning mode

Use this mode for an epic or feature needing several independently testable outcomes.

### 1. Describe the ideal end state

Write user outcomes, not components. Cover the main workflow, permissions, integrations, migration, reporting, failures, and operations.

Write the parent story:

> As a `<persona>`, I can `<action>`, so that `<outcome>`.

Add another story only for a materially different persona or workflow.

### 2. Find the minimal valuable feature

Remove capabilities from the ideal state one at a time.

After each removal, ask:

1. Can a real user still complete a meaningful story?
2. Can the team release and support this state safely?
3. Does it preserve a path to the ideal state?
4. Does it avoid throwaway work?

Do not defer access control, tenant isolation, basic errors, or data integrity.

### 3. Build additive vertical slices

Reverse the reduction path. The first slice is the minimal valuable feature.

Each slice states:

- Parent user story.
- User-visible outcome.
- Starting state.
- Smallest required data, API, and UI changes.
- Compatibility strategy.
- Test journey.
- Blockers and downstream work.

Use this test:

> If every later issue disappears, can users still complete this slice's story?

If not, merge the technical work into the user-facing slice.

Allow a technical-only issue only for a material risk, independent operation, shared infrastructure, migration, or security boundary. Name the user-facing slice it enables.

### 4. Check additivity

For adjacent slices, verify:

- Earlier routes, data, permissions, and journeys remain valid.
- Old code can read the new schema during rollout.
- Flags can disable new behavior without deleting data.
- Retries cannot duplicate effects.
- The team can stop after either slice and support users.

### 5. Map dependencies

Create:

| Order | Issue | User story | Value when complete | Blocked by | Blocks | Parallel work |
| --- | --- | --- | --- | --- | --- | --- |

Add a graph when the plan has more than four issues.

A dependency represents a real execution constraint. Order alone is not a dependency.

## Sub-issue content

Each proposed sub-issue includes:

- Parent and delivery order.
- Referenced parent story.
- Outcome and starting state.
- Scope and out of scope.
- Additive design.
- Observable acceptance criteria.
- Test setup and UI journey.
- Automated tests.
- Dependencies and parallel work.
- Rollout, rollback, and production verification.

## UI journeys

Every user-facing issue needs:

- Persona and permissions.
- Starting records, flags, and integrations.
- Exact interface steps.
- Visible expected results.
- Persistence and navigation checks.
- Restricted-user and failure checks.
- Cleanup.

A technical-only issue names the later journey that exercises it. Do not invent a fake UI test.

## Migration and integration checks

For migrations, define identity, normalization, duplicate handling, dry-run counts, reconciliation, rollback, and interface sampling.

For integrations, define validation, tenant routing, ordering, deduplication, override behavior, failure visibility, and reconciliation.

## Review before GitHub changes

Show one review package containing:

1. Item disposition table.
2. Full issue drafts.
3. Scope questions grouped by draft.
4. Proposed issue order and dependency graph.
5. Operational defaults for parent, labels, and project.
6. A clear statement that GitHub is unchanged.

Wait for approval. Keep scope questions separate from GitHub administration.

## Apply approved scope

After approval, confirm parent, labels, project, and dependencies.

Use current native GitHub CLI flags:

```bash
gh issue create --repo <owner>/<repo> --title "<title>" --body-file <draft> --parent <parent>
gh issue edit <issue> --repo <owner>/<repo> --add-blocked-by <blockers> --add-blocking <downstream>
```

Verify created issues with:

```bash
gh issue view <issue> --repo <owner>/<repo> --json parent,subIssues,blockedBy,blocking
```

Report every original item's final disposition, including existing work, shipped work, skipped items, and new issues.

## Quality gate

Before calling scope ready, verify:

- Every claim is sourced or marked unknown.
- The request matches the verified mechanism.
- No duplicate issue is proposed.
- Factual scopes contain no hidden recommendation.
- Delivery plans start with a releasable user story.
- Every later slice adds distinct value.
- Dependencies have no cycle.
- Permissions and tenant isolation start in the first slice.
- UI journeys test visible behavior, persistence, errors, and access.
- Rollout, rollback, and production verification have owners.

Use `orwell-writing` for issue prose. Use `implement-issue` after the scope is approved.
