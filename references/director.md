# Dirección de un code-film

Se juzga en este orden: **se entiende**, ritmo, sonido, cámara, belleza. Un frame bonito que no se alcanza a leer es falla.

## 0. Vara de producción: que enganche, nada documental

- Gancho visual y sonoro en el primer segundo: algo ya pasa en el frame 1 (ráfaga, caos, contraste).
- Contraste de actos: blanco ↔ negro, ruido ↔ silencio, caos ↔ orden. El corte duro a negro con silencio es el arma más fuerte.
- La tipografía es protagonista: cinética, palabra por palabra en el momento en que se dice (`kinetic`), con golpe en la palabra clave.
- Transiciones diseñadas, nunca fundidos: barrido que nace de una línea, objeto que se transforma en otro, todo que se recoge en un punto.
- Materia: sombras suaves, profundidad de campo (capas borrosas), resortes con rebote en la UI, cámara que empuja en el momento clave.
- Cero taglines o firmas genéricas ("Ingeniería agéntica, en español" quedó prohibido).
- Valor: la historia deja una regla aplicable (ej. "permiso vs evidencia"), no solo una anécdota.

## 1. Ritmo (feedback de uso real)

La v1 de "Nivel operativo" (30 s, un nivel cada 1.5 s, sin pausas) se sintió "muy rápido, no se alcanza a leer o
comprender, satura". La v2 (61 s, voz guiando, pausas) es la vara. Reglas:

- **La voz manda.** Toda aparición importante cae en la palabra que la nombra. Nada aparece "porque sí" entre frases.
- **Mover, aterrizar, quedarse.** Después de cada movimiento de cámara, ≥ 1 s quieto antes del siguiente.
  Un movimiento dura entre 1.1 y 1.6 s (eio). Nunca dos movimientos encadenados sin pausa.
- **Frases cortas de voz con pausa entre ellas** (0.7 a 1 s) cuando cada frase introduce un elemento visual nuevo.
  Si la voz nombra 3 cosas en 2 s, se parte la línea en varias (así se hizo con v3a a v3e).
- **Mapa primero, recorrido después.** Estructuras (niveles, pasos, arquitectura) se muestran completas y tenues;
  luego se recorren e iluminan.
- **Una idea por pantalla.** Máximo 2 líneas de texto en pantalla y un solo color de acento.
- Duración: corto de 45 a 60 s. Gancho visible y audible en los primeros 2 s.
- Lectura: cada texto ≥ letras/14 + 1.5 s (build.sh lo verifica; antes era /12 + 2 s y el episodio 00 se sintió lento). Velocidad de voz cómoda: 2.4 a 3.0 palabras/s.

## 2. Estructura del "salseo" (la que funcionó)

1. **Gancho**: la afirmación provocadora con atribución (si es de alguien más, se le acredita en pantalla).
2. **Mapa**: el marco que la explica, completo y tenue.
3. **Recorrido**: cada pieza del marco, nombrada y mostrada, con pausa.
4. **Giro**: la tensión (lo que nadie dice, el costo, el riesgo). Visualmente: algo se rompe o se apaga.
5. **Regla propia**: la postura del autor en primera persona, con prueba (sistema real, cliente, decisión).
6. **Eco**: volver a la imagen del inicio, transformada. Cierre de identidad, nunca CTA de clic.

Otras estructuras válidas: antes/después en pantalla dividida, un proceso que se construye pieza por pieza, un número
que se explica. Escribe siempre 3 candidatas en el treatment; la primera que se ocurre suele ser el cliché.

## 3. Voz y texto

- **Suena como si lo dijera el autor.** Contundente, cero relleno, experiencia sólida detrás, algo de hype y autoridad
  implícita: "tengo la respuesta" sin decirlo nunca. La solución se cuenta como hecha ("Las rehice."), sin titubeos.
- **Prohibidas las fórmulas de narrador**: "X lo dijo sin rodeos", "sin anestesia", "te voy a explicar", "en este video",
  "hoy hablamos de", "la verdad es que", "déjame decirte", "básicamente", "vamos a ver", "spoiler", "es importante entender".
  Suenan a locutor de documental, no a una persona.
- Si la idea es de otra persona, el crédito va en un kicker pequeño en pantalla; jamás como frase hablada.
- Primera frase = la apuesta o la herida. Cada línea carga una prueba propia (sistema, número o error real).
- El hype vive en la afirmación y en la certeza, no en adjetivos de gurú ("revolucionario", "cambia todo" siguen fuera).
- Primera persona, ES, code-switch solo para nombres y términos sin
  traducción, cero guiones largos o medios, cero "¿Sabías que...?".
- Antes de generar voz: releer el guion y tachar toda palabra que no cargue peso.
- Texto en pantalla = la frase clave de lo que se dice, no la transcripción completa. El SRT lleva la transcripción.
- Nombres en inglés: `say` con la pronunciación ("Indi Dev Dan") y `text` con la ortografía real.

## 4. Sonido

- Capas: tono de cuarto (nunca silencio digital), música por secciones, foley ligado a cada acción visible, voz.
- La música baja ~9 dB bajo la voz (ducking automático en mix.py).
- Al menos dos silencios o casi silencios: antes del giro y antes del eco. La voz puede hablar dentro del silencio
  del giro: es el momento más fuerte.
- Cada aparición tiene sonido: tecla, tick, pop (más agudo por nivel), whoosh en movimientos, corte grave en el giro,
  subida + campana en la reconexión.
- Master a -14 LUFS, pico ≤ -1.2 dB (mix.py deja ~-15 y el mux ajusta).

## 5. Rúbrica de revisión (calificar 1 a 10 cada ronda; entregar con ≥ 8)

| Criterio | Pregunta |
|---|---|
| Se entiende | ¿Alguien sin contexto sabe qué se explica en cada momento? |
| Ritmo | ¿Hay pausa después de cada movimiento? ¿Algún tramo satura o se queda quieto sin voz > 3 s? |
| Sincronía | ¿Cada aparición cae en su palabra? |
| Composición | ¿El sujeto ocupa ≥ 1/3 de la altura? ¿Nada choca con el HUD o el texto? ¿Nada gigante en los zooms? |
| Marca | ¿Paleta, tipografía y lenguaje Flujo Geométrico? ¿Un acento por pantalla? |
| Voz | ¿Suena al autor? ¿Sin guiones largos, sin hype? |
| Cierre | ¿El final hace eco del inicio? |

Fallas que ya pasaron y su arreglo: `references/technique.md`, sección "Problemas ya resueltos".

## 6. Antes de entregar

- `review.sh --final`: 0 frames negros, -14 LUFS, espectro con la voz arriba de la música.
- Decir siempre qué no se verificó: el modelo no escucha el audio; tampoco se probó en celular salvo que se haga.
- Entregables: `<slug>.mp4`, `<slug>.srt`, `poster.jpg`, `TREATMENT.md`, `CREDITS`.
