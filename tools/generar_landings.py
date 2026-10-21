# -*- coding: utf-8 -*-
"""
Genera las landings estáticas de Abogados en Barinas:

  /abogados/                         -> índice de municipios y parroquias
  /abogados/<municipio>/             -> landing de cada municipio
  /abogados/<municipio>/<parroquia>/ -> landing de cada parroquia
  /saren-en-linea/                   -> landing principal de SAREN en línea
  /sitemap.xml                       -> sitemap con todas las URLs
  /404.html                          -> página de error con estilo iOS

Uso (desde la raíz del repositorio):
    python3 tools/generar_landings.py
"""

import datetime
import html
import json
import os
import re
import sys
import unicodedata
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from barinas_data import MUNICIPIOS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://abogadosenbarinas.pages.dev"
PHONE_DISPLAY = "0416-7775771"
PHONE_TEL = "+584167775771"
WA_NUMBER = "584167775771"
IMAGE = SITE + "/assets/images/abogados-en-barinas-justicia-og.jpg"
TODAY = datetime.date.today().isoformat()
ORG_ID = SITE + "/#organizacion"

e = html.escape


def slugify(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto


def wa(mensaje):
    return "https://wa.me/%s?text=%s" % (WA_NUMBER, quote(mensaje))


# ---------------------------------------------------------------------------
# Servicios
# ---------------------------------------------------------------------------

SAREN_ITEMS = [
    ("fa-calendar-check", "Citas SAREN en línea", "Solicitamos y gestionamos tu cita en Registros y Notarías sin colas."),
    ("fa-file-lines", "Copias certificadas de actas", "Partidas de nacimiento, matrimonio y defunción certificadas."),
    ("fa-stamp", "Legalización de documentos", "Legalización ante el SAREN de actas, títulos y documentos."),
    ("fa-globe", "Apostilla para el exterior", "Preparamos tus documentos para validez internacional."),
    ("fa-file-signature", "Poderes y autenticaciones", "Poderes generales y especiales, declaraciones juradas."),
    ("fa-house", "Compraventa de inmuebles", "Redacción, visado y protocolización de casas y terrenos."),
    ("fa-car", "Compraventa de vehículos", "Documento notariado de traspaso de carros y motos."),
    ("fa-building", "Registro Mercantil", "Firmas personales, compañías anónimas y actas de asamblea."),
    ("fa-map", "Títulos supletorios", "Registro de bienhechurías y documentos de propiedad."),
    ("fa-scroll", "Sucesiones y herencias", "Declaración sucesoral y registro de bienes heredados."),
    ("fa-pen-nib", "Redacción y visado", "Documentos redactados y visados por abogado colegiado."),
    ("fa-truck-fast", "Retiro y envío", "Retiramos tus documentos y los enviamos dentro o fuera de Venezuela."),
]

SERVICIOS = [
    {
        "id": "civil", "icono": "fa-scale-balanced", "color": "blue", "nombre": "Derecho Civil",
        "desc": "Contratos, propiedad y documentos con plena validez legal.",
        "items": ["Contratos de arrendamiento y compraventa", "Títulos supletorios", "Cobro de deudas", "Daños y perjuicios"],
    },
    {
        "id": "familia", "icono": "fa-people-roof", "color": "red", "nombre": "Derecho de Familia",
        "desc": "Acompañamiento humano y rápido en asuntos familiares.",
        "items": ["Divorcio de mutuo acuerdo y contencioso", "Custodia y régimen de convivencia", "Pensión de alimentos", "Partición de bienes"],
    },
    {
        "id": "sucesiones", "icono": "fa-scroll", "color": "indigo", "nombre": "Herencias y Sucesiones",
        "desc": "Declaración sucesoral, únicos y universales herederos y partición.",
        "items": ["Declaración sucesoral ante el SENIAT", "Únicos y universales herederos", "Testamentos", "Partición de herencia"],
    },
    {
        "id": "laboral", "icono": "fa-briefcase", "color": "orange", "nombre": "Derecho Laboral",
        "desc": "Defensa del trabajador y asesoría a patronos según la LOTTT.",
        "items": ["Cálculo y cobro de prestaciones", "Despidos injustificados", "Accidentes laborales", "Reclamos ante la Inspectoría"],
    },
    {
        "id": "penal", "icono": "fa-gavel", "color": "purple", "nombre": "Derecho Penal",
        "desc": "Defensa técnica desde la audiencia de presentación. Atención 24/7.",
        "items": ["Audiencias de presentación", "Medidas cautelares", "Estafas y fraudes", "Recursos de apelación"],
    },
    {
        "id": "accidentes", "icono": "fa-car-burst", "color": "red", "nombre": "Accidentes de Tránsito",
        "desc": "Reclamos a seguros e indemnizaciones por daños y lesiones.",
        "items": ["Reclamos a aseguradoras", "Indemnizaciones", "Defensa de conductores", "Expedientes de tránsito"],
    },
    {
        "id": "mercantil", "icono": "fa-handshake", "color": "teal", "nombre": "Derecho Mercantil",
        "desc": "Creación y regularización de empresas y comercios.",
        "items": ["Firmas personales y C.A.", "Actas de asamblea", "Contratos comerciales", "Registro de marcas (SAPI)"],
    },
    {
        "id": "agrario", "icono": "fa-tractor", "color": "green", "nombre": "Derecho Agrario",
        "desc": "Regularización de tierras y fundos en el llano barinés.",
        "items": ["Trámites ante el INTI", "Títulos de adjudicación", "Conflictos de linderos", "Servidumbres de paso"],
    },
    {
        "id": "exterior", "icono": "fa-earth-americas", "color": "navy", "nombre": "Documentos para el Exterior",
        "desc": "Para venezolanos en el extranjero: lo hacemos por ti en Barinas.",
        "items": ["Partidas y actas certificadas", "Legalización y apostilla", "Poderes desde el exterior", "Envío internacional"],
    },
    {
        "id": "intt", "icono": "fa-id-card", "color": "gold", "nombre": "Trámites INTT",
        "desc": "Asesoría en licencias de conducir y documentos de vehículos.",
        "items": ["Licencia de conducir", "Certificado médico vial", "Título de propiedad de vehículos", "Traspasos"],
    },
]

# ---------------------------------------------------------------------------
# Bloques comunes
# ---------------------------------------------------------------------------

def head(titulo, descripcion, url, keywords, schema, robots="index, follow, max-image-preview:large"):
    return f"""<!DOCTYPE html>
<html lang="es-VE">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-RFW5F7YBBR"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-RFW5F7YBBR');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>{e(titulo)}</title>
    <meta name="description" content="{e(descripcion)}">
    <meta name="keywords" content="{e(keywords)}">
    <meta name="robots" content="{robots}">
    <link rel="canonical" href="{url}">
    <meta name="geo.region" content="VE-E">
    <meta name="geo.placename" content="Barinas, Venezuela">

    <!-- PWA / iOS -->
    <link rel="manifest" href="/manifest.webmanifest">
    <meta name="theme-color" content="#1a237e">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Abogados Barinas">
    <meta name="format-detection" content="telephone=yes">
    <link rel="icon" href="/assets/icons/favicon.svg" type="image/svg+xml">
    <link rel="icon" href="/assets/icons/favicon-32.png" sizes="32x32" type="image/png">
    <link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">

    <!-- Open Graph / Twitter -->
    <meta property="og:locale" content="es_VE">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Abogados en Barinas">
    <meta property="og:title" content="{e(titulo)}">
    <meta property="og:description" content="{e(descripcion)}">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{IMAGE}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Estatua de la justicia sobre el mapa de Venezuela - Abogados en Barinas">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{e(titulo)}">
    <meta name="twitter:description" content="{e(descripcion)}">
    <meta name="twitter:image" content="{IMAGE}">

    <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="/assets/css/ios.css">
    <link rel="preload" as="image" href="/assets/images/abogados-en-barinas-justicia-movil.webp" type="image/webp" media="(max-width: 767.98px)">
    <link rel="preload" as="image" href="/assets/images/abogados-en-barinas-justicia.webp" type="image/webp" media="(min-width: 768px)">

    <script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False, indent=2)}
    </script>
</head>
<body class="ios-page has-ios-tabbar">
"""


def nav():
    return f"""
    <header class="ios-nav">
        <div class="ios-wrap">
            <a class="ios-brand" href="/" aria-label="Abogados en Barinas, inicio">
                <span class="ios-brand-icon">AB</span>
                <span class="ios-brand-text"><strong>ABOGADOS BARINAS</strong><small>Directorio legal · SAREN en línea</small></span>
            </a>
            <nav class="ios-nav-links" aria-label="Principal">
                <a href="/">Inicio</a>
                <a href="/saren-en-linea/">SAREN en línea</a>
                <a href="/abogados/">Municipios</a>
                <a class="ios-nav-cta" aria-label="WhatsApp {PHONE_DISPLAY}" href="{wa('Hola, necesito un abogado en Barinas')}" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i><span class="ios-nav-num"> {PHONE_DISPLAY}</span></a>
            </nav>
        </div>
    </header>
"""


def tabbar(mensaje, activo=""):
    return f"""
    <!-- Barra inferior fija: Llamar / WhatsApp -->
    <nav class="ios-tabbar" aria-label="Contacto rápido">
        <a class="ios-tab ios-tab--call" href="tel:{PHONE_TEL}" aria-label="Llamar al {PHONE_DISPLAY}"><i class="fas fa-phone"></i><span>Llamar ahora</span></a>
        <a class="ios-tab ios-tab--wa" href="{wa(mensaje)}" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp"><i class="fab fa-whatsapp"></i><span>WhatsApp</span></a>
    </nav>
"""


def footer():
    munis = "\n".join(
        f'                        <li><a href="/abogados/{slugify(m["nombre"])}/">{e(m["nombre"])}</a></li>'
        for m in MUNICIPIOS
    )
    return f"""
    <footer class="ios-footer">
        <div class="ios-wrap">
            <div class="ios-footer-grid">
                <div>
                    <h3>ABOGADOS BARINAS</h3>
                    <p>Directorio legal especializado y gestión de trámites SAREN en línea en los 12 municipios del estado Barinas, Venezuela.</p>
                    <p><a href="tel:{PHONE_TEL}"><i class="fas fa-phone"></i> {PHONE_DISPLAY}</a><br>
                    <a href="{wa('Hola, necesito asesoría legal en Barinas')}" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i> WhatsApp {PHONE_DISPLAY}</a><br>
                    <i class="fas fa-clock"></i> Atención 24/7</p>
                </div>
                <div>
                    <h3>Servicios</h3>
                    <ul>
                        <li><a href="/saren-en-linea/">SAREN en línea</a></li>
                        <li><a href="/#directorio">Directorio de abogados</a></li>
                        <li><a href="/#servicios">Servicios legales</a></li>
                        <li><a href="/#faq">Preguntas frecuentes</a></li>
                        <li><a href="/abogados/">Todos los municipios y parroquias</a></li>
                    </ul>
                </div>
                <div>
                    <h3>Municipios</h3>
                    <ul>
{munis}
                    </ul>
                </div>
            </div>
            <div class="ios-footer-bottom">&copy; {datetime.date.today().year} Abogados en Barinas · Directorio Legal Especializado. La información de esta página es orientativa y no sustituye la asesoría de un abogado.<br>
                <span class="ios-credit">Página web desarrollada por <strong>Grupo 360 Soluciones</strong> · <a href="https://makeseo.app" target="_blank" rel="noopener">Diseño de páginas webs - SEO Local</a></span></div>
        </div>
    </footer>
"""


def end():
    return """
</body>
</html>
"""


def breadcrumb_html(items):
    lis = []
    for i, (nombre, url) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li aria-current="page">{e(nombre)}</li>')
        else:
            lis.append(f'<li><a href="{url}">{e(nombre)}</a></li>')
    return '<ol class="ios-breadcrumb">' + "".join(lis) + "</ol>"


def breadcrumb_schema(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
            for i, (n, u) in enumerate(items)
        ],
    }


