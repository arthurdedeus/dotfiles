---
name: seo-site-audit
description: "Run a comprehensive SEO site audit and technical diagnosis on a website. Use this skill whenever the user wants to audit a website's SEO health, diagnose technical SEO issues, check Core Web Vitals readiness, analyze crawlability, review schema/structured data implementation, assess mobile-friendliness, find broken links, check indexation issues, or produce a prioritized SEO fix list. Trigger when the user mentions 'SEO audit', 'site audit', 'technical SEO check', 'SEO health check', 'crawl issues', 'indexation problems', 'schema markup audit', 'Core Web Vitals', or provides a URL and asks what's wrong with their SEO. Also trigger when the user uploads a Screaming Frog crawl export, Sitebulb export, or any CSV/Excel with crawl data and wants it analyzed. Do NOT trigger for keyword research, content strategy, backlink analysis, or rank tracking — those have dedicated skills."
---

# SEO Site Audit & Diagnosis

Produces a prioritized, actionable SEO technical audit from either a live URL or crawl data exports.

## Input Types

The user may provide:
1. **A URL** — audit by fetching and analyzing directly
2. **Crawl data export** (CSV/XLSX from Screaming Frog, Sitebulb, etc.)
3. **Google Search Console export** — indexation and coverage data
4. **Multiple inputs combined**

## Audit Process

### Step 1: Determine Data Sources

Ask what data is available. More sources = better audit:
- Live URL (minimum viable input)
- Screaming Frog / Sitebulb crawl export
- Google Search Console coverage/performance export
- PageSpeed Insights / Core Web Vitals data
- robots.txt and sitemap.xml access

If only a URL is provided, proceed — don't block on missing data.

### Step 2: Technical Crawl Analysis

If crawl data (CSV/XLSX) is provided, analyze:

**Crawlability & Indexation**
- Pages blocked by robots.txt that shouldn't be
- noindex on pages that should be indexed (and vice versa)
- Canonical issues (missing self-referencing, conflicting, chains)
- Redirect chains (3+ hops), loops, 302s that should be 301s
- HTTP/HTTPS mixed content
- Orphan pages (no internal links to them)
- Crawl depth — flag pages >3 clicks from homepage

**HTTP Status Issues**
- 4xx errors, 5xx errors
- Soft 404s (200 status, thin/empty content)
- Redirect inventory and chains

**On-Page Technical Elements**
- Missing/duplicate title tags and meta descriptions
- Missing H1, multiple H1s per page
- Title length (flag >60 or <30 chars), meta desc length (flag >160 or <70 chars)
- Image alt text coverage
- Missing hreflang for multi-language sites

**Structured Data / Schema**
- What schema types are implemented
- Missing schema for page types that need it:
  Homepage → Organization, Products → Product, Blog → Article, FAQ → FAQPage, Local → LocalBusiness
- Validate schema for missing required fields

**Internal Linking**
- Pages with <3 internal links
- Orphan pages, broken internal links
- Link equity distribution

### Step 3: Core Web Vitals

If performance data is available:
- LCP — good: <2.5s, poor: >4.0s
- INP — good: <200ms, poor: >500ms
- CLS — good: <0.1, poor: >0.25
- Flag: render-blocking resources, unoptimized images, excessive JS

### Step 4: AI-Readiness Assessment

- Content structured for extraction? (headings, direct answers, scannable)
- Schema markup presence
- Freshness signals (last modified, publication dates)
- FAQ/Q&A patterns (feed AI Overviews)
- robots.txt AI crawler directives (GPTBot, ClaudeBot, PerplexityBot)

### Step 5: Mobile & UX

- Viewport meta tag, responsive design
- Intrusive interstitials, font readability, tap target sizing

## Output Format

ALWAYS use this structure:

```
# SEO Site Audit Report: [Domain]
**Audit Date:** [Date]
**Data Sources Used:** [List]

## Executive Summary
[2-3 sentences: overall health, biggest risks, quick wins]

## Critical Issues (Fix Immediately)
- **Issue:** / **Impact:** / **Pages Affected:** / **Fix:**

## High Priority (Fix Within 30 Days)
[Same format]

## Medium Priority (Fix Within 90 Days)
[Same format]

## Low Priority / Nice to Have

## AI-Readiness Score
- AI Crawler Access: [Allowed/Blocked/Partial]
- Schema Coverage: [X%]
- Content Extractability: [Assessment]

## Technical Vitals Summary
| Metric | Status | Value | Target |
|--------|--------|-------|--------|

## Action Plan
[Ordered by impact/effort ratio]
```

## Analysis Principles

**Prioritize by impact.** Weight: pages affected × traffic potential × severity.

**Diagnose root causes.** 500 duplicate titles = template issue. Recommend the systemic fix.

**Be specific.** Not "improve title tags" but "add unique titles to 47 product pages using '[Product Name] - [Feature] | Brand'".

**Distinguish debt from harm.** Best practices not followed (medium) vs. actively blocking indexing (critical).

**Scale to site type.** 50K-page ecommerce ≠ 20-page B2B site.

## Working with Crawl Exports

1. Read with pandas (CSV) or openpyxl (XLSX)
2. Common Screaming Frog columns: `Address`, `Status Code`, `Title 1`, `Meta Description 1`, `H1-1`, `Canonical Link Element 1`, `Indexability`, `Word Count`, `Inlinks`, `Outlinks`, `Crawl Depth`
3. Summary statistics first, then individual issues
4. For >10,000 rows, sample and summarize

## URL-Only Mode

1. web_fetch to get HTML
2. Analyze: title, meta, H1, schema, canonical, robots meta
3. Check robots.txt and sitemap.xml
4. Be transparent about limitations
5. Recommend Screaming Frog for deeper audit
