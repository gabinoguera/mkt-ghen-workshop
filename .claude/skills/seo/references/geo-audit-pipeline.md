# Pipeline GEO: Auditoría, Optimización y Medición con MCPs

**Basado en:** sesión gsc-seo-audit (2026-03-12), datos reales [YOUR_SITE_URL]
**MCPs requeridos:** `mcp__gsc__*`, `mcp__google-analytics__*`, `mcp__playwright__*`

---

## El ciclo completo

```
DETECTAR            DIAGNOSTICAR         ACTUAR              MEDIR
GSC + GA4 MCPs  →  Señales de AI    →  Reescritura     →  Playwright + GSC
                   Overview            GEO-first           (2-6 semanas)
```

---

## FASE 1 — Detectar señales de AI Overview en GSC + GA4

### Extracción de datos (90 días)

```
# Overview general
mcp__gsc__get_performance_overview(site_url="sc-domain:[YOUR_DOMAIN]", days=90)

# Top queries con CTR
mcp__gsc__get_search_analytics(site_url="sc-domain:[YOUR_DOMAIN]", days=90,
    dimensions="query", limit=100)

# Top páginas
mcp__gsc__get_search_analytics(site_url="sc-domain:[YOUR_DOMAIN]", days=90,
    dimensions="page", limit=50)

# Comparativa periodos
mcp__gsc__compare_search_periods(site_url="sc-domain:[YOUR_DOMAIN]",
    period1_start="YYYY-MM-DD", period1_end="YYYY-MM-DD",
    period2_start="YYYY-MM-DD", period2_end="YYYY-MM-DD",
    dimensions="page")

# Sesiones + engagement por página (GA4)
mcp__google-analytics__run_report(
    property_id="<YOUR_GA4_PROPERTY_ID>",
    date_ranges=[{"start_date": "90daysAgo", "end_date": "yesterday"}],
    dimensions=["pagePath"],
    metrics=["sessions", "engagedSessions", "bounceRate",
             "averageSessionDuration", "screenPageViews"],
    dimension_filter={"filter": {"field_name": "sessionDefaultChannelGroup",
        "string_filter": {"match_type": "EXACT", "value": "Organic Search"}}},
    order_bys=[{"metric": {"metric_name": "sessions"}, "desc": true}],
    limit=50
)
```

### Señales de alerta GEO (fórmulas de detección)

```
SEÑAL 1 — AI Overview activo (CTR anomalía):
  GSC: impresiones > 500 AND CTR < 0.5% AND posición < 10
  → La IA responde la pregunta antes del clic

SEÑAL 2 — Contenido sin valor añadido post-clic:
  GA4: averageSessionDuration < 60s en páginas con señal 1
  → El usuario que sí hace clic no encuentra nada nuevo

SEÑAL 3 — Queries definitivas sin citación:
  GSC: queries "qué es X" o "cómo funciona X" con 200+ imp y CTR < 0.3%
  → AI Overview para queries informacionales directas

QUICK WIN oculto — Excelente contenido, mala posición:
  GA4: bounceRate < 20% AND averageSessionDuration > 120s
  GSC: posición > 15
  → Artículo que engancha pero le falta autoridad/links
```

---

## FASE 2 — Diagnosticar y priorizar

### Tabla cruzada GSC + GA4

Construir por página:

| Página | GSC Clics | GSC Imp | CTR | Pos | GA4 Sesiones | Bounce | Avg Time | Diagnóstico |
|--------|-----------|---------|-----|-----|--------------|--------|----------|-------------|
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Matriz de priorización

```
MÁXIMA PRIORIDAD (impacto × esfuerzo):
  - CTR < 0.5% + impresiones > 1000 → reformulación completa
  - Bounce < 20% + posición > 15   → link building interno urgente
  - Avg time < 60s + CTR > 1%      → reescritura de contenido

ALTA PRIORIDAD:
  - Posición 11-20 + impresiones > 200 → quick win SEO clásico
  - CTR < 1% + posición 5-10          → mejora de snippet

MEDIA PRIORIDAD:
  - Posición 5-10 + CTR aceptable      → añadir FAQ schema
  - Artículos sin internal links       → link building plan
```

---

## FASE 3 — Actuar: reescritura GEO-first

### Checklist antes de publicar

- [ ] Respuesta directa en las primeras 2 frases (Initial Contact Section fuerte)
- [ ] Definición en formato "X es Y que Z" en la primera aparición del concepto
- [ ] Al menos una tabla EAV (Entidad | Atributo | Valor)
- [ ] Datos propios o experiencia no replicable (Information Gain)
- [ ] H2s que responden queries independientes
- [ ] FAQ schema al final (mínimo 4 preguntas)
- [ ] Schema Article con autor y fechas en Rank Math
- [ ] Internal links a artículos del cluster (mínimo 2)

