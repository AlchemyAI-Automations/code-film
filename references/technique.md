# Técnica

## Pipeline

```
script.json ──voice.py──► voices/<id>.wav + timing.json (palabras con tiempo)
film.js (SEQ + at() + escenas) ──events.mjs──► events.json (DUR, voz, foley, secciones)
                               ──readcheck──► prueba de lectura (letras/12 + 2 s)
                               ──video.mjs──► out/video.mp4 (Chrome headless, 4 workers, JPEG → ffmpeg)
events.json + voces ──mix.py──► out/mix.wav (voz comprimida, música con ducking, foley, ~-15 LUFS)
mux.sh ──► <slug>.mp4 (-14 LUFS, pico ≤ -1.2 dB) · srt.py ──► <slug>.srt · poster.jpg
```

Todo eso lo corre `build.sh`.

Tiempos medidos (Mac M-series, 2026-10-04):

| Etapa | "Niñera" (52.5 s, partículas pesadas) | "Nivel operativo v2" (61 s) |
|---|---|---|
| Render (4 workers) | 110 s | 27 a 63 s (según carga de la máquina) |
| Mezcla | 23 s | ~20 s |
| Master con `master.sh` (copia el video) | 4 s | ~4 s |
| Master viejo de lemo (recodificaba en `slow`) | 136 s | · |

Largo de prueba con 2 capítulos (113 s) y un solo capítulo cambiado: 41 s en total.

## Contrato de la página (motor lemo-opuscar)

| Global | Uso |
|---|---|
| `window.render(t)` | dibuja el frame en el segundo t. Pura: sin `Date.now`, sin `Math.random` sin semilla, sin estado entre frames |
| `window.DUR` | duración (sale de la línea de tiempo) |
| `window.EV` | eventos para la mezcla: `meta` (secciones, marcas), `voice`, foley |
| `window.TEXTS(t)` | textos visibles con su caja, para la prueba de lectura |
| `window.READY` | true cuando cargaron las fuentes |

Rutas: la película se sirve en `/@film/`; el motor en `/core/...`. `film.js` importa `./kit.js` y kit importa `/core/lib.js`.

## Línea de tiempo guiada por la voz (kit.js)

```js
const SEQ = [{ pause: 1.2 }, { line: 'v1' }, { pause: 2.2 }, { mark: 'hookOut' }, ...];
const TL = await k.loadTimeline(SEQ);       // lee script.json y voices/timing.json
TL.L.v1.t0 / TL.L.v1.t1                      // inicio y fin de la línea
TL.at('v3a', 'estructura')                   // inicio absoluto de esa palabra (sin acentos, por prefijo si no hay exacta)
TL.M.cut                                     // marca
```

Sin `timing.json` (antes de gastar voz) estima 2.4 palabras/s: sirve para maquetar. Con voz real, todo se reacomoda solo.

## Primitivas (kit.js)

`conduit(p, t, a, {particles, speed, phase, reverse, color, alpha, w})` · `blob(...)` · `wrap(t, a, x, y, rx, ry, seed, fill, stroke, alpha, wob)`
· `pop(t, a, x, y, draw)` · `label(str, x, y, size, color, align, font, weight)` · `stext(id, parts, x, y, size, FONT.x, tIn, tOut, t)`
· `grid(s, cx, cy)` · `veil(x0, y0, x1, y1, ladoDifuso, ancho, alpha)` · `col(hex, alpha)` (respeta el gris global)
· estado: `init`, `setSC`, `setGrey`, `setWorld`, `setFlow`, `setTX`.

Patrón de niveles con zoom: `s` = nivel de cámara; nivel i se dibuja con escala `K^(i - s)`, del mayor al menor; se
omite si la escala < 0.012 o si estamos "adentro" (escala > 9). Ver `nivel-operativo-v2/film.js`.

## Primitivas de producción (kit.js, sección "nivel director")

`springIn(t, a, dur, rebote)` · `shake(t, amp, seed)` (ruido, no seno) · `wordTimes(línea, textoVisible)` ·
`kinetic(id, línea, [{text, color, accent:{palabra: color}}], t, {x, y, size, align, out, punch:{palabra:true}})` ·
`cursorArrow(x, y, press, escala)`. Profundidad de campo: dibujar capas en canvases fuera de pantalla y componer con
`ctx.filter = 'blur(Npx)'` una vez por capa (no por objeto). Cámara por escena: una función que devuelve el
`setTransform` con zoom y foco, aplicada solo a los objetos del mundo (no a subtítulos ni etiquetas).

