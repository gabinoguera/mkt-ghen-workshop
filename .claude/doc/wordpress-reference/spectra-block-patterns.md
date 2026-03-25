# Spectra Block Patterns — archivofinal.com

Reference document for building WordPress pages on archivofinal.com.
Extracted from the live site (homepage ID:3111, LEO page ID:2797).

**Theme:** Astra 4.12.3 + Astra Child
**Builder:** Gutenberg + Spectra (Ultimate Addons for Gutenberg — free)
**Last updated:** 2026-03-03

---

## Astra Global Color Palette

The site uses Astra's global color system. Reference these CSS variables in block attributes.

| Variable | Token | Approximate Color | Usage |
|----------|-------|-------------------|-------|
| `var(--ast-global-color-0)` | `ast-global-color-0` | Teal #426a65 | Primary brand color, CTAs, icons, accents |
| `var(--ast-global-color-2)` | `ast-global-color-2` | Dark charcoal | Body text, secondary buttons |
| `var(--ast-global-color-4)` | `ast-global-color-4` | Off-white / cream | Light section backgrounds |
| `var(--ast-global-color-5)` | `ast-global-color-5` | Lighter gray-white | Alternate section backgrounds |
| `var(--ast-global-color-6)` | `ast-global-color-6` | White | Card backgrounds, button text on teal |
| `var(--ast-global-color-7)` | `ast-global-color-7` | Border gray | Default borders, dividers |

**Important:** In block comment JSON attributes, `--` must be escaped as `\u002d\u002d` to avoid breaking HTML comment parsing. Example: `"backgroundColor":"var(\u002d\u002dast-global-color-5)"`.

---

## Block Types in Use

Pages on archivofinal.com use these block types exclusively:

| Block | Namespace | Purpose |
|-------|-----------|---------|
| **Container** | `uagb/container` | ALL layout (replaces wp:group, wp:columns) |
| **Advanced Heading** | `uagb/advanced-heading` | Section headings inside containers |
| **Info Box** | `uagb/info-box` | Feature cards with icon + title + description |
| **FAQ** | `uagb/faq` + `uagb/faq-child` | Accordion FAQ with FAQPage schema |
| **Buttons (Spectra)** | `uagb/buttons` + `uagb/buttons-child` | Spectra button groups |
| **Icon** | `uagb/icon` | Standalone decorative icons |
| Paragraph | `wp:paragraph` | Body text (native Gutenberg) |
| Heading | `wp:heading` | Simple headings (native Gutenberg) |
| Buttons | `wp:buttons` + `wp:button` | Button groups (native Gutenberg) |
| Image | `wp:image` | Images (native Gutenberg) |

**Rule:** For page layout, ALWAYS use `uagb/container` instead of `wp:group` or `wp:columns`. The site does NOT use native WordPress layout blocks.

---

## uagb/container — Layout Block

The primary layout building block. Two variants: **root** and **inner**.

### Root Container (section-level)

Full-width section. Has `isBlockRootParent: true`, `alignfull`, and inner wrapper div.

```html
<!-- wp:uagb/container {"block_id":"UNIQUE_8CHAR_HEX","variationSelected":true,"isBlockRootParent":true,"topPaddingDesktop":70,"bottomPaddingDesktop":70,"topPaddingTablet":40,"bottomPaddingTablet":40,"leftPaddingTablet":30,"rightPaddingTablet":30,"topPaddingMobile":30,"bottomPaddingMobile":30,"leftPaddingMobile":20,"rightPaddingMobile":20,"paddingLink":false} -->
<div class="wp-block-uagb-container uagb-block-UNIQUE_8CHAR_HEX alignfull uagb-is-root-container"><div class="uagb-container-inner-blocks-wrap">

[INNER BLOCKS HERE]

</div></div>
<!-- /wp:uagb/container -->
```

**Optional attributes:**

| Attribute | Values | Description |
|-----------|--------|-------------|
| `backgroundType` | `"color"`, `"image"` | Background type |
| `backgroundColor` | CSS var or hex | Background color |
| `anchor` | string | HTML id for anchor links |
| `rowGapDesktop` | number | Gap between children (vertical) |
| `columnGapDesktop` | number | Gap between children (horizontal) |
| `overflow` | `"hidden"` | Hide overflow |
| `equalHeight` | `true` | Equal height children |

**With background color:**
```json
{"backgroundType":"color","backgroundColor":"var(\u002d\u002dast-global-color-5)"}
```

**With anchor for navigation:**
```json
{"anchor":"section-name"}
```
```html
<div class="wp-block-uagb-container uagb-block-XXX alignfull uagb-is-root-container" id="section-name">
```

