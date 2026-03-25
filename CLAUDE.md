# CLAUDE.md — [YOUR_BRAND] SEO & Content Workspace

<!-- TODO: Rename this file header with your brand/project name -->

## Project Overview

**[YOUR_BRAND]** — Workspace dedicado a la estrategia SEO, GEO y publicación de contenido para [YOUR_BLOG_URL].

- **Sitio objetivo:** [YOUR_SITE_URL] (WordPress, [YOUR_THEME] + Gutenberg + Rank Math)
- **Autor:** [YOUR_NAME]
- **SEO Plugin:** Rank Math  <!-- TODO: Adapt if using Yoast or other -->
- **Idioma principal:** [YOUR_LANGUAGE]  <!-- e.g. Español (España), English (US) -->
- **Objetivo:** [YOUR_BUSINESS_GOAL]  <!-- e.g. Visibilidad profesional, captación de leads -->

## Qué es [YOUR_BRAND]

<!-- TODO: Describe tu blog/proyecto. Ejemplo de referencia: -->
<!-- GHEN Digital es el blog personal de Gabriel Noguera, desarrollador especialista en IA aplicada. -->

[YOUR_BLOG_DESCRIPTION]

Las verticales del blog son:

<!-- TODO: Lista las verticales temáticas de tu blog -->
- **[VERTICAL_1]** — [Descripción breve]
- **[VERTICAL_2]** — [Descripción breve]
- **[VERTICAL_3]** — [Descripción breve]

### Secciones estratégicas principales

<!-- TODO: Define las secciones editoriales clave (p.ej. Actualidad, Lab, Tutoriales) -->

1. **[SECTION_1]** (`/[slug]/`) — [Tipo de contenido y propósito]
2. **[SECTION_2]** (`/[slug]/`) — [Tipo de contenido y propósito]

### Perfil del autor

<!-- TODO: Rellena con tu perfil profesional. Cuanto más específico, mejor contexto tendrán los agentes. -->

- [YOUR_ROLE] — [Tu especialización principal]
- [YOUR_CREDENTIAL_1]  <!-- e.g. Docente en X, Fundador de Y -->
- [YOUR_CREDENTIAL_2]
- **Expertise:** [YOUR_EXPERTISE_KEYWORDS]

**Objetivo del blog:** [YOUR_BLOG_GOAL]

### Estructura del sitio

<!-- TODO: Adapta la tabla con las URLs reales de tu WordPress -->

| Sección | URL | Propósito |
|---------|-----|-----------|
| Home | [YOUR_SITE_URL] | Feed — últimas publicaciones |
| [SECTION_1] | /[slug]/ | [Propósito] |
| [SECTION_2] | /[slug]/ | [Propósito] |
| About | /about/ | Perfil profesional |
| Contacto | /contacto/ | Captación de leads |

### Categorías WordPress

<!-- TODO: Lista las categorías exactas tal como aparecen en tu WordPress -->

`[CATEGORY_1]`, `[CATEGORY_2]`, `[CATEGORY_3]`

## Stack Técnico WordPress

| Componente | Herramienta | Función |
|------------|-------------|---------|
| CMS | WordPress | Gestión de contenido |
| Tema | [YOUR_THEME]  | Diseño base |
| Editor | Gutenberg (nativo) | Bloques de contenido |
| SEO | Rank Math | Meta tags, schema page-level, sitemaps |
| Schema blocks | Spectra (free) | FAQPage, HowTo (block-level) — blocks `wp:uagb/faq`, `wp:uagb/how-to` |
| Cookies/GDPR | Plugin activo | Consentimiento |

> **Recomendación Spectra:** Instalar Spectra (free) para habilitar FAQ, How-To y Review schema blocks. Es 100% compatible con Astra y Gutenberg. Mejora significativamente la capacidad de schema markup y el layout de páginas.

### Schema Markup Strategy

- **Rank Math:** Schema page-level (Article, BlogPosting, WebPage, Organization, BreadcrumbList)
- **Spectra:** Schema block-level (FAQPage, HowTo, Review)
- No duplicar tipos entre ambos plugins

### WordPress REST API

Publicación programática via `tools/wp_publisher.py`:
- WordPress Application Passwords para autenticación (`WORDPRESS_APP_CREDENTIALS` en `.env`)
- `POST /wp-json/wp/v2/posts` para crear/actualizar posts
- `register_post_meta` snippet en Astra Child `functions.php` para escribir Rank Math SEO meta fields via API
- Imágenes destacadas generadas con Gemini via `tools/image_generator.py`

