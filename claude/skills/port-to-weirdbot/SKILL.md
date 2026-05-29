---
name: port-to-weirdbot
description: Use when porting a standalone Claude skill prompt (a SKILL.md, a pasted prompt block, or a buy-domain-style spec) into the weirdbot repo at ~/Code/weird/weirdbot — i.e. wiring it up as a real `@weirdbot` skill. This is a Claude Code skill for the human developers of weirdbot, run from a local terminal. It is NOT a `@weirdbot` Slack skill, must never be invoked from Slack, and must never be added to weirdbot's `SkillId` union, `skills[]` registry, or categorizer. Triggers include "port this prompt to weirdbot", "let's add this as a weirdbot skill", "convert this SKILL.md into a weirdbot skill", "wire up <foo>-skill in weirdbot", or any request to take an upstream prompt and ship it inside ~/Code/weird/weirdbot. Skip if the work is purely editing an existing live weirdbot skill or fixing a bug in one — read AGENTS.md and work directly in that case.
---

# port-to-weirdbot

**Audience:** the human developers of weirdbot, working locally in Claude Code. This skill orchestrates a codebase edit; it does not become part of weirdbot's runtime surface and is never exposed to Slack. Do not register this skill's name anywhere inside `~/Code/weird/weirdbot` (no entry in `src/skills/`, `modal_app/skills/`, `src/skills/types.ts`, `src/categorize.ts`, or anywhere else). It lives only at `~/.claude/skills/port-to-weirdbot/SKILL.md` on the developer's machine.

## What this is

weirdbot is a Cloudflare Worker (`~/Code/weird/weirdbot`) that classifies `@weirdbot` Slack mentions and dispatches to a per-skill handler. v1 ships with most skills as **stubs** (`makeStubbed(...)` from `src/skills/stubbed.ts`). Porting a standalone prompt means converting one of those stubs (or adding a brand new skill) into a working **Pattern B** skill: prompt-as-markdown file in two places, a tiny TS dispatcher on the Worker, a Python handler in `modal_app/`, a vitest, and a few registry edits.

The canonical pairs to copy from are:

- **Deterministic Python** (parse brief once with Haiku tool-use, then run a fixed flow): `src/skills/merch.ts` + `modal_app/skills/merch.py`
- **Agentic loop with terminator tools** (open-ended research, multi-step decisions, multi-turn): `src/skills/merch-procurement.ts` + `modal_app/skills/merch_procurement.py`

Read both before you write anything. AGENTS.md at the repo root is the framework contract — re-read it every time, it's where the runtime constraints live.

## Pre-flight

1. **Cd to the repo.** `~/Code/weird/weirdbot`. If you're in a worktree, that's fine — the worktree is at `/Users/arthur/.posthog-code/worktrees/<id>/weirdbot` and shares the same `git worktree list`.
2. **Read AGENTS.md end-to-end.** It's the framework contract.
3. **Re-read the canonical pair** that matches your shape (deterministic vs agentic — see below).
4. **Confirm `pnpm typecheck && pnpm test` is green** before you touch anything, so a regression is yours and not pre-existing.

## Pick a pattern: deterministic vs agentic

| Your prompt looks like… | Use pattern | Canonical pair |
|---|---|---|
| Parse → fixed API call(s) → maybe confirm → done. The "decision tree" is small and you can write it as if-statements. | **Deterministic.** Parse brief with Haiku tool-use, run a Python flow. | `merch.py` |
| Open-ended research, multi-step decisions, the model needs to call tools iteratively (web search, web fetch, custom tools), or there's real multi-turn dialogue beyond a single yes/no. | **Agentic loop.** System-prompt the model with the SKILL.md, give it `ask_user` / `request_approval` / `produce_artifact` terminator tools. | `merch_procurement.py` |
| Long-running compute (image / video / audio gen, sandbox code execution) | **Custom Pattern B.** Look at `image_gen.py` / `video_gen.py`. | `image_gen.py` |

When in doubt: deterministic. The agentic loop is correct when the prompt genuinely needs the model to think between steps; otherwise it's overkill, slower, and harder to debug.

A multi-turn confirmation flow (yes/no on a price) does **not** require the agentic loop — handle it deterministically by checking `ctx.is_followup` and scanning `ctx.thread_history` for the pending state, as in `buy_domain.py`.

## Workflow

### 1. Land the prompt as the source-of-truth markdown

Drop the prompt into **both** of these locations, verbatim:

