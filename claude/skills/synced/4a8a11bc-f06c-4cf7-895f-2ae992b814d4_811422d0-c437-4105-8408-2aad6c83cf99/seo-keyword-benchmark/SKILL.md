---
name: seo-keyword-benchmark
description: "Benchmark and analyze keyword rankings and SERP competitive position for SEO. Use this skill when the user wants to analyze keyword rankings, benchmark competitive SERP position, track ranking progress over time, identify keyword cannibalization, find CTR anomalies, measure share of voice, analyze SERP feature ownership, compare keyword portfolios between domains, or diagnose why rankings dropped. Trigger on: 'keyword analysis', 'ranking analysis', 'SERP analysis', 'share of voice', 'keyword cannibalization', 'CTR analysis', 'ranking benchmark', 'competitive keywords', 'keyword tracking', 'why did my rankings drop', 'position tracking', or when the user provides keyword/ranking data exports and wants insights. Also trigger when comparing search visibility between two or more domains. Do NOT trigger for technical audits, content strategy, backlink analysis, or dashboard creation."
---

# Keyword & SERP Competitive Benchmarking

Analyzes keyword ranking data to produce competitive position analysis — where you're winning, losing ground, cannibalizing, and where CTR anomalies suggest optimization opportunities.

## Input Types

1. **Google Search Console performance export** (queries, clicks, impressions, CTR, position)
2. **Semrush/Ahrefs organic keywords export** (keyword, position, volume, URL, traffic estimate)
3. **Semrush Keyword Gap or Position Tracking export** (multi-domain comparison)
4. **Rank tracking tool export** (Nightwatch, SE Ranking, AccuRanker, etc.)
5. **Multiple time periods** for trend analysis

The richer the data, the better the analysis. GSC data is ground truth for your own performance. Third-party tools add competitor context and volume estimates.

## Analysis Framework

### Step 1: Keyword Portfolio Overview

Build the big picture first:

**Distribution Analysis**
- Total keywords ranking (and trend if historical data available)
- Position distribution: #1, #2-3, #4-10, #11-20, #21-50, #51-100
- Estimated total organic traffic from keyword portfolio
- Traffic concentration: what % of traffic comes from top 10 keywords?

**Keyword Type Segmentation**
- Branded vs. non-branded keywords (separate these — branded rankings inflate metrics)
- Informational vs. transactional vs. navigational intent
- Head terms (<3 words) vs. long-tail (3+ words)

### Step 2: Competitive Position Analysis

If multi-domain data is available:

**Share of Voice (SOV)**
- Calculate SOV: sum of estimated traffic from all ranking keywords per domain
- Compare SOV across competitor set
- SOV by topic/keyword cluster (who dominates which topics?)

**Keyword Overlap**
- Keywords only you rank for (exclusive)
- Keywords only competitors rank for (pure gaps)
- Keywords where you overlap — and who ranks higher
- "Striking distance" keywords: you're #4-20, competitor is #1-3

**SERP Feature Ownership**
- Who owns featured snippets for target keywords
- AI Overview presence (if data available from tools that track this)
- People Also Ask ownership
- Knowledge panel presence

### Step 3: Performance Anomalies & Opportunities

**CTR Analysis** (requires GSC data)
- Compare actual CTR vs. expected CTR for position
  - Position 1: ~27-31% expected CTR
  - Position 2: ~15-17%
  - Position 3: ~10-12%
  - Position 4-5: ~6-8%
  - Position 6-10: ~2-5%
- Flag keywords with CTR significantly below expected for their position → title/meta description optimization opportunity
- Flag keywords with CTR significantly above expected → these pages are doing something right, learn from them

**Keyword Cannibalization Detection**
- Multiple URLs from same domain ranking for the same keyword
- Identify by: same keyword → multiple URLs in ranking data
- Assess severity: are both URLs bouncing in/out of rankings? Is neither ranking as well as a consolidated page would?
- Recommend consolidation targets

**Striking Distance Keywords**
- Keywords ranking #4-20 with high volume — these are the biggest ROI opportunities
- For each: current position, URL, search volume, estimated traffic if moved to position 1-3
- Prioritize by: (Volume × Position Improvement Potential) / Difficulty

**Ranking Volatility**
- If historical data spans multiple periods: which keywords are stable vs. volatile?
- Sudden drops: correlate with known algorithm updates or site changes
- Trending up vs. trending down clusters

### Step 4: SERP Environment Assessment

For top keywords, analyze the SERP landscape:

