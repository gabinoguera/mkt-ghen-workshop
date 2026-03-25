#!/usr/bin/env python3
"""Generate FAQ page content using Spectra (uagb) block markup.

Produces Gutenberg-compatible HTML with:
- uagb/container for layout
- uagb/advanced-heading for section headings
- uagb/faq + uagb/faq-child for FAQ sections with FAQPage schema
- wp:buttons for CTAs

Matches the existing page structure of archivofinal.com (Astra + Spectra).
"""

import hashlib
import json
import sys

_counter = 0


def bid():
    """Generate unique 8-char hex block ID."""
    global _counter
    _counter += 1
    return hashlib.md5(f"faq-page-block-{_counter}".encode()).hexdigest()[:8]


def esc(text):
    """Escape HTML chars for use inside block comment JSON attribute values.

    WordPress block comments store attributes as JSON inside HTML comments.
    HTML special chars must be unicode-escaped to avoid breaking comment parsing.
    CSS -- must also be escaped to avoid breaking HTML comment delimiters.
    """
    return (text
            .replace("--", "\\u002d\\u002d")
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace('"', "\\u0022"))


def root_container_open(block_id, bg_color="", top_pad=70, bottom_pad=70, anchor="", extra_attrs=None):
    """Open a root-level uagb/container block."""
    attrs = {
        "block_id": block_id,
        "variationSelected": True,
        "isBlockRootParent": True,
        "topPaddingDesktop": top_pad,
        "bottomPaddingDesktop": bottom_pad,
        "topPaddingTablet": 40,
        "bottomPaddingTablet": 40,
        "leftPaddingTablet": 30,
        "rightPaddingTablet": 30,
        "topPaddingMobile": 30,
        "bottomPaddingMobile": 30,
        "leftPaddingMobile": 20,
        "rightPaddingMobile": 20,
        "paddingLink": False,
    }
    if bg_color:
        attrs["backgroundType"] = "color"
        attrs["backgroundColor"] = bg_color
    if anchor:
        attrs["anchor"] = anchor
    if extra_attrs:
        attrs.update(extra_attrs)

    json_str = json.dumps(attrs, ensure_ascii=False)
    # Escape -- in CSS vars within JSON
    json_str = json_str.replace("--", "\\u002d\\u002d")

    anchor_html = f' id="{anchor}"' if anchor else ""
    return (
        f'<!-- wp:uagb/container {json_str} -->\n'
        f'<div class="wp-block-uagb-container uagb-block-{block_id} alignfull uagb-is-root-container"{anchor_html}>'
        f'<div class="uagb-container-inner-blocks-wrap">'
    )


def root_container_close():
    return '</div></div>\n<!-- /wp:uagb/container -->'


def inner_container_open(block_id, direction="", extra_attrs=None):
    """Open an inner uagb/container block."""
    attrs = {
        "block_id": block_id,
        "topPaddingDesktop": 20,
        "bottomPaddingDesktop": 20,
        "leftPaddingDesktop": 25,
        "rightPaddingDesktop": 25,
        "paddingLink": False,
    }
    if direction:
        attrs["directionDesktop"] = direction
    if extra_attrs:
        attrs.update(extra_attrs)

    json_str = json.dumps(attrs, ensure_ascii=False)
    json_str = json_str.replace("--", "\\u002d\\u002d")

    return (
        f'<!-- wp:uagb/container {json_str} -->\n'
        f'<div class="wp-block-uagb-container uagb-block-{block_id}">'
    )


def inner_container_close():
    return '</div>\n<!-- /wp:uagb/container -->'


def advanced_heading(block_id, text, level=2, align="left"):
    """Generate uagb/advanced-heading block."""
    attrs = {
        "block_id": block_id,
        "classMigrate": True,
        "headingDescToggle": False,
        "headingAlign": align,
        "headSpace": 0,
        "blockTopPadding": 0,
        "blockBottomPadding": 15,
    }
    json_str = json.dumps(attrs, ensure_ascii=False)
    tag = f"h{level}"
    return (
        f'<!-- wp:uagb/advanced-heading {json_str} -->\n'
        f'<div class="wp-block-uagb-advanced-heading uagb-block-{block_id}">'
        f'<{tag} class="uagb-heading-text">{text}</{tag}></div>\n'
        f'<!-- /wp:uagb/advanced-heading -->'
    )


def faq_block(block_id, children_blocks):
    """Generate uagb/faq block wrapping faq-child blocks."""
    attrs = {
        "block_id": block_id,
        "enableSchemaSupport": True,
        "borderStyle": "",
        "borderWidth": "",
        "borderRadius": "",
        "borderColor": "",
        "overallBorderTopWidth": 1,
        "overallBorderLeftWidth": 1,
        "overallBorderRightWidth": 1,
        "overallBorderBottomWidth": 1,
        "overallBorderTopLeftRadius": 2,
        "overallBorderTopRightRadius": 2,
        "overallBorderBottomLeftRadius": 2,
        "overallBorderBottomRightRadius": 2,
        "overallBorderStyle": "solid",
        "overallBorderColor": "#D2D2D2",
    }
    json_str = json.dumps(attrs, ensure_ascii=False)
    lines = [f'<!-- wp:uagb/faq {json_str} -->']
    for child in children_blocks:
        lines.append(child)
    lines.append('<!-- /wp:uagb/faq -->')
    return "\n".join(lines)


