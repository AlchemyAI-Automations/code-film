#!/usr/bin/env python3
"""Voz de un code-film con ElevenLabs: TTS por línea + forced alignment (tiempos por palabra).

Uso:
  python3 voice.py <film_dir> [--profile NOMBRE] [--voice ENV_O_ID] [--model eleven_v3] [--speed 1.0] [--force] [--check] [--only v1,v3]

Lee   <film_dir>/script.json   {"lines": [{"id": "v1", "text": "...", "say": "opcional, lo que se pronuncia"}]}
Escribe <film_dir>/voices/<id>.mp3, <id>.wav (48 kHz mono) y voices/timing.json
Caché en voices/.cache/: misma línea + misma voz + mismos ajustes = no se vuelve a cobrar.

La key se toma de ELEVENLABS_API_KEY o del envFile de config.json. Nunca se imprime ni se escribe a disco.
--check transcribe cada audio con el STT de ElevenLabs y compara contra el texto (detecta palabras mal dichas).
"perform": "perf/v6.m4a" en una línea = usar tu propia actuación grabada (celular sirve) y convertirla a la voz del clon.
"""
import argparse, difflib, hashlib, json, os, re, subprocess, sys, unicodedata, urllib.error, urllib.request, uuid

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(SKILL, 'config.json' if os.path.exists(os.path.join(SKILL, 'config.json')) else 'config.example.json')))
API = 'https://api.elevenlabs.io/v1'


def env_file():
    p = os.path.expanduser(CFG.get('envFile', ''))
    out = {}
    if p and os.path.exists(p):
        for line in open(p):
            m = re.match(r'^([A-Z0-9_]+)=(.*)$', line.strip())
            if m: out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


def secret(name):
    v = os.environ.get(name) or env_file().get(name)
    if not v: sys.exit(f'✗ falta {name} (variable de entorno o envFile de config.json)')
    return v


def resolve_voice(v):
    return secret(v) if re.fullmatch(r'[A-Z0-9_]+', v) else v