def faq_schema(faqs):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }


def legal_service_schema(url, nombre, lugar_area, localidad, descripcion):
    return {
        "@type": "LegalService",
        "@id": url + "#servicio-legal",
        "name": nombre,
        "description": descripcion,
        "url": url,
        "image": IMAGE,
        "telephone": PHONE_TEL,
        "priceRange": "$$",
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00",
            "closes": "23:59",
        },
        "address": {
            "@type": "PostalAddress",
            "addressLocality": localidad,
            "addressRegion": "Barinas",
            "addressCountry": "VE",
        },
        "areaServed": lugar_area,
        "parentOrganization": {"@id": ORG_ID},
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": PHONE_TEL,
            "contactType": "customer service",
            "areaServed": "VE",
            "availableLanguage": ["es"],
        },
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Servicios legales",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "SAREN en línea: " + t}}
                for _, t, _ in SAREN_ITEMS
            ] + [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["nombre"], "description": s["desc"]}}
                for s in SERVICIOS
            ],
        },
    }


def saren_service_schema(url, lugar, area):
    return {
        "@type": "Service",
        "@id": url + "#saren-en-linea",
        "name": f"SAREN en línea en {lugar}",
        "serviceType": "Gestión de trámites del SAREN (Registros y Notarías)",
        "description": f"Gestión de citas SAREN en línea, copias certificadas, legalizaciones, poderes, compraventas y registro mercantil para {lugar}, estado Barinas.",
        "provider": {"@id": url + "#servicio-legal"},
        "areaServed": area,
        "availableChannel": {
            "@type": "ServiceChannel",
            "servicePhone": {"@type": "ContactPoint", "telephone": PHONE_TEL},
            "serviceUrl": url,
        },
    }


