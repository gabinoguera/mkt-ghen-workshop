# Marketing & SEO Agent Pipeline Workspace

Un workspace listo para usar con Claude Code (y GitHub Copilot) que implementa un **pipeline multi-agente de marketing, SEO e implementación WordPress**. Diseñado para ser adaptado a cualquier blog o proyecto de contenido.

Basado en la metodología del workshop **"Pipelines de Agentes IA para Marketing y SEO"**.

---

## Qué incluye

- **4 agentes especializados** con roles definidos: SEO estratégico, SEO técnico, copywriter y publicador WordPress
- **2 skills invocables** (`/seo`, `/copywriting`) con bases de conocimiento adjuntas
- **5 herramientas CLI Python** para WordPress REST API, análisis SERP, QA de contenido y generación de imágenes con Gemini
- **MCPs preconfigurados** para Google Search Console, Google Analytics 4, Playwright, GitHub y más
- **Plantilla de sesión** para coordinar el trabajo entre agentes en cada feature
- **Referencias SEO**: Holistic SEO, GEO, Core Web Vitals, autoridad topical, multilingüe

---

## Prerrequisitos

| Herramienta | Para qué |
|-------------|---------|
| [Claude Code](https://claude.ai/code) | CLI principal — agentes y skills |
| [GitHub Copilot](https://github.com/features/copilot) | Alternativa/complemento en VS Code |
| Python 3.11+ | Herramientas CLI (`tools/`) |
| WordPress + Rank Math | Sitio de destino para publicación |
| Spectra plugin (free) | Schema blocks (FAQPage, HowTo) |
| Google Cloud account | GSC + GA4 MCPs |
| Gemini API key | Generación de imágenes destacadas |

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/gabinoguera/mkt-ghen-workshop.git
cd mkt-ghen-workshop
```

### 2. Configurar credenciales

```bash
cp .env.example .env
# Edita .env con tus datos de WordPress y Gemini
```

Crea una **Application Password** en WordPress:
`WP Admin → Users → Profile → Application Passwords → Add New`

### 3. Instalar dependencias Python

```bash
cd tools && ./setup.sh
```

Esto crea un virtualenv en `tools/.venv/` e instala todas las dependencias.

### 4. Configurar MCPs

Edita `.mcp.json` y reemplaza todos los placeholders `<YOUR_*>`:

```json
// GitHub
"GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_GITHUB_TOKEN>"

// Opik (observabilidad LLM) — opcional
"--apiKey", "<YOUR_OPIK_API_KEY>"

// Google Analytics 4
"GOOGLE_PROJECT_ID": "<YOUR_GCP_PROJECT_ID>",
"GA_PROPERTY_ID": "<YOUR_GA4_PROPERTY_ID>"

// Google Search Console — coloca tu client_secrets.json en la raíz
"GSC_OAUTH_CLIENT_SECRETS_FILE": "./your_client_secrets.json"
```

Para GA4/GSC, autentica con Google Cloud:
```bash
gcloud auth application-default login \
  --scopes="openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/analytics.readonly"
```

### 5. Snippet PHP en WordPress (para Rank Math via API)

Añade esto al `functions.php` de tu Child Theme:

```php
add_action('init', function () {
    $fields = ['rank_math_title', 'rank_math_description',
               'rank_math_focus_keyword', 'rank_math_canonical_url'];
    foreach ($fields as $field) {
        register_post_meta('post', $field, [
            'show_in_rest'  => true,
            'single'        => true,
            'type'          => 'string',
            'auth_callback' => function () { return current_user_can('edit_posts'); },
        ]);
    }
});
```

Sin este snippet los posts se publican correctamente, pero sin los meta SEO de Rank Math.

### 6. Adaptar CLAUDE.md a tu proyecto

Este es el paso más importante. Abre `CLAUDE.md` y rellena todos los placeholders `[YOUR_*]`:

- `[YOUR_BRAND]` — nombre de tu blog/proyecto
- `[YOUR_SITE_URL]` — URL de tu WordPress
- `[YOUR_NAME]` — tu nombre (cómo quieres que te llamen los agentes)
- `[YOUR_VERTICALS]` — temas principales de tu blog
- `[YOUR_LANGUAGE]` — idioma del contenido
- `[YOUR_CORE_ENTITY]` — entidad semántica central de tu dominio
- Estructura del sitio, categorías WP, audiencias, diferenciadores

> Un `CLAUDE.md` bien configurado es lo que hace que los agentes generen contenido relevante para tu proyecto específico, no genérico.

---

## Cómo usar el pipeline

### Iniciar una feature (artículo, landing, auditoría...)

1. Crea el documento de sesión a partir de la plantilla:
   ```bash
   cp .claude/sessions/TEMPLATE.md .claude/sessions/mi-articulo.md
   ```

2. Rellena el título y contexto inicial en la sesión

3. Invoca el primer agente en Claude Code:
   ```
   @seo-strategist Analiza la competencia y crea el brief para el artículo sobre [TOPIC]. Lee primero .claude/sessions/mi-articulo.md
   ```

4. Sigue el pipeline de agentes:
   ```
   @seo-strategist → @marketing-copywriter → qa_checker.py → @wp-implementer → @seo-tecnico
   ```

### Skills invocables

```
/seo         → Estrategia SEO, topical maps, content briefs, auditoría GEO
/copywriting → Copy de páginas, landings, artículos técnicos
/seo-tecnico → Auditoría técnica: indexación, CWV, schema, canonicals
/publish     → Publicación WordPress, imagen destacada, Rank Math meta
```

### Herramientas CLI

```bash
# Publicar un post en WordPress
python tools/wp_publisher.py --file content.md --status draft

# Analizar las SERPs de una keyword
python tools/serp_analyzer.py --query "tu keyword" --lang es

# QA de contenido antes de publicar
python tools/qa_checker.py --file content.md

# Generar imagen destacada con Gemini
python tools/image_generator.py --prompt "descripción de la imagen"
```

---

## Estructura de agentes

```
@seo-strategist       → Topical maps, content briefs, análisis competencia, GEO
@marketing-copywriter → Artículos, landings, copy técnico en tu idioma
@wp-implementer       → Publica en WP via API, gestiona schema, sube imágenes
@seo-tecnico          → Auditoría técnica: indexación, CWV, schema, canonicals
```

El flujo estándar:

```
backlog → strategy → copy → qa-review → implementation → tecnico-review → done
```

---

## Estructura de directorios

```
.
├── .claude/
│   ├── agents/           # Definiciones de los 4 agentes
│   ├── skills/           # Skills /seo y /copywriting con referencias
│   ├── sessions/         # Sesiones activas + TEMPLATE.md
│   └── doc/              # Deliverables por feature
│       └── wordpress-reference/
├── tools/                # CLI Python
├── competitive-analysis/ # Research de competencia
├── content-briefs/       # Briefs de contenido
├── topical-maps/         # Mapas topicales
├── site-audit/           # Auditorías del sitio
├── outputs/              # Imágenes generadas (gitignored)
├── .env.example          # Template de credenciales
├── .mcp.json             # Configuración de MCP servers
├── CLAUDE.md             # Contexto del proyecto para los agentes
├── README.md             # Este archivo
└── WORKSHOP.md           # Guía del workshop
```

---

## Recursos adicionales

- **Metodología SEO:** `.claude/skills/seo/references/` — Holistic SEO, GEO, Core Web Vitals, autoridad topical
- **Copywriting:** `.claude/skills/copywriting/references/` — frameworks de copy, transiciones
- **WordPress:** `.claude/doc/wordpress-reference/` — Spectra block patterns, schema snippets
- **Pipeline GEO:** `.claude/skills/seo/references/geo-audit-pipeline.md`

---

## Contribuciones y adaptaciones

Este workspace es un punto de partida. Cada proyecto requerirá:
- Adaptar los agentes a las herramientas y CMS de tu stack
- Añadir referencias específicas de tu dominio en `.claude/skills/*/references/`
- Crear nuevos agentes para roles específicos de tu equipo
- Extender los tools Python para integraciones adicionales
