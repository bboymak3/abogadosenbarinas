# Abogados en Barinas · Directorio Legal Especializado

Sitio estático del directorio de abogados del estado Barinas (Venezuela), publicado en Cloudflare Pages:

**🌐 https://abogadosenbarinas.pages.dev/**

Conecta a personas y empresas con abogados especialistas en derecho civil, familia, laboral, penal, mercantil, agrario, accidentes de tránsito y trámites SAREN/INTT, con atención por WhatsApp (**0416-7775771**) en los 12 municipios del estado.

## Páginas

| URL | Archivo | Tipo de schema |
|-----|---------|----------------|
| `/` | `index.html` | `WebSite`, `LegalService` + `Organization`, `WebPage`, `FAQPage` |
| `/quienes-somos` | `quienes-somos.html` | `AboutPage`, `BreadcrumbList` |
| `/contacto` | `contacto.html` | `ContactPage`, `BreadcrumbList` |
| `/politica-de-privacidad` | `politica-de-privacidad.html` | `WebPage`, `BreadcrumbList` |
| cualquier ruta inexistente | `404.html` | `noindex` |

Cloudflare Pages sirve `pagina.html` como `/pagina` (sin extensión), así que los enlaces internos, los canonical y el sitemap usan las URLs limpias.

## Estructura

```
├── index.html                  # Portada: directorio, guía legal, servicios, FAQ
├── quienes-somos.html          # Misión, visión, valores y cómo trabajamos
├── contacto.html               # WhatsApp, teléfono, horario, contacto por especialidad
├── politica-de-privacidad.html # Privacidad, cookies y aviso legal (ley venezolana)
├── 404.html                    # Página de error
├── style.css                   # Hoja de estilos compartida por todas las páginas
├── sitemap.xml                 # Sitemap (con extensión de imagen)
├── robots.txt
├── _headers                    # Cabeceras de seguridad y caché (Cloudflare Pages)
└── _redirects                  # Alias 301: /nosotros, /privacidad, /contactanos…
```

## SEO y fragmentos enriquecidos

- **JSON-LD** con `@graph` enlazado por `@id` (`/#organization`, `/#website`) en todas las páginas.
- **FAQPage** con las mismas 5 preguntas que se ven en la sección FAQ de la portada. Si cambias una pregunta visible, cámbiala también en el JSON-LD.
- **BreadcrumbList** en las páginas internas, con sus migas de pan visibles.
- Meta `description`, `robots`, Open Graph, Twitter Card, `hreflang es-VE` y metadatos geográficos (`VE-E`, Barinas).
- `sitemap.xml` con `lastmod` actualizado; `robots.txt` apunta al sitemap.
- `404.html` evita que Cloudflare Pages devuelva la portada para cualquier URL inexistente (contenido duplicado).

Valida los cambios en:
- https://search.google.com/test/rich-results
- https://validator.schema.org/

## Desarrollo local

No hay paso de compilación. Para verlo en local:

```bash
python3 -m http.server 8000
# abre http://localhost:8000/
```

Dependencias por CDN: Bootstrap 5.3, Font Awesome 6.4 y AOS 2.3 (animaciones; la página funciona aunque AOS no cargue).

## Despliegue

Cloudflare Pages publica el contenido de la raíz del repositorio (sin build command, output directory `/`).
Después de cada cambio de contenido, actualiza `lastmod` en `sitemap.xml` y `dateModified` en el JSON-LD.

## Contacto

- WhatsApp: [0416-7775771](https://wa.me/584167775771)
- Teléfono: +58 416-7775771
- Cobertura: los 12 municipios del estado Barinas, Venezuela