def webpage_schema(url, titulo, descripcion):
    return {
        "@type": "WebPage",
        "@id": url + "#pagina",
        "url": url,
        "name": titulo,
        "description": descripcion,
        "inLanguage": "es-VE",
        "isPartOf": {"@id": SITE + "/#sitio"},
        "about": {"@id": url + "#servicio-legal"},
        "dateModified": TODAY,
        "primaryImageOfPage": {"@type": "ImageObject", "url": IMAGE},
    }


def org_ref():
    return {
        "@type": "Organization",
        "@id": ORG_ID,
        "name": "Abogados en Barinas",
        "url": SITE + "/",
        "logo": SITE + "/assets/icons/icon-512.png",
        "telephone": PHONE_TEL,
    }


def area(muni, parroquia=None):
    estado = {"@type": "State", "name": "Barinas", "containedInPlace": {"@type": "Country", "name": "Venezuela"}}
    m = {"@type": "AdministrativeArea", "name": f"Municipio {muni['nombre']}", "containedInPlace": estado}
    if parroquia:
        return {"@type": "AdministrativeArea", "name": f"Parroquia {parroquia}", "containedInPlace": m}
    return m


# ---------------------------------------------------------------------------
# Secciones de contenido
# ---------------------------------------------------------------------------

def saren_section(lugar, mensaje):
    items = "\n".join(
        f"""                    <div class="ios-saren-item"><i class="fas {ic}"></i><div><strong>{e(t)}</strong><span>{e(d)}</span></div></div>"""
        for ic, t, d in SAREN_ITEMS
    )
    return f"""
        <section class="ios-section" id="saren-en-linea">
            <div class="ios-saren">
                <span class="ios-eyebrow"><i class="fas fa-star"></i> Servicio destacado</span>
                <h2>SAREN en línea para {e(lugar)}</h2>
                <p>Hacemos tus trámites del <strong>SAREN</strong> (Servicio Autónomo de Registros y Notarías) sin que pierdas días en colas: solicitamos la cita en línea, revisamos y visamos tus documentos, te acompañamos al Registro o la Notaría y hacemos seguimiento hasta la entrega. Ideal si vives en {e(lugar)} o si estás fuera de Venezuela.</p>
                <div class="ios-saren-grid">
{items}
                </div>
                <div class="ios-saren-actions">
                    <a class="ios-btn ios-btn--wa" href="{wa(mensaje)}" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i> Gestionar mi trámite SAREN</a>
                    <a class="ios-btn ios-btn--glass" href="tel:{PHONE_TEL}"><i class="fas fa-phone"></i> Llamar {PHONE_DISPLAY}</a>
                    <a class="ios-btn ios-btn--glass" href="/saren-en-linea/"><i class="fas fa-circle-info"></i> Guía SAREN en línea</a>
                </div>
            </div>
            <p class="ios-note">Somos gestores y abogados independientes; no somos una oficina del SAREN. Las tasas oficiales se pagan directamente al organismo.</p>
        </section>
"""


