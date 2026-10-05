---
name: code-film
description: Produce videos explicativos hechos 100% con código (sin generador de video IA) estilo Flujo Geométrico, con voz de ElevenLabs sincronizada palabra por palabra, música y efectos sintetizados. Escenas en canvas 2D donde cada frame es función pura del tiempo; render con el motor de lemo-opuscar. Úsalo cuando diga "haz un video con código", "code-film", "corto animado de ingeniería agéntica", "video para LinkedIn/YouTube de [tema]", "variación del video", "/code-film".
---

# code-film

Videos explicativos de 40 a 60 s (cortos) o capítulos más largos, con la voz guiando el ritmo. Nada se genera con IA de video:
la IA escribe el programa que dibuja cada frame y la voz sale de ElevenLabs.

**Películas de referencia (léelas antes de escribir una escena nueva):**
- `code-films/permiso-vs-evidencia/`: **la vara de producción actual** (avalancha de UI con profundidad de campo, corte a
  negro con tipografía cinética, barrido que nace de una línea, objeto que se transforma, cámara que empuja, diseño sonoro propio).
- `code-films/nivel-operativo-v2/`: zoom de escala por niveles y HUD.  `code-films/ninera-de-agentes/`: re-flujo de un grafo.

## Reglas que no se negocian

1. **La voz manda el ritmo.** Cada aparición cae en la palabra que la nombra (`at(línea, palabra)`), y después de cada
   movimiento de cámara hay al menos 1 s quieto. Con ritmo apurado no se alcanza a leer.
2. **Mapa primero, recorrido después.** Si hay una estructura (niveles, pasos, arquitectura), se muestra completa y tenue,
   y luego se recorre.
3. **Una idea por frase de voz, un acento de color por pantalla.** El texto en pantalla es la frase clave de lo que se dice.
4. **Voz del autor**: primera persona,
   cero guiones largos o medios, cero pregunta retórica de gancho, cero hype. Polémica solo con prueba propia detrás.
5. **Nunca publicar.** Se entrega el MP4 + SRT + póster; el autor decide.
6. **Prueba de lectura** (build.sh la corre): cada texto ≥ letras/14 + 1.5 s. Si falla, se alargan pausas, no se recorta texto.

## Flujo

1. **Brief en una sola ronda de preguntas**: tema y fuente, la postura (qué "salseo" y cuál es la prueba propia), duración
   (default 45 a 60 s), formato (16:9 default; 4:5 para el feed de LinkedIn necesita maquetar la escena para ese tamaño),
   voz (default la de `config.json`). Lo que ya esté en el pedido no se pregunta.
2. **Guion** en `script.json`: líneas cortas (una idea cada una). `say` lleva pausas ("...") y, para v3, etiquetas de
   emoción (`[serious]`, `[pause]`); en otros modelos se quitan solas. `direction` por línea (stability, style) dirige la
   actuación. `asr` si el STT escribe distinto algo bien dicho. Perfiles de ejemplo en `config.example.json`: `narrador` (parejo), `narrador_energico` (más variación de tono) y `narrador_v3` (etiquetas de emoción).
3. **Treatment** (`TREATMENT.md`): 3 estructuras candidatas y la elegida, beat sheet, plan de sonido. Ver `references/director.md`.
4. **Crear la carpeta**: `sh ~/.claude/skills/code-film/scripts/new_film.sh <slug>` (o `--from <película>` para una variación).
5. **Voz**: `python3 ~/.claude/skills/code-film/scripts/voice.py <film> --check`. Usa caché (no vuelve a cobrar la misma
   línea). Revisa palabras/s (cómodo: 2.4 a 3.0) y que el check diga OK.
6. **Escena** en `film.js`: `SEQ` con líneas y pausas, anclas con `at()`, niveles y HUD con las primitivas de `kit.js`
   (`references/technique.md`). Copia patrones de la referencia, no su historia.
7. **Ciclo de revisión** (mínimo 2 rondas, máximo 4): `sh scripts/review.sh <film> t1 t2 ...` → mira la hoja con Read,
   califica 1 a 10 contra la rúbrica de `references/director.md`, lista las 3 peores fallas, corrige. Termina con ≥ 8.
