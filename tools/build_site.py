#!/usr/bin/env python3
"""Genera y valida el sitio estático de Abogados en Barinas.

Uso:
    python3 tools/build_site.py           # genera las páginas (solo escribe lo que cambia)
    python3 tools/build_site.py --check   # solo valida; sale con código 1 si algo falla

Sin dependencias externas (solo biblioteca estándar de Python 3.8+).

Los datos del negocio viven ÚNICAMENTE en el diccionario NEGOCIO de este archivo.
Las páginas .html, assets/site.js, sitemap.xml y robots.txt son archivos generados:
no los edites a mano; cambia este script (o src/home.html) y vuelve a ejecutarlo.
"""

import datetime
import difflib
import html
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import parse_qs, quote, unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# DATOS DEL NEGOCIO: única fuente de verdad. Todo lo publicado sale de aquí.
# ---------------------------------------------------------------------------
NEGOCIO = {
    "nombre": "Abogados en Barinas",
    "nombre_largo": "Abogados en Barinas - Directorio Legal Especializado",
    "dominio": "https://abogadosenbarinas.pages.dev",
    # Único número publicado (teléfono y WhatsApp).
    "telefono": "0416-7775771",
    "telefono_e164": "+584167775771",
    "whatsapp": "584167775771",
    # Código que se añade al final de todos los mensajes de WhatsApp de esta web
    # (abogadosvalencia.pages.dev usa "g33").
    "codigo_whatsapp": "b33",
    # Sin oficina pública: negocio con área de servicio (no se publica address).
    "direccion": None,
    "area_servicio": "Los 12 municipios del estado Barinas, Venezuela",
    "horario": "Atención 24/7 por WhatsApp",
    "horario_schema": [
        {
            "dias": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "abre": "00:00",
            "cierra": "23:59",
        }
    ],
    "anio_inicio": 2024,
    # URLs de redes sociales reales. Vacío = no se muestran íconos ni sameAs.
    "redes": {},
    # Google Analytics. Cadena vacía = sin Analytics.
    "ga_id": "G-RFW5F7YBBR",
    "imagen": "/images/abogados-en-barinas.jpg",
    "imagen_ancho": 498,
    "imagen_alto": 332,
}

# Municipios del estado Barinas (12) con su capital.
MUNICIPIOS = [
    {
        "slug": "barinas", "nombre": "Barinas", "capital": "Barinas",
        "intro": "El municipio Barinas es la capital del estado y el centro judicial y administrativo de la región. Aquí funcionan los tribunales del Circuito Judicial del estado, los registros públicos y mercantiles, las notarías y las oficinas regionales de los organismos nacionales, por lo que buena parte de los trámites legales de todo el estado termina en esta ciudad.",
        "contexto": "Por su tamaño y actividad comercial, en la ciudad son frecuentes los juicios civiles y mercantiles, los divorcios y procesos de familia, la defensa penal ante los tribunales de control y las gestiones de registro y notaría. Un abogado que conozca los despachos de la capital te ahorra idas y vueltas.",
        "casos": [
            ("Defensa penal inmediata", "Asistencia desde la audiencia de presentación ante los tribunales de control."),
            ("Divorcios y familia", "Divorcio de mutuo acuerdo o contencioso, custodia y obligación de manutención."),
            ("Empresas y comercio", "Constitución de compañías, firmas personales y actas de asamblea ante el Registro Mercantil."),
            ("Compraventa de inmuebles", "Revisión de documentos, redacción del contrato y protocolización en el registro."),
        ],
    },
    {
        "slug": "alberto-arvelo-torrealba", "nombre": "Alberto Arvelo Torrealba", "capital": "Sabaneta",
        "intro": "El municipio Alberto Arvelo Torrealba, con capital en Sabaneta, es una zona de tradición agrícola donde el cultivo de la caña de azúcar y las pequeñas y medianas fincas marcan la vida económica y, con ella, buena parte de las consultas legales.",
        "contexto": "En Sabaneta las dudas más comunes giran en torno a la tenencia de la tierra, las relaciones de trabajo en el campo y la agroindustria, y el reparto de fincas cuando fallece el propietario. También atendemos trámites de documentos para familiares que viven fuera del país.",
        "casos": [
            ("Tierras y regularización", "Acompañamiento ante el INTI para títulos de adjudicación y cartas agrarias."),
            ("Derecho laboral en el campo", "Cálculo y reclamo de prestaciones sociales de trabajadores agrícolas y de la agroindustria."),
            ("Sucesiones de fincas", "Declaración sucesoral y partición de bienes rurales entre herederos."),
            ("Documentos para el exterior", "Partidas, legalizaciones y apostilla para quienes emigraron."),
        ],
    },
    {
        "slug": "andres-eloy-blanco", "nombre": "Andrés Eloy Blanco", "capital": "El Cantón",
        "intro": "El municipio Andrés Eloy Blanco, cuya capital es El Cantón, es un municipio rural de vocación agropecuaria. Muchos de sus habitantes viven en caseríos alejados de los tribunales, por lo que la orientación a distancia por WhatsApp es especialmente útil.",
        "contexto": "Aquí son habituales las consultas sobre bienhechurías construidas sin papeles, compraventas de lotes y parcelas, obligación de manutención de hijos y poderes para que un familiar haga gestiones en nombre de otro.",
        "casos": [
            ("Títulos supletorios", "Documento que acredita la propiedad de bienhechurías (casas y mejoras) para poder venderlas o heredarlas."),
            ("Compraventa de parcelas", "Revisión de la cadena de propiedad antes de pagar y redacción del documento."),
            ("Manutención y custodia", "Fijación o revisión de la obligación de manutención ante el tribunal de protección."),
            ("Poderes", "Redacción de poderes generales o especiales para gestiones de terceros."),
        ],
    },
    {
        "slug": "antonio-jose-de-sucre", "nombre": "Antonio José de Sucre", "capital": "Socopó",
        "intro": "El municipio Antonio José de Sucre tiene su capital en Socopó, una ciudad comercial atravesada por la Troncal 5, la carretera que une los llanos con el estado Táchira. El tránsito constante de vehículos de carga y pasajeros y el comercio local definen el tipo de asuntos legales más frecuentes.",
        "contexto": "En Socopó atendemos sobre todo accidentes de tránsito en carretera, reclamos a aseguradoras, conflictos entre comerciantes y la formalización de negocios. También casos laborales de empleados del comercio y el transporte.",
        "casos": [
            ("Accidentes en la Troncal 5", "Reclamos por lesiones y daños materiales, y defensa del conductor."),
            ("Formalizar tu negocio", "Registro de firma personal o compañía para operar legalmente."),
            ("Cobro de deudas comerciales", "Letras de cambio, facturas y acuerdos de pago entre comerciantes."),
            ("Reclamos laborales", "Despidos y prestaciones de trabajadores del comercio y el transporte."),
        ],
    },
    {
        "slug": "arismendi", "nombre": "Arismendi", "capital": "Arismendi",
        "intro": "El municipio Arismendi se encuentra en el llano bajo barinés, una zona de grandes extensiones dedicadas a la ganadería. Las distancias hasta los despachos públicos son largas, por eso preparar bien los documentos antes de viajar hace la diferencia.",
        "contexto": "Las consultas más comunes en Arismendi tienen que ver con los fundos: sus linderos, su regularización ante el INTI, la compraventa de ganado y la sucesión cuando fallece el dueño. Podemos adelantar gran parte del trabajo a distancia.",
        "casos": [
            ("Linderos de fundos", "Mediación o demanda cuando hay conflicto por los límites entre propiedades rurales."),
            ("Regularización ante el INTI", "Trámites para títulos de adjudicación y certificados de finca productiva."),
            ("Sucesiones ganaderas", "Reparto de tierras, ganado y bienhechurías entre herederos."),
            ("Contratos de ganado", "Compraventa, arrendamiento de pastos y medianería por escrito."),
        ],
    },
    {
        "slug": "bolivar", "nombre": "Bolívar", "capital": "Barinitas",
        "intro": "El municipio Bolívar, con capital en Barinitas, está en el piedemonte andino, a la entrada de la vía que sube hacia la sierra de Mérida. Su clima y su paisaje han impulsado el turismo y los pequeños negocios, junto a la agricultura de montaña.",
        "contexto": "En Barinitas atendemos la formalización de posadas y comercios, contratos de arrendamiento, compraventa de terrenos en zonas de montaña y conflictos de linderos, además de los casos de familia y laborales de todos los días.",
        "casos": [
            ("Posadas y turismo", "Firma personal, contratos de arrendamiento y permisos para tu negocio."),
            ("Terrenos en el piedemonte", "Revisión de documentos y títulos antes de comprar o vender."),
            ("Conflictos de linderos", "Solución a desacuerdos por límites de terrenos y servidumbres de paso."),
            ("Divorcios y familia", "Divorcio, custodia y régimen de convivencia familiar."),
        ],
    },
    {
        "slug": "cruz-paredes", "nombre": "Cruz Paredes", "capital": "Barrancas",
        "intro": "El municipio Cruz Paredes tiene su capital en Barrancas. Es un municipio de actividad agrícola y comercial cuyos vecinos suelen desplazarse a la capital del estado para los trámites judiciales y de registro.",
        "contexto": "Para evitar viajes innecesarios, en Barrancas trabajamos con orientación previa por WhatsApp: revisamos qué documentos necesitas, redactamos el escrito y te decimos exactamente dónde y cuándo presentarlo.",
        "casos": [
            ("Divorcio de mutuo acuerdo", "Redacción del convenio y presentación ante el tribunal."),
            ("Prestaciones sociales", "Cálculo de tu liquidación según la LOTTT y reclamo si no te pagan."),
            ("Partidas y legalizaciones", "Solicitud de actas en línea y legalización ante el SAREN."),
            ("Contratos de alquiler", "Contratos de arrendamiento de vivienda o local claros y equilibrados."),
        ],
    },
    {
        "slug": "ezequiel-zamora", "nombre": "Ezequiel Zamora", "capital": "Santa Bárbara",
        "intro": "El municipio Ezequiel Zamora, con capital en Santa Bárbara, es tierra ganadera y agrícola. La compraventa de animales, el trabajo en las fincas y la herencia de las tierras familiares generan la mayoría de las consultas.",
        "contexto": "En Santa Bárbara ayudamos a poner por escrito los negocios de ganado, registrar el hierro, regularizar la finca y resolver las sucesiones antes de que se conviertan en conflictos entre hermanos.",
        "casos": [
            ("Registro de hierro", "Registro de la marca de hierro que identifica tu ganado."),
            ("Sucesiones familiares", "Declaración sucesoral ante el SENIAT y partición amistosa o judicial."),
            ("Trabajadores de finca", "Contratos, liquidaciones y reclamos laborales en el campo."),
            ("Tierras e INTI", "Regularización de la tenencia y defensa de la finca productiva."),
        ],
    },
    {
        "slug": "obispos", "nombre": "Obispos", "capital": "Obispos",
        "intro": "El municipio Obispos está muy cerca de la capital del estado, lo que hace que muchos de sus vecinos trabajen, estudien o hagan negocios en la ciudad. Esa cercanía facilita llevar los casos ante los tribunales y registros sin grandes desplazamientos.",
        "contexto": "En Obispos son frecuentes los reclamos laborales de quienes trabajan en la ciudad, los accidentes en la vía, los divorcios y los trámites de vivienda: compraventas, títulos supletorios y contratos de arrendamiento.",
        "casos": [
            ("Accidentes en la vía", "Reclamos a seguros y defensa del conductor tras un choque."),
            ("Despidos injustificados", "Reenganche o pago de prestaciones sociales."),
            ("Vivienda", "Compraventa, título supletorio y documento de propiedad de tu casa."),
            ("Familia", "Divorcio, manutención y reconocimiento de hijos."),
        ],
    },
    {
        "slug": "pedraza", "nombre": "Pedraza", "capital": "Ciudad Bolivia",
        "intro": "El municipio Pedraza, con capital en Ciudad Bolivia, es uno de los de mayor historia del estado: en su territorio está Pedraza La Vieja, antiguo asentamiento colonial. Hoy es una zona agrícola y ganadera del piedemonte.",
        "contexto": "Las tierras que pasan de generación en generación sin papeles al día son el origen de muchas consultas en Ciudad Bolivia. Ordenamos la documentación, tramitamos títulos y resolvemos sucesiones para que la propiedad quede clara.",
        "casos": [
            ("Tierras heredadas sin papeles", "Reconstrucción de la cadena de propiedad y título supletorio."),
            ("Declaración sucesoral", "Trámite ante el SENIAT y reparto de bienes entre herederos."),
            ("Regularización agraria", "Gestiones ante el INTI para fincas y parcelas."),
            ("Contratos agrícolas", "Arrendamiento de tierras, medianería y venta de cosechas."),
        ],
    },
    {
        "slug": "rojas", "nombre": "Rojas", "capital": "Libertad",
        "intro": "El municipio Rojas tiene su capital en Libertad y combina actividad agropecuaria con un comercio local en crecimiento. Sus vecinos buscan sobre todo asesoría en asuntos de familia, trabajo y propiedad.",
        "contexto": "En Libertad atendemos casos de manutención y custodia, reclamos laborales, defensa penal y documentos de propiedad. Te orientamos primero por WhatsApp y te decimos si tu caso requiere acudir al tribunal.",
        "casos": [
            ("Custodia y manutención", "Acuerdos o demandas ante el tribunal de protección de niños y adolescentes."),
            ("Defensa penal", "Asistencia a detenidos y a sus familias desde el primer momento."),
            ("Liquidaciones laborales", "Revisión del cálculo de prestaciones, vacaciones y utilidades."),
            ("Documentos de propiedad", "Compraventas, títulos supletorios y registro."),
        ],
    },
    {
        "slug": "sosa", "nombre": "Sosa", "capital": "Ciudad de Nutrias",
        "intro": "El municipio Sosa tiene su capital en Ciudad de Nutrias, una de las poblaciones más antiguas del estado, que fue puerto fluvial sobre el río Apure. Es una zona llanera y ganadera, alejada de los principales despachos públicos.",
        "contexto": "Por la distancia, en Ciudad de Nutrias es clave hacer bien los trámites a la primera. Ayudamos con partidas y registros antiguos, sucesiones de tierras y ganado, y poderes para que un familiar gestione en tu nombre.",
        "casos": [
            ("Partidas y registros antiguos", "Búsqueda y certificación de actas de nacimiento, matrimonio y defunción."),
            ("Sucesiones de tierras y ganado", "Herencias de fundos y bienhechurías."),
            ("Poderes a distancia", "Autoriza a un familiar o abogado a gestionar por ti."),
            ("Asuntos agrarios", "Regularización de la tierra y conflictos de linderos."),
        ],
    },
]