def servicios_section(lugar, titulo_lugar):
    cards = []
    for s in SERVICIOS:
        lis = "".join(f'<li><i class="fas fa-check"></i>{e(i)}</li>' for i in s["items"])
        msg = f"Hola, necesito un abogado de {s['nombre']} en {lugar}, Barinas"
        cards.append(f"""
                <article class="ios-card ios-service">
                    <div class="ios-icon ios-icon--{s['color']}"><i class="fas {s['icono']}"></i></div>
                    <h3>{e(s['nombre'])} en {e(titulo_lugar)}</h3>
                    <p>{e(s['desc'])}</p>
                    <ul>{lis}</ul>
                    <a class="ios-btn ios-btn--tinted" href="{wa(msg)}" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i> Consultar</a>
                </article>""")
    return f"""
        <section class="ios-section" id="servicios">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Servicios legales</span>
                <h2>Todos nuestros servicios en {e(titulo_lugar)}</h2>
                <p>Abogados verificados para cada área del derecho, con primera orientación gratuita por WhatsApp.</p>
            </div>
            <div class="ios-grid">{''.join(cards)}
            </div>
        </section>
"""


def pasos_section():
    return """
        <section class="ios-section">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Cómo funciona</span>
                <h2>Tu trámite en 3 pasos</h2>
            </div>
            <div class="ios-steps">
                <div class="ios-card ios-step"><h3>Escríbenos</h3><p>Cuéntanos tu caso por WhatsApp o llámanos. La primera orientación es gratuita.</p></div>
                <div class="ios-card ios-step"><h3>Recibe tu presupuesto</h3><p>Te indicamos requisitos, tiempos y costos antes de empezar. Sin sorpresas.</p></div>
                <div class="ios-card ios-step"><h3>Nosotros lo gestionamos</h3><p>Redactamos, visamos, tramitamos en el SAREN o el tribunal y te mantenemos informado.</p></div>
            </div>
        </section>
"""


def faq_section(faqs):
    items = "\n".join(
        f"""                <details{' open' if i == 0 else ''}><summary>{e(q)}</summary><div>{e(a)}</div></details>"""
        for i, (q, a) in enumerate(faqs)
    )
    return f"""
        <section class="ios-section ios-faq" id="faq">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Preguntas frecuentes</span>
                <h2>Dudas comunes</h2>
            </div>
{items}
        </section>
"""


def cta_section(lugar, mensaje):
    return f"""
        <section class="ios-section">
            <div class="ios-cta">
                <h2>¿Necesitas un abogado en {e(lugar)}?</h2>
                <p>Respuesta en minutos, consulta confidencial y abogados verificados. Atendemos todos los días.</p>
                <div class="ios-hero-actions">
                    <a class="ios-btn ios-btn--wa" href="{wa(mensaje)}" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i> Escribir por WhatsApp</a>
                    <a class="ios-btn ios-btn--call" href="tel:{PHONE_TEL}"><i class="fas fa-phone"></i> Llamar {PHONE_DISPLAY}</a>
                </div>
            </div>
        </section>
"""


def hero(chip, h1_html, lead, crumbs, mensaje, pills):
    pills_html = "".join(f"<span>{e(p)}</span>" for p in pills)
    return f"""
    <section class="ios-hero">
        <div class="ios-wrap">
            {breadcrumb_html(crumbs)}
            <span class="ios-chip"><i class="fas fa-location-dot"></i> {e(chip)}</span>
            <h1>{h1_html}</h1>
            <p class="lead">{lead}</p>
            <div class="ios-hero-actions">
                <a class="ios-btn ios-btn--wa" href="{wa(mensaje)}" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i> Consultar por WhatsApp</a>
                <a class="ios-btn ios-btn--glass" href="tel:{PHONE_TEL}"><i class="fas fa-phone"></i> Llamar ahora</a>
            </div>
            <div class="ios-hero-pills">{pills_html}</div>
        </div>
    </section>
"""


def municipios_chips(actual_slug=None):
    chips = []
    for m in MUNICIPIOS:
        s = slugify(m["nombre"])
        cur = ' class="is-current" aria-current="page"' if s == actual_slug else ""
        chips.append(f'<a href="/abogados/{s}/"{cur}>{e(m["nombre"])}</a>')
    return '<div class="ios-chips">' + "".join(chips) + "</div>"


# ---------------------------------------------------------------------------
# Textos con variaciones (evita contenido duplicado entre landings)
# ---------------------------------------------------------------------------

INTRO_MUNICIPIO = [
    "En el municipio {m}, {zona}, contar con un abogado de confianza marca la diferencia. Te ayudamos con divorcios, herencias, compraventas, problemas laborales, defensa penal y, sobre todo, con tus trámites del SAREN en línea, para que tus documentos queden listos sin que tengas que perder días en colas.",
    "Si vives en {capital} o en cualquiera de las {n} parroquias del municipio {m}, ponemos a tu disposición una red de abogados verificados del estado Barinas. El municipio es {zona}; por eso combinamos atención presencial con gestión en línea de Registros y Notarías (SAREN).",
    "Atendemos a personas, familias, productores y comerciantes del municipio {m} ({zona}). Desde la redacción de un contrato hasta la protocolización en el Registro, pasando por la regularización de tierras o una defensa penal urgente, te acompañamos en cada paso con atención inmediata por WhatsApp.",
]

INTRO_PARROQUIA = [
    "Vecinos de la parroquia {p}, en el municipio {m}, ahora tienen acceso directo a abogados verificados y a la gestión de trámites del SAREN en línea. Te orientamos gratis por WhatsApp y nos encargamos de tus documentos para que no tengas que trasladarte innecesariamente.",
    "¿Estás en la parroquia {p} y necesitas resolver un asunto legal? Atendemos divorcios, herencias, compraventas, títulos supletorios, casos laborales y penales, y hacemos tus trámites de Registros y Notarías (SAREN) en línea, con seguimiento hasta la entrega.",
    "Damos cobertura legal completa a la parroquia {p} del municipio {m}, estado Barinas. Nuestro equipo combina asesoría a distancia con gestiones presenciales en {capital} y en la ciudad de Barinas, donde se concentran los Registros, Notarías y tribunales.",
]


