// kit.js · Flujo Geométrico para code-films (canvas 2D, cada frame es función pura de t).
// Cada película lleva su propia copia (vendoring): si el kit cambia, las películas viejas se siguen renderizando igual.
import { clamp, lerp, seg, ss, eio, eo, ei, back, hash } from '/core/lib.js';
export { clamp, lerp, seg, ss, eio, eo, ei, back, hash };

// ======== paleta oficial (Marketing/brand-personal/visual-language.md) ========
export const C = {
  bg: '#FFFFFF', ink: '#0E1A18', ink2: '#1E2C29', mid: '#8A9794', line: '#D3DDD9', dot: '#DCE6E2',
  soft: '#EAF2EF', pri: '#0aad98', teal: '#3DD4BE', coral: '#FF6B4A', legacy: '#96a1a0',
};
export const FONT = { claim: '600 SIZEpx Clash', mono: '500 SIZEpx JBM', ui: '500 SIZEpx Satoshi' };

// ======== estado del frame (lo fija la escena antes de dibujar) ========
export let ctx = null, W = 1920, H = 1080, S = 1, SC = 1, G = 0, TX = null, INWORLD = false;
let FLOW = t => t;
export function init(canvas) { ctx = canvas.getContext('2d'); W = innerWidth; H = innerHeight; canvas.width = W; canvas.height = H; S = W / 1920; }
// dibuja en otro lienzo del mismo tamaño (capas, miniaturas de la propia película); devuelve el contexto anterior
export function bind(c2d) { const prev = ctx; ctx = c2d; return prev; }
export const setSC = v => { SC = v; };          // escala de pantalla del nivel que se dibuja
export const setGrey = v => { G = v; };         // 0..1: el mundo se apaga (estado "roto")
export const setTX = v => { TX = v; };          // lista de textos para readcheck (null = no recolectar)
export const setWorld = v => { INWORLD = v; };  // true mientras se dibuja en coordenadas de mundo
export const setFlow = fn => { FLOW = fn; };    // tiempo de flujo de partículas (permite frenarlas)
export const flow = t => FLOW(t);
export const px = v => v / SC;                  // grosor en px de pantalla aunque el nivel esté escalado