# Especialidades (a partir de las secciones que ya existían en la portada).
ESPECIALIDADES = [
    {
        "slug": "derecho-civil", "nombre": "Derecho Civil", "icono": "fa-balance-scale",
        "h1": "Abogados de Derecho Civil en Barinas",
        "intro": "El derecho civil regula las relaciones entre personas: contratos, propiedad, herencias y obligaciones. Es la rama a la que acudes cuando compras o vendes una casa, firmas un alquiler, heredas bienes o alguien no cumple lo que acordó contigo.",
        "items": [
            ("Contratos y obligaciones", "Redacción y revisión de contratos de arrendamiento, compraventa, préstamo y donación bajo las leyes civiles venezolanas."),
            ("Propiedad y bienes", "Protección de la propiedad, cadena documental y demandas por daños y perjuicios."),
            ("Sucesiones y herencias", "Trámite ante el SENIAT y los tribunales para transmitir los bienes de una persona fallecida a sus herederos."),
            ("Títulos supletorios", "Documento que acredita la propiedad de bienhechurías construidas sobre terreno propio o ajeno, necesario para notarías y registros."),
            ("Documentos legales", "Visado de documentos: firma y sello de abogado exigidos por notarías y registros."),
        ],
        "mensaje": "Hola, necesito un abogado de DERECHO CIVIL en Barinas.",
    },
    {
        "slug": "derecho-de-familia", "nombre": "Derecho de Familia", "icono": "fa-users",
        "h1": "Abogados de Familia en Barinas: divorcio y custodia",
        "intro": "Los asuntos de familia necesitan rapidez y tacto. Te acompañamos en divorcios, custodia, manutención y régimen de convivencia, siempre buscando primero el acuerdo y protegiendo el interés de los niños.",
        "items": [
            ("Divorcio de mutuo acuerdo", "El más rápido y económico: ambas partes acuerdan la separación de bienes y la custodia, y se presenta el convenio ante el tribunal."),
            ("Divorcio contencioso", "Cuando no hay acuerdo, el abogado demuestra la causal y defiende tus derechos sobre los bienes comunes."),
            ("Custodia de menores", "Responsabilidad de crianza y custodia ante el tribunal de protección de niños, niñas y adolescentes."),
            ("Obligación de manutención", "Fijación, aumento o cobro de la pensión alimenticia."),
            ("Régimen de convivencia familiar", "Acuerdo o fijación judicial de las visitas del padre o madre que no tiene la custodia."),
            ("Adopciones", "Asesoría en el procedimiento de adopción ante el tribunal competente."),
        ],
        "mensaje": "Hola, necesito un abogado de FAMILIA en Barinas (divorcio/custodia).",
    },
    {
        "slug": "derecho-laboral", "nombre": "Derecho Laboral", "icono": "fa-briefcase",
        "h1": "Abogados Laborales en Barinas",
        "intro": "Según la LOTTT, todo trabajador tiene derecho a sus prestaciones sociales, vacaciones y utilidades. Si te despidieron o no te pagan lo que te corresponde, un abogado laboral calcula tu liquidación exacta y la reclama.",
        "items": [
            ("Despidos injustificados", "Solicitud de reenganche y pago de salarios caídos, o indemnización."),
            ("Cobro de prestaciones sociales", "Cálculo de la liquidación y reclamo ante la Inspectoría del Trabajo o los tribunales."),
            ("Accidentes laborales", "Indemnizaciones por accidentes y enfermedades ocupacionales."),
            ("Contratos colectivos", "Asesoría a trabajadores y empresas sobre convenciones colectivas."),
            ("Reclamo de vacaciones y utilidades", "Pago de vacaciones fraccionadas, bono vacacional y utilidades."),
        ],
        "mensaje": "Hola, necesito un abogado LABORAL en Barinas.",
    },
    {
        "slug": "derecho-penal", "nombre": "Derecho Penal", "icono": "fa-gavel",
        "h1": "Abogados Penalistas en Barinas",
        "intro": "En materia penal las primeras horas son decisivas. El abogado garantiza que se respete el debido proceso y los derechos fundamentales desde la audiencia de presentación ante los tribunales de control.",
        "items": [
            ("Asistencia en audiencias", "Representación inmediata desde la audiencia de presentación."),
            ("Medidas cautelares", "Solicitud de medidas cautelares sustitutivas de la privación de libertad."),
            ("Juicios orales", "Defensa técnica durante todo el juicio."),
            ("Recursos de apelación", "Impugnación de decisiones ante la Corte de Apelaciones."),
            ("Estafas y fraudes", "Defensa y acusación en delitos contra el patrimonio."),
        ],
        "mensaje": "Hola, URGENTE: necesito un abogado PENALISTA en Barinas.",
    },
    {
        "slug": "accidentes-de-transito", "nombre": "Accidentes de Tránsito", "icono": "fa-car-crash",
        "h1": "Abogados de Accidentes de Tránsito en Barinas",
        "intro": "Después de un accidente, primero asegura tu salud y denuncia el hecho ante las autoridades. No firmes acuerdos sin asesoría: un abogado reclama la indemnización por daños materiales y lesiones personales a las aseguradoras.",
        "items": [
            ("Lesiones personales", "Reclamo de gastos médicos, incapacidad y daño moral."),
            ("Reclamos a seguros", "Gestión del siniestro y negociación con la aseguradora."),
            ("Indemnizaciones", "Cálculo y cobro de los daños materiales al vehículo."),
            ("Defensa de conductores", "Asistencia al conductor señalado como responsable."),
            ("Delitos de tránsito", "Defensa en procesos penales derivados de un accidente."),
        ],
        "mensaje": "Hola, tuve un accidente de tránsito en Barinas y necesito un abogado.",
    },
    {
        "slug": "derecho-mercantil", "nombre": "Derecho Mercantil", "icono": "fa-handshake",
        "h1": "Abogados de Derecho Mercantil en Barinas",
        "intro": "Formalizar tu negocio te da seguridad jurídica y acceso a bancos, proveedores y licitaciones. Te ayudamos a elegir la figura adecuada y a mantener tus documentos al día ante el Registro Mercantil.",
        "items": [
            ("Registro de empresas (Pymes)", "Constitución de sociedades mercantiles, con su objeto social y capital suscrito."),
            ("Firmas personales", "Figura para que una persona natural ejerza el comercio con un nombre comercial propio."),
            ("Actas de asamblea", "Cambios de junta directiva, aumentos de capital y venta de acciones."),
            ("Marcas y patentes", "Registro ante el SAPI para proteger el nombre y la imagen de tu negocio."),
            ("Contratos comerciales y cobro de deudas", "Contratos con clientes y proveedores, letras de cambio y cobranza."),
        ],
        "mensaje": "Hola, necesito un abogado MERCANTIL en Barinas para asuntos de empresa.",
    },
    {
        "slug": "derecho-agrario", "nombre": "Derecho Agrario e INTI", "icono": "fa-tractor",
        "h1": "Abogados de Derecho Agrario e INTI en Barinas",
        "intro": "Barinas es un estado agrícola y ganadero, y la tenencia de la tierra es una de las principales fuentes de conflicto. Te acompañamos ante el Instituto Nacional de Tierras (INTI) y los tribunales agrarios.",
        "items": [
            ("Regularización ante el INTI", "Títulos de adjudicación de tierras y certificados de finca productiva."),
            ("Conflictos de linderos", "Mediación o demanda en disputas por los límites entre fundos y fincas."),
            ("Vialidad y servidumbre", "Acuerdos para permitir el paso o el acceso a servicios a través de terrenos vecinos."),
            ("Contratos agrarios", "Arrendamiento de tierras, medianería y compraventa de ganado y cosechas."),
        ],
        "mensaje": "Hola, necesito un abogado AGRARIO en Barinas para regularización de tierras ante el INTI.",
    },
    {
        "slug": "tramites-saren", "nombre": "Trámites SAREN en línea", "icono": "fa-laptop-house",
        "h1": "Trámites SAREN en línea desde Barinas",
        "intro": "Los trámites legales en Venezuela se gestionan a través del SAREN (Servicio Autónomo de Registros y Notarías). Muchos se solicitan en línea; otros, como poderes y compraventas, requieren cita previa y la presencia de las partes.",
        "items": [
            ("Partidas en línea", "Solicitud de actas de nacimiento, matrimonio y defunción."),
            ("Registros y notarías", "Protocolización de compraventas, registro de empresas y autenticación de poderes."),
            ("Legalización de documentos", "Actas y títulos universitarios certificados ante el SAREN."),
            ("Citas y recaudos", "Solicitud de cita en el portal, pago de tasas y revisión de recaudos antes de acudir."),
            ("Trámites desde el exterior", "Gestionamos tus documentos y te los enviamos digitalizados o físicos."),
        ],
        "mensaje": "Hola, necesito ayuda con un trámite SAREN en línea desde Barinas.",
    },
    {
        "slug": "legalizacion-apostilla", "nombre": "Legalización y Apostilla", "icono": "fa-globe-americas",
        "h1": "Legalización y Apostilla de Documentos en Barinas",
        "intro": "Si vives en el exterior o planeas emigrar, necesitas que tus documentos venezolanos tengan validez en otro país. Te explicamos la diferencia entre copia certificada y documento legalizado, y gestionamos todo el proceso.",
        "items": [
            ("Copia certificada (uso nacional)", "Una autoridad da fe de que la copia es idéntica al original; sirve para trámites dentro de Venezuela."),
            ("Legalización", "Autentica la firma y el sello del funcionario que emitió el documento."),
            ("Apostilla", "Da validez internacional al documento en los países del Convenio de La Haya."),
            ("Partidas y sentencias", "Obtención de partidas de nacimiento, actas de matrimonio y sentencias de divorcio."),
            ("Envío al exterior", "Te enviamos los documentos digitalizados o físicos a cualquier país."),
        ],
        "mensaje": "Hola, necesito legalizar o apostillar documentos en Barinas para usarlos en el exterior.",
    },
]

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def esc(texto):
    return html.escape(texto, quote=True)


