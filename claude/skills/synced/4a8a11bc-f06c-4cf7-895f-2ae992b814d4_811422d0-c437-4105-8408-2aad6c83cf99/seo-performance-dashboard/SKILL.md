---
name: seo-performance-dashboard
description: "Generate consolidated SEO performance dashboards and reports from multiple data sources. Use this skill when the user wants to create an SEO performance report, build an SEO dashboard, combine data from Search Console + GA4 + rank tracking into one view, produce monthly/quarterly SEO reports, track SEO KPIs over time, create executive-level SEO summaries, visualize organic traffic trends, or generate a report showing SEO progress and ROI. Trigger on: 'SEO report', 'SEO dashboard', 'monthly SEO report', 'SEO performance report', 'organic traffic report', 'SEO KPIs', 'SEO progress report', 'show me how SEO is doing', 'executive SEO summary', 'SEO ROI report', or when the user provides multiple SEO data exports and wants a unified view. Also trigger when the user says 'combine these SEO exports' or 'make sense of this data'. Do NOT trigger for technical audits, content gap analysis, keyword deep-dives, or backlink analysis — those have dedicated skills."
---

# SEO Performance Dashboard Generator

Combines raw data from multiple SEO sources into a consolidated performance report with KPI tracking, trend analysis, and actionable insights.

## Input Types

Accepts any combination of:
1. **Google Search Console export** (Performance → Search Results: queries, clicks, impressions, CTR, position)
2. **GA4 export** (organic traffic, landing pages, conversions, engagement metrics)
3. **Rank tracking export** (keyword positions over time from any tool)
4. **Semrush/Ahrefs domain overview export** (traffic estimates, keyword counts, DR/DA)
5. **Previous period data** for comparison (month-over-month, quarter-over-quarter, year-over-year)
6. **Business KPIs** (revenue from organic, leads from organic, conversion targets)

The user might provide just one source or all of them. Work with what's available.

## Report Generation Process

### Step 1: Data Inventory & Alignment

1. Read all provided files and identify what data is available
2. Align time periods — ensure comparisons use matching date ranges
3. Identify what's missing and note limitations (e.g., "no conversion data available — report focuses on traffic metrics")
4. Ask the user for context if needed:
   - What time period should the report cover?
   - Is there a comparison period they care about? (last month, last year, before/after a specific event)
   - Any specific goals or targets to benchmark against?
   - Who is the audience? (technical team vs. executive/stakeholder)

### Step 2: Core KPI Calculation

Calculate these metrics from available data:

**Traffic Metrics** (from GSC and/or GA4)
- Total organic clicks/sessions — current period vs. comparison period
- Organic traffic growth rate (%)
- Organic as % of total traffic (if GA4 total traffic available)
- Top landing pages by organic traffic
- Traffic by device (mobile vs. desktop)
- Traffic by country/region (if relevant)

