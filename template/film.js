// Plantilla de code-film (Flujo Geométrico, guiado por la voz). Copia de trabajo: reescribe las escenas, conserva el contrato.
// Referencia completa: Marketing/brand-personal/code-films/nivel-operativo-v2/film.js
import * as k from './kit.js';
const { C, FONT, col, conduit, wrap, pop, label, stext, grid, px } = k;

k.init(document.getElementById('c'));
const ctx = k.ctx, W = k.W, H = k.H, S = k.S;

// 1) Secuencia: la voz manda; las pausas dan tiempo de ver (regla: ≥ 1 s quieto después de cada movimiento)
const SEQ = [{ pause: .8 }, { line: 'v1' }, { pause: 1.4 }, { line: 'v2' }, { pause: 1.6 }, { line: 'v3' }, { pause: 2.8 }];
const TL = await k.loadTimeline(SEQ);
const { L, at } = TL, DUR = TL.DUR;
// 2) Anclas: cada aparición cae en la palabra que la nombra
const T = { agent: at('v1', 'agente'), system: at('v1', 'sistema'), connect: at('v2', 'conectas'), out: L.v3.t0 - .4, sign: L.v3.t0 };
const NODES = [[-300, 0], [0, -150], [300, 0], [0, 150]];

function render(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  const cx = 960 * S, cy = 470 * S; grid(0, cx, cy);
  k.setSC(S); ctx.setTransform(S, 0, 0, S, cx, cy); k.setWorld(true);
  // un nodo cuando se dice "agente"; el resto + conductos cuando se dice "sistema"; la célula cuando se dice "conectas"
  wrap(t, T.connect, 0, 0, 420, 250, 2.1, C.soft, C.pri, 1);
  NODES.forEach(([x, y], i) => i && conduit([NODES[0][0], NODES[0][1], x * .3, y - 60, x * .7, y - 60, x, y], t, T.system + .2 + i * .12, { particles: 2 }));
  NODES.forEach(([x, y], i) => pop(t, i ? T.system + i * .12 : T.agent, x, y, () => {
    ctx.beginPath(); ctx.arc(0, 0, 34, 0, Math.PI * 2); ctx.fillStyle = col(C.bg); ctx.fill(); ctx.strokeStyle = col(C.pri); ctx.lineWidth = px(2); ctx.stroke();
    label(`agente ${i + 1}`, 0, 66, 22, C.ink2);
  }));
  k.setWorld(false); ctx.setTransform(1, 0, 0, 1, 0, 0);
  stext('t1', [['Un sistema ', C.ink], ['hace un proceso.', C.pri]], 360, 900, 64, FONT.claim, T.system - .1, T.out, t);
  stext('t2', [['Ingeniería agéntica, en español.', C.mid]], 360, 900, 28, FONT.mono, T.sign, 1e9, t);
}
const EV = [{ t: 0, type: 'meta', dur: DUR, sections: { setup: [0, T.system], climb: [T.system, T.out], outro: [T.out, DUR] } }, ...TL.voices,
  { t: T.agent, type: 'pop', level: 0 }, { t: T.system, type: 'pop', level: 2 }, { t: T.connect, type: 'rise', d: .8 }, { t: T.sign + .4, type: 'ding', v: .4 }];
window.DUR = DUR; window.EV = EV.sort((a, b) => a.t - b.t); window.render = render;
window.TEXTS = t => { k.setTX([]); render(t); const out = k.TX; k.setTX(null); return out; };
await Promise.all(['600 20px Clash', '500 20px Satoshi', '500 20px JBM'].map(f => document.fonts.load(f)));
render(0); window.READY = true;