def wa_url(mensaje):
    """Enlace wa.me con el mensaje terminado SIEMPRE en el código de la web."""
    texto = mensaje.strip() + " " + NEGOCIO["codigo_whatsapp"]
    return "https://wa.me/{}?text={}".format(NEGOCIO["whatsapp"], quote(texto, safe=""))


def wa_generico(titulo):
    return wa_url("Hola, vengo de la página «{}» y necesito asesoría legal.".format(titulo))


def wa_reservar(titulo):
    return wa_url("Hola, quiero reservar una cita con un abogado. Vengo de la página «{}».".format(titulo))


def url_abs(path):
    return NEGOCIO["dominio"] + path


def copyright_texto(anio_actual):
    inicio = NEGOCIO["anio_inicio"]
    anios = str(inicio) if inicio == anio_actual else "{}–{}".format(inicio, anio_actual)
    return "© {} {}".format(anios, NEGOCIO["nombre"])


def ruta_archivo(path):
    """URL limpia de Cloudflare Pages -> archivo del repositorio."""
    p = path.split("#")[0].split("?")[0]
    if p == "/":
        return "index.html"
    if p.endswith("/"):
        return p.lstrip("/") + "index.html"
    rel = p.lstrip("/")
    if os.path.splitext(rel)[1]:
        return rel
    return rel + ".html"


# ---------------------------------------------------------------------------
# Schema.org
# ---------------------------------------------------------------------------
def schema_negocio():
    org = {
        "@type": "LegalService",
        "@id": url_abs("/#organization"),
        "name": NEGOCIO["nombre"],
        "alternateName": NEGOCIO["nombre_largo"],
        "url": url_abs("/"),
        "telephone": NEGOCIO["telefono_e164"],
        "image": url_abs(NEGOCIO["imagen"]),
        "logo": url_abs(NEGOCIO["imagen"]),
        "description": "Directorio de abogados especializados en derecho civil, familia, laboral, penal, mercantil, agrario, accidentes de tránsito y trámites SAREN en el estado Barinas, Venezuela.",
        "areaServed": {
            "@type": "State",
            "name": "Barinas",
            "containedInPlace": {"@type": "Country", "name": "Venezuela"},
        },
        "knowsAbout": [e["nombre"] for e in ESPECIALIDADES],
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": NEGOCIO["telefono_e164"],
            "contactType": "customer service",
            "areaServed": "VE",
            "availableLanguage": "es",
        },
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": h["dias"], "opens": h["abre"], "closes": h["cierra"]}
            for h in NEGOCIO["horario_schema"]
        ],
    }
    if NEGOCIO["redes"]:
        org["sameAs"] = list(NEGOCIO["redes"].values())
    if NEGOCIO["direccion"]:
        org["address"] = dict({"@type": "PostalAddress"}, **NEGOCIO["direccion"])
    return org


def schema_pagina(pg, fecha):
    url = url_abs(pg["path"])
    grafo = [
        {
            "@type": "WebSite",
            "@id": url_abs("/#website"),
            "url": url_abs("/"),
            "name": NEGOCIO["nombre"],
            "inLanguage": "es-VE",
            "publisher": {"@id": url_abs("/#organization")},
        },
        schema_negocio(),
        {
            "@type": pg.get("tipo_schema", "WebPage"),
            "@id": url + "#webpage",
            "url": url,
            "name": pg["titulo"],
            "description": pg["descripcion"],
            "inLanguage": "es-VE",
            "isPartOf": {"@id": url_abs("/#website")},
            "about": {"@id": url_abs("/#organization")},
            "dateModified": fecha.isoformat(),
            "breadcrumb": {"@id": url + "#breadcrumb"},
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": nombre, "item": url_abs(path)}
                for i, (nombre, path) in enumerate(pg["migas"])
            ],
        },
    ]
    grafo.extend(pg.get("schema_extra", []))
    return json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, indent=2)


def schema_servicio(nombre, tipo, url, area):
    return {
        "@type": "Service",
        "@id": url + "#service",
        "name": nombre,
        "serviceType": tipo,
        "url": url,
        "provider": {"@id": url_abs("/#organization")},
        "areaServed": area,
    }


# ---------------------------------------------------------------------------
# Plantilla común (menú, bloques y pie iguales en todas las páginas)
# ---------------------------------------------------------------------------
MENU = [
    ("/", "Inicio"),
    ("/servicios/", "Especialidades"),
    ("/municipios/", "Municipios"),
    ("/servicios/tramites-saren", "Trámites SAREN en línea"),
    ("/quienes-somos", "Quiénes Somos"),
    ("/contacto", "Contacto"),
]


def bloque_saren(pg):
    if pg["path"] == "/servicios/tramites-saren":
        enlace = ""
    else:
        enlace = '<a href="/servicios/tramites-saren" class="btn btn-outline-primary">Ver trámites SAREN en línea</a>'
    return '''
    <!-- Bloque: Trámites SAREN en línea (presente en todas las páginas) -->
    <section class="saren-block py-5" id="saren-en-linea">
        <div class="container">
            <div class="row align-items-center g-4">
                <div class="col-lg-8">
                    <h2 class="h3 fw-bold"><i class="fas fa-laptop-house me-2"></i>Trámites SAREN en línea</h2>
                    <p class="mb-0">Partidas de nacimiento, matrimonio y defunción, legalizaciones, poderes, registro de empresas y compraventas. Te guiamos con la cita, los recaudos y las tasas del SAREN, estés en Barinas o en el exterior.</p>
                </div>
                <div class="col-lg-4 text-lg-end d-flex flex-wrap gap-2 justify-content-lg-end">
                    {enlace}
                    <a href="{wa}" target="_blank" rel="noopener" class="btn btn-success"><i class="fab fa-whatsapp me-2"></i>Ayuda con mi trámite</a>
                </div>
            </div>
        </div>
    </section>
'''.format(enlace=enlace, wa=wa_url("Hola, necesito ayuda con un trámite SAREN en línea. Vengo de la página «{}».".format(pg["titulo"])))


def bloque_contacto(pg):
    return '''
    <!-- Bloque: contacto (presente en todas las páginas) -->
    <section class="contact-block py-5" id="contacto-rapido">
        <div class="container">
            <h2 class="section-title">Contacto</h2>
            <div class="row g-4 justify-content-center text-center">
                <div class="col-md-4">
                    <div class="contact-card">
                        <i class="fab fa-whatsapp"></i>
                        <h3 class="h6 fw-bold">Teléfono y WhatsApp</h3>
                        <p class="mb-0"><a href="tel:{tel_e164}" data-dato="telefono">{tel}</a></p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="contact-card">
                        <i class="fas fa-map-marked-alt"></i>
                        <h3 class="h6 fw-bold">Área de servicio</h3>
                        <p class="mb-0" data-dato="area">{area}</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="contact-card">
                        <i class="fas fa-clock"></i>
                        <h3 class="h6 fw-bold">Horario</h3>
                        <p class="mb-0" data-dato="horario">{horario}</p>
                    </div>
                </div>
            </div>
            <div class="text-center mt-4">
                <a href="{reservar}" target="_blank" rel="noopener" class="btn btn-success btn-lg fw-bold px-4" data-reservar>
                    <i class="fab fa-whatsapp me-2"></i>Reservar cita por WhatsApp
                </a>
            </div>
        </div>
    </section>
'''.format(tel=NEGOCIO["telefono"], tel_e164=NEGOCIO["telefono_e164"], area=esc(NEGOCIO["area_servicio"]),
           horario=esc(NEGOCIO["horario"]), reservar=wa_reservar(pg["titulo"]))


def redes_html(wa):
    iconos = {"facebook": "fab fa-facebook-f", "instagram": "fab fa-instagram", "tiktok": "fab fa-tiktok",
              "x": "fab fa-x-twitter", "youtube": "fab fa-youtube", "linkedin": "fab fa-linkedin-in"}
    enlaces = ['<a href="{}" class="social-link" target="_blank" rel="noopener" aria-label="WhatsApp"><i class="fab fa-whatsapp"></i></a>'.format(wa),
               '<a href="tel:{}" class="social-link" aria-label="Llamar"><i class="fas fa-phone"></i></a>'.format(NEGOCIO["telefono_e164"])]
    for red, url in NEGOCIO["redes"].items():
        enlaces.append('<a href="{}" class="social-link" target="_blank" rel="noopener me" aria-label="{}"><i class="{}"></i></a>'.format(
            esc(url), red.capitalize(), iconos.get(red, "fas fa-link")))
    return "\n                        ".join(enlaces)


