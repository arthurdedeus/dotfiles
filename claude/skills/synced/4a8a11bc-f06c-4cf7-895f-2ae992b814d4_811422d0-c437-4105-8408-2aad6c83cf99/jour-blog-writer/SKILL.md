---
name: jour-blog-writer
description: >
  Write SEO-optimized blog articles for the Jour journaling app (jour.caipora.site). Use this skill whenever the user asks to write, draft, or create a blog post, article, or content piece for Jour. Trigger on phrases like "write a blog post for Jour", "create an article about journaling", "draft the next blog article", "write content for the Jour blog", or any request to produce written blog content related to Jour, journaling, mental health and journaling, habit tracking, or self-reflection. Also trigger when the user provides a topic, keyword, or article slug and asks for a blog post to be written around it. Even if the user says "write about journaling for anxiety" or "create a comparison article" without explicitly mentioning "Jour", use this skill if Jour blog content is the established context of the conversation.
---

# Jour Blog Writer

Write blog articles for the Jour journaling app. Every article must be genuinely useful to readers, grounded in evidence where relevant, optimized for search engines and AI citation, and true to Jour's calm, honest brand voice.

## First Step — Always Read the Brand Guide

Before writing any article, read:
```
references/brand-guide.md
```
This contains Jour's voice, tone, product facts, citation standards, and SEO requirements. Read it every time — it defines what good Jour content looks like and what to avoid.

## Inputs

The user may provide any of:
- A **topic** ("write about journaling for anxiety")
- A **keyword** ("target keyword: best free journaling apps")
- An **article slug** from a content roadmap ("write /blog/science-of-journaling")
- A **content gap report** with specific recommendations (title, keywords, word count, angle)
- A **competitor article URL** to differentiate against
- Just a vague direction ("write the next blog post") — in which case, ask what topic to cover

If the user provides a content gap report or roadmap, extract the relevant entry (topic, target keywords, recommended word count, angle, differentiation notes) and use it as the brief. If not, work with whatever topic information is given.

## Writing Process

### Step 1: Research (non-negotiable)

Before writing a single word:

**For every article type:**
- Use `web_search` to check what currently ranks in the top 5 for the target keyword. Understand what exists so you can differentiate.
- Note the common structure, depth, and angle of ranking content. Your article needs to offer something they don't.

**For research/science articles:**
- Search for peer-reviewed studies on the specific topic (PubMed, Google Scholar).
- Verify every study citation: author names, journal, year, and key findings. Do NOT fabricate or guess.
- Find at least 5 real studies for science-focused articles.

**For comparison articles:**
- Search for current pricing, features, and platform support for each app being compared.
- Verify facts — app pricing and features change frequently. Do not rely on the brand guide alone for competitor data.

**For guides and how-to articles:**
- Search for current best practices and any recent research that informs the advice.

### Step 2: Plan the Article

Before writing, produce a brief plan (share with user or note internally):

```
Target keyword: [primary keyword]
Secondary keywords: [3-5 related terms]
Search intent: [what the searcher actually wants]
Angle: [what makes this article different from what already ranks]
Word count target: [from content gap report, or estimate based on article type]
Article type: [research | comparison | guide | prompts | other]
Jour feature tie-ins: [which Jour features are naturally relevant, if any]
```

Article type guidelines for word count:
- Research/science deep-dives: 2,500-3,500 words
- Comparison/alternatives: 2,500-3,000 words
- How-to guides: 2,000-2,500 words
- Prompt lists: 1,500-2,500 words
- Focused mental health use cases: 1,800-2,500 words
- Definitional/explainer: 1,200-1,800 words

### Step 3: Write the Article

Follow these structural rules:

**Opening (first 100 words):**
- Answer the core question or state the key insight immediately. No preamble, no "in today's busy world" filler.
- Include the primary keyword naturally in the first 2-3 sentences.
- If the article targets a question keyword (e.g., "does journaling help anxiety?"), answer it directly in the first paragraph. Then spend the rest of the article providing evidence and depth.

