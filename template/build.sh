#!/bin/sh
# Render de un code-film: eventos, prueba de lectura, video, mezcla, master, subtítulos y póster.
#   ./build.sh                 película completa
#   MASTER=0 ./build.sh        solo video + mezcla (lo usa build_long.sh para capítulos)
#   FORCE=1 ./build.sh         vuelve a renderizar aunque el video esté al día
#   SIZE=1080x1350 ./build.sh  vertical (la escena debe maquetar para ese tamaño)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=${LIB:-$HOME/lemo-opuscar}; export LIB
SIZE=${SIZE:-1920x1080}; FPS=${FPS:-30}; NAME=$(basename "$HERE"); WORKERS=${WORKERS:-4}
SKILL=${SKILL:-$HOME/.claude/skills/code-film}
[ -f "$LIB/core/render/video.mjs" ] || { echo "✗ no encuentro el motor en $LIB (ver SKILL.md, Instalación)"; exit 1; }
mkdir -p "$HERE/out"; T0=$(date +%s)
cd "$LIB"
node core/render/events.mjs "$HERE" --size "$SIZE" > /dev/null
if ! node core/render/readcheck.mjs "$HERE" --size "$SIZE" --latin-cps 14 --pad 1.5 > "$HERE/out/readcheck.txt" 2>&1; then
  grep -v '^OK' "$HERE/out/readcheck.txt"; echo "✗ $NAME: hay textos que no dan tiempo de leerse (letras/12 + 2 s)"; exit 1
fi
# incremental: solo se vuelve a renderizar si cambió algo que afecta la imagen
STALE=1
if [ -z "$FORCE" ] && [ -f "$HERE/out/video.mp4" ]; then
  CH=$(find "$HERE" -maxdepth 2 -newer "$HERE/out/video.mp4" \( -name film.js -o -name kit.js -o -name script.json -o -name timing.json -o -name index.html \) | head -1)
  [ -z "$CH" ] && STALE=0
fi
if [ "$STALE" = 1 ]; then node core/render/video.mjs "$HERE" --fps "$FPS" --workers "$WORKERS" --size "$SIZE" --out "$HERE/out/video.mp4" | tail -1
else echo "video al día ($NAME): no se vuelve a renderizar"; fi
T1=$(date +%s)
"$LIB/.venv/bin/python" "$HERE/mix.py" > /dev/null; T2=$(date +%s)
echo "⏱ $NAME · render $((T1 - T0)) s · mezcla $((T2 - T1)) s"
[ "${MASTER:-1}" = 0 ] && exit 0
sh "$SKILL/scripts/master.sh" "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/$NAME.mp4"
python3 "$SKILL/scripts/srt.py" "$HERE" "$HERE/$NAME.srt" > /dev/null
T=$(python3 -c "import json;d=json.load(open('$HERE/events.json'));print(round(d['dur']*.45,2))")
ffmpeg -hide_banner -loglevel error -y -ss "$T" -i "$HERE/$NAME.mp4" -frames:v 1 -update 1 "$HERE/poster.jpg"
echo "✓ $HERE/$NAME.mp4 · total $(( $(date +%s) - T0 )) s"