def http(method, path, key, body=None, headers=None, raw=False):
    h = {'xi-api-key': key, **(headers or {})}
    req = urllib.request.Request(API + path, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read()
            return data if raw else json.loads(data)
    except urllib.error.HTTPError as e:
        sys.exit(f'✗ ElevenLabs {path.split("?")[0]} respondió {e.code}: {e.read().decode(errors="replace")[:400]}')


def multipart(fields, files):
    b = uuid.uuid4().hex; out = b''
    for k, v in fields.items():
        out += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, (name, data, ctype) in files.items():
        out += f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\nContent-Type: {ctype}\r\n\r\n'.encode() + data + b'\r\n'
    return out + f'--{b}--\r\n'.encode(), f'multipart/form-data; boundary={b}'


def strip_tags(s):   # los audio tags de v3 ([serio], [pausa]) no se alinean ni se transcriben
    return re.sub(r'\s{2,}', ' ', re.sub(r'\[[^\]\n]{1,40}\]', '', s)).strip()


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return re.sub(r'[^a-z0-9ñ ]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn')).split()


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).decode().strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('film'); ap.add_argument('--profile'); ap.add_argument('--voice'); ap.add_argument('--model'); ap.add_argument('--speed', type=float)
    ap.add_argument('--force', action='store_true'); ap.add_argument('--check', action='store_true'); ap.add_argument('--only')
    a = ap.parse_args()
    film_profile = json.load(open(os.path.join(os.path.abspath(a.film), 'script.json'))).get('profile')
    prof = a.profile or film_profile or CFG.get('defaultProfile', 'narrador')
    if prof not in CFG['profiles']: sys.exit(f'✗ perfil de voz desconocido: {prof} (hay: {", ".join(CFG["profiles"])})')
    vc = {k: v for k, v in CFG['profiles'][prof].items() if k != 'note'}
    print(f'voz: perfil {prof} · modelo {vc["model"]}')
    if a.voice: vc['voice'] = a.voice
    if a.model: vc['model'] = a.model
    if a.speed: vc['speed'] = a.speed
    key = secret('ELEVENLABS_API_KEY'); voice_id = resolve_voice(vc['voice'])
    film = os.path.abspath(a.film); vdir = os.path.join(film, 'voices'); cdir = os.path.join(vdir, '.cache')
    os.makedirs(cdir, exist_ok=True)
    script = json.load(open(os.path.join(film, 'script.json')))
    tpath = os.path.join(vdir, 'timing.json')
    timing = json.load(open(tpath)) if os.path.exists(tpath) else {'lines': {}}
    only = set(a.only.split(',')) if a.only else None
    settings = {'stability': vc['stability'], 'similarity_boost': vc['similarity_boost'], 'style': vc['style'], 'use_speaker_boost': True}
    if vc.get('speed', 1.0) != 1.0: settings['speed'] = vc['speed']   # turbo no acepta speed; 1.0 es el default de todos
    chars = 0
    for line in script['lines']:
        lid = line['id']
        if only and lid not in only: continue
        say = line.get('say') or line['text']
        if vc['model'] != 'eleven_v3': say = strip_tags(say)   # las etiquetas de emoción solo existen en v3; en otros modelos se leerían en voz alta
        ls = dict(settings)
        for k2, v2 in (line.get('direction') or {}).items():   # dirección por línea: stability, style, similarity_boost, speed
            if k2 == 'speed' and v2 == 1.0: ls.pop('speed', None)
            else: ls[k2] = v2
        if vc['model'] == 'eleven_v3': ls['stability'] = min((0.0, 0.5, 1.0), key=lambda x: abs(x - ls['stability']))   # v3 solo acepta 0, 0.5, 1
        h = hashlib.sha1(json.dumps([voice_id, vc['model'], ls, say, line.get('prime') or vc.get('prime')], sort_keys=True).encode()).hexdigest()[:16]
        mp3c, alc = os.path.join(cdir, h + '.mp3'), os.path.join(cdir, h + '.align.json')
        perf = os.path.join(film, line['perform']) if line.get('perform') else None
        if perf and os.path.exists(perf):   # actuación propia → voz limpia del clon (speech-to-speech), conserva la intención
            h = hashlib.sha1(open(perf, 'rb').read() + json.dumps([voice_id, ls], sort_keys=True).encode()).hexdigest()[:16]
            mp3c, alc = os.path.join(cdir, h + '.mp3'), os.path.join(cdir, h + '.align.json')
        if perf and os.path.exists(perf) and (a.force or not os.path.exists(mp3c)):
            wav_in = os.path.join(cdir, h + '.in.wav')
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', perf, '-ar', '44100', '-ac', '1', wav_in], check=True)
            body, ctype = multipart({'model_id': 'eleven_multilingual_sts_v2', 'remove_background_noise': 'true',
                                     'voice_settings': json.dumps({'stability': ls['stability'], 'similarity_boost': ls['similarity_boost'], 'style': ls.get('style', 0)})},
                                    {'audio': ('in.wav', open(wav_in, 'rb').read(), 'audio/wav')})
            open(mp3c, 'wb').write(http('POST', f'/speech-to-speech/{voice_id}?output_format=mp3_44100_128', key, body, {'Content-Type': ctype}, raw=True))
            if os.path.exists(alc): os.remove(alc)
            print(f'  {lid}: actuación convertida con speech-to-speech ({os.path.basename(perf)})')
        elif a.force or not os.path.exists(mp3c):
            req = {'text': say, 'model_id': vc['model'], 'voice_settings': ls}
            prime = line.get('prime') or vc.get('prime')   # contexto emocional previo: el modelo lo "oye", no lo pronuncia
            if prime and vc['model'] != 'eleven_v3': req['previous_text'] = prime
            if vc['model'] in ('eleven_turbo_v2_5', 'eleven_flash_v2_5'): req['language_code'] = 'es'   # fija el idioma en los modelos rápidos
            body = json.dumps(req).encode()
            audio = http('POST', f'/text-to-speech/{voice_id}?output_format=mp3_44100_128', key, body, {'Content-Type': 'application/json', 'Accept': 'audio/mpeg'}, raw=True)
            open(mp3c, 'wb').write(audio); chars += len(say)
            if os.path.exists(alc): os.remove(alc)
        if not os.path.exists(alc):
            body, ctype = multipart({'text': strip_tags(say)}, {'file': ('audio.mp3', open(mp3c, 'rb').read(), 'audio/mpeg')})
            json.dump(http('POST', '/forced-alignment', key, body, {'Content-Type': ctype}), open(alc, 'w'))
        al = json.load(open(alc))
        mp3, wav = os.path.join(vdir, lid + '.mp3'), os.path.join(vdir, lid + '.wav')
        subprocess.run(['cp', mp3c, mp3], check=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3, '-ar', '48000', '-ac', '1', wav], check=True)
        words = [{'text': w['text'], 'start': round(w['start'], 3), 'end': round(w['end'], 3)} for w in al.get('words', []) if w['text'].strip()]
        dur = duration(wav)
        timing['lines'][lid] = {'dur': round(dur, 3), 'words': words, 'hash': h}
        wps = len(words) / max(dur, .1)
        print(f'✓ {lid}  {dur:5.2f}s  {wps:.2f} palabras/s  "{say[:60]}"')
        if a.check:
            body, ctype = multipart({'model_id': CFG.get('sttModel', 'scribe_v1'), 'language_code': 'spa'}, {'file': ('audio.mp3', open(mp3, 'rb').read(), 'audio/mpeg')})
            heard = http('POST', '/speech-to-text', key, body, {'Content-Type': ctype}).get('text', '')
            exp, got = norm(strip_tags(line.get('asr') or say)), norm(heard)   # 'asr': cómo lo escribe el STT cuando es correcto
            ratio = difflib.SequenceMatcher(None, ''.join(exp), ''.join(got)).ratio()   # tolera "Indie Dev Dan" vs "Indy Devdan"
            miss = [w for w in exp if w not in got and len(w) > 3]
            print(f'   check: {"OK" if ratio >= .9 else "REVISAR"} ({ratio:.2f})  oído: "{heard[:90]}"' + (f'  dudosas: {miss}' if ratio < .9 else ''))
    ids = {l['id'] for l in script['lines']}
    timing['lines'] = {k: v for k, v in timing['lines'].items() if k in ids}   # quita líneas borradas del guion
    timing.update({'voice': vc['voice'], 'model': vc['model'], 'settings': settings})
    json.dump(timing, open(tpath, 'w'), ensure_ascii=False, indent=1)
    print(f'timing.json listo · caracteres cobrados en esta corrida: {chars}')


if __name__ == '__main__':
    main()
