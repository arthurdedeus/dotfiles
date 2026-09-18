---
name: seo-content-gap
description: "Analyze content gaps and topical authority for SEO. Use this skill when the user wants to find content gaps between their site and competitors, assess topical authority coverage, build a content strategy or content roadmap, map existing content into topic clusters, identify missing subtopics, evaluate content quality vs. competition, determine which content to create/consolidate/kill, or perform a content audit with SEO focus. Trigger on: 'content gap analysis', 'topical authority', 'content audit', 'topic clusters', 'content roadmap', 'what content should I create', 'competitor content analysis', 'content strategy SEO', or when the user provides keyword/page data and asks what content is missing. Also trigger when comparing two or more domains for content coverage. Do NOT trigger for technical SEO audits, backlink analysis, or rank tracking."
---

# Content Gap & Topical Authority Analysis

Identifies where your content coverage is thin vs. competitors, maps content into topic clusters, and produces an actionable content roadmap.

## Input Types

The user may provide:
1. **Keyword gap export** (CSV from Semrush Keyword Gap, Ahrefs Content Gap) — shows keywords competitors rank for but you don't
2. **Organic keywords export** (CSV from Semrush/Ahrefs) — your current keyword portfolio
3. **Site crawl with content data** (URLs, titles, word counts, traffic estimates)
4. **Competitor URLs/domains** for comparison
5. **Just a domain** — you'll work with what you can gather

## Analysis Process

### Step 1: Map Your Existing Content

If content data is provided (crawl export, keyword export, or sitemap):

1. **Inventory existing content**: List all indexable pages with their primary target keywords
2. **Cluster by topic**: Group pages into topic clusters using semantic similarity
   - A topic cluster = one pillar topic + its subtopics
   - Example: "Email Marketing" pillar → subtopics: automation, list building, deliverability, templates, analytics, A/B testing
3. **Score cluster completeness**: For each cluster, assess:
   - Number of pages covering the topic
   - Depth of coverage (surface-level vs. comprehensive)
   - Internal linking between cluster pages
   - Whether a pillar page exists

### Step 2: Analyze Competitor Coverage

If competitor keyword data is provided:

1. **Identify competitor topics you don't cover at all** — these are pure content gaps
2. **Identify topics where competitors have deeper coverage** — they have 10 pages on a topic, you have 2
3. **Identify high-value gaps** — topics with significant search volume where competitors rank and you don't
4. **Note competitor content formats** — are they using guides, tools, videos, data studies?

If only competitor URLs are provided (no keyword data):
1. Fetch sitemaps to understand their content structure
2. Categorize their pages by topic
3. Compare topic coverage breadth

### Step 3: Keyword Opportunity Scoring

For each content gap identified, score by:

- **Search volume** — how much traffic potential
- **Keyword difficulty** — how hard to rank (if KD data is in the export)
- **Business relevance** — how closely it maps to what the user sells/does (ask the user about their business if unclear)
- **Competition gap size** — are all competitors covering this, or just one?
- **Content type required** — blog post, landing page, tool, guide, data study

Score formula (simplified): `Opportunity = (Search Volume × Business Relevance) / Keyword Difficulty`

### Step 4: Content Consolidation Analysis

Look for content that should be merged or killed:

- **Keyword cannibalization**: Multiple pages targeting the same keyword (identify using keyword overlap in exports)
- **Thin content**: Pages with <300 words and no meaningful differentiation
- **Outdated content**: Pages with old dates and declining traffic (if traffic data available)
- **Duplicate intent**: Multiple pages answering the same user question in different ways

For each, recommend: **Keep**, **Merge into [specific page]**, **Update**, or **Kill (redirect to [target])**

### Step 5: AI/LLM Content Opportunity Assessment

Evaluate content gaps specifically for AI visibility:

- **Question-format content**: Are there FAQ/how-to gaps that AI Overviews would surface?
- **Definitive answer content**: Topics where AI needs a clear, authoritative source to cite
- **Comparison/list content**: "Best X for Y" formats that LLMs frequently pull from
- **Data-rich content**: Original research, statistics, benchmarks that LLMs reference as sources
- **Entity establishment**: Content that establishes your brand as a known entity in the topic space

## Output Format

```
# Content Gap & Topical Authority Report: [Domain]
**Analysis Date:** [Date]
**Competitors Analyzed:** [List]
**Data Sources:** [What exports were used]

## Executive Summary
[Current state of content coverage, biggest gaps, estimated traffic opportunity]

## Topical Authority Map

### Cluster: [Topic Name]
- **Your Coverage:** [X pages, depth assessment]
- **Best Competitor Coverage:** [Competitor name, X pages]
- **Authority Score:** [Strong / Moderate / Weak / Absent]
- **Key Gaps:** [Missing subtopics]

[Repeat for each major cluster]

## Top Content Gaps by Priority

### Tier 1: High Volume + Low Competition + High Relevance
| Topic/Keyword | Est. Monthly Volume | KD | Competitor Ranking | Content Type Needed |
|---------------|--------------------|----|-------------------|-------------------|

### Tier 2: High Volume + Moderate Competition
[Same format]

### Tier 3: Low Volume + High Business Relevance (Long-tail)
[Same format]

## Content Consolidation Recommendations
| Current Page(s) | Issue | Action | Target |
|-----------------|-------|--------|--------|
[Cannibalization, thin content, and merge recommendations]

## AI Visibility Content Opportunities
[Specific content pieces that would improve AI/LLM citation likelihood]

## 90-Day Content Roadmap

### Month 1: Quick Wins + Foundation
[Specific pieces to create/update, with target keywords and content type]

### Month 2: Gap Filling
[Content to address biggest competitive gaps]

### Month 3: Authority Building
[Pillar content, original research, comprehensive guides]

## Methodology Notes
[What data was used, limitations, assumptions]
```

## Analysis Principles

**Gaps aren't all equal.** A keyword gap for a term with 50 monthly searches and no business relevance is noise. Filter ruthlessly by business value.

**Think in clusters, not individual keywords.** The goal is topical authority — ranking for a cluster of related terms because Google sees you as the expert. One great page targeting 50 related long-tail terms beats 50 thin pages targeting one keyword each.

**Account for search intent.** A "content gap" where the competitor ranks with a tool or calculator can't be filled with a blog post. Match the content format to the intent.

**Consolidation is as important as creation.** Many sites have more content than they need — it's just spread thin and cannibalizing itself. Sometimes the biggest win is merging 5 weak pages into 1 strong one.

**Freshness matters for AI.** LLMs tend to cite recently updated content. Recommend publication dates, last-updated signals, and content refresh cadences.

## Working with Export Files

**Semrush Keyword Gap export**: Columns typically include `Keyword`, `Search Volume`, `KD%`, `CPC`, `[Your Domain] Position`, `[Competitor] Position`, `SERP Features`

**Ahrefs Content Gap**: Similar structure with `Keyword`, `Volume`, `KD`, `Traffic Potential`, positions per domain

**Semrush Organic Research export**: `Keyword`, `Position`, `Search Volume`, `URL`, `Traffic`, `Traffic Cost`

For all exports:
1. Read with pandas
2. Filter to relevant keywords (remove branded competitor terms, irrelevant topics)
3. Group by topic/intent cluster
4. Calculate aggregate opportunity per cluster