- `src/skills/prompts/<id>.md` — git of record + bundleable for the Worker
- `modal_app/prompts/<id>.md` — what the Python handler actually reads at runtime (Modal image bundles the `prompts/` dir into `/root/prompts/`)

**Adapt the prompt to the Modal-worker runtime:**
- **Strip hardcoded credentials.** Replace with env-var references — the real values live in Modal secrets (`weirdbot-secrets`), not in the prompt file.
- **Add a `## Runtime context` preamble** explaining that the skill runs inside a Modal worker triggered by `@weirdbot` Slack activity, that credentials come from Modal secrets, and (for multi-turn) that the user's reply re-enters with the full thread transcript.
- **Don't paraphrase the substance.** Keep the original prompt's instructions, tables, examples, and error-handling matrix intact.

### 2. Replace the stub with a Pattern B dispatcher (TS side)

`src/skills/<id>.ts` — roughly 25 lines. Copy the shape of `src/skills/merch-procurement.ts`. Description and examples matter — they go into the categorizer's system prompt. Examples should be **distinctively** different from neighboring skills.

### 3. Write the Python handler

`modal_app/skills/<id>.py` — exposes `async def handle(payload: dict) -> None`.

Common building blocks:

| Need | Where it lives |
|---|---|
| `post_reply`, `post_blocks`, `upload_image`, `md_to_mrkdwn`, `build_mailto` | `modal_app/slack.py` |
| Loading the prompt at runtime | `_load_prompt()` pattern from `merch_procurement.py` — checks `/root/prompts/<id>.md` then falls back to source-relative path for local dev |
| Marker for multi-turn routing | `MARKER = f"_(weirdbot · {SKILL_ID} · v1)_"`; helper `_with_marker(text)` that appends the marker to every bot reply |
| Pulling thread state on follow-up | `ctx["is_followup"]` boolean, `ctx["thread_history"]` list of `{role, text}` turns; scan this list to recover prior state |
| Structured logging | `_log(kind, **extra)` that prints `json.dumps({"skill": SKILL_ID, "kind": kind, **extra})` to stderr |
| Calling Anthropic for brief parsing | Pattern from `merch.py:_parse_brief` — Haiku + `tool_choice: {type: "tool", name: "..."}` for guaranteed structured output |
| Agentic tool-use loop | Pattern from `merch_procurement.py:_run_agent` — adaptive thinking, `web_search_20260209` / `web_fetch_20260209` server tools, `pause_turn` / `end_turn` handling, max-loop safety |

### 4. Wire up the registries

- **`modal_app/skills/__init__.py`** — add `from .<id> import handle as <id>_handle` and `"<id>": <id>_handle` in the `SKILLS` dict. (Convert hyphens to underscores in the Python module name.)
- **`src/skills/index.ts`** — already imports stubs by name, so for stub conversions this needs no change. For a **brand new** skill, add the import + push into `skills[]`.
- **`src/skills/types.ts`** — only for a brand new `SkillId`: add to the union.
- **`src/categorize.ts`** — only for a brand new `SkillId`: add to the `SKILL_IDS` array.
- **`AGENTS.md`** — flip the skill's line in the "Repo layout" tree from `← STUB` to `← LIVE: <one-line description>`.

### 5. Write the test

`test/skills/<id>.test.ts` — copy `test/skills/merch.test.ts` verbatim and rename the imports + assertions. Two tests:
- Dispatches a signed POST to `env.MODAL_DISPATCH_URL` with the right body
- Posts a Slack error reply when Modal returns non-2xx

**Never hit real APIs.** Always `vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(...)`.

### 6. Validate

```
pnpm typecheck
pnpm test
```

Both green or you don't ship. No `--no-verify`. Paste the output back to the user.

### 7. Secrets (don't auto-run — tell the user)

Provider keys for Pattern B skills go on Modal, **not** the Worker. The Worker only ever sees the dispatch secret + Anthropic key.

`modal secret create weirdbot-secrets` is **all-or-nothing** — every existing key must be re-supplied. Walk the user through it; do not run it without an explicit go-ahead since it overwrites the bundle.

```
modal secret get weirdbot-secrets         # to see what's currently there
modal secret create weirdbot-secrets \
  EXISTING_KEY1="..." \
  EXISTING_KEY2="..." \
  NEW_PROVIDER_KEY="..." \
  --force
```

### 8. Deploy (don't auto-run — confirm first)

```
pnpm run deploy:all       # Modal first, then the Worker
pnpm tail                 # Worker logs
pnpm run tail:modal       # Modal logs
```

