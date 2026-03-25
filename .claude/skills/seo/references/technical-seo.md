# Technical SEO Reference — WordPress + Rank Math

> Reference for `@seo-tecnico`. Covers technical SEO diagnosis on ghendigital.com.
> Stack: WordPress + Astra Child + Gutenberg + Rank Math + Spectra (pending).
> Based on Lighthouse SEO audits and Google Search Central guidelines.

---

## Crawlability

### robots.txt

Location: `https://ghendigital.com/robots.txt`

WordPress default (via Rank Math) allows all crawlers. Common issues to check:
- Is `/wp-admin/` disallowed? ✅ (correct)
- Are CSS/JS files accidentally blocked? ❌ (breaks rendering)
- Is the sitemap declared? `Sitemap: https://ghendigital.com/sitemap_index.xml`

Verification:
```
mcp__playwright__browser_navigate url: "https://ghendigital.com/robots.txt"
```

### Meta robots

Rank Math injects meta robots at page level. Common issues:
- Pages accidentally set to `noindex` in Rank Math settings
- Category/tag archives set to `noindex` (intentional, usually correct for thin content)
- Paginated pages: `/page/2/` should be indexable or handled with canonical

Verification via DOM:
```javascript
// In mcp__playwright__browser_evaluate
document.querySelector('meta[name="robots"]')?.content
```

Expected output for indexable pages: `index, follow` or `index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1`

### Canonical URLs

Rank Math injects `<link rel="canonical">`. Common issues on ghendigital.com:

| Issue | Example found | Fix |
|-------|--------------|-----|
| Canonical points to wrong category | `/code/` declared but Google indexed `/lab/` | Change in Rank Math → Advanced → Canonical URL |
| Self-referencing missing | No canonical on page | Enable in Rank Math → Titles & Meta → Global |
| Trailing slash inconsistency | `/lab/post/` vs `/lab/post` | Enforce one in WordPress permalink settings |
| HTTP vs HTTPS canonical | canonical points to `http://` | Fix in Rank Math or .htaccess redirect |

Verification:
```javascript
// Declared canonical
document.querySelector('link[rel="canonical"]')?.href

// vs Google's selected canonical (always check both):
// mcp__gsc__inspect_url_enhanced → googleInspectionResult.indexStatusResult.googleCanonical
```

**Always compare declared canonical vs Google-selected canonical.** A mismatch means Google disagrees with your declaration — investigate why.

---

## XML Sitemap (Rank Math)

Rank Math generates a sitemap index at `/sitemap_index.xml` with sub-sitemaps:
- `/post-sitemap.xml` — blog posts
- `/page-sitemap.xml` — static pages
- `/category-sitemap.xml` — category archives (optional)

Common issues:
- Pages with `noindex` appearing in sitemap (Rank Math should auto-exclude, but verify)
- Sitemap not submitted in GSC
- `lastmod` dates stale or missing
- Draft posts leaking into sitemap

Verification:
```
mcp__gsc__list_sitemaps_enhanced site_url: "sc-domain:ghendigital.com"
mcp__playwright__browser_navigate url: "https://ghendigital.com/sitemap_index.xml"
```

Key metrics from GSC sitemap report:
- **Submitted** vs **Indexed** — large gap = indexation problem
- **Last read** — if stale, Google hasn't re-crawled recently

---

## URL Structure

WordPress permalink structure: `/%category%/%postname%/` or `/%postname%/`

ghendigital.com uses category-based URLs:
- `/actualidad-ia/{slug}/`
- `/lab/{slug}/`
- `/inteligencia-artificial/{slug}/`
- `/seo/{slug}/`

Best practices (to verify):
- Lowercase only ✅ (WordPress default)
- Hyphens not underscores ✅ (WordPress default)
- No date in URL (avoid `/2024/01/post/`) ✅
- Short and descriptive slugs
- Target keyword present in slug

Verification:
```
mcp__gsc__get_search_analytics — check page URLs for consistency
```

---

## On-Page Meta Tags

Rank Math manages title tags and meta descriptions. Audit checklist:

### Title Tags

| Check | Target | Tool |
|-------|--------|------|
| Present and unique | Every page | GSC Coverage + DOM |
| Length | 50–60 chars | DOM inspect |
| Primary keyword near start | — | Visual review |
| Brand suffix | `\| GHEN Digital` | DOM inspect |
| Unique per page | No duplicates | Screaming Frog / GSC |

DOM verification:
```javascript
document.title
document.querySelector('meta[property="og:title"]')?.content
```

### Meta Descriptions

| Check | Target | Tool |
|-------|--------|------|
| Present | Every indexable page | DOM |
| Length | 150–160 chars | DOM |
| Contains focus keyword | — | Visual |
| Unique | No duplicates | — |
| CTA or compelling hook | — | Visual |

DOM verification:
```javascript
document.querySelector('meta[name="description"]')?.content
```

### Heading Structure

Single `<h1>` per page. Logical hierarchy H1 → H2 → H3.

