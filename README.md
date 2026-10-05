# code-film

Videos explicativos hechos 100% con código, con voz sintética sincronizada palabra por palabra. Esta es la receta con la que se hizo el episodio "Nada de esto existe".

Un video de 98 s, sin cámara, sin micrófono y sin editor. Cada cuadro lo dibuja un programa. La voz es un modelo de mi voz.

## Las piezas

| Pieza | Qué es | Para qué sirve |
|---|---|---|
| Modelo de IA | Claude Opus 5.5, dentro de Claude Code | Escribe el guion, la escena (`film.js`) y la mezcla de sonido (`mix.py`), y revisa cuadros sueltos |
| Skill | `code-film` (instrucciones y plantilla para Claude Code) | Fija el flujo: guion, voz, escena, revisión, render y master. Trae las reglas de ritmo y de lectura |
| Librería de render | lemo-opuscar (MIT) | Abre la página en Chrome sin pantalla, captura cada cuadro y lo pasa a ffmpeg |
| Kit de animación | `kit.js` (canvas 2D) | Conductos con partículas, células, tipografía cinética, resortes, profundidad de campo |
| Voz | Clon profesional de mi voz en ElevenLabs (`eleven_multilingual_v2`) | Genera cada línea. Alineación forzada de ElevenLabs para el tiempo de cada palabra |
| Revisión de la voz | Transcripción automática de ElevenLabs | Compara lo que dice la voz contra el guion |
| Sonido | Síntesis en Python (numpy y scipy) | Música, efectos y mezcla; la voz domina la música con ducking |
| Master | ffmpeg | −14 LUFS, color BT.709, sin recodificar el video |

## La técnica

1. **Cada cuadro es una función del tiempo.** La página expone `render(t)`, sin azar ni estado entre cuadros. El render pide `t = 0, 1/30, 2/30, ...` y guarda una imagen por cada uno.
2. **La voz manda el ritmo.** Primero se genera la voz y la alineación da el segundo exacto de cada palabra. Cada animación se ancla con `at('v3', 'código')`. Si cambias una palabra del guion, todo se reacomoda solo.
3. **Una prueba de lectura automática.** Cada texto en pantalla debe durar al menos letras/14 + 1.5 s. Si falla, el render se detiene.
4. **Revisión por cuadros.** Antes de renderizar, se congelan 10 o 12 instantes y se mira la hoja de contacto.
5. **Datos reales en pantalla.** Las formas de onda salen de los audios, la factura sale de mediciones del propio episodio.

## Los ajustes de la voz

Perfil `angel_promo`: estabilidad 0.15, similitud 0.8, estilo 0.8, velocidad 1.10. Cada línea lleva un texto previo que le da la intención ("lo digo con entusiasmo...") y el modelo no lo pronuncia. Una voz clonada reproduce cómo hablaste al entrenarla, así que para más emoción hay que grabarla con esa energía.

## Lo que costó un episodio de ~100 s

Medido en la sesión del episodio 00: unos 1,100 créditos de voz por pasada completa, del orden de 40 a 100 s de render con 4 procesos en una máquina libre, y 84 llamadas al modelo en total contando varias rondas de ajuste.

## Cómo se arma desde cero

1. Instala Claude Code, ffmpeg, Node y Python 3.
2. Clona lemo-opuscar (MIT) en `~/lemo-opuscar` y corre su `setup.sh deps`.
3. Clona este repo en `~/.claude/skills/code-film`.
4. Copia `config.example.json` a `config.json`, pon tu `TU_VOICE_ID` y exporta `ELEVENLABS_API_KEY` (nunca la guardes en el repo).
5. Descarga las tipografías (ver `template/fonts/LEEME.md`).
6. En Claude Code: `/code-film` y describe el video. O a mano: `scripts/new_film.sh mi-video`, edita `script.json`, `scripts/voice.py <película> --check`, pide la escena, `scripts/review.sh`, `./build.sh`.

La clonación de una voz profesional pide unos 30 minutos de lectura y varias horas de entrenamiento en ElevenLabs. Ver `references/voice-cloning.md`.

## Licencia

MIT para el código de este repo. Las tipografías no se incluyen y cada una tiene su propia licencia.
