# Workshop: Pipelines de Agentes IA para Marketing y SEO

**Fecha:** Valencia, 22-23 de abril de 2025 (por confirmar)
**Formato:** Presencial, jornada intensiva
**Cupo:** 30 personas

Aprenderás a construir desde cero un pipeline de agentes IA que automatiza la estrategia SEO, la redacción de contenido y la publicación en WordPress — el mismo sistema que está en este repositorio.

---

## Lo que construiremos juntos

Un workflow multi-agente completo con:

- Agentes especializados con roles definidos (estratega SEO, copywriter, implementador WP, auditor técnico)
- Skills invocables con bases de conocimiento adjuntas
- Conexión con MCPs: Google Search Console, Analytics, GitHub, navegador, memoria persistente
- Herramientas CLI Python para publicación, análisis SERP y generación de imágenes
- Sesiones compartidas para coordinar el trabajo entre agentes
- Buenas prácticas de gobernabilidad y seguridad

**Caso práctico:** El propio repositorio que tienes en tus manos — lo construiremos desde cero durante el taller.

---

## Prerrequisitos técnicos

Trae esto instalado y funcionando el día del workshop:

### Obligatorio

- [ ] **Claude Code** — [claude.ai/code](https://claude.ai/code)
  - Cuenta Anthropic con acceso a Claude (plan Pro o superior recomendado)
  - CLI instalada y autenticada: `claude --version`
- [ ] **VS Code** con la extensión **GitHub Copilot** activa
  - Suscripción Copilot Individual o Business
- [ ] **Git** — `git --version`
- [ ] **Python 3.11+** — `python3 --version`
- [ ] **Node.js 18+** — `node --version` (para MCPs via npx)
- [ ] **GitHub account** con acceso a [github.com/gabinoguera/mkt-ghen-workshop](https://github.com/gabinoguera/mkt-ghen-workshop)

### Muy recomendado

- [ ] **WordPress** accesible (staging, local o producción) con:
  - Rank Math plugin instalado y activo
  - Application Password generada (WP Admin → Users → Profile)
- [ ] **Gemini API key** (gratuita) — [aistudio.google.com](https://aistudio.google.com/app/apikey)
- [ ] **Docker Desktop** — para MCP Sequential Thinking

### Opcional (para bloques avanzados)

- [ ] **Google Cloud account** con GSC + Analytics API habilitadas
- [ ] **gcloud CLI** instalada y autenticada

---

## Agenda del día

### Bloque 1 — Fundamentos (90 min)

**"Por qué los agentes, no los chats"**

- Limitaciones de los workflows de chat para trabajo repetitivo
- Arquitectura de un pipeline multi-agente: roles, contexto, coordinación
- Anatomía de un agente en Claude Code: frontmatter, descripción, instrucciones
- Qué es una skill y cuándo crearla vs. un agente
- MCPs: qué son, cómo se conectan, qué puedes hacer con ellos
- Demo en vivo: el pipeline completo ejecutándose

> **Ejercicio:** Analiza el repositorio que acabas de clonar. Identifica los 4 agentes, las 2 skills y los 10 MCPs.

---

### Bloque 2 — Setup y configuración (60 min)

**"De cero a pipeline en tu máquina"**

- Clonar el repo y entender la estructura
- Configurar `.env` con credenciales de WordPress y Gemini
- Instalar dependencias Python (`tools/setup.sh`)
- Configurar `.mcp.json` — reemplazar todos los placeholders
- Verificar que Claude Code detecta los agentes y skills
- Troubleshooting común

> **Ejercicio:** Cada participante tiene el pipeline funcionando en su máquina. Test rápido: `@seo-strategist dime qué ves en este workspace`.

---

### Bloque 3 — Tu proyecto (90 min)

**"Adaptar CLAUDE.md — el ejercicio central"**

Este es el momento más importante del taller. `CLAUDE.md` es lo que convierte una herramienta genérica en tu asistente de contenido personalizado.

Cada participante rellena su propio `CLAUDE.md`:

1. **Project Overview** — URL, autor, idioma, objetivo
2. **Qué es tu blog** — verticales, secciones editoriales
3. **Perfil del autor** — credenciales, expertise, diferenciadores
4. **Knowledge Domain** — entidad central, grafo semántico, audiencias
5. **Stack técnico** — tema, plugins, categorías WP

> **Ejercicio guiado:** Rellena tu CLAUDE.md en tiempo real. Al terminar: `@seo-strategist dame 5 ideas de artículos para mi blog`. Compara resultados antes y después de configurar CLAUDE.md.

---

### Bloque 4 — Crear y modificar agentes (90 min)

**"Construir el equipo desde cero"**

- Crear un agente nuevo desde cero (frontmatter + instrucciones)
- Modificar el rol de un agente existente para tu caso de uso
- Añadir referencias a una skill (nuevos documentos de conocimiento)
- Conectar un nuevo MCP — ejemplo en vivo con `memory` o `drawio`
- Crear un plugin compartible para tu equipo
- Buenas prácticas: gobernabilidad, permisos, qué NO delegar a un agente

> **Ejercicio:** Crea un agente nuevo específico para tu vertical (p.ej. un agente de redes sociales, un agente de email, un agente de análisis de datos). Invócalo y verifica que funciona.

---

### Bloque 5 — Pipeline completo (90 min)

**"De brief a publicado en una jornada"**

Ejecutamos el pipeline completo con un artículo real:

1. Crear sesión: `cp .claude/sessions/TEMPLATE.md .claude/sessions/mi-primer-articulo.md`
2. `@seo-strategist` — análisis de competencia + brief SEO
3. `@marketing-copywriter` — redacción del artículo
4. `python tools/qa_checker.py` — validación mecánica antes de publicar (keyword density, headings, estilo)
5. `@wp-implementer` — generación de imagen + publicación como draft
6. `@seo-tecnico` — validación técnica post-publicación

Con GitHub Copilot: mismo ejercicio desde VS Code con Copilot Agent.

> **Ejercicio final:** Cada participante lanza su propio pipeline con un artículo de su blog. El resultado: un draft publicado en su WordPress con meta SEO, imagen destacada y validación técnica.

---

## Tu Proyecto — Template para rellenar

Usa esta sección como guía para preparar `CLAUDE.md` durante el Bloque 3.

```
Nombre del blog/proyecto: ___________________________________
URL del sitio:            ___________________________________
Tu nombre:                ___________________________________
Idioma del contenido:     ___________________________________
Objetivo principal:       ___________________________________

Verticales (3-5 temas):
  1. _____________________________________________________
  2. _____________________________________________________
  3. _____________________________________________________

Secciones del blog (con sus slugs):
  1. /________/ — ________________________________________
  2. /________/ — ________________________________________

Tu perfil en 3 líneas:
  - Rol: __________________________________________________
  - Credencial clave: ______________________________________
  - Expertise: ____________________________________________

Entidad central (tema que lo une todo): ____________________

Audiencia principal: ______________________________________

¿Por qué te deberían leer a ti? __________________________
```

---

## Recursos y referencias

Incluidos en este repositorio:

| Archivo | Qué encontrarás |
|---------|----------------|
| `.claude/skills/seo/references/semantic-seo.md` | Fundamentos de SEO semántico |
| `.claude/skills/seo/references/topical-authority.md` | Cómo construir autoridad topical |
| `.claude/skills/seo/references/generative-engine-optimization.md` | GEO — optimización para IA generativa |
| `.claude/skills/seo/references/geo-audit-pipeline.md` | Pipeline completo de auditoría GEO |
| `.claude/skills/seo/references/core-web-vitals.md` | Core Web Vitals y rendimiento |
| `.claude/skills/seo/references/technical-seo.md` | SEO técnico completo |
| `.claude/skills/copywriting/references/copy-frameworks.md` | Frameworks de copywriting |
| `.claude/doc/wordpress-reference/` | Patrones de bloques Spectra + schema |

---

## Preguntas frecuentes

**¿Necesito tener WordPress?**
Para el bloque 4 (publicación) sí. Para el resto del taller, no. Puedes seguir todo el ejercicio hasta el paso de publicación con un site de staging o incluso con un WordPress local (LocalWP funciona perfectamente).

**¿Funciona con Yoast en lugar de Rank Math?**
El `wp_publisher.py` usa los meta fields de Rank Math por defecto. Tiene que adaptarse para Yoast, pero la arquitectura es la misma. Lo vemos en el bloque 4.

**¿Puedo usar un CMS diferente a WordPress?**
Sí, pero tendrías que reescribir `wp_publisher.py` para tu CMS. Los agentes SEO y copywriter funcionan con cualquier plataforma.

**¿Funciona igual con GitHub Copilot que con Claude Code?**
Los agentes son específicos de Claude Code. En Copilot trabajarás con el contexto del workspace de otra manera — lo comparamos en el bloque 5.

**¿Los agentes tienen acceso a internet?**
Solo a través de MCPs (Playwright para navegación, GSC para Search Console, etc.). No hacen peticiones arbitrarias a la red.
