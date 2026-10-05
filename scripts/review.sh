#!/bin/sh
# Revisión visual. Uso:
#   review.sh <film_dir> 2.5 8 14.2 ...   → fotogramas exactos + hoja de contacto en review/sheet-<n>.jpg
#   review.sh <film_dir> --final          → sobre el MP4: frames negros, sonoridad, espectro y hoja cada 2 s
set -e
F=$(cd "$1" && pwd); shift; LIB=${LIB:-$HOME/lemo-opuscar}; NAME=$(basename "$F"); mkdir -p "$F/review"
if [ "$1" = "--final" ]; then
  V="$F/$NAME.mp4"
  echo "frames negros: $(ffmpeg -hide_banner -i "$V" -vf blackdetect=d=0.1:pix_th=0.1 -an -f null - 2>&1 | grep -c black_start)"
  ffmpeg -hide_banner -nostats -i "$V" -af ebur128=peak=true -f null - 2>&1 | grep -A14 Summary | grep -E " I:|Peak:"
  ffmpeg -hide_banner -y -loglevel error -i "$V" -lavfi "showspectrumpic=s=1600x240:legend=0:scale=log" "$F/review/spectrum.png"
  ffmpeg -hide_banner -y -loglevel error -i "$V" -vf "fps=0.5,scale=320:-1,tile=6x6:padding=4:color=0x222222" -frames:v 1 "$F/review/final-sheet.jpg"
  echo "$F/review/final-sheet.jpg · $F/review/spectrum.png"; exit 0
fi
rm -rf "$F/stills"; (cd "$LIB" && node core/render/still.mjs "$F" "$@" > /dev/null)
N=$(ls "$F/review" | grep -c '^sheet-' || true); OUT="$F/review/sheet-$((N + 1)).jpg"
"$LIB/.venv/bin/python" "$LIB/core/render/sheet.py" "$OUT" $(ls "$F"/stills/*.jpg | sort -t_ -k2 -n) --cols 3 --w 640 > /dev/null
rm -rf "$F/stills"; echo "$OUT"