def render(pg, fecha):
    titulo = pg["titulo"]
    wa_gen = wa_generico(titulo)
    anio = fecha.year
    menu_escritorio = "\n                ".join(
        '<a href="{}" class="nav-link{}">{}</a>'.format(h, " active" if h == pg.get("menu_activo") else "", t)
        for h, t in MENU)
    menu_movil = "\n            ".join('<a href="{}">{}</a>'.format(h, t) for h, t in MENU)

    ga = ""
    if NEGOCIO["ga_id"]:
        ga = '''    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{id}');
    </script>

'''.format(id=NEGOCIO["ga_id"])

    if pg.get("noindex"):
        seo = '    <meta name="robots" content="noindex, follow">\n'
    else:
        seo = '''    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
    <link rel="canonical" href="{url}">
    <link rel="alternate" hreflang="es-VE" href="{url}">
    <script type="application/ld+json">
{ld}
    </script>
'''.format(url=url_abs(pg["path"]), ld="\n".join("    " + l for l in schema_pagina(pg, fecha).split("\n")))

    if pg.get("hero"):
        cabecera = pg["hero"]
    else:
        migas = "\n                ".join(
            '<li><a href="{}">{}</a></li>'.format(p, esc(n)) if i < len(pg["migas"]) - 1
            else '<li aria-current="page">{}</li>'.format(esc(n))
            for i, (n, p) in enumerate(pg["migas"]))
        cabecera = '''    <header class="page-hero">
        <div class="container">
            <h1>{h1}</h1>
            <p class="lead">{lead}</p>
        </div>
    </header>

    <nav class="breadcrumb-bar" aria-label="Ruta de navegación">
        <div class="container">
            <ol>
                {migas}
            </ol>
        </div>
    </nav>
'''.format(h1=esc(pg["h1"]), lead=pg["lead"], migas=migas)

    return '''<!DOCTYPE html>
<html lang="es-VE">
<head>
{ga}    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <meta name="description" content="{desc}">
    <meta name="author" content="{nombre}">
    <meta name="theme-color" content="#1a237e">
    <meta name="geo.region" content="VE-E">
    <meta name="geo.placename" content="Barinas">
{seo}    <link rel="icon" href="/images/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="{img}">

    <!-- Open Graph / redes -->
    <meta property="og:locale" content="es_VE">
    <meta property="og:site_name" content="{nombre}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{titulo}">
    <meta property="og:description" content="{desc}">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{img_abs}">
    <meta property="og:image:width" content="{img_w}">
    <meta property="og:image:height" content="{img_h}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{titulo}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="{img_abs}">

    <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
    <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://cdn.jsdelivr.net/npm/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <link rel="stylesheet" href="/style.css">
</head>
<body>

    <!-- Navegación -->
    <nav class="main-nav">
        <div class="nav-container">
            <a href="/" class="logo">
                <div class="logo-img">AB</div>
                <div>
                    <div class="logo-text">ABOGADOS BARINAS</div>
                    <div class="logo-subtext">DIRECTORIO LEGAL ESPECIALIZADO</div>
                </div>
            </a>

            <div class="desktop-menu">
                {menu_escritorio}
                <a href="{wa_gen}" class="whatsapp-btn-nav" target="_blank" rel="noopener">
                    <i class="fab fa-whatsapp"></i> {tel}
                </a>
            </div>

            <button class="mobile-menu-toggle" id="mobileMenuToggle" aria-label="Abrir menú" aria-controls="mobileMenu" aria-expanded="false">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
        <div class="mobile-menu" id="mobileMenu">
            {menu_movil}
            <a href="{wa_gen}" target="_blank" rel="noopener"><i class="fab fa-whatsapp me-2"></i>{tel}</a>
        </div>
    </nav>

{cabecera}
    <main{main_cls}>
{cuerpo}
    </main>
{saren}{contacto}
    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="row">
                <div class="col-lg-4 mb-4 mb-lg-0">
                    <div class="footer-logo">ABOGADOS BARINAS</div>
                    <p class="mb-3">Directorio legal especializado en derecho civil, familiar, laboral, penal, mercantil y agrario. Cobertura en los 12 municipios del estado Barinas con atención inmediata vía WhatsApp.</p>
                    <div class="social-links">
                        {redes}
                    </div>
                </div>

                <div class="col-lg-3 col-md-6 mb-4 mb-md-0">
                    <div class="footer-links">
                        <h5>Especialidades</h5>
                        <ul>
                            {footer_esp}
                        </ul>
                    </div>
                </div>

                <div class="col-lg-2 col-md-6 mb-4 mb-md-0">
                    <div class="footer-links">
                        <h5>El sitio</h5>
                        <ul>
                            <li><a href="/municipios/">Municipios</a></li>
                            <li><a href="/servicios/tramites-saren">Trámites SAREN en línea</a></li>
                            <li><a href="/quienes-somos">Quiénes Somos</a></li>
                            <li><a href="/contacto">Contacto</a></li>
                            <li><a href="/politica-de-privacidad">Privacidad</a></li>
                        </ul>
                    </div>
                </div>

                <div class="col-lg-3 col-md-12">
                    <div class="footer-links">
                        <h5>Contacto Directo</h5>
                        <ul>
                            <li><a href="tel:{tel_e164}"><i class="fas fa-phone me-2"></i>{tel}</a></li>
                            <li><a href="{wa_gen}" target="_blank" rel="noopener"><i class="fab fa-whatsapp me-2 text-success"></i>WhatsApp</a></li>
                            <li><i class="fas fa-map-marker-alt me-2"></i>{area}</li>
                            <li><i class="fas fa-clock me-2"></i>{horario}</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="text-center mt-5 pt-4 border-top border-secondary">
                <p class="mb-2 small footer-note" data-dato="copyright">{copyright}. Todos los derechos reservados.</p>
                <p class="mb-0 small footer-legal">
                    <a href="/politica-de-privacidad">Política de Privacidad y Tratamiento de Datos</a> ·
                    <a href="/quienes-somos">Quiénes Somos</a> ·
                    <a href="/contacto">Contacto</a>
                </p>
                <p class="mt-2 mb-0 small footer-note">La información de este sitio es orientativa y no sustituye la asesoría de un abogado sobre tu caso.</p>
            </div>
        </div>
    </footer>

    <!-- WhatsApp Modal -->
    <div id="whatsappModal" class="modal-whatsapp" onclick="closeWhatsAppModal(event)">
        <div class="modal-content-custom" onclick="event.stopPropagation()">
            <span class="close-modal" onclick="closeWhatsAppModal()">&times;</span>
            <div class="urgente-badge"><i class="fas fa-bolt"></i> ATENCIÓN INMEDIATA</div>
            <div class="whatsapp-giant"><i class="fab fa-whatsapp"></i></div>
            <h2 class="h3 mb-3">Abogado en Barinas</h2>
            <p class="text-muted mb-4" id="modalText">Te conectaremos con un abogado especialista disponible en tu municipio.</p>
            <div class="d-grid gap-3">
                <a id="whatsappLink" href="{wa_gen}" target="_blank" rel="noopener" class="btn btn-success btn-lg py-3">
                    <i class="fab fa-whatsapp fa-lg me-2"></i> <span>Abrir WhatsApp Ahora</span>
                    <small class="d-block mt-1 opacity-75">{tel}</small>
                </a>
                <button class="btn btn-outline-secondary" onclick="closeWhatsAppModal()">Cancelar</button>
            </div>
            <div class="mt-4 pt-3 border-top text-center">
                <small class="text-muted"><i class="fas fa-lock text-success me-1"></i> Consulta confidencial</small>
            </div>
        </div>
    </div>

    <!-- WhatsApp Float Button -->
    <a href="{wa_gen}" class="whatsapp-float" target="_blank" rel="noopener" aria-label="Contactar por WhatsApp" onclick="event.preventDefault(); openWhatsAppModal('boton flotante');">
        <i class="fab fa-whatsapp"></i>
    </a>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/aos@2.3.1/dist/aos.js"></script>
    <script src="/assets/site.js"></script>
</body>
</html>
'''.format(
        ga=ga, titulo=esc(titulo), desc=esc(pg["descripcion"]), nombre=esc(NEGOCIO["nombre"]), seo=seo,
        url=url_abs(pg["path"]), img=NEGOCIO["imagen"], img_abs=url_abs(NEGOCIO["imagen"]),
        img_w=NEGOCIO["imagen_ancho"], img_h=NEGOCIO["imagen_alto"],
        menu_escritorio=menu_escritorio, menu_movil=menu_movil, wa_gen=wa_gen, tel=NEGOCIO["telefono"],
        tel_e164=NEGOCIO["telefono_e164"], cabecera=cabecera,
        main_cls="" if pg.get("hero") else ' class="content-page"',
        cuerpo=pg["cuerpo"].rstrip("\n"), saren=bloque_saren(pg), contacto=bloque_contacto(pg),
        redes=redes_html(wa_gen),
        footer_esp="\n                            ".join(
            '<li><a href="/servicios/{}">{}</a></li>'.format(e["slug"], e["nombre"]) for e in ESPECIALIDADES[:6]),
        area=esc(NEGOCIO["area_servicio"]), horario=esc(NEGOCIO["horario"]), copyright=copyright_texto(anio),
    )


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------
def pagina_inicio():
    with open(os.path.join(ROOT, "src", "home.html"), encoding="utf-8") as f:
        cuerpo = f.read()
    tags = "\n".join(
        '                <a class="municipio-tag" href="/municipios/{}">{}</a>'.format(
            m["slug"], m["capital"] if m["capital"] == m["nombre"] else "{} ({})".format(m["capital"], m["nombre"]))
        for m in MUNICIPIOS)
    cuerpo = (cuerpo.replace("{{MUNICIPIO_TAGS}}", tags)
              .replace("{{TEL_HREF}}", "tel:" + NEGOCIO["telefono_e164"])
              .replace("{{TEL}}", NEGOCIO["telefono"]))
    faqs = extraer_faqs(cuerpo)
    hero_fin = cuerpo.index("</section>") + len("</section>")
    return {
        "path": "/", "salida": "index.html",
        "titulo": "Abogados en Barinas | Directorio Legal Especializado",
        "descripcion": "Directorio de abogados en Barinas, Venezuela. Especialistas en derecho civil, familia, laboral, penal, mercantil, agrario y trámites SAREN en línea. Consulta vía WhatsApp en los 12 municipios.",
        "migas": [("Inicio", "/")],
        "menu_activo": "/",
        "hero": "    " + cuerpo[:hero_fin].replace("\n", "\n    ") + "\n",
        "cuerpo": "    " + cuerpo[hero_fin:].strip("\n").replace("\n", "\n    "),
        "schema_extra": [{
            "@type": "FAQPage",
            "@id": url_abs("/#faq"),
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in faqs],
        }],
    }


def limpiar(fragmento):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragmento))).strip()


def extraer_faqs(cuerpo):
    """Toma las preguntas frecuentes VISIBLES de la portada para el FAQPage."""
    faqs = []
    # Sección #faq (acordeón)
    sec = cuerpo[cuerpo.index('id="faq"'):]
    sec = sec[:sec.index("</section>")]
    for q, a in re.findall(r'<button class="accordion-button[^"]*"[^>]*>(.*?)</button>.*?<div class="accordion-body">(.*?)</div>', sec, re.S):
        faqs.append((limpiar(q), limpiar(a)))
    # Barra lateral de la guía legal
    for q, a in re.findall(r'data-bs-target="#faq\d"[^>]*>(.*?)</button>\s*<div class="collapse mt-2" id="faq\d">\s*<p[^>]*>(.*?)</p>', cuerpo, re.S):
        faqs.append((limpiar(q), limpiar(a)))
    return faqs


