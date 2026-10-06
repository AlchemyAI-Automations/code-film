#!/usr/bin/env python3
"""Miniatura de un code-film: arte con GPT Image 2.5 Sunburst + titular con la tipografía real de la marca.
Uso: thumbnail.py <film_dir> [--variants dark,light] [--art-only] [--redo-art]
Lee <film_dir>/thumbnail.json:
  {"kicker": "EPISODIO 00", "headline": ["NADA", "DE ESTO", "EXISTE."], "accent": 2, "footer": "0 cámaras · 0 editores",
   "art": {"dark": "prompt en inglés del arte oscuro", "light": "prompt en inglés del arte claro"}}
`accent` es el índice de la línea del titular que va en teal. Escribe en <film_dir>/miniatura/:
  arte-<v>.png (sin texto, 1920x1080), miniatura-<v>.png y miniatura-<v>.jpg (1280x720, menos de 2 MB).
La llave OPENAI_API_KEY sale de la variable de entorno o del envFile de config.json; nunca se imprime."""
import argparse, base64, json, os, subprocess, sys, tempfile, urllib.request
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFGP = os.path.join(SKILL, 'config.json' if os.path.exists(os.path.join(SKILL, 'config.json')) else 'config.example.json')
CFG = json.load(open(CFGP))
MODEL = 'gpt-image-2.5-sunburst'
COMMON = ("Premium tech-film aesthetic, ultra clean, crisp, high contrast, cinematic lighting, shallow depth of field. "
          "Absolutely NO text, NO letters, NO numbers, NO logos, NO watermarks anywhere in the image. "
          "Leave the left 42 percent of the frame as calm uncluttered negative space for a headline to be added later. "
          "The subject sits on the right 58 percent. No real human face: abstract only. "
          "Palette strictly: white, mint, ink #0E1A18, teal #0aad98, light teal #3DD4BE, one tiny coral #FF6B4A accent.")


def secret(name):
    if os.environ.get(name): return os.environ[name]
    p = os.path.expanduser(CFG.get('envFile', '') or '')
    if p and os.path.exists(p):
        for line in open(p):
            if line.startswith(name + '='): return line.split('=', 1)[1].strip().strip('"\'')
    sys.exit(f'✗ falta {name} (variable de entorno o envFile de config.json)')


def make_art(prompt, out):
    body = json.dumps({'model': MODEL, 'prompt': prompt + ' ' + COMMON, 'n': 1, 'size': '1920x1088', 'quality': 'high', 'output_format': 'png'}).encode()
    req = urllib.request.Request('https://api.openai.com/v1/images/generations', body,
                                 {'Authorization': 'Bearer ' + secret('OPENAI_API_KEY'), 'Content-Type': 'application/json'})
    try: r = json.load(urllib.request.urlopen(req, timeout=600))
    except urllib.error.HTTPError as e: sys.exit(f'✗ OpenAI {e.code}: {e.read()[:300].decode(errors="ignore")}')
    open(out, 'wb').write(base64.b64decode(r['data'][0]['b64_json']))
    from PIL import Image   # el modelo pide múltiplos de 16: 1920x1088; se recorta a 16:9 exacto
    im = Image.open(out)
    if im.size != (1920, 1080): im.crop((0, (im.height - 1080) // 2, 1920, (im.height - 1080) // 2 + 1080)).save(out)


HTML = """<!doctype html><meta charset=utf-8><style>
@font-face{font-family:Clash;src:url(FONTS/ClashDisplay-700.woff2);font-weight:700}
@font-face{font-family:JBM;src:url(FONTS/JetBrainsMono-500.woff2);font-weight:500}
html,body{margin:0;background:#000}#c{position:relative;width:1920px;height:1080px;overflow:hidden}
#c img{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}
.t{position:absolute;left:96px;font:700 206px/0.92 Clash;letter-spacing:-4px;word-spacing:46px;color:#fff;text-shadow:0 8px 60px rgba(0,0,0,.55)}
.t b{color:#3DD4BE;font-weight:700}.k{position:absolute;left:104px;font:500 38px JBM;letter-spacing:2px;color:#3DD4BE}
.f{position:absolute;left:104px;bottom:104px;font:500 40px JBM;color:#9FB2AD}
.l .t{color:#0E1A18;text-shadow:none}.l .t b{color:#0aad98}.l .k{color:#0aad98}.l .f{color:#5C6F6B}
</style><div id=c class="CLS"><img src="IMG"><div class=k style="top:TOPKpx">KICKER</div><div class=t style="top:TOPTpx">HEAD</div><div class=f>FOOT</div></div>
<script>document.fonts.ready.then(()=>{document.title='ready'})</script>"""


def compose(film, spec, variants):
    lines = spec['headline']; n = len(lines)
    size_top = max(240, 540 - 105 * n)               # titular centrado en vertical para 2 a 4 líneas
    acc = spec.get('accent', n - 1)
    head = '<br>'.join(f'<b>{l}</b>' if i == acc else l for i, l in enumerate(lines))
    tmp = tempfile.mkdtemp(); shots = []
    for v in variants:
        art = os.path.join(film, 'miniatura', f'arte-{v}.png')
        html = (HTML.replace('FONTS', 'file://' + os.path.join(SKILL, 'template', 'fonts')).replace('CLS', 'l' if v == 'light' else '')
                .replace('IMG', 'file://' + art).replace('KICKER', spec.get('kicker', '')).replace('HEAD', head)
                .replace('FOOT', spec.get('footer', '')).replace('TOPK', str(size_top - 66)).replace('TOPT', str(size_top)))
        hp = os.path.join(tmp, f'{v}.html'); open(hp, 'w').write(html); shots.append((v, hp))
    js = os.path.join(tmp, 'shot.mjs'); lib = os.path.expanduser(CFG.get('lib', '~/lemo-opuscar'))
    open(js, 'w').write(f"""import {{ chromium }} from '{lib}/node_modules/playwright-core/index.mjs';
const b = await chromium.launch();
for (const [v, hp, out] of JSON.parse(process.argv[2])) {{
  const pg = await b.newPage({{ viewport: {{ width: 1920, height: 1080 }} }});
  await pg.goto('file://' + hp); await pg.waitForFunction(() => document.title === 'ready'); await pg.waitForTimeout(300);
  await pg.screenshot({{ path: out }}); await pg.close();
}}
await b.close();""")
    jobs = [[v, hp, os.path.join(film, 'miniatura', f'miniatura-{v}.png')] for v, hp in shots]
    subprocess.run(['node', js, json.dumps(jobs)], check=True)
    from PIL import Image
    for v, _, png in jobs:
        jpg = png[:-4] + '.jpg'; Image.open(png).convert('RGB').resize((1280, 720), Image.LANCZOS).save(jpg, quality=92, optimize=True)
        print('✓', jpg, os.path.getsize(jpg) // 1024, 'KB')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('film'); ap.add_argument('--variants', default='dark,light')
    ap.add_argument('--art-only', action='store_true'); ap.add_argument('--redo-art', action='store_true'); a = ap.parse_args()
    film = os.path.abspath(a.film); spec = json.load(open(os.path.join(film, 'thumbnail.json')))
    os.makedirs(os.path.join(film, 'miniatura'), exist_ok=True); variants = a.variants.split(',')
    for v in variants:
        out = os.path.join(film, 'miniatura', f'arte-{v}.png')
        if a.redo_art or not os.path.exists(out): print('arte', v, '...', flush=True); make_art(spec['art'][v], out)
        else: print('arte', v, 'ya existe (--redo-art para regenerar)')
    if not a.art_only: compose(film, spec, variants)