def faqs_municipio(m):
    nombre, capital = m["nombre"], m["capital"]
    return [
        (f"¿Puedo hacer trámites del SAREN en línea desde el municipio {nombre}?",
         f"Sí. Gestionamos citas SAREN en línea, copias certificadas, legalizaciones, poderes, compraventas y registros mercantiles para personas de {capital} y de todo el municipio {nombre}. Solo necesitas escribirnos por WhatsApp al {PHONE_DISPLAY} con tu caso."),
        (f"¿Qué tipo de abogados atienden en {capital}?",
         "Contamos con abogados de derecho civil, familia, sucesiones, laboral, penal, mercantil, agrario y accidentes de tránsito, además de gestores especializados en trámites del SAREN e INTT."),
        ("¿La primera consulta tiene costo?",
         "La primera orientación por WhatsApp o llamada es gratuita. Luego te enviamos un presupuesto claro con requisitos, tiempos y honorarios antes de iniciar cualquier trámite."),
        (f"Vivo fuera de Venezuela, ¿pueden hacer mis trámites en el municipio {nombre}?",
         "Sí. Podemos obtener partidas y actas certificadas, legalizar documentos, prepararlos para apostilla y gestionar poderes para que tu representante actúe en Venezuela. Te enviamos los documentos digitalizados o físicos."),
    ]


def faqs_parroquia(m, p):
    return [
        (f"¿Atienden trámites del SAREN en línea para la parroquia {p}?",
         f"Sí. Gestionamos tus trámites de Registros y Notarías (SAREN) en línea para la parroquia {p} del municipio {m['nombre']}: citas, copias certificadas, legalizaciones, poderes y compraventas, con seguimiento hasta la entrega."),
        (f"¿Tengo que viajar desde {p} hasta la ciudad de Barinas?",
         "En la mayoría de los casos no. La orientación, revisión de documentos y solicitud de citas se hacen a distancia; solo te indicaremos cuándo tu presencia es obligatoria, por ejemplo para firmar ante la Notaría o el Registro."),
        (f"¿Qué servicios legales ofrecen en la parroquia {p}?",
         "Divorcios, custodia y pensión de alimentos, herencias y declaraciones sucesorales, compraventa de inmuebles y vehículos, títulos supletorios, casos laborales, defensa penal, derecho agrario ante el INTI, registro de empresas y documentos para el exterior."),
        ("¿Cómo los contacto?",
         f"Por WhatsApp o llamada al {PHONE_DISPLAY}, todos los días. Usa los botones de Llamar y WhatsApp de la barra inferior para comunicarte al instante."),
    ]


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

def write(rel_path, contenido):
    destino = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(contenido)


def pagina_municipio(idx, m):
    ms = slugify(m["nombre"])
    path = f"/abogados/{ms}/"
    url = SITE + path
    nombre, capital, n = m["nombre"], m["capital"], len(m["parroquias"])
    lugar = f"el municipio {nombre}"
    titulo = f"Abogado en {capital}, Municipio {nombre} | SAREN en Línea Barinas"
    if len(titulo) > 70:
        titulo = f"Abogado en {capital}, Municipio {nombre} | Barinas"
    desc = (f"Abogado en {capital}, municipio {nombre}, Barinas: trámites SAREN en línea, divorcios, herencias, "
            f"compraventas, laboral y penal en {capital} y sus {n} parroquias. Consulta gratis por WhatsApp {PHONE_DISPLAY}.")
    keywords = (f"abogado en {capital.lower()}, abogado en {nombre.lower()}, abogados {capital.lower()}, saren en línea {capital.lower()}, "
                f"notaría {capital.lower()}, registro {capital.lower()}, divorcio {capital.lower()}, abogados barinas")
    crumbs = [("Inicio", "/"), ("Municipios", "/abogados/"), (f"Municipio {nombre}", path)]
    mensaje = f"Hola, necesito un abogado en el municipio {nombre} ({capital}), Barinas"
    msg_saren = f"Hola, necesito hacer un trámite SAREN en línea en el municipio {nombre}, Barinas"
    faqs = faqs_municipio(m)
    schema = {"@context": "https://schema.org", "@graph": [
        org_ref(),
        webpage_schema(url, titulo, desc),
        legal_service_schema(url, f"Abogado en {capital}, Municipio {nombre} - Abogados en Barinas", area(m), capital, desc),
        saren_service_schema(url, f"el municipio {nombre}", area(m)),
        breadcrumb_schema(crumbs),
        faq_schema(faqs),
    ]}
    intro = INTRO_MUNICIPIO[idx % len(INTRO_MUNICIPIO)].format(m=nombre, capital=capital, n=n, zona=m["zona"])

    parroquias_li = "\n".join(
        f'                    <li><a href="{path}{slugify(p)}/"><span>Abogado en {e(p)}</span><small>Parroquia</small></a></li>'
        for p in m["parroquias"]
    )

    body = hero(
        f"Municipio {nombre} · Estado Barinas",
        f"Abogado en <span>{e(capital)}</span>, Municipio {e(nombre)}",
        f"Trámites <strong>SAREN en línea</strong>, asesoría legal y defensa en {e(capital)} y sus {n} parroquias. Primera consulta gratis.",
        crumbs, mensaje,
        ["✓ SAREN en línea", "✓ Atención 24/7", "✓ Consulta gratis", f"✓ {n} parroquias"],
    )
    body += f"""
    <main class="ios-wrap">
        <section class="ios-section">
            <div class="ios-card ios-prose">
                <p>{e(intro)}</p>
                <p>Capital del municipio: <strong>{e(capital)}</strong>. Parroquias atendidas: {e(', '.join(m['parroquias']))}.</p>
            </div>
        </section>
{saren_section(f'el municipio {nombre}', msg_saren)}
{servicios_section(f'el municipio {nombre}', nombre)}
        <section class="ios-section" id="parroquias">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Cobertura</span>
                <h2>Parroquias del municipio {e(nombre)}</h2>
                <p>Elige tu parroquia para ver los servicios disponibles cerca de ti.</p>
            </div>
            <ul class="ios-list">
{parroquias_li}
            </ul>
        </section>
{pasos_section()}
{faq_section(faqs)}
        <section class="ios-section">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Estado Barinas</span>
                <h2>Otros municipios</h2>
            </div>
            {municipios_chips(ms)}
        </section>
{cta_section(f'el municipio {nombre}', mensaje)}
    </main>
"""
    write(f"abogados/{ms}/index.html",
          head(titulo, desc, url, keywords, schema) + nav() + body + footer() + tabbar(mensaje) + end())
    return path