def pagina_municipio(m):
    nombre, capital = m["nombre"], m["capital"]
    lugar = nombre if nombre == capital else "{} ({})".format(nombre, capital)
    path = "/municipios/" + m["slug"]
    titulo = "Abogados en {} | {}".format(lugar, NEGOCIO["nombre"]) if nombre != "Barinas" \
        else "Abogados en el municipio Barinas | Directorio Legal"
    casos = "\n".join('''                <div class="col-md-6">
                    <div class="value-card">
                        <h3 class="h5 fw-bold">{}</h3>
                        <p class="mb-0 text-muted">{}</p>
                    </div>
                </div>'''.format(esc(t), esc(d)) for t, d in m["casos"])
    especialidades = "\n".join('                    <li><a href="/servicios/{}">{}</a></li>'.format(e["slug"], e["nombre"])
                               for e in ESPECIALIDADES)
    wa = wa_url("Hola, necesito un abogado en {}. Vengo de la página «{}».".format(lugar, titulo))
    cuerpo = '''        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-9">
                    <h2>Asesoría legal en {lugar}</h2>
                    <p>{intro}</p>
                    <p>{contexto}</p>
                    <p class="text-center my-4">
                        <a href="{wa}" target="_blank" rel="noopener" class="btn btn-success btn-lg"><i class="fab fa-whatsapp me-2"></i>Consultar un abogado en {capital}</a>
                    </p>
                </div>
            </div>

            <h2 class="text-center">Casos frecuentes en {capital}</h2>
            <div class="row g-4 my-2">
{casos}
            </div>

            <div class="row justify-content-center mt-4">
                <div class="col-lg-9">
                    <h2>Especialidades disponibles</h2>
                    <ul class="columnas-2">
{especialidades}
                    </ul>
                    <p class="small text-muted">¿Tu caso es de otra zona? Consulta la <a href="/municipios/">lista de municipios</a> del estado.</p>
                </div>
            </div>
        </div>'''.format(lugar=esc(lugar), intro=esc(m["intro"]), contexto=esc(m["contexto"]), wa=wa,
                         capital=esc(capital), casos=casos, especialidades=especialidades)
    area = [{"@type": "AdministrativeArea", "name": "Municipio {}".format(nombre)}]
    if capital != nombre:
        area.append({"@type": "City", "name": capital})
    return {
        "path": path, "salida": "municipios/{}.html".format(m["slug"]),
        "titulo": titulo,
        "descripcion": "Abogados en {}: {}, {} y más. Consulta por WhatsApp.".format(
            "el municipio Barinas, capital del estado" if nombre == "Barinas" else lugar + ", estado Barinas",
            m["casos"][0][0].lower(), m["casos"][1][0].lower()),
        "h1": "Abogados en {}".format(lugar),
        "lead": "Orientación legal para vecinos de {} por WhatsApp.".format(esc(lugar)),
        "migas": [("Inicio", "/"), ("Municipios", "/municipios/"), (nombre, path)],
        "menu_activo": "/municipios/",
        "cuerpo": cuerpo,
        "municipio": m,
        "schema_extra": [schema_servicio("Abogados en {}".format(lugar), "Asesoría legal", url_abs(path), area)],
    }


def pagina_municipios():
    tarjetas = "\n".join('''                <div class="col-md-6 col-lg-4">
                    <a class="municipio-card" href="/municipios/{slug}">
                        <span class="h5 fw-bold d-block mb-1">{nombre}</span>
                        <span class="text-muted">Capital: {capital}</span>
                    </a>
                </div>'''.format(slug=m["slug"], nombre=esc(m["nombre"]), capital=esc(m["capital"])) for m in MUNICIPIOS)
    cuerpo = '''        <div class="container">
            <p class="text-center mb-5">El estado Barinas tiene 12 municipios. Elige el tuyo para ver los casos más frecuentes en tu zona y hablar con un abogado.</p>
            <div class="row g-4">
{}
            </div>
        </div>'''.format(tarjetas)
    return {
        "path": "/municipios/", "salida": "municipios/index.html",
        "titulo": "Abogados por municipio en el estado Barinas | " + NEGOCIO["nombre"],
        "descripcion": "Encuentra abogados en los 12 municipios del estado Barinas: Barinas, Sabaneta, El Cantón, Socopó, Arismendi, Barinitas, Barrancas, Santa Bárbara, Obispos, Ciudad Bolivia, Libertad y Ciudad de Nutrias.",
        "h1": "Abogados por municipio en Barinas",
        "lead": "Los 12 municipios del estado Barinas, con su capital.",
        "migas": [("Inicio", "/"), ("Municipios", "/municipios/")],
        "menu_activo": "/municipios/",
        "tipo_schema": "CollectionPage",
        "cuerpo": cuerpo,
        "schema_extra": [{
            "@type": "ItemList",
            "@id": url_abs("/municipios/#lista"),
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": "Abogados en " + m["nombre"],
                                 "url": url_abs("/municipios/" + m["slug"])} for i, m in enumerate(MUNICIPIOS)],
        }],
    }


def pagina_especialidad(e):
    path = "/servicios/" + e["slug"]
    titulo = "{} | {}".format(e["h1"], NEGOCIO["nombre"])
    items = "\n".join('''                        <li class="mb-3"><strong>{}:</strong> {}</li>'''.format(esc(t), esc(d)) for t, d in e["items"])
    otras = "\n".join('                        <li><a href="/servicios/{}">{}</a></li>'.format(o["slug"], o["nombre"])
                      for o in ESPECIALIDADES if o is not e)
    extra = ""
    if e["slug"] == "tramites-saren":
        extra = '''
                    <h2>Pasos clave</h2>
                    <ol>
                        <li>Solicitar la cita a través del portal del SAREN.</li>
                        <li>Pagar las tasas según el servicio requerido.</li>
                        <li>Presentar la cédula y los documentos originales el día de la cita.</li>
                    </ol>
                    <p><a href="https://www.saren.gob.ve/" target="_blank" rel="noopener">Portal oficial del SAREN <i class="fas fa-external-link-alt ms-1"></i></a></p>'''
    cuerpo = '''        <div class="container">
            <div class="row g-5">
                <div class="col-lg-8">
                    <h2>¿En qué te ayudamos?</h2>
                    <p>{intro}</p>
                    <ul class="lista-servicio">
{items}
                    </ul>{extra}
                    <p class="text-center my-4">
                        <a href="{wa}" target="_blank" rel="noopener" class="btn btn-success btn-lg"><i class="fab fa-whatsapp me-2"></i>Consultar sobre {nombre}</a>
                    </p>
                </div>
                <aside class="col-lg-4">
                    <div class="value-card">
                        <h2 class="h5 fw-bold mt-0">Otras especialidades</h2>
                        <ul class="mb-3">
{otras}
                        </ul>
                        <p class="small mb-0">Atendemos en los <a href="/municipios/">12 municipios del estado</a>.</p>
                    </div>
                </aside>
            </div>
        </div>'''.format(intro=esc(e["intro"]), items=items, extra=extra, otras=otras, nombre=esc(e["nombre"]),
                         wa=wa_url("{} Vengo de la página «{}».".format(e["mensaje"], titulo)))
    return {
        "path": path, "salida": "servicios/{}.html".format(e["slug"]),
        "titulo": titulo,
        "descripcion": "{} Consulta con abogados en el estado Barinas por WhatsApp.".format(e["intro"].split(". ")[0].rstrip(".") + "."),
        "h1": e["h1"],
        "lead": "Abogados especialistas en {} en el estado Barinas.".format(esc(e["nombre"].lower()) if e["slug"].startswith("derecho") else esc(e["nombre"])),
        "migas": [("Inicio", "/"), ("Especialidades", "/servicios/"), (e["nombre"], path)],
        "menu_activo": "/servicios/tramites-saren" if e["slug"] == "tramites-saren" else "/servicios/",
        "cuerpo": cuerpo,
        "schema_extra": [schema_servicio(e["nombre"], e["nombre"], url_abs(path),
                                         {"@type": "State", "name": "Barinas"})],
    }


def pagina_servicios():
    tarjetas = "\n".join('''                <div class="col-md-6 col-lg-4">
                    <a class="municipio-card" href="/servicios/{slug}">
                        <i class="fas {icono} fa-2x mb-2" style="color: var(--accent);"></i>
                        <span class="h5 fw-bold d-block mb-1">{nombre}</span>
                        <span class="text-muted small">{resumen}</span>
                    </a>
                </div>'''.format(slug=e["slug"], icono=e["icono"], nombre=esc(e["nombre"]),
                                 resumen=esc(e["items"][0][0] + ", " + e["items"][1][0].lower() + "…")) for e in ESPECIALIDADES)
    cuerpo = '''        <div class="container">
            <p class="text-center mb-5">Elige la materia de tu caso para conocer qué incluye y hablar con el especialista.</p>
            <div class="row g-4">
{}
            </div>
        </div>'''.format(tarjetas)
    return {
        "path": "/servicios/", "salida": "servicios/index.html",
        "titulo": "Especialidades legales en Barinas | " + NEGOCIO["nombre"],
        "descripcion": "Derecho civil, familia, laboral, penal, accidentes de tránsito, mercantil, agrario e INTI, trámites SAREN en línea y legalización y apostilla en el estado Barinas.",
        "h1": "Especialidades legales en Barinas",
        "lead": "Abogados por materia para cada tipo de caso.",
        "migas": [("Inicio", "/"), ("Especialidades", "/servicios/")],
        "menu_activo": "/servicios/",
        "tipo_schema": "CollectionPage",
        "cuerpo": cuerpo,
    }