### Inner Container (sub-layout)

Nested container without `alignfull` or inner wrapper div.

```html
<!-- wp:uagb/container {"block_id":"UNIQUE_HEX","topPaddingDesktop":20,"bottomPaddingDesktop":20,"leftPaddingDesktop":25,"rightPaddingDesktop":25,"paddingLink":false} -->
<div class="wp-block-uagb-container uagb-block-UNIQUE_HEX">

[INNER BLOCKS HERE]

</div>
<!-- /wp:uagb/container -->
```

### Row Layout (horizontal children)

For side-by-side items (replaces `wp:columns`). Add `directionDesktop: "row"`.

```json
{
  "block_id": "XXX",
  "directionDesktop": "row",
  "directionMobile": "column",
  "childrenWidthDesktop": "equal",
  "columnGapDesktop": 20,
  "rowGapMobile": 15
}
```

### Card / Tile Container

Styled container with border, radius, shadow, and background. Used for feature tiles, category cards, etc.

```json
{
  "block_id": "XXX",
  "topPaddingDesktop": 30,
  "bottomPaddingDesktop": 30,
  "leftPaddingDesktop": 25,
  "rightPaddingDesktop": 25,
  "containerBorderTopLeftRadius": 15,
  "containerBorderTopRightRadius": 15,
  "containerBorderBottomLeftRadius": 15,
  "containerBorderBottomRightRadius": 15,
  "containerBorderStyle": "solid",
  "containerBorderColor": "#e0e0e0",
  "containerBorderTopWidth": 1,
  "containerBorderLeftWidth": 1,
  "containerBorderRightWidth": 1,
  "containerBorderBottomWidth": 1,
  "backgroundType": "color",
  "backgroundColor": "var(\u002d\u002dast-global-color-6)",
  "boxShadowVOffset": 4,
  "boxShadowBlur": 12,
  "boxShadowSpread": -4
}
```

---

## uagb/advanced-heading

Section headings inside Spectra containers.

```html
<!-- wp:uagb/advanced-heading {"block_id":"XXX","classMigrate":true,"headingDescToggle":false,"headingAlign":"center","headSpace":0,"blockTopPadding":0,"blockBottomPadding":15} -->
<div class="wp-block-uagb-advanced-heading uagb-block-XXX"><h2 class="uagb-heading-text">Heading Text Here</h2></div>
<!-- /wp:uagb/advanced-heading -->
```

**Key attributes:**

| Attribute | Values | Description |
|-----------|--------|-------------|
| `headingAlign` | `"left"`, `"center"` | Text alignment |
| `headingDescToggle` | `false` | Hide subtitle |
| `headingDescPosition` | `"above-heading"` | Subtitle position |
| `headSpace` | number | Space below heading |

---

## uagb/faq — FAQ Accordion with Schema

Generates `FAQPage` JSON-LD structured data. Uses self-closing `faq-child` blocks.

### Parent Block

```html
<!-- wp:uagb/faq {"block_id":"XXX","enableSchemaSupport":true,"borderStyle":"","borderWidth":"","borderRadius":"","borderColor":"","overallBorderTopWidth":1,"overallBorderLeftWidth":1,"overallBorderRightWidth":1,"overallBorderBottomWidth":1,"overallBorderTopLeftRadius":2,"overallBorderTopRightRadius":2,"overallBorderBottomLeftRadius":2,"overallBorderBottomRightRadius":2,"overallBorderStyle":"solid","overallBorderColor":"#D2D2D2"} -->

[FAQ CHILDREN HERE]

<!-- /wp:uagb/faq -->
```

**Critical:** `"enableSchemaSupport":true` activates FAQPage JSON-LD. Without it, no schema is generated.

### Child Block (self-closing)

```html
<!-- wp:uagb/faq-child {"block_id":"XXX","question":"¿Pregunta aquí?","answer":"Respuesta aquí."} /-->
```

**HTML in answers:** The `answer` attribute supports HTML tags. Escape them as JSON unicode:

| Character | Escape | Example |
|-----------|--------|---------|
| `<` | `\u003c` | `\u003cstrong\u003e` → `<strong>` |
| `>` | `\u003e` | `\u003c/strong\u003e` → `</strong>` |
| `"` | `\u0022` | `href=\u0022/url/\u0022` → `href="/url/"` |
| `--` | `\u002d\u002d` | CSS custom properties |

**Example with HTML answer:**
```html
<!-- wp:uagb/faq-child {"block_id":"abc123","question":"¿Cuánto cuesta?","answer":"Archivo Final opera con modelo freemium: los primeros 3 informes son gratuitos.\u003cbr\u003e\u003cbr\u003eVer \u003ca href=\u0022/como-funciona/\u0022\u003ecómo funciona\u003c/a\u003e."} /-->
```