def faq_child(block_id, question, answer_html):
    """Generate self-closing uagb/faq-child block.

    The answer_html should contain raw HTML (links, bold, lists, etc.).
    This function escapes it for the block attribute.
    """
    escaped_q = esc(question)
    escaped_a = esc(answer_html)
    return f'<!-- wp:uagb/faq-child {{"block_id":"{block_id}","question":"{escaped_q}","answer":"{escaped_a}"}} /-->'


def paragraph(text, align="", font_size=""):
    """Generate wp:paragraph block."""
    attrs = {}
    if align:
        attrs["align"] = align
    if font_size:
        attrs["fontSize"] = font_size

    classes = []
    if align:
        classes.append(f"has-text-align-{align}")
    if font_size:
        classes.append(f"has-{font_size}-font-size")

    class_str = f' class="{" ".join(classes)}"' if classes else ""
    attrs_str = f" {json.dumps(attrs, ensure_ascii=False)}" if attrs else ""

    return (
        f'<!-- wp:paragraph{attrs_str} -->\n'
        f'<p{class_str}>{text}</p>\n'
        f'<!-- /wp:paragraph -->'
    )


def buttons_block(button_list):
    """Generate wp:buttons block with child buttons."""
    lines = [
        '<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center","orientation":"horizontal"}} -->',
        '<div class="wp-block-buttons">'
    ]
    for btn in button_list:
        lines.append(btn)
    lines.append('</div>')
    lines.append('<!-- /wp:buttons -->')
    return "\n".join(lines)


def primary_button(text, url):
    """Primary CTA button matching site style."""
    return (
        '<!-- wp:button {"backgroundColor":"ast-global-color-0","textColor":"ast-global-color-6",'
        '"className":"is-style-outline","style":{"border":{"width":"1px",'
        '"color":"var(\\u002d\\u002dast-global-color-0)","radius":"10px"},'
        '"elements":{"link":{"color":{"text":"var:preset|color|ast-global-color-6"}}},'
        '"typography":{"fontStyle":"normal","fontWeight":"100"}},"fontSize":"medium"} -->\n'
        '<div class="wp-block-button is-style-outline">'
        f'<a class="wp-block-button__link has-ast-global-color-6-color has-ast-global-color-0-background-color '
        f'has-text-color has-background has-link-color has-border-color has-medium-font-size has-custom-font-size '
        f'wp-element-button" href="{url}" '
        f'style="border-color:var(--ast-global-color-0);border-width:1px;border-radius:10px;'
        f'font-style:normal;font-weight:100">{text}</a></div>\n'
        '<!-- /wp:button -->'
    )


def secondary_button(text, url):
    """Secondary CTA button matching site style."""
    return (
        '<!-- wp:button {"backgroundColor":"ast-global-color-4","textColor":"ast-global-color-2",'
        '"className":"is-style-fill","style":{"border":{"radius":"10px","width":"1px"},'
        '"elements":{"link":{"color":{"text":"var:preset|color|ast-global-color-2"}}},'
        '"typography":{"fontStyle":"normal","fontWeight":"100"}},"fontSize":"medium",'
        '"borderColor":"cyan-bluish-gray"} -->\n'
        '<div class="wp-block-button is-style-fill">'
        f'<a class="wp-block-button__link has-ast-global-color-2-color has-ast-global-color-4-background-color '
        f'has-text-color has-background has-link-color has-border-color has-cyan-bluish-gray-border-color '
        f'has-medium-font-size has-custom-font-size wp-element-button" href="{url}" '
        f'style="border-width:1px;border-radius:10px;font-style:normal;font-weight:100">{text}</a></div>\n'
        '<!-- /wp:button -->'
    )


# --- FAQ Content Data ---