## Voz (ElevenLabs)

- `eleven_v3`, una voz masculina mexicana. stability 0.8 (con 0.5 v3 cambió el acento a
  media frase), similarity 0.75, style 0, speed 0.94 para explicar con calma.
- Costo: v3 = 2 créditos por carácter. Un corto de 60 s ≈ 750 caracteres. Plan Pro: 500k caracteres al mes.
- Tiempos por palabra con `POST /v1/forced-alignment` (texto sin audio tags). Check con `POST /v1/speech-to-text`.
- Audio tags de v3 (`[serio]`, `[pausa]`) se permiten en `say`; se quitan antes de alinear.

## Problemas ya resueltos (no repetirlos)

| Síntoma | Causa | Arreglo |
|---|---|---|
| Elementos entran gigantes y chocan con el HUD | aparecían por tiempo, antes de caber en el encuadre | aparecer al 55% del movimiento (`outAt`); células al 45% (`cellAt`) |
| Fondo de color al final | el relleno de una célula ampliada cubre la pantalla al volver | desvanecer niveles con escala > 4.5 (`inside`) |
| Etiquetas enormes en los zooms | texto del mundo a 6x | `label` se desvanece entre 34 y 64 px efectivos |
| Mancha gris oscura en estado roto | se mezclaba todo hacia el gris medio | superficies claras van a `#E4E8E7` |
| Texto atenuado sin razón | `globalAlpha` heredado del último nivel | resetear alpha después del loop de niveles |
| Hook y estado roto sin movimiento | escenas fijas > 3 s | push-in lento en el gancho; deriva hacia afuera en el gris |
| Pico arriba de -1.2 dB tras el mux | mezcla a -19 LUFS y loudnorm subía los picos | mix.py normaliza a ~-15 y comprime antes del limitador |
| El master tardaba más que el render | `mux.sh` de lemo recodificaba todo en preset `slow` | `master.sh`: copia el H.264, marca BT.709 con `h264_metadata`, solo procesa audio |
| Todo "va muy rápido" | un nivel cada 1.5 s sin pausa | la voz manda + pausas ≥ 1 s (director.md §1) |
| SRT con "Indi Dev Dan" | usaba la pronunciación | srt.py usa `text` y reparte tiempos |

## Formatos

- 16:9 1920×1080 por defecto (YouTube, LinkedIn). Vertical 1080×1350 o 1080×1920: `SIZE=1080x1350 ./build.sh`, pero la
  escena debe maquetar con `W`/`H` (las coordenadas actuales asumen 1920×1080).
- Fase 2 (cámara cenital + cuadro translúcido): render con fondo transparente (PNG frames → ProRes 4444 o WebM VP9 con
  alpha) y componer en el editor al 70 a 85% de opacidad. Pendiente de construir: hace falta un modo `transparent` en kit.

## Piezas del episodio 00 (`code-films/nada-de-esto-existe/`, 2026-10-05)

| Pieza | Cómo | Dónde copiarla |
|---|---|---|
| Dibujar en otro lienzo | `k.bind(ctx2d)` cambia el contexto del kit; en film.js, `withCtx(canvas, fn)` cambia ambos y restaura | `withCtx`, `quiet` (apaga la recolección de textos) |
| Capas en 3D | cada capa a un lienzo propio; cada plano con `setTransform` (giro en el plano + inclinación ortográfica) y etiqueta a la derecha | `escCapas` |
| La película dentro de sí misma | `render(τ)` a un lienzo de apoyo y `drawImage` reducido; hoja de contacto de 144 cuadros reales con `DEPTH` para no recursar | `viewport`, `buildAtlas` |
| Formas de onda reales | `envelope.py` → `voices/env.json` (RMS a 100 Hz); `wav(id, x0, pps, yc, alto, {m})` | `wav`, `waveV2` |
| Factura real | `metrics.py base` antes de la voz, `metrics.py final <render_s>` antes del render final; film.js lee `metrics.json` | `metrics.py`, `receipt` |
| Cinta que se frena | `tapestop(bus, t)` en mix.py: re-muestreo con velocidad que cae a 0 y silencio después | `mix.py` |
| Zoom de toda una escena a un punto | variable `ZOOM` que respeta `D()` (los textos de kit no se escalan: hay que sacarlos antes) | `escSistema`, `escEco` |

Medido: 120.9 s, 3,626 cuadros, render 102 a 106 s con 4 procesos, 36 min de pared desde el pedido hasta el último render.
