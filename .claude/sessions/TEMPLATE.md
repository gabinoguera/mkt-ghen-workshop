# Feature: {feature_name}

> Documento de sesión compartido entre agentes. Cada agente lee TODO el documento
> antes de trabajar y rellena SU sección al terminar. Los deliverables completos
> van en `.claude/doc/{feature_name}/`.

**Estado:** `backlog` → `strategy` → `copy` → `implementation` → `tecnico-review` → `done`

**Estado actual:** `backlog`

**Fecha inicio:** YYYY-MM-DD
**Última actualización:** YYYY-MM-DD

---

## Decisiones estratégicas

> Rellena: `@seo-strategist` · Deliverable completo: `.claude/doc/{feature_name}/seo-strategy.md`

- **Target query principal:**
- **Queries secundarias:**
- **Intent:** informational | commercial | transactional | navigational
- **Tipo de contenido:** blog post | landing page | pillar page | micro-topic
- **URL slug:** `/`
- **Word count orientativo:**
- **Schema recomendado:**
  - Rank Math (page-level):
  - Spectra (block-level):
- **Information Gain angle:**
- **Competidores analizados:** (URLs o referencia a `competitive-analysis/`)
- **Internal links recomendados:**
  - [anchor text](URL destino)
- **Notas para copywriter:**

---

## Decisiones de copy

> Rellena: `@marketing-copywriter` · Deliverable completo: `.claude/doc/{feature_name}/copy-deliverable.md`

- **H1 elegido:**
- **Audiencia principal:** writers B2C | editorial B2B
- **SEO meta:**
  - Title (≤60):
  - Description (≤155):
  - Focus keyword:
- **Prompt imagen destacada:**
  ```
  (prompt en inglés, ~60-80 palabras)
  ```
- **QA score:** /100
- **Secciones con Spectra blocks:**
  - FAQ: sí/no
  - How-To: sí/no
  - Review: sí/no
- **Notas para implementer:**

---

## Implementación

> Rellena: `@wp-implementer` · Deliverable completo: `.claude/doc/{feature_name}/wp-implementation.md`

- **Post ID:**
- **Post URL:**
- **Estado WP:** draft | publish
- **Categoría:**
- **Tags:**
- **Imagen destacada:**
  - Media ID:
  - Archivo: `outputs/`
- **Rank Math meta aplicado:** sí/no
- **Schema verificado:** sí/no
- **Verificaciones:**
  - [ ] Post visible en preview
  - [ ] Schema válido (Rich Results Test)
  - [ ] Meta tags correctos (inspeccionar fuente)
  - [ ] Imagen destacada visible
  - [ ] Internal links funcionan
- **Notas / incidencias:**
- **Notas para seo-tecnico:** _(opcional: flagear issues técnicos detectados durante implementación)_

---

## Diagnóstico técnico SEO

> Rellena: `@seo-tecnico` · Deliverable completo: `.claude/doc/{feature_name}/tech-seo-audit.md`
> Esta sección es **opcional** — solo aplica cuando interviene `@seo-tecnico`.

- **URL(s) auditada(s):**
- **Modo:** standalone | post-implementación | cross-consult
- **Indexación:** indexada | no indexada | excluida (motivo)
- **Canonical declarado:**
- **Canonical seleccionado por Google:**
- **Core Web Vitals:**
  - LCP: — (lab) | — (field)
  - INP: — (lab) | — (field)
  - CLS: — (lab) | — (field)
- **Schema válido:** sí | no | parcial
- **Issues críticos:**
- **Issues altos:**
- **Issues medios:**
- **Acciones para @wp-implementer:**
- **Notas para @seo-strategist:**