def pagina_quienes(fecha):
    cuerpo = '''        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-9">
                    <h2>Nuestra historia</h2>
                    <p><strong>{nombre}</strong> comenzó en {inicio} como un directorio legal en línea para el estado Barinas. Nació para resolver un problema concreto: encontrar rápido a un abogado de confianza que conozca los tribunales, registros y notarías de la región, sin tener que recorrer oficinas.</p>
                    <p>Desde entonces conectamos a personas, familias y empresas de los 12 municipios del estado con abogados según la materia de su caso, y atendemos también a venezolanos en el exterior que necesitan gestionar documentos en Barinas.</p>

                    <h2>Nuestra misión</h2>
                    <p>Acercar la asesoría jurídica a cualquier persona en Barinas, con una primera orientación por WhatsApp y la derivación al especialista que corresponde a su caso.</p>

                    <h2>Nuestra visión</h2>
                    <p>Ser la referencia de consulta legal en línea del estado Barinas por la rapidez de respuesta, la claridad de la información y el trato cercano.</p>
                </div>
            </div>

            <div class="row g-4 my-4">
                <div class="col-md-6 col-lg-3"><div class="value-card text-center"><i class="fas fa-bolt"></i><h3 class="h5 fw-bold">Rapidez</h3><p class="mb-0 small text-muted">Respuesta por WhatsApp sin esperas ni citas previas para la primera orientación.</p></div></div>
                <div class="col-md-6 col-lg-3"><div class="value-card text-center"><i class="fas fa-user-shield"></i><h3 class="h5 fw-bold">Confidencialidad</h3><p class="mb-0 small text-muted">Tu consulta está protegida por el secreto profesional.</p></div></div>
                <div class="col-md-6 col-lg-3"><div class="value-card text-center"><i class="fas fa-map-marked-alt"></i><h3 class="h5 fw-bold">Conocimiento local</h3><p class="mb-0 small text-muted">Experiencia con el Circuito Judicial, el SAREN y el INTI en Barinas.</p></div></div>
                <div class="col-md-6 col-lg-3"><div class="value-card text-center"><i class="fas fa-hands-helping"></i><h3 class="h5 fw-bold">Claridad</h3><p class="mb-0 small text-muted">Te explicamos tu caso sin tecnicismos antes de dar el siguiente paso.</p></div></div>
            </div>

            <div class="row justify-content-center">
                <div class="col-lg-9">
                    <h2>Cómo trabajamos</h2>
                    <ol>
                        <li><strong>Nos escribes</strong> por WhatsApp al {tel} con un resumen de tu caso y tu municipio.</li>
                        <li><strong>Te orientamos</strong> sobre la materia y los pasos a seguir.</li>
                        <li><strong>Te conectamos</strong> con el abogado especialista para tu zona.</li>
                        <li><strong>Acuerdas directamente</strong> con el profesional los honorarios y la estrategia.</li>
                    </ol>
                    <h2>Dónde atendemos</h2>
                    <p>No tenemos oficina de atención al público: trabajamos a distancia y los abogados de la red atienden en los <a href="/municipios/">12 municipios del estado Barinas</a>. Consulta también nuestras <a href="/servicios/">especialidades</a>.</p>
                    <div class="legal-note mt-4">
                        <p class="mb-0 small"><strong>Importante:</strong> {nombre} es un directorio de orientación y contacto. La información publicada es general y no sustituye la asesoría de un abogado sobre tu caso concreto. Los servicios profesionales los prestan abogados en libre ejercicio.</p>
                    </div>
                </div>
            </div>
        </div>'''.format(nombre=esc(NEGOCIO["nombre"]), inicio=NEGOCIO["anio_inicio"], tel=NEGOCIO["telefono"])
    if NEGOCIO["direccion"]:
        cuerpo = cuerpo.replace("No tenemos oficina de atención al público: trabajamos a distancia y los", "Los")
    return {
        "path": "/quienes-somos", "salida": "quienes-somos.html",
        "titulo": "Quiénes Somos | " + NEGOCIO["nombre"],
        "descripcion": "Conoce {}: directorio legal que desde {} conecta con abogados especialistas en los 12 municipios del estado Barinas.".format(NEGOCIO["nombre"], NEGOCIO["anio_inicio"]),
        "h1": "Quiénes Somos",
        "lead": "El directorio legal que conecta a Barinas con el abogado que su caso necesita.",
        "migas": [("Inicio", "/"), ("Quiénes Somos", "/quienes-somos")],
        "menu_activo": "/quienes-somos",
        "tipo_schema": "AboutPage",
        "cuerpo": cuerpo,
    }


def pagina_contacto():
    botones = "\n".join('                        <a class="municipio-tag" target="_blank" rel="noopener" href="{}">{}</a>'.format(
        wa_url("{} Vengo de la página «Contacto».".format(e["mensaje"])), esc(e["nombre"])) for e in ESPECIALIDADES)
    cuerpo = '''        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-9">
                    <h2>Escríbenos por especialidad</h2>
                    <p>Elige la materia de tu caso y se abrirá WhatsApp con un mensaje listo para enviar:</p>
                    <div class="d-flex flex-wrap gap-2 mb-4">
{botones}
                    </div>

                    <h2>Qué incluir en tu primer mensaje</h2>
                    <ul>
                        <li>Tu nombre y el municipio donde está el caso.</li>
                        <li>Un resumen breve de la situación (qué pasó y cuándo).</li>
                        <li>Si hay fechas límite: audiencias, citaciones o plazos para responder.</li>
                        <li>Los documentos que ya tienes (contratos, actas, sentencias, cédula).</li>
                    </ul>

                    <h2>Dónde atendemos</h2>
                    <p>Atendemos a distancia en los <a href="/municipios/">12 municipios del estado Barinas</a> y a venezolanos en el exterior.</p>

                    <div class="legal-note mt-4">
                        <p class="mb-0 small">Al escribirnos aceptas que tratemos los datos que nos envíes solo para atender tu consulta, según nuestra <a href="/politica-de-privacidad">Política de Privacidad y Tratamiento de Datos</a>. No envíes información sensible que no sea necesaria para una primera orientación.</p>
                    </div>
                </div>
            </div>
        </div>'''.format(botones=botones)
    return {
        "path": "/contacto", "salida": "contacto.html",
        "titulo": "Contacto | {} - WhatsApp {}".format(NEGOCIO["nombre"], NEGOCIO["telefono"]),
        "descripcion": "Contacta a {} por WhatsApp o teléfono ({}). {}. Área de servicio: estado Barinas.".format(
            NEGOCIO["nombre"], NEGOCIO["telefono"], NEGOCIO["horario"]),
        "h1": "Contacto",
        "lead": "Orientación por WhatsApp en todo el estado Barinas.",
        "migas": [("Inicio", "/"), ("Contacto", "/contacto")],
        "menu_activo": "/contacto",
        "tipo_schema": "ContactPage",
        "cuerpo": cuerpo,
    }


def pagina_privacidad(fecha):
    fecha_txt = "{} de {} de {}".format(fecha.day, MESES[fecha.month - 1], fecha.year)
    cuerpo = '''        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-9">
                    <p class="text-muted small">Última actualización: {fecha}</p>

                    <h2>1. Responsable</h2>
                    <p>El sitio <strong>{dominio}</strong> es operado por <strong>{nombre}</strong>, directorio legal con área de servicio en el estado Barinas, Venezuela. Contacto: teléfono y WhatsApp <a href="tel:{tel_e164}">{tel}</a>.</p>

                    <h2>2. Marco legal</h2>
                    <p>Tratamos los datos personales conforme a la Constitución de la República Bolivariana de Venezuela, en particular:</p>
                    <ul>
                        <li><strong>Artículo 28:</strong> toda persona tiene derecho a acceder a la información y a los datos que sobre sí misma consten en registros oficiales o privados, a conocer el uso que se haga de ellos y su finalidad, y a solicitar ante el tribunal competente su actualización, rectificación o destrucción si fuesen erróneos o afectasen ilegítimamente sus derechos (<em>habeas data</em>).</li>
                        <li><strong>Artículo 60:</strong> toda persona tiene derecho a la protección de su honor, vida privada, intimidad, propia imagen, confidencialidad y reputación; la ley limitará el uso de la informática para garantizar esos derechos.</li>
                    </ul>
                    <p>También aplican la Ley Especial contra los Delitos Informáticos, la Ley sobre Mensajes de Datos y Firmas Electrónicas y el secreto profesional que rige la abogacía (Ley de Abogados y Código de Ética Profesional del Abogado Venezolano).</p>

                    <h2>3. Datos que tratamos</h2>
                    <ul>
                        <li><strong>Datos que nos envías voluntariamente</strong> por WhatsApp o llamada: nombre, número de teléfono, municipio, descripción de tu consulta y los documentos que decidas compartir.</li>
                        <li><strong>Código de origen:</strong> los mensajes de WhatsApp que se abren desde esta web terminan con el código «{codigo}», que solo sirve para saber que el contacto llegó desde este sitio.</li>
                        <li><strong>Datos de navegación</strong> recopilados de forma agregada por Google Analytics (páginas visitadas, dispositivo, navegador, ubicación aproximada y tiempo de visita).</li>
                    </ul>
                    <p>Este sitio no tiene formularios de registro ni guarda tus datos en una base de datos propia.</p>

                    <h2>4. Finalidad del tratamiento</h2>
                    <ul>
                        <li>Responder a tu consulta y darte una orientación inicial.</li>
                        <li>Ponerte en contacto con el abogado especialista adecuado para tu caso.</li>
                        <li>Medir el uso del sitio para mejorar sus contenidos.</li>
                    </ul>
                    <p>No vendemos ni cedemos tus datos, ni los usamos para enviar publicidad no solicitada.</p>

                    <h2>5. Con quién compartimos los datos</h2>
                    <ul>
                        <li><strong>Abogados de la red del directorio</strong>, solo cuando pides que te pongamos en contacto y solo la información necesaria para atender tu caso. Están obligados por el secreto profesional.</li>
                        <li><strong>WhatsApp (Meta Platforms)</strong>, como medio de comunicación, según sus propias condiciones.</li>
                        <li><strong>Google</strong>, como proveedor de analítica web.</li>
                        <li><strong>Cloudflare</strong>, como proveedor de alojamiento del sitio.</li>
                        <li>Autoridades competentes, solo cuando lo exija la ley.</li>
                    </ul>

                    <h2>6. Cookies</h2>
                    <p>Usamos cookies de Google Analytics para obtener estadísticas de visitas. Puedes bloquearlas o eliminarlas desde tu navegador o instalar el <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">complemento de inhabilitación de Google Analytics</a>. El sitio funciona igual sin ellas.</p>

                    <h2>7. Conservación</h2>
                    <p>Las conversaciones se conservan el tiempo necesario para atender tu consulta y su seguimiento. Puedes pedir en cualquier momento que borremos tu historial.</p>

                    <h2>8. Tus derechos</h2>
                    <p>Puedes pedir acceso, rectificación, actualización o eliminación de tus datos, u oponerte a su uso, escribiendo al WhatsApp <a href="tel:{tel_e164}">{tel}</a>. Además, puedes ejercer la acción de <em>habeas data</em> del artículo 28 de la Constitución ante el tribunal competente.</p>

                    <h2>9. Seguridad</h2>
                    <p>El sitio se sirve por HTTPS y las conversaciones de WhatsApp tienen cifrado de extremo a extremo. Aun así, te recomendamos compartir solo la información necesaria para una primera orientación.</p>

                    <h2>10. Menores de edad</h2>
                    <p>El sitio está dirigido a mayores de edad. Los casos de niños, niñas y adolescentes deben gestionarse a través de su representante legal.</p>

                    <h2>11. Aviso legal</h2>
                    <p>El contenido del sitio es informativo y general. No constituye asesoría jurídica ni crea una relación abogado-cliente. Cada caso debe ser evaluado por un abogado inscrito en el Inpreabogado.</p>

                    <h2>12. Cambios</h2>
                    <p>Podemos actualizar esta política. La fecha de la última versión aparece al inicio de esta página.</p>
                </div>
            </div>
        </div>'''.format(fecha=fecha_txt, dominio=NEGOCIO["dominio"].replace("https://", ""), nombre=esc(NEGOCIO["nombre"]),
                         tel=NEGOCIO["telefono"], tel_e164=NEGOCIO["telefono_e164"], codigo=NEGOCIO["codigo_whatsapp"])
    if not NEGOCIO["ga_id"]:
        cuerpo = re.sub(r"\s*<li><strong>Datos de navegación</strong>.*?</li>", "", cuerpo, flags=re.S)
    return {
        "path": "/politica-de-privacidad", "salida": "politica-de-privacidad.html",
        "titulo": "Política de Privacidad y Tratamiento de Datos | " + NEGOCIO["nombre"],
        "descripcion": "Política de privacidad y tratamiento de datos de {} conforme a los artículos 28 y 60 de la Constitución de Venezuela: datos que tratamos, finalidad, cookies y tus derechos.".format(NEGOCIO["nombre"]),
        "h1": "Política de Privacidad y Tratamiento de Datos",
        "lead": "Cómo tratamos tus datos cuando nos consultas o visitas este sitio.",
        "migas": [("Inicio", "/"), ("Política de Privacidad", "/politica-de-privacidad")],
        "cuerpo": cuerpo,
    }


