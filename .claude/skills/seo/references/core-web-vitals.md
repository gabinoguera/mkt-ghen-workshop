# Core Web Vitals Reference — WordPress + Astra + Gutenberg

> Reference for `@seo-tecnico`. CWV diagnosis specific to [YOUR_SITE_URL] stack.
> Stack: WordPress + Astra Child + Gutenberg + Rank Math.

---

## The Three Metrics

| Metric | Measures | Good | Needs work | Poor | Google threshold |
|--------|----------|------|------------|------|-----------------|
| **LCP** | Largest Contentful Paint (loading) | ≤ 2.5s | 2.5s – 4s | > 4s | 75th percentile |
| **INP** | Interaction to Next Paint (interactivity) | ≤ 200ms | 200ms – 500ms | > 500ms | 75th percentile |
| **CLS** | Cumulative Layout Shift (visual stability) | ≤ 0.1 | 0.1 – 0.25 | > 0.25 | 75th percentile |

Google ranks based on **field data** (real users, CrUX dataset). Lab data (Lighthouse/Playwright) is diagnostic — use it to identify causes, but always cross-reference with field data when available.

---

## Data Sources

### Field Data (real users — authoritative for ranking)

```
mcp__google-analytics__run_report
  property_id: "<YOUR_GA4_PROPERTY_ID>"
  metrics: [
    "userEngagementDuration",  // proxy for session quality
  ]
  // GA4 collects CWV via web-vitals.js if the snippet is present
  // Check if [YOUR_SITE_URL] has CWV tracking configured in GA4
```

For GSC CWV report (aggregated):
```
mcp__gsc__get_performance_overview
  site_url: "sc-domain:[YOUR_DOMAIN]"
  // Note: GSC CWV data is under "Core Web Vitals" report in Search Console UI
  // Not directly available via current MCP — use Playwright to navigate to GSC if needed
```

### Lab Data (diagnostic — Playwright/Lighthouse)

```
mcp__playwright__browser_navigate  url: "https://[YOUR_SITE_URL]/..."
mcp__playwright__browser_snapshot  // Captures render state + timing
```

For Lighthouse specifically, use `browser_evaluate` to run performance timing:
```javascript
// Get LCP approximation
new PerformanceObserver((list) => {
  const entries = list.getEntries();
  console.log('LCP:', entries[entries.length-1].startTime);
}).observe({type: 'largest-contentful-paint', buffered: true});
```

---

## LCP: Largest Contentful Paint

### What triggers LCP on [YOUR_SITE_URL]

Typical LCP elements on a WordPress blog:
- **Featured image** (hero image at top of post) — most common LCP element
- **H1 heading** (if no image above the fold)
- **Background hero image** (on homepage or landing pages)

### WordPress-specific LCP causes

| Cause | Specific to [YOUR_SITE_URL] | Diagnosis |
|-------|---------------------------|-----------|
| Featured image not preloaded | Rank Math/WordPress doesn't auto-preload | Check `<link rel="preload">` in DOM |
| Large featured image file size | Images from `tools/image_generator.py` (Gemini) | Check image size in network tab |
| Image not in WebP format | Generated images may be PNG/JPEG | Check `src` extension |
| Astra theme CSS blocking render | External stylesheet loaded synchronously | Check render-blocking resources |
| Google Fonts blocking | If Astra loads Google Fonts | Look for `fonts.googleapis.com` in `<head>` |
| Rank Math scripts in `<head>` | Rank Math JS for schema/tracking | Check script load order |
| No CDN / slow hosting | Static assets served from origin | Check TTFB in network timing |
| Gutenberg block JS | Block library scripts loaded for all pages | Check `/wp-includes/js/` scripts |

### LCP Diagnosis Checklist

```javascript
// Check if featured image is preloaded
document.querySelector('link[rel="preload"][as="image"]')?.href

// Check featured image size and format
document.querySelector('.wp-post-image, .entry-featured-image img, article img:first-child')?.src

// Check render-blocking resources
[...document.querySelectorAll('link[rel="stylesheet"]')].map(l => l.href)
[...document.querySelectorAll('script:not([defer]):not([async])')].map(s => s.src)
```

### LCP Fixes to prescribe to @wp-implementer

1. **Add `fetchpriority="high"` to featured image** — in Astra Child `functions.php` hook
2. **Add `<link rel="preload">` for featured image** — WordPress `wp_head` action
3. **Convert images to WebP** — via `tools/image_generator.py` (already uses Gemini, check output format)
4. **Enable Astra's built-in performance options** — Lazy Load, Preload, Google Fonts optimization
5. **Defer non-critical Rank Math JS** — in Rank Math → General Settings → Performance

---

## INP: Interaction to Next Paint

INP replaced FID in March 2024. Measures responsiveness to all interactions (clicks, taps, key presses).

### WordPress-specific INP causes