ESCRITORES_FAQ = [
    ("¿Qué es Archivo Final?",
     "Archivo Final es una plataforma de evaluación literaria profesional que genera informes de lectura de manuscritos mediante inteligencia artificial. Analizamos tu obra de ficción narrativa con LEO, un sistema que evalúa 8 métricas profesionales. Los manuscritos que superan el umbral de calidad (todas las métricas >= 7) pueden crear un perfil de autor verificado y conectar con editoriales afines.<br><br>Nuestro objetivo es democratizar el acceso a la evaluación profesional y facilitar el camino hacia la publicación. Ver <a href=\"/como-funciona/\">cómo funciona el proceso completo</a>."),

    ("¿Cómo funciona el informe de lectura de LEO?",
     "LEO analiza tu manuscrito en 8 métricas profesionales: sinopsis, originalidad, coherencia narrativa, adaptabilidad multiplataforma, personajes, fluidez, calidad textual y género literario. Cada métrica recibe una puntuación de 1 a 10 con análisis detallado y justificación.<br><br>El análisis tarda minutos (no semanas) y es completamente objetivo. LEO utiliza Google Gemini via Vertex AI, con prompts diseñados por profesionales editoriales. Ver todos los detalles en <a href=\"/leo/\">LEO: Informe de lectura inteligente</a>."),

    ("¿Cuánto cuesta?",
     "Archivo Final opera con modelo freemium: los primeros 3 informes de lectura son gratuitos. Puedes subir hasta 3 manuscritos distintos y recibir el informe completo de LEO sin coste.<br><br>Después de los 3 informes gratuitos, ofreceremos opciones premium (actualmente en desarrollo). Nunca pagarás por crear tu perfil de autor ni por aparecer en el catálogo para profesionales editoriales."),

    ("¿Cuántos informes gratuitos tengo?",
     "Cada usuario tiene 3 informes de lectura gratuitos. Puedes usar los 3 con el mismo manuscrito (si lo corriges y reenvías) o con manuscritos diferentes. Los informes gratuitos tienen exactamente la misma calidad y contenido que los informes premium.<br><br>Tu cuenta de Archivo Final muestra cuántos informes gratuitos te quedan disponibles."),

    ("¿Qué formatos de manuscrito acepta Archivo Final?",
     "Archivo Final acepta únicamente manuscritos en formato PDF. El archivo debe cumplir estos requisitos:<br><br><ul><li><strong>Formato:</strong> PDF</li><li><strong>Tamaño máximo:</strong> 25 MB</li><li><strong>Idioma:</strong> Español</li><li><strong>Género:</strong> Ficción narrativa (novela o relato)</li><li><strong>Estado:</strong> Obra terminada (no fragmentos ni obras en proceso)</li></ul><br>Si tu manuscrito está en formato Word (.doc/.docx), expórtalo a PDF antes de subirlo."),

    ("¿Cuál es el tamaño máximo de archivo?",
     "El tamaño máximo de archivo es 25 MB. La mayoría de manuscritos en PDF cumplen este límite sin problemas. Si tu archivo supera 25 MB, prueba estas soluciones:<br><br><ul><li>Reduce la calidad de imágenes incrustadas (si las hay)</li><li>Elimina páginas innecesarias (portadas decorativas, ilustraciones)</li><li>Usa herramientas de compresión de PDF (Adobe Acrobat, herramientas online)</li></ul>"),

    ("¿Qué géneros literarios evalúa LEO?",
     "LEO está optimizado para ficción narrativa en español: novela y relato en todos los géneros (realismo, fantástico, ciencia ficción, thriller, histórico, romántico, etc.). Utilizamos el estándar THEMA v1.6 con 161 géneros profesionales para clasificar tu manuscrito.<br><br>Actualmente no evaluamos poesía, teatro, ensayo ni no-ficción. Estamos trabajando en ampliar géneros progresivamente."),

    ("¿Evaluáis manuscritos en otros idiomas además de español?",
     "Actualmente solo evaluamos manuscritos en español. LEO está entrenado específicamente para narrativa en español con conocimiento del mercado editorial hispano.<br><br>Planeamos ampliar a otros idiomas en el futuro."),

    ("¿Cuánto tarda el informe de lectura?",
     "El informe de lectura de LEO se genera en minutos. El tiempo exacto depende de la longitud del manuscrito, pero habitualmente recibes tu informe entre 5 y 15 minutos después de subir el PDF.<br><br>Si tu manuscrito cualifica (todas las métricas >= 7) y pasa por validación de <a href=\"/lectores-profesionales/\">lectores profesionales</a>, esa fase adicional tarda entre 3 y 7 días laborables."),

    ("¿Qué son las 8 métricas de LEO?",
     "LEO evalúa tu manuscrito en 8 dimensiones profesionales:<br><br><ol><li><strong>Sinopsis</strong> — Claridad de premisa y conflicto central</li><li><strong>Originalidad</strong> — Propuesta narrativa diferenciada</li><li><strong>Coherencia</strong> — Consistencia interna de la trama</li><li><strong>Adaptabilidad</strong> — Potencial multiplataforma (audiovisual, podcast, etc.)</li><li><strong>Personajes</strong> — Desarrollo, motivación y arco narrativo</li><li><strong>Fluidez</strong> — Ritmo y progresión narrativa</li><li><strong>Calidad textual</strong> — Prosa, estilo y técnica literaria</li><li><strong>Género</strong> — Clasificación THEMA v1.6 profesional</li></ol><br>Cada métrica incluye puntuación (1-10), análisis detallado y justificación. Ver explicación completa en <a href=\"/leo/\">LEO: Informe de lectura</a>."),

    ("¿Cómo funciona el sistema de puntuación (1-10)?",
     "Cada métrica recibe una puntuación de 1 a 10:<br><br><ul><li><strong>1-4:</strong> Necesita trabajo significativo</li><li><strong>5-6:</strong> Nivel aceptable pero mejorable</li><li><strong>7-8:</strong> Nivel profesional sólido</li><li><strong>9-10:</strong> Nivel excepcional</li></ul><br>LEO no puntúa con aprobado/suspenso sino con una escala gradual que refleja el nivel de desarrollo de cada dimensión. La puntuación viene siempre acompañada de análisis detallado explicando el porqué."),

    ('¿Qué significa que mi manuscrito "cualifica"?',
     "Un manuscrito cualifica cuando obtiene puntuación igual o superior a 7 en las 8 métricas de LEO. Este umbral indica que tu obra tiene nivel editorial profesional en todas las dimensiones evaluadas.<br><br>Cuando tu manuscrito cualifica:<br><ul><li>Puedes crear un <a href=\"/perfil-de-autor/\">perfil de autor verificado</a></li><li>Tu manuscrito pasa por validación de <a href=\"/lectores-profesionales/\">lectores profesionales</a></li><li>Tu perfil aparece en el catálogo para <a href=\"/para-profesionales/\">profesionales editoriales</a></li><li>Te conectamos con editoriales afines a tu género</li></ul><br>Aproximadamente el 20-30% de los manuscritos analizados alcanzan este umbral."),

    ("¿Qué ocurre si no alcanzo el umbral de 7 en todas las métricas?",
     "Si tu manuscrito no alcanza 7 en todas las métricas, recibes el informe completo de LEO con análisis detallado de cada dimensión. El informe te indica exactamente qué aspectos funcionan bien y cuáles necesitan trabajo.<br><br>Puedes usar este feedback para revisar tu manuscrito y volver a subirlo cuando lo hayas mejorado. Cada reenvío cuenta como un nuevo informe dentro de tu cuota de informes gratuitos o premium."),

    ("¿Qué es THEMA v1.6?",
     "THEMA v1.6 es el estándar internacional de clasificación de géneros editoriales. Es el mismo sistema que utilizan editoriales profesionales, distribuidores y bibliotecas para categorizar libros.<br><br>THEMA tiene 161 géneros literarios organizados jerárquicamente, desde categorías amplias (como \"Ficción moderna y contemporánea\") hasta específicas (como \"Ficción gótica\" o \"Thriller tecnológico\"). LEO clasifica tu manuscrito con THEMA v1.6, y los <a href=\"/lectores-profesionales/\">lectores profesionales</a> refinan esa clasificación para asegurar precisión según el mercado editorial."),

    ("¿Por qué es importante la clasificación THEMA?",
     "La clasificación THEMA es importante porque es el idioma común del sector editorial profesional. Cuando presentas tu manuscrito con clasificación THEMA:<br><br><ul><li>Las editoriales saben exactamente en qué categoría encaja tu obra</li><li>Puedes comparar tu género con catálogos editoriales existentes</li><li>Los distribuidores y librerías comprenden dónde ubicar tu libro</li><li>Tu perfil aparece en búsquedas precisas de profesionales que buscan tu género específico</li></ul><br>Una clasificación THEMA precisa aumenta las posibilidades de conectar con la editorial adecuada."),

    ("¿Cómo creo mi perfil de autor?",
     "Solo puedes crear un perfil de autor si tu manuscrito cualifica (todas las métricas >= 7). Cuando tu manuscrito alcanza este umbral, recibes una invitación para completar tu perfil.<br><br>El perfil incluye:<br><ul><li>Biografía profesional</li><li>Datos de contacto</li><li>Información sobre tu trayectoria literaria</li><li>El informe LEO completo de tu manuscrito</li></ul><br>Los <a href=\"/lectores-profesionales/\">lectores profesionales</a> validan tu perfil antes de hacerlo visible para editoriales. Ver más detalles en <a href=\"/perfil-de-autor/\">Tu perfil de autor</a>."),

    ("¿Quién valida mi perfil?",
     "Tu perfil es validado por <a href=\"/lectores-profesionales/\">lectores profesionales</a> con experiencia editorial y conocimiento del estándar THEMA v1.6. Revisan:<br><br><ul><li>Coherencia del análisis de LEO con tu manuscrito</li><li>Precisión de la clasificación THEMA según el mercado editorial</li><li>Calidad profesional de la información en tu perfil</li></ul><br>Esta validación asegura que solo perfiles con información adecuada y manuscritos de calidad verificada aparecen en el catálogo para profesionales. El proceso tarda entre 3 y 7 días laborables."),

    ("¿Qué ven las editoriales en mi perfil?",
     "Las editoriales que acceden al catálogo de Archivo Final ven:<br><br><ul><li><strong>Informe LEO completo</strong> con las 8 métricas y análisis detallado</li><li><strong>Clasificación THEMA v1.6</strong> profesional de tu manuscrito</li><li><strong>Sinopsis</strong> generada por LEO</li><li><strong>Tu biografía</strong> profesional y trayectoria literaria</li><li><strong>Datos de contacto</strong> para comunicarse contigo directamente</li></ul><br>No ven tu manuscrito completo. Ven la información profesional que necesitan para decidir si tu obra encaja con su línea editorial. Si muestran interés, te contactan directamente para solicitar el manuscrito completo."),

    ("¿Qué pasa con mi manuscrito después del análisis?",
     "Tu manuscrito en PDF se elimina automáticamente de nuestros servidores una vez completado el análisis de LEO. No almacenamos tu obra. Solo conservamos el informe de lectura generado (métricas, análisis y sinopsis).<br><br>Esta política protege tu propiedad intelectual y tu privacidad. Tus derechos de autor permanecen 100% contigo en todo momento."),

    ("¿Usáis mi manuscrito para entrenar la IA?",
     "No. Utilizamos Google Gemini via Vertex AI enterprise, que garantiza contractualmente que tus manuscritos no se usan para entrenar modelos de inteligencia artificial.<br><br>Tu manuscrito se procesa exclusivamente para generar tu informe de lectura, y después se elimina. Ver más sobre nuestra tecnología en <a href=\"/leo/\">cómo funciona LEO</a>."),

    ("¿Pierdo derechos de autor al subir mi manuscrito?",
     "No. Tu propiedad intelectual permanece 100% tuya en todo momento. Subir tu manuscrito a Archivo Final no transfiere ningún derecho.<br><br>Solo procesamos tu obra para generar el informe de lectura. Si decides compartir tu perfil con editoriales, eres tú quien gestiona los derechos y negocia cualquier acuerdo editorial. Archivo Final nunca reclama derechos sobre tu obra."),

    ("¿Dónde se almacenan mis datos?",
     "Todos los datos de Archivo Final se almacenan en servidores de Google Cloud en la región europe-west1 (Europa). Cumplimos con el Reglamento General de Protección de Datos (GDPR) de la Unión Europea.<br><br>Los manuscritos en PDF se eliminan automáticamente tras el análisis. Solo conservamos tu cuenta de usuario, el informe de lectura (métricas y análisis), y la información de tu perfil si decides crearlo."),

    ("¿Es seguro subir mi obra inédita?",
     "Sí. Tu manuscrito se procesa mediante Vertex AI enterprise (Google Cloud), se elimina automáticamente tras el análisis, y no se usa para entrenar IA. Los servidores están en Europa (GDPR compliance).<br><br>Solo tú y el sistema de análisis LEO acceden a tu manuscrito durante el procesamiento. Si tu manuscrito cualifica y creas perfil de autor, las editoriales verificadas ven tu informe y sinopsis, pero no el manuscrito completo hasta que tú decidas compartirlo."),

    ("¿Puedo volver a subir un manuscrito corregido?",
     "Sí. Puedes reenviar un manuscrito después de corregirlo. Cada reenvío genera un nuevo informe de lectura y cuenta dentro de tu cuota de informes gratuitos o premium.<br><br>No hay límite de reenvíos. Muchos autores usan el feedback del primer informe para mejorar aspectos específicos y vuelven a evaluar su manuscrito hasta alcanzar el umbral de cualificación (todas las métricas >= 7)."),

    ("¿Cuánto tiempo debo esperar entre reenvíos?",
     "No hay tiempo mínimo de espera entre reenvíos. Puedes subir un manuscrito corregido inmediatamente después de recibir el informe anterior.<br><br>Recomendamos revisar el manuscrito con calma según el feedback de LEO antes de reenviar, para que los cambios tengan impacto real en las métricas."),

    ("¿Cómo me conectáis con editoriales?",
     "Si tu manuscrito cualifica (todas las métricas >= 7), creas un <a href=\"/perfil-de-autor/\">perfil de autor verificado</a> que aparece en el catálogo exclusivo para <a href=\"/para-profesionales/\">profesionales editoriales</a>.<br><br>Las editoriales filtran el catálogo por género THEMA, consultan tu informe LEO completo, y te contactan directamente si tu manuscrito encaja con su línea editorial. Tú decides si compartes el manuscrito completo y negocias las condiciones de publicación.<br><br>No somos agentes literarios. Facilitamos la conexión, pero tú gestionas la relación con la editorial."),

    ("¿Garantizáis que una editorial publicará mi libro?",
     "No. Archivo Final evalúa la calidad de tu manuscrito y te conecta con editoriales afines, pero no garantiza publicación. La decisión final de publicar es siempre de la editorial después de leer tu obra completa y considerar su catálogo, capacidad de producción y estrategia comercial.<br><br>Lo que sí garantizamos es que tu manuscrito tiene nivel profesional (si cualifica) y que editoriales relevantes verán tu perfil en un catálogo filtrado por calidad."),

    ("¿Puedo elegir a qué editoriales me presentáis?",
     "El catálogo de Archivo Final funciona de forma inversa: las editoriales te descubren a ti, no al revés. Tu perfil aparece en búsquedas de profesionales que filtran por género THEMA y características específicas.<br><br>No enviamos tu manuscrito a editoriales específicas. Tu perfil está disponible para todas las editoriales verificadas de nuestra red, y son ellas quienes te contactan si hay interés. Este modelo asegura que solo recibes contactos de editoriales genuinamente interesadas en tu género."),
]

