// Password-protect a wikime report: the whole HTML is encrypted with AES-GCM (256-bit key
// derived from the password with PBKDF2-SHA256) and wrapped in an access screen that
// decrypts it in the reader's browser. Without the password the content cannot be read,
// not even from the page source.
//
// Usually called by build_wiki.py --protect. Standalone use:
//   WIKIME_PASSWORD='...' node protect.mjs <in.html> <out.html> [--title T] [--lang es|en] [--accent #5b7a1f] [--artifact]
//
// The password is read only from the WIKIME_PASSWORD environment variable, so it never
// shows up in the process list. --artifact writes the variant without <!doctype> that a
// claude.ai Artifact expects.
import { readFileSync, writeFileSync } from 'node:fs';
import { webcrypto } from 'node:crypto';

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 && args[i + 1] ? args.splice(i, 2)[1] : def; };
const artifact = args.includes('--artifact') ? (args.splice(args.indexOf('--artifact'), 1), true) : false;
const title = opt('--title', 'Informe');
const lang = opt('--lang', 'es').slice(0, 2);
const accent = opt('--accent', '#5b7a1f');
const [input, output] = args;
const password = process.env.WIKIME_PASSWORD || '';
if (!input || !output) { console.error('Uso: WIKIME_PASSWORD=... node protect.mjs <in.html> <out.html> [--title T] [--lang es] [--accent #hex] [--artifact]'); process.exit(2); }
if (!password) { console.error('ERROR: falta la contraseña (variable WIKIME_PASSWORD)'); process.exit(2); }
if (!/^#[0-9a-fA-F]{3,8}$/.test(accent)) { console.error('ERROR: --accent debe ser un color hex, por ejemplo #5b7a1f'); process.exit(2); }

const TXT = {
  es: { tag: 'Acceso restringido', lead: 'Ingresa la contraseña para ver el informe.', label: 'Contraseña', go: 'Entrar', busy: 'Abriendo…', bad: 'Contraseña incorrecta. Inténtalo de nuevo.' },
  en: { tag: 'Restricted access', lead: 'Enter the password to view this report.', label: 'Password', go: 'Open', busy: 'Opening…', bad: 'Wrong password. Try again.' },
}[lang] || null;
const L = TXT || { tag: 'Restricted access', lead: 'Enter the password to view this report.', label: 'Password', go: 'Open', busy: 'Opening…', bad: 'Wrong password. Try again.' };
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const html = readFileSync(input, 'utf8');
const enc = new TextEncoder();
const ITER = 250000;
const salt = webcrypto.getRandomValues(new Uint8Array(16));
const iv = webcrypto.getRandomValues(new Uint8Array(12));
const base = await webcrypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveKey']);
const key = await webcrypto.subtle.deriveKey({ name: 'PBKDF2', salt, iterations: ITER, hash: 'SHA-256' }, base,
  { name: 'AES-GCM', length: 256 }, false, ['encrypt']);
const ct = new Uint8Array(await webcrypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, enc.encode(html)));
const b64 = (u) => Buffer.from(u).toString('base64');

const page = `<title>${esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>
:root {
  --bg: #f6f6f3; --panel: #ffffff; --fg: #1b1b19; --muted: #6f6f69; --line: #e7e7e2;
  --accent: ${accent}; --accent-fg: #ffffff; --error: #b3261e;
  --font-display: 'Newsreader', Georgia, serif;
  --font-body: 'Geist', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #131312; --panel: #1c1c1a; --fg: #ecece8; --muted: #9c9c95; --line: #2a2a27;
    --accent: color-mix(in srgb, ${accent} 62%, #ffffff); --accent-fg: #131312; --error: #ff8a80; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #131312; --panel: #1c1c1a; --fg: #ecece8; --muted: #9c9c95; --line: #2a2a27;
  --accent: color-mix(in srgb, ${accent} 62%, #ffffff); --accent-fg: #131312; --error: #ff8a80; color-scheme: dark;
}
html, body { height: 100%; margin: 0; }
body { background: var(--bg); color: var(--fg); font-family: var(--font-body); font-size: 15px; }
.screen { min-height: 100%; display: grid; place-items: center; padding: 32px 16px; box-sizing: border-box; }
.card { width: 100%; max-width: 380px; background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 32px 28px; display: flex; flex-direction: column; gap: 20px; box-sizing: border-box; }
.tag { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
h1 { font-family: var(--font-display); font-weight: 400; font-size: 30px; line-height: 1.15; margin: 0; text-wrap: balance; }
p { margin: 0; color: var(--muted); line-height: 1.5; }
form { display: flex; flex-direction: column; gap: 12px; }
label { font-size: 13px; font-weight: 500; }
input { font: inherit; color: var(--fg); background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 11px 12px; width: 100%; box-sizing: border-box; }
input:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
button { font: inherit; font-weight: 600; background: var(--accent); color: var(--accent-fg); border: 0; border-radius: 8px; padding: 12px; cursor: pointer; }
button:disabled { opacity: .6; cursor: progress; }
.error { color: var(--error); font-size: 13px; min-height: 1.3em; }
</style>
<main class="screen">
  <section class="card">
    <span class="tag">${esc(L.tag)}</span>
    <h1>${esc(title)}</h1>
    <p>${esc(L.lead)}</p>
    <form id="unlock" autocomplete="off">
      <label for="pw">${esc(L.label)}</label>
      <input id="pw" type="password" autocomplete="current-password" required autofocus>
      <div class="error" id="err" role="alert"></div>
      <button id="go" type="submit">${esc(L.go)}</button>
    </form>
  </section>
</main>
<script>
(function () {
  var D = { s: "${b64(salt)}", i: "${b64(iv)}", c: "${b64(ct)}", n: ${ITER} };
  var M = ${JSON.stringify({ go: L.go, busy: L.busy, bad: L.bad })};
  var b = function (s) { return Uint8Array.from(atob(s), function (ch) { return ch.charCodeAt(0); }); };
  var form = document.getElementById("unlock"), input = document.getElementById("pw");
  var err = document.getElementById("err"), btn = document.getElementById("go");
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    err.textContent = ""; btn.disabled = true; btn.textContent = M.busy;
    try {
      var base = await crypto.subtle.importKey("raw", new TextEncoder().encode(input.value), "PBKDF2", false, ["deriveKey"]);
      var key = await crypto.subtle.deriveKey({ name: "PBKDF2", salt: b(D.s), iterations: D.n, hash: "SHA-256" }, base, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
      var plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv: b(D.i) }, key, b(D.c));
      var html = new TextDecoder().decode(plain);
      document.open(); document.write(html); document.close();
    } catch (x) {
      err.textContent = M.bad;
      btn.disabled = false; btn.textContent = M.go; input.select();
    }
  });
})();
</script>
`;
const standalone = `<!doctype html>\n<html lang="${esc(lang)}">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n` + page;
writeFileSync(output, artifact ? page : standalone);
console.log(`  protegido: ${output} (${Math.round((artifact ? page : standalone).length / 1024)} KB)`);