// ======== color ========
export const rgb = h => { const n = parseInt(h.slice(1), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; };
export const mixc = (a, b, k) => { const A = rgb(a), B = rgb(b); return A.map((v, i) => Math.round(lerp(v, B[i], k))); };
const lum = h => { const [r, g, b] = rgb(h); return .299 * r + .587 * g + .114 * b; };
export const col = (h, a = 1, grey = true) => {
  const [r, g, b] = grey && G > 0 ? mixc(h, lum(h) > 200 ? '#E4E8E7' : C.legacy, G) : rgb(h);
  return `rgba(${r},${g},${b},${a})`;
};

// ======== primitivas ========
export function rrect(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
export function bez(p, u) {
  const v = 1 - u;
  return [v * v * v * p[0] + 3 * v * v * u * p[2] + 3 * v * u * u * p[4] + u * u * u * p[6],
          v * v * v * p[1] + 3 * v * v * u * p[3] + 3 * v * u * u * p[5] + u * u * u * p[7]];
}
// Conducto: bézier que se dibuja (dibujar) y luego lleva partículas (fluir). La firma del sistema.
export function conduit(p, t, a, o = {}) {
  const prog = eo(seg(t, a, a + (o.draw ?? .6))); if (prog <= 0) return;
  const n = 48; ctx.beginPath();
  for (let i = 0; i <= n; i++) { const [x, y] = bez(p, prog * i / n); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
  ctx.strokeStyle = col(o.color || C.pri, o.alpha ?? .45); ctx.lineWidth = px(o.w || 1.6); ctx.stroke();
  if (prog < 1 || o.particles === 0) return;
  const k = o.particles ?? 2, F = flow(t) * (o.speed ?? .35);
  for (let j = 0; j < k; j++) {
    const u = ((F + j / k + (o.phase || 0)) % 1 + 1) % 1, uu = o.reverse ? 1 - u : u;
    for (let tail = 3; tail >= 0; tail--) {
      const [x, y] = bez(p, clamp(o.reverse ? uu + tail * .018 : uu - tail * .018));
      ctx.beginPath(); ctx.arc(x, y, px(tail ? 3.2 - tail * .6 : 4.2), 0, Math.PI * 2);
      ctx.fillStyle = col(tail ? C.teal : C.pri, tail ? .55 - tail * .12 : 1); ctx.fill();
    }
  }
}
// Célula: blob biomórfico que respira (morfear). wob > 1 = inestable.
export function blob(x, y, rx, ry, seed, t, fill, stroke, a = 1, wob = 1) {
  const n = 80; ctx.beginPath();
  for (let i = 0; i <= n; i++) {
    const th = i / n * Math.PI * 2;
    const k = 1 + wob * (.035 * Math.sin(3 * th + t * .9 + seed) + .025 * Math.sin(5 * th - t * 1.3 + seed * 2));
    const X = x + Math.cos(th) * rx * k, Y = y + Math.sin(th) * ry * k;
    i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y);
  }
  ctx.closePath();
  if (fill) { ctx.fillStyle = col(fill, .9 * a); ctx.fill(); }
  if (stroke) { ctx.strokeStyle = col(stroke, .7 * a); ctx.lineWidth = px(1.6); ctx.stroke(); }
}
// Encapsular: la célula se cierra alrededor de lo que ya existe (movimiento nativo del estilo)
export function wrap(t, a, x, y, rx, ry, seed, fill, stroke, al = 1, wob = 1) {
  const p = eo(seg(t, a, a + .8)); if (p <= 0) return;
  const k = lerp(1.45, 1, p); ctx.save(); ctx.globalAlpha *= p; blob(x, y, rx * k, ry * k, seed, t, fill, stroke, al, wob); ctx.restore();
}
// pop-in: escala .94 → 1 y opacidad (escalonar con a + i * 0.06)
export function pop(t, a, x, y, draw, dur = .4) {
  const p = eo(seg(t, a, a + dur)); if (p <= 0) return;
  ctx.save(); ctx.globalAlpha *= p; ctx.translate(x, y); ctx.scale(.94 + .06 * p, .94 + .06 * p); draw(p); ctx.restore();
}
// Etiqueta: en mundo se desvanece si queda gigante (evita letreros enormes en los zooms)
export function label(str, x, y, size, color = C.mid, align = 'center', font = 'JBM', weight = 400) {
  const eff = INWORLD ? size * SC / S : size, fa = INWORLD ? 1 - ss(seg(eff, 34, 64)) : 1;
  if (fa <= 0) return;
  const ga = ctx.globalAlpha; ctx.globalAlpha = ga * fa;
  ctx.font = `${weight} ${size}px ${font}`; ctx.letterSpacing = '0px'; ctx.wordSpacing = '0px';
  ctx.textAlign = align; ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = col(color); ctx.fillText(str, x, y); ctx.globalAlpha = ga;
}
export function setType(font) {
  ctx.font = font; const clash = /Clash/.test(font);
  ctx.letterSpacing = clash ? '-1px' : '0px'; ctx.wordSpacing = clash ? '3px' : '0px';
}
// Texto de pantalla: entra por clip desde la línea base y sale hacia arriba. parts = [[texto, color], ...]
export function stext(id, parts, x, y, size, font, tIn, tOut, t) {
  const p = eo(seg(t, tIn, tIn + .5)), q = ei(seg(t, tOut, tOut + .4));
  if (p <= 0 || q >= 1) return;
  if (typeof parts === 'string') parts = [[parts, C.ink]];
  ctx.save(); ctx.setTransform(S, 0, 0, S, 0, 0); setType(font.replace('SIZE', size));
  const widths = parts.map(([s]) => ctx.measureText(s).width), w = widths.reduce((a, b) => a + b, 0);
  rrect(x - 6, y - size * 1.02, w + 12, size * 1.34, 0); ctx.clip();
  const dy = (1 - p) * size * 1.2 - q * size * 1.2; let xx = x;
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  parts.forEach(([s, c], i) => { ctx.fillStyle = col(c, 1, false); ctx.fillText(s, xx, y + dy); xx += widths[i]; });
  ctx.restore();
  if (TX && q <= 0) TX.push({ id, text: parts.map(p => p[0]).join(''), x0: x * S, y0: (y - size) * S, x1: (x + w) * S, y1: (y + size * .3) * S });
}
// Retícula de puntos que acompaña el zoom (s = nivel de cámara en log base K)
export function grid(s, cx, cy, K = 6) {
  const lg = s * Math.log2(K), f = lg - Math.floor(lg);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  for (let k = 0; k < 3; k++) {
    const sp = 44 * Math.pow(2, k - f) * S, a = clamp((sp / S - 22) / 40) * clamp((190 - sp / S) / 90) * .9;
    if (a <= .01) continue;
    ctx.fillStyle = col(C.dot, a);
    const x0 = cx - Math.ceil(cx / sp) * sp, y0 = cy - Math.ceil(cy / sp) * sp;
    for (let x = x0; x < W; x += sp) for (let y = y0; y < H; y += sp) ctx.fillRect(x - 1.2 * S, y - 1.2 * S, 2.4 * S, 2.4 * S);
  }
}
// Panel blanco con borde difuso: el mundo pasa por debajo del HUD o del texto sin chocar
export function veil(x0, y0, x1, y1, fadeSide, fade, a) {
  if (a <= 0) return;
  ctx.setTransform(S, 0, 0, S, 0, 0);
  const g = fadeSide === 'right' ? ctx.createLinearGradient(x1 - fade, 0, x1, 0)
    : fadeSide === 'left' ? ctx.createLinearGradient(x0 + fade, 0, x0, 0)
    : ctx.createLinearGradient(0, y0, 0, y0 + fade);
  g.addColorStop(0, `rgba(255,255,255,${fadeSide === 'top' ? 0 : .96 * a})`);
  g.addColorStop(1, `rgba(255,255,255,${fadeSide === 'top' ? .96 * a : 0})`);
  ctx.fillStyle = g; ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
}

// ======== línea de tiempo guiada por la voz ========
// seq = [{pause: s}, {line: 'v1'}, {mark: 'cut'}, ...]. Lee script.json y voices/timing.json (si existe).
// Sin voz generada todavía, estima ~2.4 palabras/s para poder maquetar antes de gastar créditos.
const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ]/g, '');
export async function loadTimeline(seq) {
  const script = await (await fetch('script.json')).json();
  let timing = null;
  try { const r = await fetch('voices/timing.json'); if (r.ok) timing = await r.json(); } catch { /* sin voz aún */ }
  const byId = Object.fromEntries(script.lines.map(l => [l.id, l]));
  const measured = id => timing?.lines?.[id];
  const estimate = l => {
    const words = (l.say || l.text).split(/\s+/).filter(Boolean), dur = words.length / 2.4 + .3;
    const total = words.reduce((a, w) => a + w.length + 1, 0); let acc = .15;
    return { dur, words: words.map(w => { const d = (w.length + 1) / total * (dur - .3); const o = { text: w, start: acc, end: acc + d * .9 }; acc += d; return o; }) };
  };
  const L = {}, M = {}, voices = []; let t = 0;
  for (const it of seq) {
    if (it.pause) t += it.pause;
    else if (it.mark) M[it.mark] = t;
    else if (it.line) {
      const l = byId[it.line]; if (!l) throw new Error(`script.json no tiene la línea ${it.line}`);
      const m = measured(it.line) || estimate(l);
      L[it.line] = { t0: t, t1: t + m.dur, text: l.text, words: m.words.map(w => ({ ...w, start: w.start + t, end: w.end + t })) };
      voices.push({ t, type: 'voice', id: it.line, estimated: !measured(it.line) });
      t += m.dur;
    }
  }
  // at('v3', 'estructura') → inicio absoluto de esa palabra (o del primer match por prefijo)
  const at = (id, word, edge = 'start', nth = 0) => {
    const l = L[id]; if (!l) throw new Error(`línea ${id} no programada`);
    const q = norm(word); let hits = l.words.filter(w => norm(w.text) === q);
    if (!hits.length) hits = l.words.filter(w => norm(w.text).startsWith(q));
    if (!hits.length) { console.warn(`[timeline] "${word}" no está en ${id}; uso el inicio de la línea`); return l.t0; }
    return hits[Math.min(nth, hits.length - 1)][edge];
  };
  return { DUR: t, L, M, at, voices, hasVoice: !!timing };
}