8. **Build**: `<film>/build.sh` (eventos, lectura, video con 4 workers, mezcla con ducking, master a -14 LUFS sin
   recodificar el video, SRT, póster). Es incremental: si solo cambió la mezcla, no vuelve a renderizar. `FORCE=1` lo obliga.
9. **QA final**: `sh scripts/review.sh <film> --final` (frames negros, sonoridad, espectro, hoja cada 2 s).
10. **Reportar** con evidencia: duración, LUFS y pico, resultado de la prueba de lectura, qué NO se verificó
    (el modelo no escucha el audio: decirlo siempre).

## Videos largos (más de 90 s): por capítulos

1. Escribir **primero el guion completo** (un solo arco, una sola voz) y partirlo en capítulos de 45 a 75 s.
2. `sh scripts/new_long.sh <slug> <n>` crea `<slug>/chapters/01..n/` (cada uno es una película normal) y `chapters.json`.
3. Cada capítulo lo escribe un **subagente en paralelo** (Agent con `subagent_type: "fork"`), con: su parte del guion, la
   regla de transición (abajo), este SKILL.md y la película de referencia. Cada uno corre voice.py y sus rondas de revisión.
4. `sh scripts/build_long.sh <slug> -j 2`: renderiza capítulos en paralelo (solo los que cambiaron), los une sin
   recodificar, masteriza el audio completo una vez y une los SRT con su desfase.
5. **Transición entre capítulos**: cada capítulo arranca desde la retícula en blanco y termina regresando a ella
   (el último 0.5 s se vacía). Así el corte no se nota y cualquier capítulo se puede rehacer solo.

Sesión nueva por video: en una conversación larga cada llamada relee todo el contexto (se midieron ~550k tokens por
llamada); en una sesión nueva son ~50k a 100k.

## Variaciones

- Mismo tema, otro corte: `new_film.sh <slug-v2> --from <película>`; cambia guion y SEQ; la voz se regenera sola.
- Otro tema: parte de la plantilla y toma piezas de la referencia (niveles con zoom, HUD de escalera, corte en gris,
  célula que encapsula, línea de código que reescribe un agente).
- Otra voz (p. ej. tu propio clon): cambiar `voice` en `config.json`; el hash de caché cambia y se regenera todo.
  Guía de clonación: `references/voice-cloning.md`.

## Instalación (solo la primera vez en una máquina)

- Motor: `git clone https://github.com/lemomo-ai/lemo-opuscar ~/lemo-opuscar` y
  `LEMO_OPUSCAR_HOME=~/lemo-opuscar sh ~/lemo-opuscar/plugin/skills/lemo-opuscar/scripts/setup.sh deps` (npm, Chrome
  headless, venv con numpy/scipy). MIT. No se edita su `core/`.
- ffmpeg en PATH. Key de ElevenLabs: variable `ELEVENLABS_API_KEY` o un archivo `.env` indicado en `envFile` de `config.json`. La key nunca se imprime ni se copia a la película.

## Archivos

| Ruta | Qué es |
|---|---|
| `config.json` | motor, envFile, carpeta de películas, voz y ajustes de ElevenLabs |
| `template/` | index.html, kit.js (primitivas), film.js de ejemplo, script.json, mix.py, build.sh, fuentes |
| `scripts/voice.py` | TTS por línea + forced alignment + check por STT, con caché |
| `scripts/new_film.sh`, `scripts/review.sh`, `scripts/srt.py` | crear, revisar, subtítulos |
| `scripts/master.sh` | master sin recodificar el video (audio a -14 LUFS en 2 pasadas) |
| `scripts/new_long.sh`, `scripts/build_long.sh` | videos largos por capítulos |
| `references/director.md` | ritmo, estructura del "salseo", sonido, rúbrica de revisión |
| `references/style-flujo-geometrico.md` | el estilo: color, tipo, movimiento, cámara, movimientos nativos, fallas |
| `references/technique.md` | contrato de la página, API de kit.js y timeline, mezcla, problemas ya resueltos |
| `references/voice-cloning.md` | cómo clonar tu voz y conectarla |