**Body:**
- Use H2s for major sections, H3s for subsections. Every H2 should be descriptive (not "Section 1" — use "How Expressive Writing Reduces Anxiety").
- Short paragraphs: 2-4 sentences. Break up walls of text.
- Include at least one structured element (table, numbered list, or comparison grid) per article for scannability and AI extractability.
- Cite research using numbered inline references: "...reduces anxiety symptoms by 9% [1]." Each number corresponds to a full entry in the References section at the end of the article. Number references sequentially in order of first appearance.
- Weave in Jour mentions naturally, maximum 2-3 times per article. The article should be valuable regardless of whether the reader uses Jour.

**Closing:**
- Summarize the key takeaway in 1-2 sentences.
- If appropriate, include a soft CTA for Jour — not "Sign up now!" but something like "Jour is a free, minimalist journaling app built for exactly this kind of daily practice. Try it at jour.caipora.site."
- Not every article needs a Jour CTA. If it feels forced, skip it.

**References section (required for any article that cites research):**
- Place a `## References` section at the very end of the article, after the closing and any CTA.
- List every cited study in numbered order matching the inline `[1]`, `[2]`, etc. markers.
- Format each entry as: `[N] Author(s). "Title." *Journal Name*, Volume(Issue), Pages, Year. DOI or URL if available.`
- If the exact title or page numbers aren't available after search, include as much as you can verify: at minimum author(s), journal, and year.
- Only include studies you actually referenced in the text. Don't pad with unreferenced sources.

Example:
```
## References

[1] Smyth, J. M., Stone, A. A., Hurewitz, A., & Kaell, A. "Effects of writing about stressful experiences on symptom reduction in patients with asthma or rheumatoid arthritis." *JAMA*, 281(14), 1304–1309, 1999.
[2] Ramirez, G., & Beilock, S. L. "Writing about testing worries boosts exam performance in the classroom." *Science*, 331(6014), 211–213, 2011.
```

### Step 4: Generate Frontmatter & Finalize

After writing the article body, compose the YAML frontmatter (see Output Format section below for the exact fields and rules). The frontmatter replaces the need for separate SEO metadata — title, description, slug, and keywords all live there.

Also note for the user:
- **Internal links to add:** which other Jour blog articles this should link to (if they exist)
- **Estimated word count:** the actual body word count

## Article Type–Specific Guidelines

### Research / Science Articles
- Minimum 5 verified peer-reviewed citations. More is better.
- Lead with the most striking finding to hook the reader.
- Include specific numbers: "47% improvement" not "significant improvement."
- Explain studies accessibly — assume the reader is smart but not a scientist.
- End with practical application: how the reader can use this research in their journaling practice.

### Comparison / Alternatives Articles
- Be honest. Acknowledge where competitors are stronger. Readers detect and punish shill content.
- Include a feature comparison table with accurate, current data.
- Position Jour's actual strengths: minimalism, science-backed design, free, calm, focused.
- State clearly what Jour lacks compared to competitors (no native apps, no AI, no multimedia).
- Organize by use case ("Best for beginners", "Best for privacy", etc.) rather than just listing apps.

### How-To / Guide Articles
- Lead with actionable steps, not theory.
- Include specific parameters where research exists (e.g., "15-20 minutes, 3-4 times per week" for journaling frequency).
- Use numbered steps or clear section progression.
- Tie to Jour features where naturally relevant, not forced.

### Prompt / List Articles
- Organize prompts into themed categories.
- Provide brief context for why each category works (1-2 sentences with research where possible).
- Make prompts genuinely thoughtful — not generic "What are you grateful for?" that every competitor already has.
- Consider prompts that specifically leverage Jour's features (reflection questions, habit tracking observations, monthly goal check-ins).

### Definitional / Explainer Articles
- Answer the question directly in the first paragraph.
- Use clear structure with H2/H3 for each subtopic.
- Shorter format (1,200-1,800 words) is fine — don't pad.

## Quality Checks

