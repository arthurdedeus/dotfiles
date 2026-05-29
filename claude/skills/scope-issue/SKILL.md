---
name: scope-issue
description: Write a factual, non-prescriptive scoping writeup for a GitHub issue based on prior research. Use when capturing exploration findings into an issue body without proposing solutions or biasing readers toward particular implementations.
argument-hint: <issue-number-or-url>
---

# Scope an issue

Turn prior research/exploration into a GitHub issue body that documents what exists, identifies gaps and constraints, and lists open questions — **without proposing or implying a solution**.

## When to use

- After a substantive research session into a feature, system, or area of code.
- When the user wants to record findings on an issue so a future implementer (or future them) doesn't have to re-do the work.
- When the implementation approach has NOT been decided, or only some decisions have been made and the rest must remain open.

**Do not use** when:
- The user wants a design doc with a recommended approach (use a different format).
- The implementation is already agreed and the issue is about tracking work (use a task list).
- You haven't done the research yet (do that first).

## The non-negotiable rules

These rules are the entire point of this skill. If you violate them, the writeup is bad — you're back to a biased design doc. Re-read this section before drafting AND before submitting.

### 1. Findings, not recommendations
Describe what exists. Describe what doesn't exist (and how you verified). Do not prescribe what should be done. The reader decides what to do; you give them the substrate.

### 2. No claims about typicality without data
Do **not** write "typically", "rarely", "reliably", "usually", "most", "in practice", "in the common case". These are guesses dressed as facts. State the mechanism and let the reader judge frequency.

❌ "Result: the widget reliably matches; non-widget channels rarely do."
✅ "Whether a given record links to a Person depends on whether the captured identifier is also recorded as a `PersonDistinctId.distinct_id` for that team."

### 3. No "unavoidable / must / has to / needs to / should"
These words declare decisions the reader hasn't made. Cut them. If something is genuinely structurally required, state the mechanism that makes it so and let the reader infer.

❌ "A property-based Person lookup is unavoidable as a prerequisite."
✅ "PostHog's identity primitives operate on `distinct_id` strings; they do not resolve a Person by a property such as `Person.properties.email`." (Then put the question in Open Questions.)

### 4. No "presumably / would / could be carried in / one option is"
Speculating about how the future implementation will work IS prescribing it, even softened with hedges. Cut.

❌ "For the Comment-based centralizer, the Person id would presumably be carried in `item_id`..."
✅ Move to Open Questions: "How will the link between a message and a `Person` be stored?"

### 5. Open questions must not encode assumptions
A question like "What does the centralizer's `item_id` reference?" already assumes `item_id` is the link mechanism. Strip the assumption.

❌ "What does the centralizer Comment's `item_id` reference?"
✅ "How will a message be linked to its associated `Person` and `Group`?"

### 6. Open questions are NOT solution menus
"Should we use X, Y, or Z?" both enumerates and biases the option space. Prefer open-ended questions.

❌ "Person resolution: indexed property lookup, alias-via-event, real FK, or a combination?"
✅ "What is the desired behavior for linking an inbound message to a `Person` when the channel-captured identifier is not present as a `PersonDistinctId.distinct_id` for the team?"