PROFESIONALES_FAQ = [
    ("¿Cómo solicito acceso al catálogo?",
     "Completa el formulario de registro profesional en <a href=\"https://app.archivofinal.com/industria/registro/\">app.archivofinal.com/industria/registro/</a>. Proporciona información sobre tu actividad editorial (editorial que representas, rol, géneros de interés).<br><br>Nuestro equipo verifica tu perfil profesional en 3-5 días laborables. Una vez aprobado, recibes confirmación de acceso y puedes explorar el catálogo completo de autores verificados."),

    ("¿Qué información veo de cada manuscrito?",
     "Accedes al informe LEO completo con las 8 métricas y análisis detallado, clasificación THEMA v1.6 profesional, sinopsis del manuscrito, biografía del autor y datos de contacto.<br><br>No ves el manuscrito completo. Ves toda la información profesional necesaria para evaluar si la obra encaja con tu línea editorial. Si hay interés, contactas al autor directamente para solicitar el manuscrito.<br><br>Ver más detalles en <a href=\"/para-profesionales/\">Para profesionales editoriales</a>."),

    ("¿Todos los manuscritos están en el catálogo?",
     "No. Solo manuscritos con puntuación >= 7 en las 8 métricas de LEO y validados por <a href=\"/lectores-profesionales/\">lectores profesionales</a> aparecen en el catálogo.<br><br>Este doble filtro (IA + humano) asegura que solo obras con verdadero potencial editorial son visibles. Aproximadamente el 20-30% de los manuscritos analizados alcanzan este umbral."),

    ("¿Cómo funciona el filtrado por género THEMA?",
     "Puedes filtrar el catálogo por códigos THEMA v1.6 específicos o categorías amplias. Todos los manuscritos tienen clasificación THEMA validada por <a href=\"/lectores-profesionales/\">lectores profesionales</a> con conocimiento del mercado editorial.<br><br>El sistema te permite buscar géneros híbridos, explorar categorías relacionadas, o aplicar filtros combinados (por ejemplo, \"Ficción fantástica + ambientación histórica\")."),

    ("¿Cómo verificáis la calidad de los manuscritos?",
     "Aplicamos un doble filtro de calidad:<br><br><ol><li><strong>Análisis de LEO:</strong> Solo manuscritos con puntuación >= 7 en las 8 métricas acceden a validación profesional</li><li><strong>Lectores profesionales:</strong> Expertos con experiencia editorial validan coherencia del análisis, refinan clasificación THEMA y aprueban perfiles</li></ol><br>Este proceso garantiza que el catálogo mantiene un estándar de calidad constante. Ver más en <a href=\"/lectores-profesionales/\">Lectores profesionales</a>."),

    ("¿Quiénes son los lectores profesionales que validan?",
     "Los <a href=\"/lectores-profesionales/\">lectores profesionales</a> tienen experiencia en el sector editorial como editores, agentes literarios o lectores en casas editoriales. Todos conocen el estándar THEMA v1.6 y comprenden las expectativas del mercado editorial profesional.<br><br>No publicamos perfiles individuales para proteger su independencia, pero garantizamos que cada lector profesional trabaja con los mismos criterios de validación."),

    ("¿Los autores saben si he visto su perfil?",
     "No. Puedes explorar perfiles, consultar informes y revisar clasificaciones THEMA sin que el autor reciba notificaciones. Solo cuando envías un mensaje directo al autor, este sabe que has mostrado interés en su manuscrito.<br><br>Esta privacidad te permite evaluar múltiples perfiles sin compromisos antes de contactar."),

    ("¿Cómo contacto con un autor?",
     "Desde el perfil del autor puedes enviar un mensaje directo a través de la plataforma. El autor recibe una notificación en su cuenta y puede responder desde Archivo Final.<br><br>El contacto inicial es privado y gestionado dentro de la plataforma. Después puedes intercambiar información de contacto directa si ambos lo acordáis."),

    ("¿Hay coste por acceder al catálogo?",
     "No. El acceso al catálogo es gratuito para profesionales verificados de la industria editorial. Tampoco hay coste por consultar perfiles ni por contactar con autores.<br><br>Archivo Final monetiza del lado de los escritores (modelo freemium con informes gratuitos). El acceso profesional es siempre sin coste."),
]