def pagina_parroquia(idx, m, p):
    ms, ps = slugify(m["nombre"]), slugify(p)
    path = f"/abogados/{ms}/{ps}/"
    url = SITE + path
    nombre, capital = m["nombre"], m["capital"]
    titulo = f"Abogado en {p}, Municipio {nombre} | SAREN en Línea Barinas"
    if len(titulo) > 70:
        titulo = f"Abogado en {p}, Municipio {nombre} | Barinas"
    if len(titulo) > 70:
        titulo = f"Abogado en {p}, Municipio {nombre}"
    desc = (f"Abogado en {p}, municipio {nombre}: abogados en la parroquia {p}, municipio {nombre}, Barinas. SAREN en línea, divorcios, herencias, "
            f"compraventas, laboral, penal y agrario. Consulta gratis por WhatsApp {PHONE_DISPLAY}.")
    keywords = (f"abogado en {p.lower()}, abogados en {p.lower()}, abogado {p.lower()} barinas, saren en línea {p.lower()}, "
                f"notaría {capital.lower()}, abogados {nombre.lower()}, trámites legales {p.lower()}")
    crumbs = [("Inicio", "/"), ("Municipios", "/abogados/"), (f"Municipio {nombre}", f"/abogados/{ms}/"), (f"Parroquia {p}", path)]
    mensaje = f"Hola, necesito un abogado en la parroquia {p}, municipio {nombre}, Barinas"
    msg_saren = f"Hola, necesito un trámite SAREN en línea en la parroquia {p}, municipio {nombre}, Barinas"
    faqs = faqs_parroquia(m, p)
    schema = {"@context": "https://schema.org", "@graph": [
        org_ref(),
        webpage_schema(url, titulo, desc),
        legal_service_schema(url, f"Abogado en {p}, Municipio {nombre} - Abogados en Barinas", area(m, p), capital, desc),
        saren_service_schema(url, f"la parroquia {p}", area(m, p)),
        breadcrumb_schema(crumbs),
        faq_schema(faqs),
    ]}
    intro = INTRO_PARROQUIA[idx % len(INTRO_PARROQUIA)].format(p=p, m=nombre, capital=capital)

    hermanas = [x for x in m["parroquias"] if x != p]
    hermanas_html = "".join(f'<a href="/abogados/{ms}/{slugify(x)}/">{e(x)}</a>' for x in hermanas)
    hermanas_block = ""
    if hermanas:
        hermanas_block = f"""
        <section class="ios-section">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Municipio {e(nombre)}</span>
                <h2>Otras parroquias cercanas</h2>
            </div>
            <div class="ios-chips">{hermanas_html}<a href="/abogados/{ms}/">Ver municipio {e(nombre)} ›</a></div>
        </section>
"""

    body = hero(
        f"Parroquia {p} · Municipio {nombre}",
        f"Abogado en <span>{e(p)}</span>, Municipio {e(nombre)}",
        f"Servicios legales y trámites <strong>SAREN en línea</strong> para la parroquia {e(p)}, municipio {e(nombre)}, estado Barinas.",
        crumbs, mensaje,
        ["✓ SAREN en línea", "✓ Respuesta en minutos", "✓ Consulta gratis", "✓ Abogados verificados"],
    )
    body += f"""
    <main class="ios-wrap">
        <section class="ios-section">
            <div class="ios-card ios-prose">
                <p>{e(intro)}</p>
                <p>Ubicación: parroquia <strong>{e(p)}</strong>, municipio <strong>{e(nombre)}</strong> (capital {e(capital)}), estado Barinas, Venezuela.</p>
            </div>
        </section>
{saren_section(f'la parroquia {p}', msg_saren)}
{servicios_section(f'la parroquia {p}', p)}
{pasos_section()}
{faq_section(faqs)}
{hermanas_block}
        <section class="ios-section">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Estado Barinas</span>
                <h2>Municipios con cobertura</h2>
            </div>
            {municipios_chips(ms)}
        </section>
{cta_section(f'la parroquia {p}', mensaje)}
    </main>
"""
    write(f"abogados/{ms}/{ps}/index.html",
          head(titulo, desc, url, keywords, schema) + nav() + body + footer() + tabbar(mensaje) + end())
    return path


