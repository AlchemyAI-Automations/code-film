#!/bin/sh
# Crea un video largo por capítulos. Uso: new_long.sh <slug> <n_capítulos>
# Cada capítulo es una película normal (su script.json, film.js y voz) en <slug>/chapters/NN/.
set -e
SKILL=$(cd "$(dirname "$0")/.." && pwd)
SLUG=$1; N=${2:-5}; [ -n "$SLUG" ] || { echo "uso: new_long.sh <slug> <n_capítulos>"; exit 2; }
FILMS=$(python3 -c "import json,os;print(os.path.expanduser(json.load(open('$SKILL/config.json' if __import__('os').path.exists('$SKILL/config.json') else '$SKILL/config.example.json'))['filmsDir']))")
DEST="$FILMS/$SLUG"; [ -e "$DEST" ] && { echo "✗ ya existe $DEST"; exit 1; }
mkdir -p "$DEST/chapters"
i=1; LIST=""
while [ "$i" -le "$N" ]; do
  C=$(printf "%02d" "$i"); mkdir -p "$DEST/chapters/$C"; cp -R "$SKILL/template/." "$DEST/chapters/$C/"; chmod +x "$DEST/chapters/$C/build.sh"
  LIST="$LIST\"$C\","; i=$((i + 1))
done
printf '{\n  "title": "%s",\n  "chapters": [%s]\n}\n' "$SLUG" "${LIST%,}" > "$DEST/chapters.json"
echo "$DEST"