// ==================== nivel director: piezas de producción ====================
// resorte con rebote (UI que "aterriza"), 0 → 1 con overshoot
export const springIn = (t, a, dur = .55, bounce = .38) => { const u = clamp((t - a) / dur); if (u <= 0) return 0; if (u >= 1) return 1; return 1 - Math.exp(-6 * u) * Math.cos(u * Math.PI * (2 + 6 * bounce)) * (1 - u * .15); };
// temblor de cámara orgánico (ruido suave, no seno)
export const shake = (t, amp, seed = 0) => [amp * (k_vnoise(t * 9 + seed) - .5) * 2, amp * (k_vnoise(t * 9 + seed + 37) - .5) * 2];
const k_vnoise = x => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u); };

// tiempos de cada palabra visible a partir de la voz (empareja el texto en pantalla con lo que se dijo)
const knorm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ]/g, '');
export function wordTimes(line, display) {
  const out = [], spoken = line.words.map(w => ({ n: knorm(w.text), t: w.start, e: w.end })); let j = 0;
  for (const w of display.split(/\s+/).filter(Boolean)) {
    const n = knorm(w); let k2 = j;
    while (k2 < spoken.length && !(spoken[k2].n && (spoken[k2].n === n || spoken[k2].n.startsWith(n) || n.startsWith(spoken[k2].n)))) k2++;
    if (k2 < spoken.length) { out.push({ w, t: spoken[k2].t, e: spoken[k2].e }); j = k2 + 1; }
    else out.push({ w, t: out.length ? out[out.length - 1].e : line.t0, e: line.t1 });
  }
  return out;
}
// Tipografía cinética: cada palabra sube por máscara cuando se pronuncia. lines = [{text, color?, accent:{palabra: color}}]
// opts: {x, y, size, lh, align, font, out, punch:{palabra: true}} · devuelve la caja para readcheck
export function kinetic(id, line, lines, t, o) {
  const size = o.size, lh = o.lh || size * 1.08, font = (o.font || FONT.claim).replace('SIZE', size);
  ctx.save(); ctx.setTransform(S, 0, 0, S, 0, 0); setType(font);
  const all = wordTimes(line, lines.map(l => l.text).join(' ')); let wi = 0, x0 = 1e9, x1 = -1e9;
  const q = o.out ? ei(seg(t, o.out, o.out + .35)) : 0;
  lines.forEach((l, li) => {
    const ws = l.text.split(/\s+/).filter(Boolean), sp = ctx.measureText(' ').width;
    const widths = ws.map(w => ctx.measureText(w).width), W2 = widths.reduce((a, b) => a + b, 0) + sp * (ws.length - 1);
    let x = o.align === 'left' ? o.x : o.x - W2 / 2; const y = o.y + li * lh;
    x0 = Math.min(x0, x); x1 = Math.max(x1, x + W2);
    ws.forEach((w, k) => {
      const wt = all[wi++] || { t: line.t0 }, p = eo(seg(t, wt.t - .04, wt.t + .26));
      if (p > 0 && q < 1) {
        const clean = knorm(w), col2 = (l.accent && Object.entries(l.accent).find(([kk]) => knorm(kk) === clean)?.[1]) || l.color || o.color || C.ink;
        const punch = o.punch && o.punch[clean] ? 1 + .22 * (1 - springIn(t, wt.t, .5, .5)) : 1;
        ctx.save(); ctx.beginPath(); ctx.rect(x - 8, y - size * 1.05, widths[k] + 16, size * 1.42); ctx.clip();
        ctx.translate(x + widths[k] / 2, y + (1 - p) * size * .9 - q * size * 1.1); ctx.scale(punch, punch);
        ctx.fillStyle = col(col2, 1, false); ctx.textAlign = 'center'; ctx.fillText(w, 0, 0); ctx.restore();
      }
      x += widths[k] + sp;
    });
  });
  ctx.restore();
  const first = all[0]?.t ?? line.t0;
  if (TX && t >= first && q <= 0) TX.push({ id, text: lines.map(l => l.text).join(' '), x0: x0 * S, y0: (o.y - size) * S, x1: x1 * S, y1: (o.y + lh * (lines.length - 1) + size * .3) * S });
}
// Cursor de flecha (en coordenadas actuales). press 0..1 lo hunde
export function cursorArrow(x, y, press = 0, s = 1, fill = '#0E1A18') {
  ctx.save(); ctx.translate(x, y); ctx.scale(s * (1 - .12 * press), s * (1 - .12 * press));
  ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 34); ctx.lineTo(9, 26); ctx.lineTo(15, 40); ctx.lineTo(21, 37); ctx.lineTo(15, 24); ctx.lineTo(26, 24); ctx.closePath();
  ctx.fillStyle = fill; ctx.fill(); ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = 2.2; ctx.stroke(); ctx.restore();
}
