// Prueba en navegador (Playwright + Chromium) de que TODOS los mensajes de WhatsApp
// terminan con el código de la web: enlaces wa.me estáticos y los que arma site.js.
//
// Uso: node tools/test_whatsapp.js        (requiere el paquete "playwright")
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const js = fs.readFileSync(path.join(ROOT, 'assets/site.js'), 'utf8');
const CODE = js.match(/var WA_CODE = '([^']+)'/)[1];
const TIPOS = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
                '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.xml': 'application/xml', '.txt': 'text/plain' };

// Servidor estático con URLs limpias, como Cloudflare Pages
function archivo(url) {
  let p = decodeURIComponent(url.split('?')[0].split('#')[0]);
  if (p.endsWith('/')) p += 'index.html';
  else if (!path.extname(p)) p += '.html';
  return path.join(ROOT, p);
}

function paginas(dir = ROOT) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => {
    if (e.name.startsWith('.') || ['node_modules', 'src', 'tools'].includes(e.name)) return [];
    const full = path.join(dir, e.name);
    if (e.isDirectory()) return paginas(full);
    return e.name.endsWith('.html') ? ['/' + path.relative(ROOT, full).split(path.sep).join('/')] : [];
  });
}

function textoDe(href) {
  const u = new URL(href);
  return u.searchParams.get('text') || '';
}

(async () => {
  const server = http.createServer((req, res) => {
    const f = archivo(req.url);
    if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': TIPOS[path.extname(f)] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(res);
  }).listen(0);
  const base = `http://127.0.0.1:${server.address().port}`;

  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errores = [];
  let revisados = 0;
  page.on('pageerror', e => errores.push(`Error JS: ${e.message}`));
  // Los CDN externos no son necesarios para la prueba
  await page.route(/^https?:\/\/(?!127\.0\.0\.1)/, r => r.abort());

  for (const ruta of paginas()) {
    await page.goto(base + ruta, { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => typeof window.openWhatsAppModal === 'function');
    const titulo = await page.title();

    // 1) Enlaces wa.me estáticos
    const hrefs = await page.$$eval('a[href*="wa.me/"]', as => as.map(a => a.href));
    for (const h of hrefs) {
      revisados++;
      if (!textoDe(h).endsWith(' ' + CODE)) errores.push(`${ruta}: enlace sin código -> ${textoDe(h)}`);
    }
    if (!await page.$('a[data-reservar]')) errores.push(`${ruta}: falta el botón Reservar cita`);

    // 2) Cada botón que abre el modal (el mensaje lo arma JavaScript)
    const n = await page.$$eval('[onclick*="openWhatsAppModal"]', els => els.length);
    for (let i = 0; i < n; i++) {
      await page.evaluate(i => document.querySelectorAll('[onclick*="openWhatsAppModal"]')[i].click(), i);
      const href = await page.getAttribute('#whatsappLink', 'href');
      const txt = textoDe(href);
      revisados++;
      if (!txt.endsWith(' ' + CODE)) errores.push(`${ruta}: modal #${i} sin código -> ${txt}`);
      await page.evaluate(() => window.closeWhatsAppModal());
    }

    // 3) El mensaje genérico (botón flotante) incluye el título de la página
    await page.click('.whatsapp-float');
    const generico = textoDe(await page.getAttribute('#whatsappLink', 'href'));
    revisados++;
    if (!generico.includes(titulo)) errores.push(`${ruta}: el mensaje genérico no incluye el título «${titulo}»`);
    if (!generico.endsWith(' ' + CODE)) errores.push(`${ruta}: mensaje genérico sin código`);
    await page.evaluate(() => window.closeWhatsAppModal());
  }

  await browser.close();
  server.close();
  console.log(`Mensajes de WhatsApp revisados: ${revisados} | código: ${CODE}`);
  if (errores.length) {
    errores.forEach(e => console.log('  ✗ ' + e));
    process.exit(1);
  }
  console.log('Todos los mensajes terminan con el código ✓');
})();
