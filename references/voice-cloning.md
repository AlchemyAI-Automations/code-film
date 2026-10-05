# Clonar tu voz en ElevenLabs

| | Instantánea (IVC) | Profesional (PVC) |
|---|---|---|
| Audio necesario | 1 a 2 min | mínimo 30 min; ideal 2 a 3 h |
| Listo en | inmediato | 3 a 6 h (hasta 24 h) |
| Calidad | buena | más realista, mejor con acentos y voces particulares |

Recomendación: IVC para validar cómo suena en los videos y PVC cuando tengas 30 a 60 min limpios.

## Cómo grabar

- Mismo micrófono y mismo cuarto en todas las tomas, a 15 a 20 cm, con filtro antipop. Cuarto callado y sin eco.
- **El tono de la grabación es el tono del clon.** Una lectura plana da un clon plano. Graba con la energía con la que
  vas a querer sonar en los videos.
- Volumen parejo, sin música ni otra voz. Formato WAV, o MP3 de 192 kbps o más.

## Cómo conectarla

1. ElevenLabs, Voices, Add a new voice. Copia el Voice ID.
2. En `config.json` (copia de `config.example.json`) reemplaza `TU_VOICE_ID` en el perfil que uses.
3. Prueba: `python3 scripts/voice.py <película> --check` y escucha. Si el acento cambia a media frase, sube `stability`.

El perfil `narrador_energico` sube la variación de tono con poca estabilidad, mucho estilo, velocidad 1.10 y un texto
previo (`prime`) que da la intención. Un clon profesional no se entrena para `eleven_v3`; usa `eleven_multilingual_v2`.
Para más emoción de verdad, graba tú las frases clave y conviértelas con `"perform": "perf/vN.m4a"` en esa línea
(speech-to-speech): conserva tu énfasis y su voz limpia.

Fuentes: [Instant Voice Cloning](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/instant-voice-cloning),
[Professional Voice Cloning](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/professional-voice-cloning).
