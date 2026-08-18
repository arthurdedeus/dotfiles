---
name: orwell-writing
description: >-
  Use when asked to draft, rewrite, edit, review, polish, copyedit, simplify, or humanize written prose — docs, READMEs, PR descriptions, error messages, release notes, essays, posts, scripts, speeches, emails, product copy. Applies George Orwell's six rules and ASD-STE100 Simplified Technical English to remove "AI slop" while preserving the user's meaning, audience, tone, and explicit constraints. Three modes: strict (procedures, safety, error messages), flavored (general prose, the default), and creative (voice-led writing). Never applies to code, identifiers, or command syntax.
---

# Orwell Writing

Orwell's six rules and ASD-STE100 Simplified Technical English (STE), used as filters for clear, direct, honest prose.

This applies to prose only. It never applies to code, identifiers, command syntax, legal text, or required quotations. Preserve those exactly. Do not simplify them silently.

STE has writing rules and a controlled dictionary. Use an approved word with its approved meaning when the dictionary is available. Do not claim strict STE conformance without checking the current ASD-STE100 issue and dictionary.

## Pick the mode first

| Mode | Use for | What changes |
|---|---|---|
| **strict** | Procedures, runbooks, safety text, error messages | Every rule below, plus the length caps. No semicolons, no contractions. |
| **flavored** | READMEs, PR descriptions, docs, business and product prose. **The default.** | Sentence, paragraph, active-voice, and plain-verb discipline. Contractions are fine. Relax the ~900-word dictionary so the text keeps range. |
| **creative** | Fiction, poetry, memoir, scripts, lyrical prose, anything voice-led | STE is a clarity aid, not a cage. Keep intentional ambiguity, cadence, dialogue style, imagery, and character voice. Cut only language that is inherited, inflated, evasive, or lazy. |

If the user asks for strict STE on creative work, do it, and say where it kills an effect.

STE strips voice on purpose. That is correct for a runbook and wrong for an essay. Choose accordingly.

## Orwell's six rules

From "Politics and the English Language". These hold in every mode.

1. Never use a metaphor, simile, or other figure of speech which you are used to seeing in print.
2. Never use a long word where a short one will do.
3. If it is possible to cut a word out, always cut it out.
4. Never use the passive where you can use the active.
5. Never use a foreign phrase, a scientific word, or a jargon word if you can think of an everyday English equivalent.
6. Break any of these rules sooner than say anything outright barbarous.

Rule 6 governs the other five.

## The rules

### Words

- Use one name for one thing. Do not rename an item to avoid repetition.
- Use the short common word: start (not begin/commence/initiate), use (not utilize/leverage), help (not facilitate), make sure (not ensure), before (not prior to), after (not subsequent to), about (not regarding/concerning), get (not obtain/acquire), show (not demonstrate), also (not additionally/furthermore/moreover).
- Give each word one meaning. "Fall" means to move down, not to decrease.
- No marketing adjectives: seamless, robust, powerful, cutting-edge, effortless, world-class, next-generation, revolutionary.
- Use a specific technical term when accuracy needs it. Define it or link to its definition.
- Keep noun groups short. Use prepositions to show how terms relate.
- American spelling, unless the user's style guide requires another variety.

### Verbs

- Active voice. "The parser reads the file", not "the file is read by the parser".
- Use a verb for an action. "Analyze the log", not "perform an analysis of the log".
- No stacked auxiliaries. Not "it is important to note that this may help to improve". Write "this improves X".
- No "-ing" main verb where a simple tense works.
- Passive is allowed when it serves emphasis, tact, suspense, or technical accuracy, or when the actor is unknown. Outside strict mode, prefer it in those cases rather than forcing an awkward subject.

### Sentences

- One instruction or statement per sentence.
- **strict only:** max 20 words for an instruction, max 25 for a description.
- **strict only:** no contractions. Use articles: a, an, the, this, these.

### Punctuation

- **strict:** no semicolons. Write two sentences.
- **flavored:** avoid semicolons. A period almost always reads better.
- STE bans the semicolon. It does not ban the em dash. Add that ban yourself if you want it.

### Structure

- One topic per paragraph, max six sentences.
- For steps, use a numbered vertical list. One action per item, imperative form.
- Put a condition before its command. "If the build fails, check the lockfile."
- Write procedures as direct instructions. State the condition, the action, and the expected result.
- Use positive instructions where they are clear. State what the reader must do.

When strict STE is not possible, keep the text clear and mark the passages that need a domain exception.

## Workflow

### Writing from scratch

1. Identify the audience, the purpose, and the promised tone.
2. Pick the mode.
3. Draft in concrete, direct English.
4. Cut stock phrases, dead metaphors, filler, pompous diction, needless abstraction, and avoidable jargon.
5. Keep necessary nuance. Do not make prose crude, false, or flat to make it short.
6. Run the self-lint.

### Revising existing text

1. Preserve the meaning and any explicit tone or format constraint.
2. Cut words, clauses, and sentences that do no work.
3. Replace stale figures of speech with plain phrasing or a fresh, specific image.
4. Replace long, foreign, scientific, or jargon terms with everyday English where accuracy permits.
5. Make passive constructions active where the actor matters and is known.
6. Flag jargon, passive voice, or ornate phrasing you kept on purpose. Do not silently delete precision.
7. Run the self-lint.

Return only the requested text. No preamble, no summary, no closing remarks.

## Self-lint

Run this before returning text.

1. Any sentence over 20 words (strict)? Split it.
2. Any semicolon? Replace with a period.
3. Any contraction (strict)? Expand it.
4. Any passive voice with a known actor and no reason to keep it? Make it active.
5. Any "-ing" main verb, nominalization ("perform an analysis"), or phrasal verb ("spin up")? Replace with a plain verb.
6. Same thing named two ways? Pick one name.
7. Any marketing adjective? Cut it.

## Limits

These rules are mechanical and lintable, and they are what removes the form of slop. Full STE also needs human judgment: the right technical noun, and whether a sentence makes good sense. A checker cannot certify that.

This skill fixes the FORM of slop. It cannot make a hollow paragraph true.

Free official standard (do not paste it in full, it is copyrighted): https://asd-ste100.org