**Supported HTML in answers:**
- `<br><br>` — Paragraph separation
- `<strong>text</strong>` — Bold text
- `<a href="/url/">text</a>` — Links
- `<ul><li>item</li></ul>` — Unordered lists
- `<ol><li>item</li></ol>` — Ordered lists

### Schema Rules

- One `uagb/faq` block per logical section (can have multiple on one page)
- Each block generates its own `FAQPage` schema
- **Do NOT** also enable FAQPage schema in Rank Math for the same page
- Rank Math page-level schema: use `WebPage` + `BreadcrumbList` only

---

## uagb/info-box — Feature Cards with Icon

Feature cards with icon, title, and description. Used on homepage for the 3-step process.

```html
<!-- wp:uagb/info-box {"classMigrate":true,"enableMultilineParagraph":true,"headingColor":"","icon":"FONT_AWESOME_ICON_NAME","iconColor":"var(\u002d\u002dast-global-color-0)","headingTag":"p","headFontSize":28,"headFontWeight":"","block_id":"XXX","showCtaIcon":false,"iconLeftMargin":20,"iconRightMargin":20,"iconTopMargin":20,"iconBottomMargin":20,"headTopMargin":10,"blockTopPadding":10,"blockRightPadding":10,"blockLeftPadding":10,"blockBottomPadding":10,"iconView":"Stacked","iconBackgroundColor":"var(\u002d\u002dast-global-color-4)","iconBorderWidth":1,"infoboxBorderStyle":"default","infoboxBorderColor":"var(\u002d\u002dast-global-color-7)"} -->
<div class="wp-block-uagb-info-box uagb-block-XXX uagb-infobox__content-wrap uagb-infobox-icon-above-title uagb-infobox-image-valign-top"><div class="uagb-ifb-content"><div class="uagb-ifb-icon-wrap"><div class="uagb-iconbox-icon-wrap uagb-infobox-shape-circle"><svg xmlns="https://www.w3.org/2000/svg" viewBox="0 0 ..."><path d="..."></path></svg></div></div><div class="uagb-ifb-title-wrap"><p class="uagb-ifb-title">Card Title</p></div><div class="uagb-ifb-desc"><!-- wp:paragraph {"align":"center","fontSize":"medium"} -->
<p class="has-text-align-center has-medium-font-size">Card description text here.</p>
<!-- /wp:paragraph --></div></div></div>
<!-- /wp:uagb/info-box -->
```

**Note:** Info-box requires inline SVG for the icon. If generating programmatically, prefer using `uagb/container` styled as cards (with border, radius, shadow) with standard `wp:paragraph` inside. The visual result is equivalent and doesn't require SVG paths.

**Icons used on the site:** `address-card`, `stamp`, `door-open`, `arrows-to-eye`, `circle-check`, `book-open-reader` (Font Awesome 5/6 names).

---

## Button Patterns

The site uses two button styles consistently.

### Primary Button (teal background, white text)

```html
<!-- wp:button {"backgroundColor":"ast-global-color-0","textColor":"ast-global-color-6","className":"is-style-outline","style":{"border":{"width":"1px","color":"var(\u002d\u002dast-global-color-0)","radius":"10px"},"elements":{"link":{"color":{"text":"var:preset|color|ast-global-color-6"}}},"typography":{"fontStyle":"normal","fontWeight":"100"}},"fontSize":"medium"} -->
<div class="wp-block-button is-style-outline"><a class="wp-block-button__link has-ast-global-color-6-color has-ast-global-color-0-background-color has-text-color has-background has-link-color has-border-color has-medium-font-size has-custom-font-size wp-element-button" href="https://app.archivofinal.com" style="border-color:var(--ast-global-color-0);border-width:1px;border-radius:10px;font-style:normal;font-weight:100">Button Text</a></div>
<!-- /wp:button -->
```

### Secondary Button (light background, dark text)

```html
<!-- wp:button {"backgroundColor":"ast-global-color-4","textColor":"ast-global-color-2","className":"is-style-fill","style":{"border":{"radius":"10px","width":"1px"},"elements":{"link":{"color":{"text":"var:preset|color|ast-global-color-2"}}},"typography":{"fontStyle":"normal","fontWeight":"100"}},"fontSize":"medium","borderColor":"cyan-bluish-gray"} -->
<div class="wp-block-button is-style-fill"><a class="wp-block-button__link has-ast-global-color-2-color has-ast-global-color-4-background-color has-text-color has-background has-link-color has-border-color has-cyan-bluish-gray-border-color has-medium-font-size has-custom-font-size wp-element-button" href="/contacto/" style="border-width:1px;border-radius:10px;font-style:normal;font-weight:100">Button Text</a></div>
<!-- /wp:button -->
```

