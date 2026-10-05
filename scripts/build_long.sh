#!/bin/sh
# Arma un video largo: renderiza los capítulos en paralelo (solo los que cambiaron), los une sin recodificar,
# masteriza el audio completo una sola vez y une los subtítulos con su desfase.
# Uso: build_long.sh <carpeta_del_largo> [-j 2]
set -e
L=$(cd "$1" && pwd); J=2; [ "$2" = "-j" ] && J=${3:-2}
SKILL=$(cd "$(dirname "$0")/.." && pwd); NAME=$(basename "$L"); T0=$(date +%s)
CH=$(python3 -c "import json;print(' '.join(json.load(open('$L/chapters.json'))['chapters']))")
mkdir -p "$L/out"
# 1) capítulos en paralelo (cada uno con 3 workers para no saturar la máquina)
echo "$CH" | tr ' ' '\n' | xargs -P "$J" -I{} sh -c "MASTER=0 WORKERS=3 '$L/chapters/{}/build.sh' 2>&1 | grep -E '⏱|al día|✗' | sed 's/^/  [{}] /'" || { echo "✗ falló algún capítulo"; exit 1; }
T1=$(date +%s)
# 2) audio de cada capítulo alineado a la duración exacta de su video, y listas para unir
: > "$L/out/v.txt"; : > "$L/out/a.txt"; OFFS=""
for c in $CH; do
  V="$L/chapters/$c/out/video.mp4"
  D=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate -of csv=p=0 "$V" | awk -F, '{split($1,f,"/"); printf "%.6f", $2/(f[1]/f[2])}')
  ffmpeg -hide_banner -loglevel error -y -i "$L/chapters/$c/out/mix.wav" -af apad -t "$D" -ar 48000 -ac 2 -c:a pcm_s24le "$L/out/a_$c.wav"
  echo "file '$V'" >> "$L/out/v.txt"; echo "file 'a_$c.wav'" >> "$L/out/a.txt"; OFFS="$OFFS$c:$D "
done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$L/out/v.txt" -c copy "$L/out/video.mp4"
(cd "$L/out" && ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i a.txt -c copy mix.wav)
# 3) master único (misma sonoridad en todo el video) + subtítulos con desfase
sh "$SKILL/scripts/master.sh" "$L/out/video.mp4" "$L/out/mix.wav" "$L/$NAME.mp4"
python3 - "$L" "$NAME" $OFFS <<'PY'
import os, re, subprocess, sys
L, name, parts = sys.argv[1], sys.argv[2], sys.argv[3:]
skill = os.path.expanduser('~/.claude/skills/code-film/scripts/srt.py')
ts = lambda s: sum(float(x) * m for x, m in zip(s.replace(',', '.').split(':'), (3600, 60, 1)))
fmt = lambda s: f'{int(s // 3600):02}:{int(s % 3600 // 60):02}:{int(s % 60):02},{int(round(s % 1 * 1000)) % 1000:03}'
out, n, off = [], 0, 0.0
for p in parts:
    c, d = p.split(':'); cdir = os.path.join(L, 'chapters', c); tmp = os.path.join(cdir, 'out', 'chapter.srt')
    subprocess.run(['python3', skill, cdir, tmp], check=True, capture_output=True)
    if os.path.exists(tmp):
        for blk in open(tmp).read().strip().split('\n\n'):
            lines = blk.split('\n')
            if len(lines) < 3: continue
            a, b = lines[1].split(' --> '); n += 1
            out.append(f'{n}\n{fmt(ts(a) + off)} --> {fmt(ts(b) + off)}\n' + '\n'.join(lines[2:]))
    off += float(d)
open(os.path.join(L, f'{name}.srt'), 'w').write('\n\n'.join(out) + '\n')
print(f'  subtítulos: {n} · duración total {off:.1f} s')
PY
ffmpeg -hide_banner -loglevel error -y -ss 3 -i "$L/$NAME.mp4" -frames:v 1 -update 1 "$L/poster.jpg"
rm -f "$L"/out/a_*.wav "$L/out/v.txt" "$L/out/a.txt"
echo "⏱ capítulos $((T1 - T0)) s · unión + master $(( $(date +%s) - T1 )) s · total $(( $(date +%s) - T0 )) s"
echo "✓ $L/$NAME.mp4"
