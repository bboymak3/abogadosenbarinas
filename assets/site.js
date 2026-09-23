// Archivo generado por tools/build_site.py. No editar a mano.
(function () {
    'use strict';

    var WA_NUMERO = '584167775771';
    var WA_CODE = 'b33';

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