- **SERP feature saturation**: How many results are "plain blue links" vs. featured snippets, AI Overviews, People Also Ask, image packs, video carousels, shopping results?
- **Zero-click risk**: Keywords where AI Overviews or featured snippets likely satisfy the query without a click
- **Commercial intent indicators**: Presence of shopping ads, product listings suggests transactional value

### Step 5: AI Search Visibility Cross-Reference

If the user has AI visibility data (from Otterly, Peec, Semrush AIO, etc.):
- Cross-reference: keywords where you rank well in Google but are absent from AI answers
- Keywords where you're cited in AI answers but don't rank well in traditional SERPs
- AI citation rate vs. organic ranking position correlation

## Output Format

```
# Keyword & SERP Benchmark Report: [Domain]
**Analysis Date:** [Date]
**Data Sources:** [GSC, Semrush, etc.]
**Period Analyzed:** [Date range]
**Competitors Compared:** [List or N/A]

## Executive Summary
[Overall position strength, biggest opportunities, biggest risks]

## Keyword Portfolio Overview
| Metric | Value | Trend |
|--------|-------|-------|
| Total ranking keywords | X | ↑/↓ |
| Position 1 keywords | X | |
| Position 2-3 | X | |
| Position 4-10 | X | |
| Position 11-20 | X | |
| Est. monthly organic traffic | X | |
| Traffic from top 10 keywords | X% | |

## Share of Voice Comparison
| Domain | SOV | SOV Change | Top Clusters |
|--------|-----|-----------|-------------|

## Top Opportunities

### Striking Distance (Highest ROI)
| Keyword | Current Pos | Volume | URL | Traffic Upside |
|---------|------------|--------|-----|---------------|
[Keywords #4-20 with highest volume × improvement potential]

### CTR Optimization Opportunities
| Keyword | Position | Actual CTR | Expected CTR | Impressions | Fix |
|---------|---------|-----------|-------------|------------|-----|
[Keywords underperforming on CTR for their position]

### Cannibalization Issues
| Keyword | URL 1 | Pos 1 | URL 2 | Pos 2 | Recommended Action |
|---------|-------|-------|-------|-------|--------------------|

## Competitive Gaps
| Keyword Cluster | Your SOV | Best Competitor | Their SOV | Gap |
|----------------|---------|----------------|---------|-----|

## Risk Assessment
### Keywords at Risk (Declining Trends)
[Keywords losing positions, with velocity and severity]

### Zero-Click Risk
[High-volume keywords where SERP features reduce click potential]

## Recommendations
[Ordered by estimated traffic impact]
1. [Action] — Est. impact: +X monthly visits
2. ...
```

## Analysis Principles

**Separate branded from non-branded.** Branded rankings are usually strong and not actionable in the same way. Non-branded is where the real competitive battle happens. Always segment.

**CTR anomalies are low-hanging fruit.** If you rank #3 for a 10K volume keyword but your CTR is 4% instead of expected 11%, fixing the title tag and meta description could nearly triple clicks from that keyword alone — no ranking improvement needed.

**Cannibalization is more common than people think.** If two URLs from the same site rank for a keyword, Google is often confused about which to show, and both underperform. The fix is usually to merge content and redirect.

**Share of Voice predicts market share.** Research shows SOV in search correlates with actual market share. Tracking SOV over time is one of the most meaningful SEO metrics for business impact.

**Don't just count keywords — weight by value.** A site with 5,000 ranking keywords sounds impressive, but if 4,800 are position 50+ with <10 monthly searches, the effective portfolio is 200 keywords. Focus analysis on keywords that actually drive or could drive traffic.

## Working with Export Files

**Google Search Console**: Export from Performance → Search Results. Key columns: `Query`, `Clicks`, `Impressions`, `CTR`, `Position`. May also have `Page` (URL), `Country`, `Device`.

**Semrush Organic Research**: `Keyword`, `Position`, `Previous Position`, `Search Volume`, `Keyword Difficulty`, `CPC`, `URL`, `Traffic`, `Traffic (%)`, `Traffic Cost`, `SERP Features`

**Ahrefs Organic Keywords**: `Keyword`, `Volume`, `KD`, `Position`, `URL`, `Traffic`, `Traffic Potential`

**Multi-domain comparisons**: Semrush Keyword Gap provides side-by-side positions. Pivot on keywords to compare domains.

For all files:
1. Read with pandas
2. Clean: remove rows with missing keyword or position data
3. Segment by branded/non-branded (filter keywords containing brand name)
4. Group by intent cluster or topic
5. Calculate aggregates before diving into individual keyword analysis