GENERALES_FAQ = [
    ("¿Qué es Archivo Final?",
     "Archivo Final es una plataforma de evaluación literaria profesional. Analizamos manuscritos de ficción narrativa con LEO, un sistema de inteligencia artificial que evalúa 8 métricas profesionales. Los manuscritos que alcanzan nivel editorial profesional (todas las métricas >= 7) se conectan con editoriales reales a través de perfiles de autor verificados.<br><br>Fundamos Archivo Final en 2020 para democratizar el acceso a la evaluación profesional y facilitar el descubrimiento de talento literario. Ver más en <a href=\"/sobre-nosotros/\">Sobre nosotros</a>."),

    ("¿Quién está detrás de Archivo Final?",
     "Archivo Final fue fundado en 2020 por Constanza Riveré y Gabriel Noguera. El equipo combina experiencia en tecnología, literatura y mercado editorial.<br><br>Trabajamos con <a href=\"/lectores-profesionales/\">lectores profesionales</a> externos que validan los manuscritos cualificados y refinan las clasificaciones THEMA según estándares del sector. Ver más en <a href=\"/sobre-nosotros/\">Sobre nosotros</a>."),

    ("¿Cómo protegéis la propiedad intelectual de los manuscritos?",
     "Protegemos tu propiedad intelectual de tres formas:<br><br><ol><li><strong>PDFs auto-eliminados:</strong> Tu manuscrito se elimina automáticamente tras el análisis de LEO</li><li><strong>Sin training de IA:</strong> Usamos Vertex AI enterprise, que garantiza contractualmente que tus manuscritos no se usan para entrenar modelos</li><li><strong>Derechos siempre tuyos:</strong> Nunca reclamamos derechos sobre tu obra. Tú gestionas todos los acuerdos editoriales</li></ol><br>Los servidores están en Europa (GDPR compliance) y solo conservamos el informe de lectura, no el manuscrito."),

    ("¿Qué tecnología usáis?",
     "Utilizamos Google Gemini via Vertex AI enterprise para el análisis de manuscritos. Vertex AI es la plataforma de inteligencia artificial empresarial de Google Cloud, que garantiza:<br><br><ul><li>Tus manuscritos no se usan para entrenar modelos de IA</li><li>Procesamiento en servidores europeos (europe-west1)</li><li>Cumplimiento de GDPR y estándares de seguridad empresarial</li></ul><br>Los prompts de análisis están diseñados por profesionales editoriales con conocimiento del mercado literario hispano. Ver más detalles técnicos en <a href=\"/leo/\">LEO: Informe de lectura</a>."),

    ("¿Qué IA usáis para el análisis?",
     "Usamos Google Gemini via Vertex AI enterprise. Vertex AI es la plataforma de inteligencia artificial empresarial de Google Cloud, específicamente diseñada para aplicaciones profesionales con garantías de privacidad y seguridad.<br><br>El modelo Gemini analiza tu manuscrito siguiendo prompts diseñados por profesionales editoriales. El análisis es objetivo, rápido (minutos) y basado en criterios literarios profesionales."),

    ("¿Es fiable un informe generado por IA?",
     "El informe de LEO es fiable porque combina análisis de IA con validación humana posterior. LEO evalúa aspectos medibles con objetividad (estructura narrativa, coherencia, desarrollo de personajes, calidad técnica), y los <a href=\"/lectores-profesionales/\">lectores profesionales</a> validan manuscritos cualificados con su criterio experto.<br><br>Esta combinación ofrece lo mejor de ambos mundos: velocidad y objetividad de la IA, más sensibilidad y conocimiento del mercado de expertos humanos."),

    ("¿Por qué combináis IA con lectores profesionales?",
     "Combinamos IA con lectores profesionales porque cada uno aporta fortalezas complementarias:<br><br><strong>LEO (IA):</strong><br><ul><li>Análisis inmediato (minutos)</li><li>Objetividad total (8 métricas sin sesgos)</li><li>Accesible (modelo freemium)</li><li>Consistencia en la evaluación</li></ul><br><strong>Lectores profesionales:</strong><br><ul><li>Conocimiento del mercado editorial real</li><li>Refinamiento de clasificación THEMA según expectativas del sector</li><li>Validación de manuscritos cualificados antes de visibilidad editorial</li><li>Sensibilidad a matices que solo la experiencia humana capta</li></ul><br>El resultado es un sistema de evaluación completo: rápido, objetivo, y con el respaldo de criterio profesional. Ver más en <a href=\"/lectores-profesionales/\">Lectores profesionales</a>."),

    ("¿Cómo puedo contactar con el equipo de Archivo Final?",
     "Puedes contactar con nosotros a través de:<br><br><ul><li><strong>Email:</strong> hola@archivofinal.com</li><li><strong>Teléfono:</strong> 744610517</li><li><strong>Formulario web:</strong> <a href=\"/contacto/\">Hablemos</a></li></ul><br>Respondemos habitualmente en 24-48 horas laborables. Si tienes dudas sobre el funcionamiento de LEO, tu informe de lectura, o el proceso de conexión con editoriales, escríbenos."),

    ("¿Tenéis soporte técnico?",
     "Sí. Si tienes problemas técnicos al subir tu manuscrito, acceder a tu informe o gestionar tu perfil, contacta con nosotros en hola@archivofinal.com o a través del <a href=\"/contacto/\">formulario de contacto</a>.<br><br>Describir el problema con el máximo detalle posible (mensaje de error, navegador que usas, tamaño del archivo, etc.) nos ayuda a resolver tu consulta más rápidamente."),
]