### MCPs de Analítica, SEO e Indexación

<!-- TODO: Actualiza con tus credenciales reales tras configurar .mcp.json -->

| MCP | Herramienta | Identificador operativo |
|-----|-------------|------------------------|
| `mcp__gsc__*` | Google Search Console | `site_url: "sc-domain:[YOUR_DOMAIN]"` |
| `mcp__google-analytics__*` | Google Analytics 4 | `property_id: "<YOUR_GA4_PROPERTY_ID>"` ← ID numérico |
| `mcp__playwright__*` | Playwright Browser | Tests de citación en ChatGPT / Perplexity / Claude.ai |

**Credenciales GA4/GSC:** `~/.config/gcloud/application_default_credentials.json`
Scope necesario: `analytics.readonly` + `cloud-platform`. Si expiran:
```bash
gcloud auth application-default login \
  --scopes="openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/analytics.readonly"
```

**IndexNow:** Plugin recomendado en WordPress. Submit automático en cada publish/update. Alimenta Bing → ChatGPT Search + Bing Copilot en minutos.

**Pipeline GEO completo con MCPs:** `.claude/skills/seo/references/geo-audit-pipeline.md`

> **Snippet necesario en `functions.php` del Child theme** (añadir al child, NO al padre):
> ```php
> add_action('init', function () {
>     $fields = ['rank_math_title', 'rank_math_description',
>                'rank_math_focus_keyword', 'rank_math_canonical_url'];
>     foreach ($fields as $field) {
>         register_post_meta('post', $field, [
>             'show_in_rest'  => true,
>             'single'        => true,
>             'type'          => 'string',
>             'auth_callback' => function () { return current_user_can('edit_posts'); },
>         ]);
>     }
> });
> ```
> Sin este snippet los posts se publican igualmente, pero sin meta SEO de Rank Math via API.

## Knowledge Domain

<!-- TODO: Define el dominio temático de tu blog. Esto guía a los agentes en la creación de contenido. -->

**Vertical principal:** [YOUR_MAIN_VERTICAL]

### Entidad Central

**"[YOUR_CORE_ENTITY]"** — [Descripción de la entidad central de tu blog]

### Entidades Conectadas

<!-- TODO: Construye el grafo semántico de tu dominio -->

```
[YOUR_CORE_ENTITY]
├── [SUB_ENTITY_1]
│   ├── [TOPIC_1_1]
│   └── [TOPIC_1_2]
├── [SUB_ENTITY_2]
│   ├── [TOPIC_2_1]
│   └── [TOPIC_2_2]
└── [SUB_ENTITY_3]
```

### Audiencias objetivo

<!-- TODO: Define tus 3-4 audiencias con sus necesidades específicas -->

- **[AUDIENCE_1]:** [Qué buscan en tu blog]
- **[AUDIENCE_2]:** [Qué buscan en tu blog]
- **[AUDIENCE_3]:** [Qué buscan en tu blog]

### Diferenciadores de [YOUR_NAME] / [YOUR_BRAND]

<!-- TODO: ¿Por qué alguien debería leer tu blog en lugar de otro? -->

- [DIFFERENTIATOR_1]
- [DIFFERENTIATOR_2]
- [DIFFERENTIATOR_3]

## Metodología SEO

Basada en **Holistic SEO** de Koray Tugberk GUBUR (holisticseo.digital).

### Principios Fundamentales

1. **"Rank topics, not keywords"** — Temas completos, no keywords aisladas
2. **"Cost of Retrieval defines the future of SEO"** — Facilitar extracción de información
3. **"A website is not a set of pages; it is a network of meaning"** — Redes semánticas
4. **Topical Authority = Topical Coverage + Historical Data**
5. **SEO + GEO al mismo nivel** — Optimizar para buscadores Y para respuestas de IA generativa
6. **Consistencia > volumen** en publicación de contenido
7. **Information Gain** — Cada pieza debe aportar valor único vs. lo existente

### Tipos de contenido por sección

<!-- TODO: Adapta la tabla con tus secciones y formatos -->

| Sección | Tipo | Formato | Longitud |
|---------|------|---------|----------|
| [SECTION_1] | [Tipo] | [Formato] | [Longitud] palabras |
| [SECTION_2] | [Tipo] | [Formato] | [Longitud] palabras |

