#!/bin/sh
# Crea una película nueva. Uso: new_film.sh <slug> [--from <carpeta de una película existente>]
#   sin --from: copia la plantilla (film.js de ejemplo + kit + mezcla + build)
#   con --from: variación; copia film.js y script.json de esa película (la voz se regenera con voice.py)
set -e
SKILL=$(cd "$(dirname "$0")/.." && pwd)
SLUG=$1; [ -n "$SLUG" ] || { echo "uso: new_film.sh <slug> [--from <film_dir>]"; exit 2; }
FILMS=$(python3 -c "import json,os;print(os.path.expanduser(json.load(open('$SKILL/config.json' if __import__('os').path.exists('$SKILL/config.json') else '$SKILL/config.example.json'))['filmsDir']))")
DEST="$FILMS/$SLUG"; [ -e "$DEST" ] && { echo "✗ ya existe $DEST"; exit 1; }
mkdir -p "$DEST" && cp -R "$SKILL/template/." "$DEST/"
if [ "$2" = "--from" ] && [ -n "$3" ]; then cp "$3/film.js" "$3/script.json" "$DEST/"; [ -f "$3/TREATMENT.md" ] && cp "$3/TREATMENT.md" "$DEST/"; fi
chmod +x "$DEST/build.sh"
echo "$DEST"