(Acceptable variant when listing options is genuinely informative because the reader doesn't know they exist: keep the list short, frame as "for example", and label clearly as illustrative not exhaustive.)

### 7. No phasing, no T1/T2/T3, no "deliver value independently"
Phasing is a recommendation. It does not belong in a factual scope.

### 8. Acknowledge user-stated decisions; don't widen scope
If the user has decided X, write the document as if X. Don't re-litigate X in Open Questions. Re-litigating decisions the user has made is a form of disrespecting their judgment.

### 9. Cite code; cite verification
Every existence claim points to `file:line`. Every non-existence claim says how you verified ("confirmed via grep for `$groups`, `group_key`, `group_type_index`").

### 10. State constraints as facts; put their resolution in Open Questions
Constraints (e.g. "`Comment.item_id` is `varchar(72)`, `posthog_group.group_key` is `varchar(400)`") are facts. State them. Do not write "the design has to widen the column or hash long keys" — that's prescribing.

## Procedure

### Step 1: Confirm scope with the user

Before drafting, use `AskUserQuestion` if any of these are unclear:

- **Issue number/URL** — required input.
- **Where the writeup goes**: update body / new comment / both. Default: update body, preserve any existing trackable content (checklists, milestone refs) at the bottom.
- **Audience depth**: terse for an implementer who knows the code / fresh eyes from another team / TL;DR + full detail.
- **Diagrams (ERD, sequence, etc.)**: inline as DBML/Mermaid in collapsible `<details>`, link out to a hosted location (placeholder `[TODO — to be added]`), or omit.
- **Implementation tasks/checkboxes**: default **no**. Only include if user explicitly asks.

Skip the question if the user has already given the answer in their request.

### Step 2: Read the existing issue body

```bash
gh issue view <number> --repo <owner>/<repo> --json title,body,labels,milestone,comments
```

Note any existing content you must preserve (delivery checklists, milestone tracker text, comments referencing the body).

### Step 3: Draft the body

Recommended structure (adapt as needed — these are common sections, not a rigid template):

1. **TL;DR** (3–6 lines): what the issue is about, what's been decided, what remains open. Mention milestone/RFC. Include ERD link or `[TODO]` placeholder.
2. **Background — relevant existing model(s)/system(s)**: factual description with file paths.
3. **Constraints**: schema sizes, framework limits, existing FK/index structure that the design will operate within. Stated as facts. No "the design has to handle this".
4. **What exists today**: the current state of the code/feature(s) the issue touches. Tables are good for surveying multiple variants (e.g. one row per channel/source/integration).
5. **Per-gap sections** ("Person identification — current behavior", "Group identification — current behavior", etc.): one section per concept the implementation will engage with. Each section is *only* about current behavior, not about what the implementation will do.
6. **The goal** (1 short paragraph): state the goal of the work in factual terms ("surface X on Y") without prescribing how.
7. **Open questions**: grouped by topic. Phrased openly. No solution enumeration unless illustrative.
8. **References**: milestone, RFCs, code entry points cited above. ERD link.
9. **Original delivery scope (preserved)**: any pre-existing checklist from the prior issue body.

### Step 4: Self-review against the rules

Before showing the user, grep your own draft. **All of these are red flags:**

```
unavoidable | must | has to | needs to | should | would be | presumably
rarely | typically | reliably | usually | most | clearly | obviously | simply | just
we recommend | I recommend | T1 | T2 | T3 | phase 1 | phase 2 | first | then
deliver value | could be carried | one option | a natural fit | the obvious | makes sense to
```

For each match: rewrite as a factual statement, move to Open Questions, or delete.

Open questions check:
- Does each question enumerate a solution? Reframe to remove the menu.
- Does each question encode an architectural assumption? Reframe.
- Are user-stated decisions being re-litigated? Remove.

### Step 5: Show the user the draft

Write the body to a temp file (`/tmp/issue-<number>-body.md`) and either:
- Paste it in chat for review, or
- Tell the user the path and ask if they want to review before pushing.

### Step 6: Apply

```bash
gh issue edit <number> --repo <owner>/<repo> --body-file /tmp/issue-<number>-body.md
```

If the user wants a comment instead:

```bash
gh issue comment <number> --repo <owner>/<repo> --body-file /tmp/issue-<number>-body.md
```

### Step 7: Verify

```bash
gh issue view <number> --repo <owner>/<repo> --json body | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['body']), 'chars')"
```

Check the rendered issue on github.com:
- Tables and code blocks render.
- Original trackable content (delivery checklist, etc.) is preserved.
- Body length is sane (issue scopes typically 5,000–12,000 chars; readable in ≈5 min).

## Iteration: handling pushback

If the user pushes back, **do not defend the wording**. The user's editorial judgment about what's prescriptive trumps yours. Common forms of pushback and how to handle them:

| Pushback | What it means | What to do |
|---|---|---|
| "You're assuming things." | A claim about typicality without data. | Restate as a mechanism. |
| "You're making decisions here." | An "unavoidable / must / should". | Move to Open Questions. |
| "You're jumping to implementation." | Speculative future-tense ("would be carried in..."). | Delete or move to Open Questions. |
| "What does this mean?" / "How is this a use case?" | An unexplained scenario or unjustified assumption. | Either explain it crisply with a concrete example, or move to an Open Question that asks the user to validate. |
| "Your Open Questions are based on your assumptions." | Open Questions reference an architecture not agreed. | Re-frame each question to be open over the architecture, not within an assumed one. |
| "Cut implementation details and assumptions." | A general rewrite is needed. | Re-read the rules above. Do a clean pass. Don't try to surgically edit; redraft. |

After applying changes, re-run the Step 4 self-review before pushing again.

## Anti-pattern examples (real, from prior sessions)

❌ "Result: the widget reliably matches; non-widget channels rarely do."
✅ "Whether a record links depends on whether the captured identifier is also recorded as a `PersonDistinctId.distinct_id` for that team."

❌ "A property-based Person lookup is unavoidable as a prerequisite."
✅ "PostHog's identity primitives operate on `distinct_id` strings; they do not resolve a Person by `Person.properties.email`." [→ Question in Open Questions: "What is the desired behavior for linking an inbound message to a Person when the captured identifier is not a known `PersonDistinctId.distinct_id`?"]

❌ "For the Comment-based centralizer, the Person id would presumably be carried in `item_id`..."
✅ [Delete. Move to Open Questions: "How will a message be linked to a `Person`?"]

❌ "Multi-attribution is a real B2B case (consultants, vendors). Design choice for the centralizer."
✅ [Either delete, or — if the scenario is concrete — reframe as a question with an illustrative example labeled as such.]

❌ "A Group-profile communications surface can list `Comment` rows of the centralizer scope linked to that group, using the existing `(team_id, scope, item_id, deleted, -created_at)` index for timeline queries."
✅ "Goal: customer communication history accessible from a group / account profile."

❌ Open question: "Centralizer Comment scope name(s): single scope or multiple scopes (one per audience type)?"
✅ Open question: "How will messages be partitioned within the comment store?"

❌ Open question: "Person resolution at ingestion: indexed `Person.properties.email` lookup vs alias-via-event vs real FK — or some combination?"
✅ Open question: "What is the desired behavior for linking an inbound message to a `Person` when the captured identifier is not a known `PersonDistinctId.distinct_id`?"

## What success looks like

The user reads the writeup and:
1. Learns what exists without being told what to do.
2. Sees the questions that will need answers without seeing your guess at what those answers are.
3. Doesn't have to push back to remove your opinions because there are none.
4. Can hand the issue to any implementer who can then make their own decisions on the merits.

If a reader could plausibly identify "the recommended approach" from your scope, the scope failed.