Production deploys are visible-to-others actions. Confirm before pushing.

### 9. Smoke test

```
pnpm probe "<a brief that should route to your skill>"
```

Watch `pnpm tail` for `"categorized","skill":"<id>"` then watch `pnpm run tail:modal` for the handler logs.

## Adapting the prompt — what to change vs keep

| Keep | Adapt |
|---|---|
| The behavior, the tables, the error-handling matrix, the worked examples | The "Credentials" section if it has hardcoded values — point at Modal secrets instead |
| The price caps, thresholds, fixed settings | Any `curl` examples that imply CLI usage — keep them as illustrative HTTP shapes, fine |
| The decision tree (Step 1 → 2 → 3 → …) | Add a `## Runtime context` preamble explaining the Slack thread + Modal worker context |
| The frontmatter `name` + `description` | If there's no frontmatter, add one — the description is what the categorizer reads |
| The multi-turn semantics | Make them explicit: which messages should have the marker, what state needs to survive into the next turn, how the user's reply gets parsed |

## Common pitfalls

- **Forgot one of the two prompt locations.** `src/skills/prompts/` is git-of-record; `modal_app/prompts/` is what runs. Both. Always.
- **Skipped the AGENTS.md status flip.** It's tiny but it's part of the contract — STUB vs LIVE is what tells the next agent where the live wiring is.
- **Imported `from os import environ` patterns from a different runtime into the Worker.** The Worker is V8, not Node. Secrets are on `env`, not `process.env`. The Python handler in `modal_app/` does use `os.environ` — that's fine, different runtime.
- **Made the Python module name match the kebab-case skill id.** Python modules use underscores: `buy_domain.py`, not `buy-domain.py`. The `SKILLS` dict key keeps the hyphenated id.
- **Wrote tests that hit real APIs.** Don't. Mock `globalThis.fetch`.
- **Added a comment that restates what the code does.** Don't. Only "why" comments. AGENTS.md is explicit about this.
- **Used `pnpm deploy` instead of `pnpm run deploy`.** `deploy` is reserved by pnpm itself — always `run`.
- **Forgot the marker on a bot reply in a multi-turn flow.** Without the marker, the follow-up routes back through the categorizer instead of returning to your handler.
- **Auto-deployed without asking.** Production deploys are visible-to-others. Confirm.
- **Auto-overwrote `weirdbot-secrets` without listing the existing keys first.** `modal secret create … --force` blows away the bundle. Get the current keys before adding the new one.

## Red flags — STOP

| Thought | Reality |
|---|---|
| "I'll skip the test, the dispatch is so simple" | Copy `merch.test.ts`. It's 60 lines of boilerplate and catches signing regressions. |
| "I'll inline the prompt as a string in the .ts file instead of two .md files" | The two-file pattern is load-bearing — it's how the Worker and Modal stay in sync, and it's how AGENTS.md says to do it. |
| "The credentials in the upstream prompt are fine, the runtime won't see git" | Strip them. The repo is a real codebase that gets read by humans + agents. Use Modal secrets. |
| "I'll do a deep refactor of the skill registry while I'm here" | Out of scope. AGENTS.md item 6: don't suggest framework changes when adding a skill. |
| "I'll go agentic to be safe" | Default deterministic. Reach for the agentic loop only when the prompt genuinely needs the model to iterate on tools. |
| "I'll run `modal secret create` myself to save the user a step" | No. It overwrites the whole bundle. Walk them through it. |
| "I'll typecheck after I commit" | Typecheck before you commit. Commits with broken types waste everyone's time. |
| "The diff is at 800 lines and growing" | A correct conversion is ~200 lines across ~6 files. If it's much bigger, you're refactoring something you shouldn't be. |

## Quick reference

```
# files touched on a typical conversion:
src/skills/prompts/<id>.md             # new — prompt, git-of-record
modal_app/prompts/<id>.md              # new — prompt, runtime copy
src/skills/<id>.ts                     # modified — stub → Pattern B dispatcher
modal_app/skills/<id_with_underscores>.py   # new — Python handler
modal_app/skills/__init__.py           # modified — register handler
test/skills/<id>.test.ts               # new — dispatch + error tests
AGENTS.md                              # modified — STUB → LIVE

# validate
pnpm typecheck && pnpm test

# expected size: ~200 lines added, 6–7 files
```

That's the whole skill. Read AGENTS.md, pick deterministic vs agentic, copy the canonical pair, fill in the registries, validate, hand off.