## Directorios del Workspace

```
[YOUR_WORKSPACE_NAME]/
├── .claude/
│   ├── agents/           # seo-strategist, marketing-copywriter, wp-implementer, seo-tecnico
│   ├── skills/seo/       # Skill SEO invocable + references
│   ├── skills/copywriting/ # Skill copywriting + references
│   ├── sessions/         # Sesión compartida por feature (TEMPLATE.md)
│   └── doc/              # Output de planes por feature
│       └── wordpress-reference/  # Spectra block patterns, referencias WP
├── tools/                # CLI tools Python
│   ├── wp_publisher.py   # Publicación WordPress REST API
│   ├── serp_analyzer.py  # Scraping + métricas SEO
│   ├── qa_checker.py     # QA mecánico de contenido
│   ├── image_generator.py# Generación de imágenes (Gemini)
│   ├── config.py         # Config compartida (.env)
│   └── setup.sh          # Bootstrap venv + dependencias
├── outputs/              # Imágenes generadas (gitignored)
├── site-audit/           # Auditorías SEO del sitio
├── topical-maps/         # Mapas topicales generados
├── content-briefs/       # Briefs de contenido semántico
├── competitive-analysis/ # Análisis competitivo
├── CLAUDE.md             # Este archivo
└── README.md             # Guía humana del workspace
```

## Agentes

| Agente | Skill invocable | Expertise |
|--------|-----------------|-----------|
| seo-strategist | `/seo` | Estrategia SEO/GEO, topical maps, content architecture, semantic audit |
| seo-tecnico | `/seo-tecnico` | Auditoría técnica SEO: crawlability, indexación, CWV, schema validation, canonicals, mobile |
| marketing-copywriter | `/copywriting` | Copy técnico en [YOUR_LANGUAGE] para [YOUR_SITE_URL], voz de experto accesible |
| wp-implementer | `/publish` | Implementación técnica WordPress, Rank Math, schema, publicación via API |

### Workflow

```
@seo-strategist → investiga, analiza, genera planes/topical maps/briefs
        ↓                          usa: serp_analyzer.py
        ↓                          rellena: "Decisiones estratégicas"
        ↓                          estado: backlog → strategy → copy
        ↓          ← puede delegar issues técnicos a @seo-tecnico (cross-consult)
@marketing-copywriter → escribe copy + prompt de imagen destacada
        ↓                          rellena: "Decisiones de copy"
        ↓                          estado: copy → qa-review
        ↓
[QA] qa_checker.py → validación mecánica antes de publicar
        ↓                          verifica: densidad keyword, headings, estilo, longitud
        ↓                          QA score anotado en sesión → estado: qa-review → implementation
@wp-implementer → genera imagen + publica en WordPress
        ↓                          usa: image_generator.py, wp_publisher.py
        ↓                          rellena: "Implementación"
        ↓                          estado: implementation → tecnico-review
@seo-tecnico → valida salud técnica de la página publicada
                                   usa: mcp__gsc__*, mcp__playwright__*, mcp__google-analytics__*
                                   rellena: "Diagnóstico técnico SEO"
                                   estado: tecnico-review → done (o → implementation si hay fixes)
```

**Modo standalone** (auditoría periódica, sin feature):
```
@seo-tecnico → audita el sitio completo o una sección
                                   estado: backlog → tecnico-review → done
```

### Sesión compartida

Cada feature tiene un único documento de sesión en `.claude/sessions/{feature}.md` (creado desde `TEMPLATE.md`). Es el canal de comunicación entre agentes:

- **Cada agente lee TODO el documento** antes de empezar (contexto completo)
- **Cada agente rellena SU sección** al terminar y avanza el Estado
- Los deliverables detallados siguen en `.claude/doc/{feature}/`
- La sesión es el resumen ejecutivo — lo mínimo para que el siguiente agente arranque con contexto

## Convenciones

- **Idioma de archivos:** [YOUR_LANGUAGE] para contenido, inglés para nombres de archivo/código
- **Formato topical maps:** Tablas markdown + diagramas mermaid
- **Commits:** `feat(scope): description` (conventional commits)
- **No crear .md en la raíz** excepto CLAUDE.md y README.md
- **Address me as "[YOUR_NAME]"**
