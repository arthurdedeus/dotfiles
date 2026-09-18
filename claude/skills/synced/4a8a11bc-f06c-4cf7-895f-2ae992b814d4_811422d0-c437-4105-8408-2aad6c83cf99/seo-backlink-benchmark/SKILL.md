---
name: seo-backlink-benchmark
description: "Analyze and benchmark backlink profiles for SEO. Use this skill when the user wants to analyze a backlink profile, compare link profiles between domains, find link building opportunities, identify toxic/spammy links, assess domain authority/domain rating trajectory, analyze referring domain quality, find link gaps vs. competitors, evaluate link velocity, audit anchor text distribution, or plan a link building strategy. Trigger on: 'backlink analysis', 'backlink audit', 'link profile', 'domain authority', 'domain rating', 'referring domains', 'link building', 'toxic links', 'disavow', 'link gap', 'anchor text analysis', 'who links to competitors', or when the user uploads Ahrefs/Semrush/Moz backlink exports. Do NOT trigger for content strategy, technical audits, keyword analysis, or rank tracking."
---

# Backlink Profile Benchmarking

Analyzes backlink data to compare link profiles, identify quality vs. toxic links, find competitor link gaps, and produce a prioritized outreach strategy.

## Input Types

1. **Ahrefs Backlinks export** (CSV with referring domains, DR, anchor, target URL, etc.)
2. **Semrush Backlink Analytics export** (referring domains, authority score, anchor, etc.)
3. **Moz Link Explorer export** (DA, linking domains, anchor text, etc.)
4. **Multiple domain exports** for competitive comparison
5. **Google Search Console Links export** (limited but free first-party data)
6. **Just domain names** — provide analysis framework and recommend what to export

## Analysis Framework

### Step 1: Link Profile Overview

Build the foundational metrics:

**Aggregate Metrics**
- Total backlinks (raw count, usually inflated — referring domains matters more)
- Total referring domains (unique domains linking to you)
- Domain Rating / Domain Authority / Authority Score (depends on tool)
- Referring domain trend over time (if historical data available)

**Quality Distribution**
Segment referring domains by authority tier:
- Tier 1: DR/DA 70+ (high authority — news sites, major publications, .gov, .edu)
- Tier 2: DR/DA 40-69 (solid authority — established blogs, industry sites)
- Tier 3: DR/DA 20-39 (moderate — smaller niche sites, local sites)
- Tier 4: DR/DA 0-19 (low authority — may include spam)

The ratio matters more than the total. A healthy profile has a pyramid shape — many Tier 3-4, fewer Tier 2, and some Tier 1.

### Step 2: Link Quality Assessment

**Anchor Text Distribution**
Analyze anchor text categories:
- Branded (company name, domain) — should be largest segment (~30-50%)
- Naked URLs — common, natural (~15-25%)
- Generic ("click here", "read more") — natural (~10-15%)
- Exact match keyword — should be LOW (<5%). High % is a spam signal
- Partial match keyword — moderate is OK (~10-15%)
- Miscellaneous/other

Flag: Over-optimized anchor text profiles (too many exact-match keyword anchors) are a Penguin penalty risk.

**Link Type Assessment**
- Dofollow vs. nofollow ratio (natural profiles have ~70-85% dofollow)
- Link context: editorial (within content) vs. footer/sidebar vs. comments vs. directory
- Content type linking: are links from relevant, topical content?

**Toxic Link Identification**
Flag links that match these patterns:
- From domains with DR/DA 0-5 AND no real traffic
- Sitewide links (every page of a domain links to you — usually footer/sidebar)
- Links from PBN patterns (thin content sites, no real audience)
- Links from link farms, directories with no editorial standards
- Foreign language sites with no topical relevance
- Anchor text is spammy (casino, pharma keywords unrelated to your business)
- Very high number of outbound links on the referring page

Don't recommend disavow for every low-quality link. Google mostly ignores spam automatically. Only recommend disavow for clear manual penalty risk (obvious PBN networks, paid link schemes).

### Step 3: Competitive Link Gap Analysis

If multi-domain data is available:

**Referring Domain Gap**
- Domains that link to competitors but NOT to you — these are your prospects
- Sort by: authority of the referring domain, relevance to your niche, number of competitors they link to (more = easier to get)
- A domain linking to 3+ competitors but not you is a strong signal they'd link to you too

**Link Velocity Comparison**
- New referring domains per month: you vs. competitors
- Are competitors growing their link profiles faster?
- Identify competitor link building patterns (guest posts, PR, partnerships, resource pages)

**Page-Level Link Analysis**
- Which specific competitor pages attract the most links?
- What makes those pages linkable? (original research, tools, comprehensive guides, infographics)
- Can you create superior versions of those assets?

### Step 4: Link Building Opportunity Prioritization