def pagina_404():
    return {
        "path": "/404", "salida": "404.html", "noindex": True,
        "titulo": "Página no encontrada | " + NEGOCIO["nombre"],
        "descripcion": "La página que buscas no existe o fue movida.",
        "h1": "Página no encontrada",
        "lead": "La página que buscas no existe o fue movida.",
        "migas": [("Inicio", "/"), ("Página no encontrada", "/404")],
        "cuerpo": '''        <div class="container text-center">
            <p>Prueba desde el <a href="/">inicio</a>, revisa las <a href="/servicios/">especialidades</a> o busca tu <a href="/municipios/">municipio</a>.</p>
        </div>''',
    }


def todas_las_paginas(fecha):
    pags = [pagina_inicio(), pagina_servicios()]
    pags += [pagina_especialidad(e) for e in ESPECIALIDADES]
    pags.append(pagina_municipios())
    pags += [pagina_municipio(m) for m in MUNICIPIOS]
    pags += [pagina_quienes(fecha), pagina_contacto(), pagina_privacidad(fecha), pagina_404()]
    return pags


# ---------------------------------------------------------------------------
# JavaScript, sitemap y robots
# ---------------------------------------------------------------------------
def site_js():
    return '''// Archivo generado por tools/build_site.py. No editar a mano.
(function () {
    'use strict';

    var WA_NUMERO = '%(numero)s';
    var WA_CODE = '%(codigo)s';

    // Todos los mensajes de WhatsApp terminan con el código de esta web.
    function waUrl(mensaje) {
        return 'https://wa.me/' + WA_NUMERO + '?text=' + encodeURIComponent(mensaje.trim() + ' ' + WA_CODE);
    }
    window.waUrl = waUrl;

    var MUNICIPIOS = ['barinas ciudad', 'barinitas', 'socopó', 'sabaneta', 'bolivia', 'cantón', 'arismendi',
                      'barrancas', 'santa bárbara', 'obispos', 'libertad', 'nutrias'];

    window.openWhatsAppModal = function (context) {
        var modal = document.getElementById('whatsappModal');
        var modalText = document.getElementById('modalText');
        var whatsappLink = document.getElementById('whatsappLink');
        var pagina = document.title;
        var c = String(context || '').toLowerCase();
        var message = 'Hola, vengo de la página «' + pagina + '» y necesito asesoría legal.';

        if (c.indexOf('civil') !== -1) {
            message = 'Hola, vi en el Directorio de Barinas que tienen abogados de DERECHO CIVIL. Necesito ayuda con un caso.';
            modalText.textContent = 'Conectándote con un abogado especialista en Derecho Civil en Barinas...';
        } else if (c.indexOf('familia') !== -1) {
            message = 'Hola, necesito un abogado de FAMILIA en Barinas para divorcio/custodia. Vi su directorio.';
            modalText.textContent = 'Conectándote con un abogado especialista en Derecho de Familia en Barinas...';
        } else if (c.indexOf('laboral') !== -1) {
            message = 'Hola, urgente: necesito un abogado LABORAL en Barinas.';
            modalText.textContent = 'Conectándote con un abogado especialista en Derecho Laboral en Barinas...';
        } else if (c.indexOf('penal') !== -1 || c.indexOf('emergencia') !== -1) {
            message = 'Hola, URGENTE: necesito un abogado PENALISTA en Barinas. Es una emergencia.';
            modalText.textContent = 'Conectándote con un abogado penalista disponible en Barinas...';
        } else if (c.indexOf('accidente') !== -1) {
            message = 'Hola, tuve un accidente en Barinas y necesito un abogado. Vi su directorio.';
            modalText.textContent = 'Conectándote con un abogado especialista en accidentes de tránsito en Barinas...';
        } else if (c.indexOf('mercantil') !== -1 || c.indexOf('empresa') !== -1) {
            message = 'Hola, necesito un abogado MERCANTIL en Barinas para asuntos de empresa.';
            modalText.textContent = 'Conectándote con un abogado especialista en Derecho Mercantil en Barinas...';
        } else if (c.indexOf('agrario') !== -1 || c.indexOf('inti') !== -1) {
            message = 'Hola, necesito un abogado AGRARIO en Barinas para regularización de tierras ante el INTI.';
            modalText.textContent = 'Conectándote con un abogado especialista en Derecho Agrario en Barinas...';
        } else if (c.indexOf('saren') !== -1 || c.indexOf('tramite') !== -1) {
            message = 'Hola, necesito ayuda con un trámite SAREN en línea desde Barinas.';
            modalText.textContent = 'Te ayudaremos con tu trámite ante el SAREN...';
        } else if (c.indexOf('exterior') !== -1 || c.indexOf('apostilla') !== -1) {
            message = 'Hola, necesito legalizar documentos en Barinas para usarlos en el exterior.';
            modalText.textContent = 'Te asesoraremos con la legalización y apostilla de documentos...';
        } else if (c.indexOf('intt') !== -1 || c.indexOf('licencia') !== -1) {
            message = 'Hola, necesito asesoría con la licencia de conducir (INTT) en Barinas.';
            modalText.textContent = 'Te orientaremos con tu trámite ante el INTT...';
        } else if (MUNICIPIOS.some(function (m) { return c.indexOf(m) !== -1; })) {
            message = 'Hola, necesito un abogado en ' + context + ', Barinas. Vengo de la página «' + pagina + '».';
            modalText.textContent = 'Buscando abogados disponibles en ' + context + ', Barinas...';
        } else {
            modalText.textContent = 'Un asesor legal te ayudará a identificar el mejor especialista para tu caso en Barinas...';
        }

        whatsappLink.href = waUrl(message);
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    window.closeWhatsAppModal = function (event) {
        if (!event || event.target.id === 'whatsappModal' || event.target.classList.contains('close-modal')) {
            document.getElementById('whatsappModal').classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    // Animaciones: si el CDN de AOS falla, el contenido se muestra igual.
    if (window.AOS) {
        window.AOS.init({ duration: 800, easing: 'ease-in-out', once: true });
    } else {
        document.querySelectorAll('[data-aos]').forEach(function (el) { el.removeAttribute('data-aos'); });
    }

    // Desplazamiento suave para anclas de la misma página
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var id = this.getAttribute('href');
            var destino = id.length > 1 ? document.querySelector(id) : null;
            if (destino) {
                e.preventDefault();
                window.scrollTo({ top: destino.offsetTop - 80, behavior: 'smooth' });
            }
        });
    });

    // Menú móvil
    var toggle = document.getElementById('mobileMenuToggle');
    var menu = document.getElementById('mobileMenu');
    toggle.addEventListener('click', function () {
        var abierto = menu.classList.toggle('open');
        toggle.classList.toggle('active', abierto);
        toggle.setAttribute('aria-expanded', abierto);
    });
    menu.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () {
            menu.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
        });
    });
})();
''' % {"numero": NEGOCIO["whatsapp"], "codigo": NEGOCIO["codigo_whatsapp"]}


def prioridad(path):
    if path == "/":
        return "1.0"
    if path in ("/servicios/", "/municipios/") or path.startswith("/servicios/"):
        return "0.9"
    if path.startswith("/municipios/"):
        return "0.8"
    if path == "/politica-de-privacidad":
        return "0.3"
    return "0.6"


def sitemap(pags, fecha):
    urls = []
    for pg in pags:
        if pg.get("noindex"):
            continue
        urls.append('''   <url>
      <loc>{}</loc>
      <lastmod>{}</lastmod>
      <priority>{}</priority>
   </url>'''.format(url_abs(pg["path"]), fecha.isoformat(), prioridad(pg["path"])))
    return '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{}
