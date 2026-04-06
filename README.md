# Marketing & SEO Agent Pipeline Workspace

Un workspace listo para usar con Claude Code (y GitHub Copilot) que implementa un **pipeline multi-agente de marketing, SEO e implementación WordPress**. Diseñado para ser adaptado a cualquier blog o proyecto de contenido.

Basado en la metodología del workshop **"Pipelines de Agentes IA para Marketing y SEO"**.

---

## Qué incluye

- **5 agentes especializados** con roles definidos: SEO estratégico, SEO técnico, copywriter, publicador WordPress y generador HTML estático
- **3 skills invocables** (`/seo`, `/copywriting`, `/seo-tecnico`) con bases de conocimiento adjuntas
- **6 herramientas CLI Python** para WordPress REST API, análisis SERP, QA de contenido, generación de imágenes, FAQs y generación HTML
- **7 MCPs preconfigurados**: Google Search Console, Google Analytics 4, Playwright, GitHub, context7, drawio, sequentialthinking
- **Plantilla de sesión** para coordinar el trabajo entre agentes en cada feature
- **Referencias SEO y calidad web**: Holistic SEO, GEO, Core Web Vitals (Lighthouse), autoridad topical, performance, accesibilidad
- **Doble output**: Publicación en WordPress O generación de HTML estático local

---

## Prerrequisitos

| Herramienta | Para qué |
|-------------|---------|
| [Claude Code](https://claude.ai/code) | CLI principal — agentes y skills |
| [GitHub Copilot](https://github.com/features/copilot) | Alternativa/complemento en VS Code |
| Python 3.11+ | Herramientas CLI (`tools/`) |
| WordPress + Rank Math | (Opcional) Sitio de destino para publicación con `@wp-implementer` |
| Spectra plugin (free) | (Opcional) Schema blocks (FAQPage, HowTo) para WordPress |
| Google Cloud account | (Opcional) GSC + GA4 MCPs para auditorías avanzadas |
| Gemini API key | Generación de imágenes destacadas |

**Nota:** Puedes usar el pipeline completo sin WordPress si prefieres generar HTML local con `@html-implementer`.

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
   @seo-strategist → @marketing-copywriter → qa_checker.py → 
   [@wp-implementer O @html-implementer] → @seo-tecnico
   ```
   
5. Cuando llegues a implementación, decide:
   - **¿Quieres publicar en WordPress?** → invoca `@wp-implementer`
   - **¿Prefieres HTML local?** → invoca `@html-implementer`

### Skills invocables

```
/seo         → Estrategia SEO, topical maps, content briefs, auditoría GEO
/copywriting → Copy de páginas, landings, artículos técnicos
/seo-tecnico → Auditoría técnica: indexación, CWV, schema, canonicals, performance
```

> `@wp-implementer` y `@html-implementer` se invocan directamente como agentes en el pipeline — no necesitan skills standalone.

### Herramientas CLI

```bash
# Publicar un post en WordPress
python tools/wp_publisher.py publish --file content.md --status draft

# Generar HTML estático local
python tools/local_generator.py generate --file content.md --feature-name mi-articulo

# Analizar las SERPs de una keyword
python tools/serp_analyzer.py --query "tu keyword" --lang es

# QA de contenido antes de publicar
python tools/qa_checker.py check --file content.md

# Generar imagen destacada con Gemini
python tools/image_generator.py generate --prompt "descripción de la imagen"
```

---

## Estructura de agentes

```
@seo-strategist       → Topical maps, content briefs, análisis competencia, GEO
@marketing-copywriter → Artículos, landings, copy técnico en tu idioma
@wp-implementer       → Publica en WP via API, gestiona schema, sube imágenes
@html-implementer     → Genera HTML estático local con schema embebido
@seo-tecnico          → Auditoría técnica: indexación, CWV, schema, canonicals
```

El flujo estándar con **decisión de implementación**:

```
backlog → strategy → copy → qa-review → [WordPress O HTML local?] → implementation → tecnico-review → done
                                                ↓                         ↓
                                        @wp-implementer          @html-implementer
```

**¿Cuándo usar cada uno?**
- **@wp-implementer** → Si tienes WordPress configurado y quieres publicar directamente
- **@html-implementer** → Si quieres archivos HTML locales para subir manualmente, usar en hosting estático, o trabajar sin WordPress

---

## Estructura de directorios

```
.
├── .claude/
│   ├── agents/               # Definiciones de los 5 agentes
│   ├── skills/
│   │   ├── seo/              # /seo — Holistic SEO, GEO, autoridad topical
│   │   ├── copywriting/      # /copywriting — frameworks de copy
│   │   └── seo-tecnico/      # /seo-tecnico — Lighthouse, CWV, performance, a11y
│   │       └── references/   # 6 skill files de addyosmani/web-quality-skills (MIT)
│   ├── sessions/             # Sesiones activas + TEMPLATE.md
│   └── doc/
│       └── wordpress-reference/  # Spectra block patterns, schema snippets
├── tools/                    # CLI Python
│   └── outputs/
│       └── html/             # HTML generado por @html-implementer
├── competitive-analysis/     # Research de competencia
├── content-briefs/           # Briefs de contenido
├── topical-maps/             # Mapas topicales
├── site-audit/               # Auditorías del sitio
├── .env.example              # Template de credenciales
├── .mcp.json                 # Configuración de 7 MCP servers
├── CLAUDE.md                 # Contexto del proyecto para los agentes
├── README.md                 # Este archivo
└── WORKSHOP.md               # Guía pedagógica del taller
```

---

## Recursos adicionales

- **Metodología SEO:** `.claude/skills/seo/references/` — Holistic SEO, GEO, autoridad topical, multilingüe, pipeline GEO completo
- **Calidad web (Lighthouse):** `.claude/skills/seo-tecnico/references/` — Core Web Vitals, performance, accesibilidad, best practices, auditoría completa (fuente: [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills), MIT)
- **Copywriting:** `.claude/skills/copywriting/references/` — frameworks de copy, transiciones naturales
- **WordPress:** `.claude/doc/wordpress-reference/` — Spectra block patterns, schema snippets

---

## Contribuciones y adaptaciones

Este workspace es un punto de partida. Cada proyecto requerirá:
- Adaptar los agentes a las herramientas y CMS de tu stack
- Añadir referencias específicas de tu dominio en `.claude/skills/*/references/`
- Crear nuevos agentes para roles específicos de tu equipo
- Extender los tools Python para integraciones adicionales