def pagina_indice():
    path = "/abogados/"
    url = SITE + path
    total_p = sum(len(m["parroquias"]) for m in MUNICIPIOS)
    titulo = "Abogados por Municipio y Parroquia en Barinas | SAREN en Línea"
    desc = (f"Encuentra abogados en los {len(MUNICIPIOS)} municipios y {total_p} parroquias del estado Barinas. "
            "Trámites SAREN en línea, divorcios, herencias, laboral y penal. Consulta gratis por WhatsApp.")
    crumbs = [("Inicio", "/"), ("Municipios", path)]
    mensaje = "Hola, necesito un abogado en el estado Barinas"
    item_list = {
        "@type": "ItemList",
        "name": "Municipios del estado Barinas",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": f"Abogados en {m['nombre']}",
             "url": f"{SITE}/abogados/{slugify(m['nombre'])}/"}
            for i, m in enumerate(MUNICIPIOS)
        ],
    }
    schema = {"@context": "https://schema.org", "@graph": [
        org_ref(),
        {"@type": "CollectionPage", "@id": url + "#pagina", "url": url, "name": titulo, "description": desc,
         "inLanguage": "es-VE", "isPartOf": {"@id": SITE + "/#sitio"}, "dateModified": TODAY},
        item_list,
        breadcrumb_schema(crumbs),
    ]}
    bloques = []
    for m in MUNICIPIOS:
        ms = slugify(m["nombre"])
        lis = "\n".join(
            f'                    <li><a href="/abogados/{ms}/{slugify(p)}/"><span>{e(p)}</span><small>Parroquia</small></a></li>'
            for p in m["parroquias"]
        )
        bloques.append(f"""
            <div>
                <h2 style="font-size:1.1rem;margin:0 4px 8px;">Municipio {e(m['nombre'])} <small style="color:var(--ios-label-2);font-weight:500;">· {e(m['capital'])}</small></h2>
                <ul class="ios-list">
                    <li><a href="/abogados/{ms}/"><strong>Todo el municipio {e(m['nombre'])}</strong><small>{len(m['parroquias'])} parroquias</small></a></li>
{lis}
                </ul>
            </div>""")
    body = hero(
        "Estado Barinas · Venezuela",
        "Abogados por <span>municipio y parroquia</span>",
        f"Cobertura en los {len(MUNICIPIOS)} municipios y {total_p} parroquias del estado Barinas, con trámites <strong>SAREN en línea</strong>.",
        crumbs, mensaje,
        [f"✓ {len(MUNICIPIOS)} municipios", f"✓ {total_p} parroquias", "✓ SAREN en línea", "✓ Atención 24/7"],
    )
    body += f"""
    <main class="ios-wrap">
{saren_section('todo el estado Barinas', 'Hola, necesito hacer un trámite SAREN en línea en Barinas')}
        <section class="ios-section">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Cobertura</span>
                <h2>Elige tu municipio o parroquia</h2>
            </div>
            <div class="ios-columns">{''.join(bloques)}
            </div>
        </section>
{cta_section('el estado Barinas', mensaje)}
    </main>
"""
    write("abogados/index.html",
          head(titulo, desc, url, "abogados barinas, municipios barinas, parroquias barinas, saren en línea barinas", schema)
          + nav() + body + footer() + tabbar(mensaje) + end())
    return path