| Cause | Description |
|-------|-------------|
| Heavy Gutenberg block JS | Block editor scripts loaded on frontend unnecessarily |
| Rank Math analytics script | If Rank Math analytics is active, it adds JS |
| Cookie consent plugin | GDPR plugin JS firing on interactions |
| Comments section | WP comments JS (if enabled) |
| Social share buttons | Third-party embed scripts |

### INP Diagnosis

INP is hard to measure with lab tools — it requires real interaction. Proxy signals:
- Total Blocking Time (TBT) in Lighthouse correlates with INP
- Long Tasks (>50ms) block the main thread

```javascript
// Check for long tasks
const observer = new PerformanceObserver((list) => {
  list.getEntries().forEach(entry => {
    if (entry.duration > 50) console.log('Long Task:', entry.duration, entry.name);
  });
});
observer.observe({type: 'longtask', buffered: true});
```

### INP Fixes to prescribe to @wp-implementer

1. **Disable Gutenberg block styles/scripts on frontend when not needed** — via `wp_enqueue_scripts` with `has_block()` check
2. **Defer third-party scripts** — Cookie consent, social embeds
3. **Remove unused plugins** — each active plugin may add JS

---

## CLS: Cumulative Layout Shift

Measures unexpected layout movement during page load. Very common on WordPress sites.

### WordPress-specific CLS causes

| Cause | Description | Fix |
|-------|-------------|-----|
| Images without dimensions | `<img>` without `width`/`height` attributes | Always declare dimensions |
| Featured image late-loading | Image loads after text, pushes content down | Add `width`/`height` to featured image |
| Cookie consent banner | GDPR plugin injects banner that shifts content | Reserve space with `min-height` |
| Google Ads (if any) | Ad slots without reserved space | Not applicable currently |
| Web fonts causing FOUT | Flash of unstyled text shifts layout | Use `font-display: optional` or preload fonts |
| Astra sticky header | If sticky header appears/disappears on scroll | Can cause shift — check threshold |
| Gutenberg blocks with dynamic height | Accordions, tabs, etc. that expand | Reserve min-height |

### CLS Diagnosis

```javascript
// Observe layout shifts
new PerformanceObserver((list) => {
  let clsScore = 0;
  list.getEntries().forEach(entry => {
    if (!entry.hadRecentInput) {
      clsScore += entry.value;
      console.log('Layout shift:', entry.value, entry.sources?.map(s => s.node));
    }
  });
  console.log('Total CLS:', clsScore);
}).observe({type: 'layout-shift', buffered: true});
```

### CLS Fixes to prescribe to @wp-implementer

1. **Add `width`/`height` to all images** — especially featured images via Astra Child hooks
2. **Reserve space for cookie banner** — CSS `min-height` on `<body>` or banner container
3. **Preload critical fonts** — `<link rel="preload" as="font">` in `wp_head`
4. **Set `font-display: swap` or `optional`** — in Astra child CSS

---

## Astra Theme Specific Notes

Astra is performance-focused by default, but verify these settings:

| Setting | Location | Recommended |
|---------|----------|-------------|
| Preload LCP image | Astra → Performance → Preload | Enable |
| Lazy load images | Astra → Performance → Images | Enable |
| Google Fonts optimization | Astra → Performance → Fonts | Preload or self-host |
| Critical CSS | Astra Pro feature | If Pro, enable |
| Minify CSS/JS | Via caching plugin (not Astra) | Enable in caching plugin |

---

## Rank Math Performance Impact

Rank Math adds JS/CSS for:
- Schema markup output (minimal, inline JSON-LD — no performance impact)
- Analytics (if Rank Math analytics enabled) — can add JS overhead
- Breadcrumbs CSS

Verify:
```javascript
// Check Rank Math scripts loaded on frontend
[...document.querySelectorAll('script')].filter(s => s.src.includes('rank-math')).map(s => s.src)
```

---

## CWV Audit Workflow

```
1. Get field data first:
   - mcp__google-analytics__run_report (if CWV tracking is set up)
   - Note: ask Gabriel if web-vitals.js is installed in GA4

2. Run lab audit via Playwright:
   - Navigate to target URL
   - Take snapshot (captures render state)
   - Run performance observer JS for LCP/CLS approximation
   - Check render-blocking resources

3. For each failing metric:
   - Identify root cause using the tables above
   - Prescribe specific fix for @wp-implementer

4. Document in tech-seo-audit.md:
   | Metric | Lab | Field | Status |
   Always label lab vs field clearly.
```

---

## CWV Thresholds Quick Reference

```
LCP:  ✅ ≤ 2.5s  |  ⚠️ 2.5–4s  |  ❌ > 4s
INP:  ✅ ≤ 200ms |  ⚠️ 200–500ms  |  ❌ > 500ms
CLS:  ✅ ≤ 0.1   |  ⚠️ 0.1–0.25   |  ❌ > 0.25
```

All measured at the **75th percentile** of page visits.
