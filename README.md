# Abogados en Barinas · Directorio Legal Especializado

Sitio estático del directorio de abogados del estado Barinas (Venezuela), publicado en Cloudflare Pages:
**https://abogadosenbarinas.pages.dev/**

Todas las páginas se **generan** con `tools/build_site.py` (Python 3, sin dependencias). No edites los `.html`
generados a mano: cambia el script (o `src/home.html`) y vuelve a ejecutarlo.

## Datos del negocio

Viven en **un solo lugar**: el diccionario `NEGOCIO` de `tools/build_site.py`. Todo lo publicado (páginas, pie,
schema, mensajes de WhatsApp) sale de ahí.

| Dato | Valor actual |
|------|--------------|
| Nombre | Abogados en Barinas |
| Teléfono / WhatsApp (único número) | 0416-7775771 · `wa.me/584167775771` |
| Dirección | Sin oficina pública → negocio con área de servicio (sin `address` en el schema) |
| Área de servicio | Los 12 municipios del estado Barinas, Venezuela |
| Horario | Atención 24/7 por WhatsApp |
| Año de inicio | 2024 → copyright «© 2024–{año actual}» |
| Redes sociales | Ninguna (no se muestran íconos ni `sameAs`) |
| Código de WhatsApp | `b33` (abogadosvalencia.pages.dev usa `g33`) |
| Google Analytics | `G-RFW5F7YBBR` (vacío = sin Analytics) |

> El negocio **no** tiene ficha de Google Business: el sitio no enlaza a Google Maps ni muestra opiniones o
> calificaciones, y el schema no usa `aggregateRating` ni `Review` (el script lo valida).

## Uso del script

```bash
python3 tools/build_site.py           # genera/actualiza las páginas (solo escribe lo que cambia)
python3 tools/build_site.py --check   # solo valida; sale con código 1 si algo falla
node tools/test_whatsapp.js           # prueba en Chromium (Playwright) los mensajes de WhatsApp
```

- **Idempotente:** una segunda ejecución informa `Archivos modificados: 0`.
- La fecha de `lastmod` del sitemap y `dateModified` es la del día en que se genera. `--check` valida contra
  la fecha del `sitemap.xml` actual; `BUILD_DATE=AAAA-MM-DD` fuerza una fecha.

### Qué valida (`--check` y también al generar)

- Un solo `<h1>` por página; en cada landing de municipio empieza por «Abogados en {Municipio}».
- `canonical` correcto (URL limpia de Cloudflare Pages) en cada página indexable.
- Enlaces internos, anclas y recursos (`css`, `js`, imágenes) existentes; nada de `href="#"`.
- Todos los enlaces `wa.me` van al número del negocio y su mensaje **termina con el código**; `assets/site.js`
  añade el código en `waUrl()`, la única función que arma enlaces de WhatsApp.
- JSON-LD válido con `LegalService`, `WebSite`, `WebPage`, `BreadcrumbList`, `Service` (municipios y
  especialidades) y `FAQPage` (portada, generado a partir de las preguntas visibles).
- `sitemap.xml` con todas las páginas indexables y el `lastmod` de la fecha de generación, sin URLs sobrantes ni
  páginas huérfanas; `robots.txt` apunta al sitemap; no hay HTML sin generar.
- Ninguna landing menciona otro municipio y ninguna es una copia de otra (similitud < 75 %).
- Teléfono, horario y copyright idénticos en todas las páginas; ningún otro número de teléfono.
- Ninguna mención ni enlace a Google Maps u opiniones de Google, ni al dominio abogadosvalencia.
- Botón «Reservar cita por WhatsApp» y bloque «Trámites SAREN en línea» presentes en todas las páginas.

## Estructura

```
├── tools/
│   ├── build_site.py          # NEGOCIO + contenido + plantilla + validación
│   └── test_whatsapp.js       # prueba en navegador de los mensajes de WhatsApp
├── src/home.html              # contenido de la portada (plantilla con {{TEL}}, {{MUNICIPIO_TAGS}}…)
├── style.css                  # estilos compartidos (editable a mano)
├── images/                    # imágenes alojadas en este repositorio
├── _headers, _redirects       # configuración de Cloudflare Pages
│
│   (generados por el script)
├── index.html                 # /
├── servicios/index.html       # /servicios/            índice de especialidades
├── servicios/*.html           # /servicios/{slug}      9 especialidades
├── municipios/index.html      # /municipios/           índice de municipios
├── municipios/*.html          # /municipios/{slug}     12 landings
├── quienes-somos.html         # /quienes-somos
├── contacto.html              # /contacto
├── politica-de-privacidad.html# /politica-de-privacidad (Constitución, arts. 28 y 60)
├── 404.html                   # noindex, fuera del sitemap
├── assets/site.js             # modal y mensajes de WhatsApp, menú móvil
├── sitemap.xml
└── robots.txt
```

### Especialidades (`/servicios/…`)

`derecho-civil`, `derecho-de-familia` (divorcio y custodia), `derecho-laboral`, `derecho-penal`,
`accidentes-de-transito`, `derecho-mercantil`, `derecho-agrario` (INTI), `tramites-saren` (SAREN en línea,
también en el menú) y `legalizacion-apostilla`.

### Municipios (`/municipios/…`)

| Municipio | Capital | URL |
|-----------|---------|-----|
| Barinas | Barinas | `/municipios/barinas` |
| Alberto Arvelo Torrealba | Sabaneta | `/municipios/alberto-arvelo-torrealba` |
| Andrés Eloy Blanco | El Cantón | `/municipios/andres-eloy-blanco` |
| Antonio José de Sucre | Socopó | `/municipios/antonio-jose-de-sucre` |
| Arismendi | Arismendi | `/municipios/arismendi` |
| Bolívar | Barinitas | `/municipios/bolivar` |
| Cruz Paredes | Barrancas | `/municipios/cruz-paredes` |
| Ezequiel Zamora | Santa Bárbara | `/municipios/ezequiel-zamora` |
| Obispos | Obispos | `/municipios/obispos` |
| Pedraza | Ciudad Bolivia | `/municipios/pedraza` |
| Rojas | Libertad | `/municipios/rojas` |
| Sosa | Ciudad de Nutrias | `/municipios/sosa` |

## Cómo hacer cambios

1. **Datos del negocio** (teléfono, horario, redes, código, GA…): edita `NEGOCIO`.
2. **Textos** de municipios o especialidades: edita `MUNICIPIOS` / `ESPECIALIDADES` en el script.
3. **Portada**: edita `src/home.html` (usa `{{TEL}}` y `{{TEL_HREF}}` en lugar del número).
4. Ejecuta `python3 tools/build_site.py`, revisa el resultado y haz commit de todo (script y generados).

## Despliegue

Cloudflare Pages publica la raíz del repositorio (sin build command, directorio de salida `/`). Cloudflare Pages
no usa `.htaccess`; por eso se eliminó `.htaccess.txt` (además forzaba `www`, que no existe en `*.pages.dev`).
Las redirecciones van en `_redirects` y las cabeceras en `_headers`.

Después de desplegar, valida en https://search.google.com/test/rich-results y envía `sitemap.xml` en Google
Search Console.