def pagina_saren():
    path = "/saren-en-linea/"
    url = SITE + path
    titulo = "SAREN en Línea Barinas | Citas, Registros y Notarías con Abogado"
    desc = ("Gestión de trámites SAREN en línea en Barinas: citas en Registros y Notarías, copias certificadas, "
            "legalizaciones, poderes, compraventas y registro mercantil. Abogados verificados. WhatsApp " + PHONE_DISPLAY + ".")
    crumbs = [("Inicio", "/"), ("SAREN en línea", path)]
    mensaje = "Hola, necesito ayuda con un trámite SAREN en línea en Barinas"
    faqs = [
        ("¿Qué es el SAREN en línea?",
         "Es la plataforma del Servicio Autónomo de Registros y Notarías de Venezuela para solicitar citas y gestionar trámites de Registros Principales, Públicos, Mercantiles y Notarías. Nosotros te ayudamos a usarla correctamente y gestionamos el trámite completo por ti."),
        ("¿Qué trámites del SAREN pueden gestionar en Barinas?",
         "Citas en línea, copias certificadas de actas, legalizaciones, autenticación de poderes y declaraciones, compraventas de inmuebles y vehículos, constitución de firmas personales y compañías, actas de asamblea, títulos supletorios y registros de documentos sucesorales."),
        ("¿Necesito un abogado para un trámite del SAREN?",
         "Muchos documentos (compraventas, poderes, actas de asamblea, constitución de empresas) deben estar redactados y visados por un abogado para que el Registro o la Notaría los reciba. Nuestros abogados redactan y visan tus documentos."),
        ("¿Puedo hacer mi trámite SAREN si estoy en el exterior?",
         "Sí. Podemos obtener tus actas certificadas, legalizarlas y prepararlas para apostilla, o redactar un poder para que un familiar te represente en Venezuela."),
        ("¿En qué municipios de Barinas atienden?",
         "En los 12 municipios del estado: Barinas, Alberto Arvelo Torrealba, Andrés Eloy Blanco, Antonio José de Sucre, Arismendi, Bolívar, Cruz Paredes, Ezequiel Zamora, Obispos, Pedraza, Rojas y Sosa."),
    ]
    area_estado = {"@type": "State", "name": "Barinas", "containedInPlace": {"@type": "Country", "name": "Venezuela"}}
    schema = {"@context": "https://schema.org", "@graph": [
        org_ref(),
        webpage_schema(url, titulo, desc),
        legal_service_schema(url, "SAREN en línea Barinas - Abogados en Barinas", area_estado, "Barinas", desc),
        saren_service_schema(url, "el estado Barinas", area_estado),
        {
            "@type": "HowTo",
            "name": "Cómo hacer un trámite SAREN en línea en Barinas",
            "description": "Pasos para gestionar un trámite de Registros y Notarías (SAREN) con apoyo de abogado.",
            "step": [
                {"@type": "HowToStep", "position": 1, "name": "Envía tu caso", "text": "Escríbenos por WhatsApp indicando el trámite y la ciudad o municipio."},
                {"@type": "HowToStep", "position": 2, "name": "Revisión de recaudos", "text": "Revisamos documentos, cédulas y requisitos; redactamos y visamos lo necesario."},
                {"@type": "HowToStep", "position": 3, "name": "Cita SAREN en línea", "text": "Solicitamos la cita en el portal del SAREN y te indicamos el pago de tasas oficiales."},
                {"@type": "HowToStep", "position": 4, "name": "Otorgamiento y entrega", "text": "Te acompañamos a la firma y retiramos el documento registrado o notariado."},
            ],
        },
        breadcrumb_schema(crumbs),
        faq_schema(faqs),
    ]}
    body = hero(
        "Registros y Notarías · Barinas",
        "<span>SAREN en línea</span> en Barinas, sin colas",
        "Citas, documentos visados por abogado, legalizaciones, poderes, compraventas y registro mercantil. Lo gestionamos por ti en cualquier municipio de Barinas o desde el exterior.",
        crumbs, mensaje,
        ["✓ Documentos visados", "✓ Citas en línea", "✓ Seguimiento hasta la entrega", "✓ Atención desde el exterior"],
    )
    body += f"""
    <main class="ios-wrap">
{saren_section('Barinas', mensaje)}
        <section class="ios-section">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Paso a paso</span>
                <h2>Cómo gestionamos tu trámite SAREN</h2>
            </div>
            <div class="ios-steps">
                <div class="ios-card ios-step"><h3>Envía tu caso</h3><p>Escríbenos por WhatsApp indicando el trámite y tu municipio.</p></div>
                <div class="ios-card ios-step"><h3>Revisión de recaudos</h3><p>Revisamos tus documentos, redactamos y visamos lo necesario.</p></div>
                <div class="ios-card ios-step"><h3>Cita SAREN en línea</h3><p>Solicitamos la cita en el portal oficial y te guiamos con las tasas.</p></div>
                <div class="ios-card ios-step"><h3>Firma y entrega</h3><p>Te acompañamos al otorgamiento y retiramos tu documento.</p></div>
            </div>
        </section>
        <section class="ios-section">
            <div class="ios-card ios-prose">
                <h2 style="font-size:1.2rem;margin:0 0 8px;">Recaudos habituales</h2>
                <p>Cédula de identidad vigente (y RIF cuando aplica), documentos originales y copias, documento redactado y visado por abogado, comprobante de pago de las tasas y, según el trámite, documento de propiedad, ficha catastral, solvencias o acta constitutiva. Te enviamos la lista exacta para tu caso antes de empezar.</p>
                <p>Portal oficial: <a href="https://www.saren.gob.ve/" target="_blank" rel="noopener">saren.gob.ve</a>. Somos gestores y abogados independientes; no somos una oficina del SAREN.</p>
            </div>
        </section>
{servicios_section('Barinas', 'Barinas')}
{faq_section(faqs)}
        <section class="ios-section">
            <div class="ios-section-head">
                <span class="ios-eyebrow">Cobertura</span>
                <h2>SAREN en línea en todos los municipios</h2>
            </div>
            {municipios_chips()}
        </section>
{cta_section('Barinas', mensaje)}
    </main>
"""
    write("saren-en-linea/index.html",
          head(titulo, desc, url, "saren en línea, saren barinas, citas saren, notaría barinas, registro barinas, legalización barinas", schema)
          + nav() + body + footer() + tabbar(mensaje, "saren") + end())
    return path


def pagina_404():
    mensaje = "Hola, necesito un abogado en Barinas"
    schema = {"@context": "https://schema.org", "@graph": [org_ref()]}
    body = hero(
        "Error 404",
        "Página <span>no encontrada</span>",
        "La página que buscas no existe o cambió de dirección. Escríbenos y te ayudamos de inmediato.",
        [("Inicio", "/"), ("404", "/404.html")], mensaje,
        ["✓ Atención 24/7"],
    )
    body += f"""
    <main class="ios-wrap">
        <section class="ios-section">
            <ul class="ios-list">
                <li><a href="/">Ir al inicio</a></li>
                <li><a href="/saren-en-linea/">SAREN en línea</a></li>
                <li><a href="/abogados/">Abogados por municipio y parroquia</a></li>
            </ul>
        </section>
    </main>
"""
    write("404.html", head("Página no encontrada | Abogados en Barinas", "Página no encontrada.", SITE + "/404.html", "",
                           schema, robots="noindex, follow") + nav() + body + footer() + tabbar(mensaje) + end())


def sitemap(rutas):
    urls = []
    for ruta, prio, freq in rutas:
        urls.append(f"""   <url>
      <loc>{SITE}{ruta}</loc>
      <lastmod>{TODAY}</lastmod>
      <changefreq>{freq}</changefreq>
      <priority>{prio}</priority>
   </url>""")
    contenido = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 + "\n".join(urls) + "\n</urlset>\n")
    write("sitemap.xml", contenido)


def main():
    rutas = [("/", "1.0", "weekly")]
    rutas.append((pagina_saren(), "0.9", "weekly"))
    rutas.append((pagina_indice(), "0.9", "weekly"))
    contador = 0
    for i, m in enumerate(MUNICIPIOS):
        rutas.append((pagina_municipio(i, m), "0.8", "monthly"))
        for p in m["parroquias"]:
            rutas.append((pagina_parroquia(contador, m, p), "0.7", "monthly"))
            contador += 1
    pagina_404()
    sitemap(rutas)
    print(f"Generadas {len(rutas) - 1} landings ({len(MUNICIPIOS)} municipios, {contador} parroquias) + sitemap.xml + 404.html")


if __name__ == "__main__":
    main()