**Visibility Metrics** (from GSC and/or rank tracking)
- Total impressions — trend over time
- Average position — trend over time
- Total ranking keywords — trend over time
- Keyword distribution by position bucket (#1, #2-3, #4-10, #11-20, etc.)
- New keywords entered rankings / keywords dropped from rankings

**Engagement Metrics** (from GA4)
- Organic bounce rate or engagement rate
- Average session duration from organic
- Pages per session from organic
- Key events / conversions from organic traffic

**Conversion Metrics** (from GA4 + business data)
- Organic conversions (total and by type if available)
- Organic conversion rate
- Revenue from organic (if ecommerce data available)
- Cost per organic acquisition vs. paid (if paid data available for comparison)
- Organic traffic value (estimated using CPC × clicks for ranking keywords, from Semrush/Ahrefs)

### Step 3: Trend Analysis

For each key metric, analyze the trend:
- **Direction**: Up, down, or flat
- **Velocity**: How fast is it changing?
- **Anomalies**: Sudden spikes or drops — correlate with known events (algorithm updates, site changes, new content published, technical issues)
- **Seasonality**: If year-over-year data available, distinguish seasonal patterns from real growth/decline

### Step 4: Performance Segmentation

Break down performance by meaningful segments:

**By Content Type/Section**
- Blog performance vs. product pages vs. landing pages
- Which content categories are growing vs. declining?

**By Keyword Intent**
- Informational keywords (how-to, what-is)
- Transactional keywords (buy, pricing, review)
- Navigational keywords (branded)

**By Funnel Stage**
- Top of funnel (awareness content, informational queries)
- Middle of funnel (comparison, evaluation content)
- Bottom of funnel (transactional, conversion pages)

### Step 5: Insight Generation

Don't just present numbers — interpret them:

**What's working?** Identify the specific pages, keywords, or strategies driving growth. Why are they working?

**What's not working?** Where is performance declining? Diagnose likely causes.

**What changed?** If there are significant shifts, hypothesize why (content published, links earned, algorithm update, competitor movement, technical change).

**What to do next?** Based on the data, what are the top 3-5 actions that would most improve performance?

## Output Formats

The user may want different formats depending on audience. Ask if unclear.

### Format A: Comprehensive Report (Default)

Use this for detailed analysis. Produce as a well-structured document.

```
# SEO Performance Report: [Domain]
**Period:** [Date Range]
**Compared To:** [Comparison Period]
**Prepared:** [Date]

## Executive Summary
[3-5 sentences: headline metrics, trend direction, key wins, key risks, top recommendation]

## Key Performance Indicators

### Traffic
| Metric | Current Period | Previous Period | Change | Change % |
|--------|---------------|----------------|--------|----------|
| Organic Sessions/Clicks | | | | |
| Organic % of Total | | | | |
| Avg. Position | | | | |
| Total Impressions | | | | |

### Engagement
| Metric | Current | Previous | Change |
|--------|---------|----------|--------|

### Conversions
| Metric | Current | Previous | Change |
|--------|---------|----------|--------|

## Traffic Trend
[Describe the trend, include key inflection points]

## Top Performing Pages
| Page | Clicks | Impressions | Avg Position | CTR | Change |
|------|--------|-------------|-------------|-----|--------|
[Top 10-15 pages by organic traffic]

## Keyword Portfolio Health
| Bucket | Keywords | Change | % of Portfolio |
|--------|---------|--------|---------------|
| Position 1 | | | |
| Position 2-3 | | | |
| Position 4-10 | | | |
| Position 11-20 | | | |
| 21+ | | | |

## Wins This Period
[Specific achievements: keywords gained, traffic milestones, rankings improved]

## Risks & Issues
[Declining keywords, traffic drops, technical issues surfacing in data]

## Recommendations
1. [Most impactful action] — Expected impact: [X]
2. [Second action] — Expected impact: [X]
3. [Third action] — Expected impact: [X]

## Appendix
[Detailed data tables, methodology notes]
```

### Format B: Executive Summary (1-page)

For stakeholders who need the headlines. Keep it tight.

```
# SEO Monthly Summary: [Domain] — [Month Year]

**Organic Traffic:** [Number] ([+/-X%] vs last month, [+/-X%] vs last year)
**Organic Conversions:** [Number] ([+/-X%])
**Organic Revenue:** [Number] ([+/-X%]) (if available)
**Total Keywords Ranking:** [Number] ([+/-X])

**Top Win:** [One sentence]
**Top Risk:** [One sentence]
**#1 Recommendation:** [One sentence]
```

### Format C: Spreadsheet Dashboard

If the user wants an Excel/Google Sheets dashboard:
- Create an XLSX with tabs: Summary, Traffic Trends, Keywords, Top Pages, Conversions
- Include charts where possible (traffic over time, position distribution)
- Use conditional formatting (green for improvements, red for declines)
- Follow the xlsx skill patterns for professional formatting

## Analysis Principles

**Compare to something meaningful.** Raw numbers without context are useless. Always show: vs. previous period, vs. same period last year (seasonality control), vs. target/goal (if set).

**Distinguish vanity metrics from actionable ones.** Total impressions going up is meaningless if clicks are flat — it might mean you're showing up for irrelevant queries. Always pair metrics that tell a complete story.

**Correlation ≠ causation, but still useful.** If traffic dropped the same week as a Google update, note the correlation. If traffic grew after a content push, note it. But be honest about uncertainty.

**Focus the narrative.** A report with 50 metrics and no story is worthless. Lead with: what happened, why it happened (best guess), and what to do about it. The data tables are supporting evidence, not the main event.

**Tailor to audience.** An engineering team needs different details than a CMO. If the user says "this is for leadership," cut the technical jargon and focus on business impact (traffic → leads → revenue). If it's for the SEO team, include the granular keyword and page data.

## Working with Data Files

**Google Search Console**: Export has `Date`, `Query`, `Page`, `Country`, `Device`, `Clicks`, `Impressions`, `CTR`, `Position`. Aggregate by date for trends, by query for keyword analysis, by page for content analysis.

**GA4 Exports**: Variable structure. Look for: `Date`, `Session source/medium` (filter to organic), `Landing page`, `Sessions`, `Engaged sessions`, `Engagement rate`, `Conversions`, `Revenue`.

**Rank Tracking Exports**: Usually: `Keyword`, `Position`, `Date`, `Search Volume`, `URL`. Pivot on date for trend analysis.

**Semrush Domain Overview**: `Month`, `Organic Traffic`, `Organic Keywords`, `Organic Cost`, `Branded Traffic`, `Non-Branded Traffic`.

For all files:
1. Read with pandas
2. Parse dates properly (different tools use different date formats)
3. Align time periods across sources
4. Handle missing data explicitly — don't silently drop rows
5. For large datasets, aggregate first, then segment as needed