def generate_faq_section(section_id, title, faq_data):
    """Generate a complete FAQ section with container + heading + faq block."""
    parts = []

    parts.append(root_container_open(
        bid(),
        bg_color="",
        top_pad=60,
        bottom_pad=60,
        anchor=section_id,
    ))

    # Section heading
    parts.append(advanced_heading(bid(), title, level=2))

    # FAQ block with children
    children = []
    for question, answer in faq_data:
        children.append(faq_child(bid(), question, answer))

    parts.append(faq_block(bid(), children))

    parts.append(root_container_close())

    return "\n\n".join(parts)


def generate_page():
    """Generate the complete FAQ page content."""
    sections = []

    # --- Section 1: Intro ---
    sections.append(root_container_open(
        bid(),
        bg_color="",
        top_pad=50,
        bottom_pad=30,
    ))
    sections.append(paragraph(
        'Encuentra respuestas a las preguntas más comunes sobre Archivo Final, '
        'el análisis de manuscritos con LEO, perfiles de autor, conexión con editoriales, '
        'privacidad y derechos. Si no encuentras lo que buscas, contacta con nosotros en '
        '<a href="/contacto/">Hablemos</a>.',
        align="center",
    ))
    sections.append(root_container_close())

    # --- Section 2: Category tiles ---
    sections.append(root_container_open(
        bid(),
        bg_color="var(\\u002d\\u002dast-global-color-5)",
        top_pad=40,
        bottom_pad=40,
    ))

    # Row container for 3 tiles
    sections.append(inner_container_open(bid(), direction="row", extra_attrs={
        "childrenWidthDesktop": "equal",
        "columnGapDesktop": 20,
        "rowGapMobile": 15,
        "directionMobile": "column",
    }))

    # Tile 1: Escritores
    tile_attrs = {
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
        "backgroundColor": "var(\\u002d\\u002dast-global-color-6)",
        "boxShadowVOffset": 4,
        "boxShadowBlur": 12,
        "boxShadowSpread": -4,
    }
    sections.append(inner_container_open(bid(), extra_attrs=tile_attrs))
    sections.append(paragraph('<strong><a href="#escritores">Escritores y escritoras</a></strong>', align="center"))
    sections.append(paragraph(
        'Manuscritos, informes LEO, perfiles de autor, privacidad y conexión con editoriales',
        align="center", font_size="small"
    ))
    sections.append(paragraph('<strong>26 preguntas →</strong>', align="center", font_size="small"))
    sections.append(inner_container_close())

    # Tile 2: Profesionales
    sections.append(inner_container_open(bid(), extra_attrs=tile_attrs))
    sections.append(paragraph('<strong><a href="#profesionales">Profesionales de la industria</a></strong>', align="center"))
    sections.append(paragraph(
        'Acceso al catálogo, información de manuscritos, filtrado THEMA y contacto con autores',
        align="center", font_size="small"
    ))
    sections.append(paragraph('<strong>9 preguntas →</strong>', align="center", font_size="small"))
    sections.append(inner_container_close())

    # Tile 3: Generales
    sections.append(inner_container_open(bid(), extra_attrs=tile_attrs))
    sections.append(paragraph('<strong><a href="#generales">Preguntas generales</a></strong>', align="center"))
    sections.append(paragraph(
        'Sobre Archivo Final, tecnología, fiabilidad de la IA y soporte',
        align="center", font_size="small"
    ))
    sections.append(paragraph('<strong>9 preguntas →</strong>', align="center", font_size="small"))
    sections.append(inner_container_close())

    sections.append(inner_container_close())  # Close row container
    sections.append(root_container_close())  # Close tiles section

    # --- Section 3: Para escritores ---
    sections.append(generate_faq_section("escritores", "Para escritores", ESCRITORES_FAQ))

    # --- Section 4: Para profesionales editoriales ---
    sections.append(generate_faq_section("profesionales", "Para profesionales editoriales", PROFESIONALES_FAQ))

    # --- Section 5: Preguntas generales ---
    sections.append(generate_faq_section("generales", "Preguntas generales", GENERALES_FAQ))

    # --- Section 6: CTA ---
    sections.append(root_container_open(
        bid(),
        bg_color="var(\\u002d\\u002dast-global-color-5)",
        top_pad=50,
        bottom_pad=60,
    ))
    sections.append(advanced_heading(bid(), "¿No encuentras lo que buscas?", level=2, align="center"))
    sections.append(paragraph(
        'Escríbenos y te responderemos en 24-48 horas laborables.',
        align="center",
    ))

    # Buttons container
    sections.append(inner_container_open(bid(), direction="row", extra_attrs={
        "topPaddingDesktop": 22,
        "bottomPaddingDesktop": 22,
        "childrenWidthDesktop": "auto",
    }))
    sections.append(buttons_block([
        primary_button("Evaluar mi manuscrito", "https://app.archivofinal.com"),
        secondary_button("Hablemos", "/contacto/"),
    ]))
    sections.append(inner_container_close())

    sections.append(paragraph(
        '¿Eres profesional editorial? <a href="https://app.archivofinal.com/industria/registro/">Solicita acceso al catálogo</a>',
        align="center", font_size="small"
    ))
    sections.append(root_container_close())

    return "\n\n".join(sections)


if __name__ == "__main__":
    content = generate_page()
    output_path = sys.argv[1] if len(sys.argv) > 1 else "/dev/stdout"
    if output_path == "/dev/stdout":
        print(content)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated FAQ page: {output_path} ({len(content)} chars)", file=sys.stderr)