DOM verification:
```javascript
[...document.querySelectorAll('h1,h2,h3')].map(h => `${h.tagName}: ${h.textContent.trim()}`)
```

---

## Schema Markup Validation

ghendigital.com uses a two-layer schema strategy:
- **Rank Math (page-level):** Article, BlogPosting, WebPage, Person, Organization, BreadcrumbList
- **Spectra blocks (block-level):** FAQPage, HowTo (pending Spectra installation)

### Validation process

1. Extract JSON-LD from page:
```javascript
[...document.querySelectorAll('script[type="application/ld+json"]')]
  .map(s => JSON.parse(s.textContent))
```

2. Validate via Rich Results Test:
```
Navigate to: https://search.google.com/test/rich-results?url={encoded_url}
```

3. Cross-reference with GSC Rich Results report (if available)

### Common Rank Math schema issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Missing `author` on BlogPosting | Rich Results warning | Add author in Rank Math → Schema → Author |
| `datePublished` / `dateModified` mismatch | Warning | Rank Math auto-generates from WP post dates — verify |
| Organization `logo` missing | Warning | Set in Rank Math → General Settings → Logo |
| Breadcrumbs not matching URL | Error | Verify Rank Math breadcrumb settings |
| Duplicate schema types | Error | Check if Rank Math + theme both output Article |
| FAQPage declared but no Spectra block | Inconsistency | Either install Spectra or remove from Rank Math |

---

## Image SEO

| Check | How to verify |
|-------|--------------|
| Alt text present on content images | `[...document.images].filter(i => !i.alt)` |
| Descriptive filenames | Check image URLs in DOM |
| Correct dimensions declared (width/height) | `[...document.images].filter(i => !i.width)` |
| Modern format (WebP/AVIF) | Check image URLs for `.webp` |
| Lazy loading on below-fold images | `[...document.images].map(i => i.loading)` |
| Featured image has alt text | Visual check in WP media library |

---

## Internal Linking Audit

Internal linking health affects PageRank distribution and topical authority signals.

Key checks:
- Are pillar pages receiving links from cluster posts?
- Are there orphan pages (no internal links pointing to them)?
- Are anchor texts descriptive (not "click here" or "read more")?
- Are there broken internal links?

Verification:
```javascript
// Get all internal links on a page
[...document.querySelectorAll('a[href*="ghendigital.com"], a[href^="/"]')]
  .map(a => ({ href: a.href, text: a.textContent.trim() }))
  .filter(a => a.text.length > 0)
```

---

## Mobile SEO

### Viewport meta tag
```javascript
document.querySelector('meta[name="viewport"]')?.content
// Expected: "width=device-width, initial-scale=1"
```

### Font size readability
- Body text should be ≥ 16px
- No horizontal scrolling on mobile

### Tap target sizes
- Interactive elements ≥ 48×48px

Verification: Playwright screenshot at mobile viewport:
```
mcp__playwright__browser_resize width: 375, height: 812
mcp__playwright__browser_screenshot
```

---

## HTTPS & Security

All pages must be served over HTTPS. Common WordPress issues:
- Mixed content: HTTP resources loaded on HTTPS page
- Redirect chain: `http://` → `https://` should be a single 301, not a chain

Verification:
```javascript
// Check for mixed content warnings
// Use Playwright console_messages to catch "Mixed Content" errors
```

---

## Technical SEO Audit Checklist

### Crítico (fix immediately — blocks indexation or ranking)
- [ ] HTTPS enabled, no mixed content
- [ ] robots.txt allows crawling of key pages
- [ ] No `noindex` on important indexable pages
- [ ] Canonical URL declared and matches Google-selected canonical
- [ ] XML sitemap submitted and readable
- [ ] No redirect chains on key URLs

### Alto (fix soon — direct ranking impact)
- [ ] Title tags present, unique, 50-60 chars
- [ ] Meta descriptions present, 150-160 chars
- [ ] Single `<h1>` per page
- [ ] Schema markup validates without errors
- [ ] Core Web Vitals passing (see core-web-vitals.md)
- [ ] Mobile viewport set correctly

### Medio (improve incrementally)
- [ ] Image alt texts complete
- [ ] Internal linking to pillar pages
- [ ] Descriptive anchor texts
- [ ] No orphan pages
- [ ] `lastmod` in sitemap accurate
- [ ] Breadcrumbs implemented and correct

---

## Tools Reference

| Tool | Access | Use |
|------|--------|-----|
| Google Search Console | `mcp__gsc__*` | Indexation, coverage, sitemaps, URL inspection |
| Google Analytics 4 | `mcp__google-analytics__*` | CWV field data, engagement by page |
| Playwright | `mcp__playwright__*` | DOM audit, Lighthouse, screenshot, rendering |
| Rich Results Test | Navigate via Playwright | Schema validation |
| WordPress REST API | `tools/wp_publisher.py` | (Read-only for seo-tecnico — no writes) |