### Button Container

Buttons are always wrapped in a `uagb/container` with `directionDesktop: "row"` and `childrenWidthDesktop: "auto"`, then a `wp:buttons` group:

```html
<!-- wp:uagb/container {"block_id":"XXX","directionDesktop":"row","topPaddingDesktop":22,"bottomPaddingDesktop":22,"paddingLink":false,"childrenWidthDesktop":"auto"} -->
<div class="wp-block-uagb-container uagb-block-XXX">
<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center","orientation":"horizontal"}} -->
<div class="wp-block-buttons">

[PRIMARY BUTTON]
[SECONDARY BUTTON]

</div>
<!-- /wp:buttons -->
</div>
<!-- /wp:uagb/container -->
```

---

## Page Structure Pattern

Every page follows this high-level structure:

```
ROOT CONTAINER (hero section)
  ├── heading / advanced-heading
  ├── paragraph (intro)
  └── buttons container

ROOT CONTAINER (features / content section)
  ├── advanced-heading
  └── inner row container
      ├── info-box / card container
      ├── info-box / card container
      └── info-box / card container

ROOT CONTAINER (content section - repeats)
  ├── advanced-heading
  └── content blocks (paragraphs, lists, faq, etc.)

ROOT CONTAINER (CTA section — background color-5)
  ├── heading (centered)
  ├── paragraph (centered)
  └── buttons container
```

Sections alternate backgrounds:
- No background (default)
- `ast-global-color-5` (light gray)
- `ast-global-color-4` (off-white)

---

## Block ID Generation

Every Spectra block requires a unique `block_id` attribute (8-character lowercase hex string).

**Examples from live site:** `999315b8`, `0bf1dfd0`, `46fbb097`, `ad599ae3`

**Generator tool:** `tools/generate_faq_page.py` includes a `bid()` function that generates deterministic unique IDs using MD5 hashing. This can be reused for other page generators.

---

## Programmatic Page Creation

### Tools

| Tool | File | Purpose |
|------|------|---------|
| **WP Publisher** | `tools/wp_publisher.py` | Publish/update posts and pages via REST API |
| **Image Generator** | `tools/image_generator.py` | Generate featured images via Gemini |
| **FAQ Page Generator** | `tools/generate_faq_page.py` | Generate FAQ pages with Spectra blocks |

### Publishing a Page

```bash
# Publish Spectra block content as WordPress page (draft)
tools/.venv/bin/python tools/wp_publisher.py publish \
  --file content.html \
  --title "Page Title" \
  --type page \
  --slug page-slug \
  --raw \
  --status draft \
  --seo-title "SEO Title | Archivo Final" \
  --seo-description "Meta description here." \
  --focus-keyword "focus keyword" \
  --featured-image outputs/featured_image.jpg
```

**Key flags:**
- `--type page` — Creates a WordPress page (not post)
- `--raw` — Skips markdown-to-HTML conversion (sends content as-is)
- `--slug` — Sets the URL slug

### Updating a Page

```bash
tools/.venv/bin/python tools/wp_publisher.py update \
  --post-id 3161 \
  --file updated-content.html \
  --status draft
```

---

## JSON Escaping Cheatsheet

Within block comment JSON attributes (`<!-- wp:block {"key":"value"} -->`):

| Raw | Escaped | Why |
|-----|---------|-----|
| `--` | `\u002d\u002d` | Prevents `-->` closing the HTML comment |
| `<` | `\u003c` | Prevents HTML parsing issues |
| `>` | `\u003e` | Prevents HTML parsing issues |
| `"` | `\u0022` | Prevents breaking JSON string delimiters (inside nested HTML) |

These are standard JSON unicode escapes. WordPress's block parser interprets them correctly.

---

## Retrieving Raw Block Content (for reference)

To inspect the exact block structure of any page:

```bash
cd tools && .venv/bin/python -c "
import requests
from config import WP_API_URL, get_wp_auth
auth = get_wp_auth()
resp = requests.get(f'{WP_API_URL}/pages/PAGE_ID', params={'context': 'edit'}, auth=auth, timeout=15)
resp.raise_for_status()
print(resp.json()['content']['raw'][:5000])
"
```

Replace `PAGE_ID` with the numeric ID. Use `context=edit` to get the raw Gutenberg block markup (not rendered HTML).