Before finalizing, verify:
- [ ] Every research citation is real and verified via search
- [ ] Primary keyword appears in: H1, first 100 words, at least one H2, meta description
- [ ] No fabricated Jour features — only claim what's in the brand guide
- [ ] No AI-slop phrases (check the "Voice Don'ts" in brand-guide.md)
- [ ] Article would be genuinely useful to a reader who never uses Jour
- [ ] At least one structured element (table, list, comparison) for AI extractability
- [ ] Opening answers the reader's core question within the first 100 words
- [ ] Jour is mentioned at most 2-3 times, naturally, not as a sales pitch
- [ ] No `# Title` heading in the body — the title comes from frontmatter only
- [ ] Frontmatter `slug` matches the output filename
- [ ] SEO metadata is complete in frontmatter (title, slug, date, category, keywords, description)
- [ ] Word count is within the target range for this article type

## Output Format

Produce the article as an `.mdx` file with YAML frontmatter. The Jour blog renders MDX files where the frontmatter drives the title, metadata, and search functionality.

### Frontmatter

Every article MUST start with a YAML frontmatter block containing these fields:

```yaml
---
title: "The full article title as it will appear on the page"
slug: "lowercase-with-hyphens"
date: "YYYY-MM-DD"
category: "one of the categories below"
keywords:
  - "primary keyword"
  - "secondary keyword 1"
  - "secondary keyword 2"
  - "secondary keyword 3"
description: "Meta description, 140-155 chars, compelling, includes primary keyword"
---
```

**Field rules:**
- `title` — The full H1 title. Do NOT include a `# Title` heading in the body — the blog renderer generates it from the frontmatter.
- `slug` — URL path segment. Lowercase, hyphens, no stop words. The final URL will be `jour.caipora.site/blog/[slug]`.
- `date` — Publication date in ISO format. Use today's date.
- `category` — One of: `Science & Research`, `Getting Started`, `Techniques & Methods`, `Prompts`, `Mental Health`, `Comparisons`, `Habit Tracking`, `Goal Setting`, `Guides`. If none fits, propose a new one and note it for the user.
- `keywords` — Array of keywords used for the blog's search functionality. Include the primary target keyword and 3-7 secondary/related terms. These are the terms users can type in the blog search bar to find this article.
- `description` — The meta description for SEO. 140-155 characters. Compelling and includes the primary keyword.

### Body

After the frontmatter, write the article body as standard markdown:
- Do NOT include a top-level `# Title` heading — the frontmatter `title` field handles this.
- Start the body directly with the opening paragraph or the first `## Section Heading`.
- Use `##` for major sections, `###` for subsections.
- Use standard markdown: `**bold**`, `*italic*`, `[links](url)`, tables, lists, code blocks where needed.
- Inline research citations use numbered markers: `[1]`, `[2]`, etc.
- End with a `## References` section listing all cited studies.

### Complete Example

```mdx
---
title: "The Science of Journaling: What 30 Years of Research Actually Shows"
slug: "science-of-journaling"
date: "2026-04-03"
category: "Science & Research"
keywords:
  - "science of journaling"
  - "journaling research"
  - "benefits of journaling"
  - "expressive writing"
  - "journaling mental health evidence"
description: "Three decades of peer-reviewed research show journaling reduces anxiety by 9% and improves working memory. Here's what the studies actually say."
---

Expressive writing reduces anxiety symptoms by an average of 9%, according to a systematic
review of randomized controlled trials [1]. That's not a vague promise — it's a measured
outcome from clinical research spanning three decades.

## How Expressive Writing Affects the Brain

Research by Pennebaker and Beall first demonstrated in 1986 that writing about emotional
experiences produces measurable health benefits [2]...

## References

[1] Sohal, M., et al. "Efficacy of journaling in the management of mental illness." *Family Medicine and Community Health*, 10(1), 2022.
[2] Pennebaker, J. W., & Beall, S. K. "Confronting a traumatic event." *Journal of Abnormal Psychology*, 95(3), 274–281, 1986.
```

### File Naming and Output

Save the file to `/mnt/user-data/outputs/` as `[slug].mdx` and present it to the user.

The filename must match the `slug` in the frontmatter. For example, an article with `slug: "science-of-journaling"` is saved as `science-of-journaling.mdx`.
