#!/bin/sh
# Master de un code-film SIN recodificar el video: copia el H.264 tal cual (ya viene de video.mjs) y solo procesa el audio.
# Audio: loudnorm en 2 pasadas a -14 LUFS, pico real -1.5 dB, AAC 256k. Si el audio es más corto, se rellena con silencio.
# Uso: master.sh video.mp4 mix.wav salida.mp4
set -e
V=$1; A=$2; O=$3
[ -f "$V" ] && [ -f "$A" ] && [ -n "$O" ] || { echo "uso: master.sh video.mp4 mix.wav salida.mp4"; exit 2; }
M=$(ffmpeg -hide_banner -nostats -i "$A" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
g() { echo "$M" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
LN="loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true"
TMP="$O.part.mp4"; rm -f "$TMP"
# h264_metadata marca BT.709 rango limitado en el bitstream (antes lo hacía la recodificación), sin tocar un solo pixel
ffmpeg -hide_banner -loglevel error -y -i "$V" -i "$A" -map 0:v:0 -map 1:a:0 \
  -c:v copy -bsf:v h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0 \
  -af "$LN,apad" -ar 48000 -c:a aac -b:a 256k -shortest -movflags +faststart "$TMP"
mv "$TMP" "$O"
ffmpeg -hide_banner -nostats -i "$O" -af ebur128=peak=true -f null - 2>&1 | grep -A14 Summary | grep -E " I:|Peak:" | sed 's/^ */  /'