</urlset>
'''.format("\n".join(urls))


def robots():
    return "User-agent: *\nAllow: /\n\nSitemap: {}\n".format(url_abs("/sitemap.xml"))


def generar(fecha):
    """Devuelve {ruta_relativa: contenido} de todos los archivos generados."""
    pags = todas_las_paginas(fecha)
    salida = {pg["salida"]: render(pg, fecha) for pg in pags}
    salida["assets/site.js"] = site_js()
    salida["sitemap.xml"] = sitemap(pags, fecha)
    salida["robots.txt"] = robots()
    return pags, salida


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------
class Analizador(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.ids = set()
        self.enlaces = []      # (tag, atributo, valor)
        self.canonical = []
        self.titulo = ""
        self.ld = []
        self._en_titulo = False
        self._en_ld = False
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.enlaces.append((tag, "href", a["href"]))
        if tag in ("img", "script") and a.get("src"):
            self.enlaces.append((tag, "src", a["src"]))
        if tag == "link" and a.get("href"):
            if a.get("rel") == "canonical":
                self.canonical.append(a["href"])
            if a.get("rel") in ("stylesheet", "icon", "apple-touch-icon", "canonical", "alternate"):
                self.enlaces.append((tag, "href", a["href"]))
        if tag == "title":
            self._en_titulo = True
        if tag == "script" and a.get("type") == "application/ld+json":
            self._en_ld = True
            self._buffer = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._en_titulo = False
        if tag == "script" and self._en_ld:
            self._en_ld = False
            self.ld.append("".join(self._buffer))

    def handle_data(self, data):
        if self._en_titulo:
            self.titulo += data
        if self._en_ld:
            self._buffer.append(data)


PROHIBIDO = re.compile(
    r"google\.[a-z.]+/maps|maps\.google|goo\.gl/maps|maps\.app\.goo\.gl|g\.page/|google\s+maps|"
    r"opiniones\s+(?:de|en)\s+google|rese[ñn]as\s+(?:de|en)\s+google|aggregateRating|\"Review\"|abogadosvalencia",
    re.I)
TELEFONO = re.compile(r"(?<!\d)(?:\+?58[\s-]?)?0?4(?:12|14|16|24|26)[\s-]?\d{3}[\s-]?\d{4}(?!\d)")


def tokens_municipio(m):
    """Textos que identifican a un municipio (el nombre del estado 'Barinas' se excluye)."""
    return {t for t in (m["nombre"], m["capital"]) if t != "Barinas"}


def texto_principal(contenido):
    m = re.search(r"<main[^>]*>(.*?)</main>", contenido, re.S)
    return limpiar(m.group(1)) if m else ""


def validar(pags, generados, fecha):
    errores = []
    rutas_pag = {pg["salida"]: pg for pg in pags}
    tel_norm = re.sub(r"\D", "", NEGOCIO["telefono_e164"])[-10:]
    codigo = NEGOCIO["codigo_whatsapp"]
    copy = copyright_texto(fecha.year)

    # Archivos HTML del repositorio que no genera el script (huérfanos)
    for base, dirs, archivos in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "src", "tools")]
        for a in archivos:
            if a.endswith(".html"):
                rel = os.path.relpath(os.path.join(base, a), ROOT).replace(os.sep, "/")
                if rel not in rutas_pag:
                    errores.append("{}: HTML no generado por el script (huérfano)".format(rel))
    if os.path.exists(os.path.join(ROOT, ".htaccess.txt")):
        errores.append(".htaccess.txt: no se usa en Cloudflare Pages; elimínalo")

    ids_por_archivo = {}
    analisis = {}
    for salida, contenido in generados.items():
        if salida.endswith(".html"):
            an = Analizador()
            an.feed(contenido)
            analisis[salida] = an
            ids_por_archivo[salida] = an.ids

    for salida, an in analisis.items():
        pg = rutas_pag[salida]
        contenido = generados[salida]

        if an.h1 != 1:
            errores.append("{}: tiene {} H1 (debe tener 1)".format(salida, an.h1))
        if "2024" in an.titulo:
            errores.append("{}: el título contiene '2024'".format(salida))
        if not pg.get("noindex"):
            esperado = url_abs(pg["path"])
            if an.canonical != [esperado]:
                errores.append("{}: canonical {} (esperado {})".format(salida, an.canonical, esperado))
        if 'href="#"' in contenido:
            errores.append('{}: enlace vacío href="#"'.format(salida))
        if "Reservar cita por WhatsApp" not in contenido or "data-reservar" not in contenido:
            errores.append("{}: falta el botón 'Reservar cita por WhatsApp'".format(salida))
        if "Trámites SAREN en línea" not in contenido or 'id="saren-en-linea"' not in contenido:
            errores.append("{}: falta el bloque 'Trámites SAREN en línea'".format(salida))
        if copy not in contenido:
            errores.append("{}: falta el copyright '{}'".format(salida, copy))
        if 'data-dato="horario">{}<'.format(esc(NEGOCIO["horario"])) not in contenido:
            errores.append("{}: horario distinto o ausente".format(salida))
        if 'data-dato="telefono">{}<'.format(NEGOCIO["telefono"]) not in contenido:
            errores.append("{}: teléfono distinto o ausente".format(salida))
        if PROHIBIDO.search(contenido):
            errores.append("{}: contiene '{}' (Google Maps, opiniones u otro dominio)".format(
                salida, PROHIBIDO.search(contenido).group(0)))

        # Teléfonos: solo el número del negocio
        for t in TELEFONO.findall(contenido):
            if re.sub(r"\D", "", t)[-10:] != tel_norm:
                errores.append("{}: teléfono ajeno {}".format(salida, t))

        # Enlaces internos, recursos y WhatsApp
        for tag, attr, valor in an.enlaces:
            if "wa.me/" in valor or "api.whatsapp.com" in valor:
                u = urlparse(valor)
                if u.path.strip("/") != NEGOCIO["whatsapp"]:
                    errores.append("{}: WhatsApp a otro número {}".format(salida, valor))
                texto = parse_qs(u.query).get("text", [""])[0]
                if not texto.endswith(" " + codigo):
                    errores.append("{}: mensaje de WhatsApp sin el código '{}': {}".format(salida, codigo, texto[:80]))
                continue
            if valor.startswith(("http://", "https://", "//", "tel:", "mailto:", "data:")):
                continue
            if valor.startswith("#"):
                if valor[1:] and valor[1:] not in an.ids:
                    errores.append("{}: ancla inexistente {}".format(salida, valor))
                continue
            if not valor.startswith("/"):
                errores.append("{}: enlace relativo {} (usa rutas absolutas /...)".format(salida, valor))
                continue
            destino = ruta_archivo(valor)
            existe = destino in generados or os.path.isfile(os.path.join(ROOT, destino))
            if not existe:
                errores.append("{}: enlace o recurso roto {}".format(salida, valor))
            elif "#" in valor:
                ancla = valor.split("#", 1)[1]
                if ancla and ancla not in ids_por_archivo.get(destino, set()):
                    errores.append("{}: ancla inexistente {}".format(salida, valor))

        # JSON-LD
        if not pg.get("noindex"):
            if not an.ld:
                errores.append("{}: sin JSON-LD".format(salida))
            tipos = []
            for bloque in an.ld:
                try:
                    datos = json.loads(bloque)
                except ValueError as e:
                    errores.append("{}: JSON-LD inválido ({})".format(salida, e))
                    continue
                for nodo in datos.get("@graph", [datos]):
                    t = nodo.get("@type")
                    tipos.extend(t if isinstance(t, list) else [t])
                    if t == "LegalService":
                        for campo in ("name", "url", "telephone", "areaServed", "knowsAbout", "contactPoint",
                                      "openingHoursSpecification"):
                            if campo not in nodo:
                                errores.append("{}: LegalService sin {}".format(salida, campo))
                        if "address" in nodo and not NEGOCIO["direccion"]:
                            errores.append("{}: LegalService con address sin dirección real".format(salida))
                        if nodo.get("telephone") != NEGOCIO["telefono_e164"]:
                            errores.append("{}: teléfono del schema distinto".format(salida))
                        if sorted(nodo.get("sameAs", [])) != sorted(NEGOCIO["redes"].values()):
                            errores.append("{}: sameAs no coincide con las redes reales".format(salida))
            for requerido in ("LegalService", "WebSite", "BreadcrumbList"):
                if requerido not in tipos:
                    errores.append("{}: JSON-LD sin {}".format(salida, requerido))
            if not any(t in tipos for t in ("WebPage", "AboutPage", "ContactPage", "CollectionPage")):
                errores.append("{}: JSON-LD sin WebPage".format(salida))
            if (pg.get("municipio") or pg["path"].startswith("/servicios/") and pg["path"] != "/servicios/") \
                    and "Service" not in tipos:
                errores.append("{}: JSON-LD sin Service".format(salida))
            if pg["path"] == "/" and "FAQPage" not in tipos:
                errores.append("{}: JSON-LD sin FAQPage".format(salida))

        # Landing de municipio: sin nombres de otros municipios
        m = pg.get("municipio")
        if m:
            h1 = re.search(r"<h1>(.*?)</h1>", contenido).group(1)
            if not html.unescape(h1).startswith("Abogados en " + m["nombre"]):
                errores.append("{}: H1 '{}' no es 'Abogados en {}'".format(salida, h1, m["nombre"]))
            for otro in MUNICIPIOS:
                if otro is m:
                    continue
                for tok in tokens_municipio(otro) - tokens_municipio(m):
                    if re.search(r"(?<![\w-])" + re.escape(tok) + r"(?![\w-])", contenido):
                        errores.append("{}: menciona otro municipio ({})".format(salida, tok))

    # Landings con contenido propio (no copias con otro nombre)
    landings = [(pg["salida"], pg["municipio"]) for pg in pags if pg.get("municipio")]
    textos = {}
    for salida, m in landings:
        t = texto_principal(generados[salida])
        for tok in sorted(tokens_municipio(m) | {m["nombre"]}, key=len, reverse=True):
            t = t.replace(tok, "X")
        textos[salida] = t
    for i, (a, _) in enumerate(landings):
        for b, _ in landings[i + 1:]:
            r = difflib.SequenceMatcher(None, textos[a], textos[b]).ratio()
            if r > 0.75:
                errores.append("{} y {}: contenido demasiado parecido ({:.0%})".format(a, b, r))

    # FAQPage = FAQ visibles
    if not extraer_faqs(generados["index.html"]):
        errores.append("index.html: no se encontraron preguntas frecuentes")

    # Sitemap
    locs = re.findall(r"<loc>(.*?)</loc>", generados["sitemap.xml"])
    esperadas = sorted(url_abs(pg["path"]) for pg in pags if not pg.get("noindex"))
    if sorted(locs) != esperadas:
        errores.append("sitemap.xml: faltan {} / sobran {}".format(
            sorted(set(esperadas) - set(locs)), sorted(set(locs) - set(esperadas))))
    for lm in re.findall(r"<lastmod>(.*?)</lastmod>", generados["sitemap.xml"]):
        if lm != fecha.isoformat():
            errores.append("sitemap.xml: lastmod {} distinto de {}".format(lm, fecha.isoformat()))
    # URLs huérfanas: toda página indexable debe recibir al menos un enlace interno
    enlazadas = set()
    for an in analisis.values():
        for tag, attr, v in an.enlaces:
            if tag == "a" and v.startswith("/"):
                enlazadas.add(ruta_archivo(v))
    for pg in pags:
        if not pg.get("noindex") and pg["salida"] not in enlazadas:
            errores.append("{}: página huérfana (ningún enlace interno la apunta)".format(pg["salida"]))
    if "Sitemap: {}".format(url_abs("/sitemap.xml")) not in generados["robots.txt"]:
        errores.append("robots.txt: no apunta al sitemap")

    # WhatsApp en JavaScript
    js = generados["assets/site.js"]
    if "var WA_CODE = '{}';".format(codigo) not in js or "encodeURIComponent(mensaje.trim() + ' ' + WA_CODE)" not in js:
        errores.append("assets/site.js: waUrl no añade el código al final")
    if js.count("wa.me/") != 1:
        errores.append("assets/site.js: hay enlaces wa.me fuera de waUrl()")
    return errores


# ---------------------------------------------------------------------------
def fecha_de_trabajo(check):
    if os.environ.get("BUILD_DATE"):
        return datetime.date.fromisoformat(os.environ["BUILD_DATE"])
    if check:
        # En --check se valida contra la fecha con la que se generó el sitio.
        try:
            with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
                m = re.search(r"<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>", f.read())
            if m:
                return datetime.date.fromisoformat(m.group(1))
        except OSError:
            pass
    return datetime.date.today()


def main():
    check = "--check" in sys.argv[1:]
    fecha = fecha_de_trabajo(check)
    pags, generados = generar(fecha)

    errores = validar(pags, generados, fecha)
    cambios = []
    for rel, contenido in sorted(generados.items()):
        ruta = os.path.join(ROOT, rel)
        actual = None
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                actual = f.read()
        if actual != contenido:
            cambios.append(rel)
            if not check:
                os.makedirs(os.path.dirname(ruta), exist_ok=True)
                with open(ruta, "w", encoding="utf-8", newline="\n") as f:
                    f.write(contenido)

    if check and cambios:
        errores += ["{}: desactualizado; ejecuta python3 tools/build_site.py".format(c) for c in cambios]

    print("Páginas: {} | Archivos generados: {} | Fecha: {}".format(len(pags), len(generados), fecha.isoformat()))
    if not check:
        print("Archivos modificados: {}".format(len(cambios)))
        for c in cambios:
            print("  - " + c)
    if errores:
        print("\n{} error(es) de validación:".format(len(errores)))
        for e in errores:
            print("  ✗ " + e)
        sys.exit(1)
    print("Validación OK ✓")


if __name__ == "__main__":
    main()