### Patrón de sección GEO-optimizada

```
[H2: La pregunta escrita como la buscaría alguien]

[Respuesta directa en 1-2 frases — esto es lo que citará la IA]

[Desarrollo y contexto para el lector humano]

[Datos / código / evidencia — Information Gain]

[Link interno contextual al cluster]
```

---

## FASE 4 — Publicar con IndexNow

**Plugin:** IndexNow activo en [YOUR_SITE_URL] (auto-submit en cada publish/update)

**Submit manual** (para artículos actualizados sin re-publicar):
WP Admin → IndexNow Plugin → Manual URL Submission

**Por qué importa para GEO:**
- Google tarda días en re-rastrear contenido actualizado
- Bing procesa IndexNow en minutos
- Bing alimenta: ChatGPT Search + Bing Copilot
- Resultado: contenido nuevo en corpus de ChatGPT en minutos, no días

---

## FASE 5 — Medir citación con Playwright MCP

### Tests de citación en LLMs (ejecutar 48-72h post-publicación)

```python
# Ejemplo de queries a testear para cada artículo publicado
queries_to_test = [
    "qué es GEO en SEO",
    "generative engine optimization español",
    "cómo optimizar para ai overviews",
    "geo seo diferencias",
]

# Plataformas a testear
platforms = [
    "https://chatgpt.com",      # ChatGPT Search
    "https://www.perplexity.ai", # Perplexity
    "https://claude.ai",         # Claude.ai
]
```

Con Playwright MCP:
1. Navegar a la plataforma
2. Hacer la query
3. Capturar la respuesta (screenshot o texto)
4. Verificar si [YOUR_SITE_URL] aparece citado
5. Registrar: ¿citado? ¿con qué fragmento? ¿en qué posición?

### Señales indirectas en GSC (2-6 semanas post-publicación)

```
MEJORA CONFIRMADA:
  - CTR sube > 0.5% en queries que tenían AI Overview  → el snippet ya compite
  - Nuevas queries long-tail relacionadas               → LLM usa el contenido
  - Impresiones suben sin cambio de posición           → más AI Overviews citando

PROBLEMA PERSISTENTE:
  - CTR sigue < 0.3% con posición estable              → AI Overview no citable todavía
  - Avg time sigue bajo post-reescritura               → mismatch de intención
```

---

## Configuración MCPs (referencia rápida)

### GSC MCP
```
site_url: "sc-domain:[YOUR_DOMAIN]"
Estado: operativo
Autenticación: OAuth via your_client_secrets.json
```

### GA4 MCP
```
property_id: "<YOUR_GA4_PROPERTY_ID>"   ← ID numérico (NO el Measurement ID G-6B1KRTNV0Q)
Estado: operativo
Credenciales: ~/.config/gcloud/application_default_credentials.json
Scope requerido: analytics.readonly + cloud-platform
```

**Si las credenciales expiran:**
```bash
gcloud auth application-default login \
  --scopes="openid,https://www.googleapis.com/auth/userinfo.email,\
https://www.googleapis.com/auth/cloud-platform,\
https://www.googleapis.com/auth/analytics.readonly"
```

**Si el error es SERVICE_DISABLED:**
Habilitar Google Analytics Data API en:
`https://console.developers.google.com/apis/api/analyticsdata.googleapis.com/overview?project=<YOUR_GCP_PROJECT_ID>`

### Playwright MCP
```
Disponible como: mcp__playwright__*
Uso principal: verificar citación en ChatGPT, Perplexity, Claude.ai
```

---

## Datos de referencia — [YOUR_SITE_URL] (90 días, mar-2026)

| Métrica | Valor | Contexto |
|---------|-------|---------|
| Total clics/mes | ~180 | En crecimiento desde dic'25 |
| Total imp/mes | ~20,000 | Pico: 1,429 imp el 10-mar |
| CTR medio | 0.91% | Benchmark interno: SDD 2.73%, FastAPI 3.30% |
| Posición media | 14.2 | Objetivo: < 10 en 6 meses |
| Sesiones orgánicas/mes | ~936 | GA4, incluye Bing y otros |
| Bounce rate medio | 62% (GA4) | Varía mucho por artículo |

**Páginas benchmark (CTR referencia):**
- SDD con IA: pos 6.2, CTR 2.73% — fragmento técnico + problema específico
- FastAPI + LangChain: pos 7.9, CTR 3.30% — mejor CTR del sitio

**AI Overviews confirmados (señal CTR):**
- "claude code templates": 3,924 imp, CTR 0.51%, pos 7.4
- "comet ai browser": 6,525 imp, CTR 0.20%, pos 8.0
- "ddev": 654 imp, CTR 0.46%, pos 7.3
- "que es crewai": 429 imp, CTR 0.23%, pos 31.5
