#!/usr/bin/env python3
"""Subtítulos .srt de un code-film: events.json (inicio de cada línea de voz) + voices/timing.json (palabras).
Usa el texto visible de script.json ("text"), no la versión fonética ("say"). Piezas de 42 caracteres como máximo,
sin traslapes. Uso: srt.py <film_dir> <out.srt>"""
import json, os, sys

film, out = sys.argv[1], sys.argv[2]
ev = json.load(open(os.path.join(film, 'events.json')))['ev']
tpath = os.path.join(film, 'voices', 'timing.json')
if not os.path.exists(tpath): print('sin voz: no hay subtítulos'); sys.exit(0)
timing = json.load(open(tpath))['lines']
script = {l['id']: l for l in json.load(open(os.path.join(film, 'script.json')))['lines']}
fmt = lambda s: f'{int(s // 3600):02}:{int(s % 3600 // 60):02}:{int(s % 60):02},{int(round(s % 1 * 1000)) % 1000:03}'


def words_for(lid):
    al, line = timing[lid]['words'], script.get(lid, {})
    text = line.get('text', '')
    if not line.get('say') or not al: return al
    # "say" difiere del texto visible: reparte las palabras visibles en el tramo hablado, proporcional a su largo
    vis = text.split(); a, b = al[0]['start'], al[-1]['end']; total = sum(len(w) + 1 for w in vis); acc = a; out = []
    for w in vis:
        d = (len(w) + 1) / total * (b - a); out.append({'text': w, 'start': acc, 'end': acc + d * .92}); acc += d
    return out


cues = []
for e in ev:
    if e['type'] != 'voice' or e['id'] not in timing: continue
    cur = []
    for w in words_for(e['id']):
        if cur and len(' '.join(x['text'] for x in cur + [w])) > 42:
            cues.append([e['t'] + cur[0]['start'], e['t'] + cur[-1]['end'], ' '.join(x['text'] for x in cur)]); cur = []
        cur.append(w)
    if cur: cues.append([e['t'] + cur[0]['start'], e['t'] + cur[-1]['end'], ' '.join(x['text'] for x in cur)])
for i, c in enumerate(cues):   # mínimo 1 s en pantalla, pero nunca encima del siguiente
    nxt = cues[i + 1][0] - .04 if i + 1 < len(cues) else 1e9
    c[1] = min(max(c[1] + .25, c[0] + 1.0), nxt)
with open(out, 'w') as f:
    for i, (a, b, txt) in enumerate(cues, 1): f.write(f'{i}\n{fmt(a)} --> {fmt(b)}\n{txt}\n\n')
print(f'✓ {out} ({len(cues)} subtítulos)')