Score each prospect by:
- **Authority**: DR/DA of the referring domain
- **Relevance**: How topically related is the site to your niche?
- **Accessibility**: Do they have guest post policies, resource pages, or active outreach patterns?
- **Competitor links**: Do they already link to your competitors? (warm prospect)
- **Link type likely**: Editorial mention, guest post, resource page, broken link replacement?

### Step 5: Link Profile Health Score

Produce an overall assessment:
- **Strength**: How does total referring domain count and quality compare to competitors ranking for your target keywords?
- **Risk**: Any penalty risk from toxic links or over-optimized anchors?
- **Velocity**: Are you gaining or losing link momentum?
- **Diversity**: Links from varied sources and domains, or concentrated?

## Output Format

```
# Backlink Profile Benchmark: [Domain]
**Analysis Date:** [Date]
**Tools Used:** [Ahrefs/Semrush/Moz]
**Competitors Compared:** [List]

## Executive Summary
[Overall link profile strength, biggest risks, key opportunities]

## Link Profile Overview
| Metric | Your Site | Competitor 1 | Competitor 2 | Competitor 3 |
|--------|----------|-------------|-------------|-------------|
| Referring Domains | | | | |
| DR/DA/AS | | | | |
| Dofollow % | | | | |
| Link Velocity (new RDs/mo) | | | | |

## Quality Distribution
| Authority Tier | Your RDs | % | Comp 1 | Comp 2 |
|---------------|---------|---|--------|--------|
| Tier 1 (DR 70+) | | | | |
| Tier 2 (DR 40-69) | | | | |
| Tier 3 (DR 20-39) | | | | |
| Tier 4 (DR 0-19) | | | | |

## Anchor Text Analysis
| Anchor Type | % of Profile | Status |
|------------|-------------|--------|
| Branded | X% | [Healthy/Over/Under] |
| Naked URL | X% | |
| Exact Match | X% | [Flag if >5%] |
| Partial Match | X% | |
| Generic | X% | |

## Toxic Link Assessment
- **Risk Level:** [Low/Medium/High]
- **Potentially Toxic Links:** [Count]
- **Disavow Recommended:** [Yes/No — only for clear penalty risk]
[If yes, list specific domains to disavow and why]

## Link Gap: Top Prospects
| Referring Domain | DR | Links to Comp 1 | Links to Comp 2 | Relevance | Approach |
|-----------------|----|----|----|----|------|
[Top 20-30 prospects sorted by authority × relevance × accessibility]

## Most Linkable Competitor Content
| URL | Referring Domains | Why It Attracts Links | Can You Replicate? |
|-----|------------------|----------------------|-------------------|

## Link Building Action Plan

### Immediate (Low-hanging fruit)
[Broken link building, unlinked brand mentions, resource page additions]

### Short-term (1-3 months)
[Guest post prospects, industry roundup participation, partnership links]

### Long-term (3-6 months)
[Linkable asset creation — original research, tools, comprehensive guides]

## Link Profile Health Score
| Dimension | Score (1-10) | Notes |
|-----------|-------------|-------|
| Strength | | |
| Quality | | |
| Risk | | |
| Velocity | | |
| Diversity | | |
| **Overall** | | |
```

## Analysis Principles

**Referring domains > total backlinks.** 100 links from 1 domain = 1 meaningful link signal. Always focus on unique referring domains.

**Context matters more than metrics.** A DR 30 niche blog in your exact industry can be more valuable than a DR 70 generic news site. Authority scores are proxies — relevance is the real signal.

**Natural profiles look diverse.** A healthy link profile has varied anchor text, mixed dofollow/nofollow, links from different site types, and gradual growth. Anything that looks manufactured (sudden spikes, all exact-match anchors) is a risk.

**Don't panic about toxic links.** Google's algorithms largely ignore spam links automatically. Disavow files should be used sparingly — only when there's clear evidence of a manual action or obvious paid link scheme. Over-disavowing can hurt more than help.

**Link building is a content strategy.** The best link building is creating content people want to reference. Original data, tools, and comprehensive resources earn links naturally. Outreach works best when you have something genuinely worth linking to.

## Working with Export Files

**Ahrefs Backlinks**: Key columns: `Referring Page URL`, `Referring Page Title`, `DR`, `UR`, `Domains to Referring Page`, `Dofollow`, `Anchor`, `Target URL`, `First Seen`, `Last Seen`

**Ahrefs Referring Domains**: `Domain`, `DR`, `Dofollow Backlinks`, `Total Backlinks`, `First Seen`

**Semrush Backlink Analytics**: `Source URL`, `Target URL`, `Anchor`, `Authority Score`, `Follow/Nofollow`, `First Seen`, `Last Seen`

**Moz Link Explorer**: `URL`, `Anchor Text`, `DA`, `PA`, `Spam Score`, `Link Status`

For all exports:
1. Read with pandas
2. Deduplicate by referring domain (keep highest authority page per domain)
3. Segment by authority tier
4. For gap analysis: merge multiple domain exports on referring domain
5. Filter out obviously irrelevant links (different language, unrelated topic) before presenting results
