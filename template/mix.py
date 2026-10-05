"""Mezcla de un code-film: voz + música por secciones + foley, todo desde events.json (el mismo timeline del dibujo).
Uso: LIB=~/lemo-opuscar $LIB/.venv/bin/python mix.py   → out/mix.wav (~ -15 LUFS, el mux lo deja en -14)

Secciones que entiende (events.json → meta.sections): hook, setup, climb, broken, resolve, outro.
Eventos de foley: key (agent=True más agudo), snap, tick, pop (level), whoosh (d), knife, cut, rise (d), ding.
Una película nueva normalmente solo ajusta NOTES, BPM y las ganancias de la tabla GAIN.
"""
import json, os, sys
import numpy as np, soundfile as sf
from scipy.ndimage import maximum_filter1d, uniform_filter1d

LIB = os.environ.get('LIB') or os.path.expanduser('~/lemo-opuscar')
sys.path.insert(0, os.path.join(LIB, 'core', 'audio'))
import sfx  # noqa: E402
from sfx import SR, t_, lp, hp, bp, noise, norm, add, brown, limit  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ev = json.load(open(os.path.join(HERE, 'events.json')))
DUR = ev['dur']; EV = ev['ev']; META = EV[0]; SEC = META.get('sections', {}); ARR = META.get('arrivals', [])
BPM = 100; BEAT = 60 / BPM
NOTES = [110.0, 130.81, 146.83, 164.81, 196.0, 220.0]          # bajo que sube un grado por nivel (La menor)
MINOR = [220.0, 261.63, 329.63, 493.88]; MAJOR = [220.0, 277.18, 329.63, 493.88]
GAIN = {'voice': 1.0, 'music': .9, 'foley': 1.0, 'duck_db': -9}
N = int(DUR * SR) + SR
voice, music, fol = (np.zeros((N, 2)) for _ in range(3))
sec = lambda name: SEC.get(name)


def env(d, a=.005, r=.08):
    tt = t_(d); return np.minimum(1, tt / max(a, 1e-4)) * np.clip((d - tt) / max(r, 1e-4), 0, 1)


def tone(f, d, harm=(1, .35, .15), a=.004, r=.12, decay=None):
    tt = t_(d); x = sum(h * np.sin(2 * np.pi * f * (k + 1) * tt) for k, h in enumerate(harm)); e = env(d, a, r)
    return x * (e * np.exp(-tt / decay) if decay else e)


def pad(freqs, d, lpf=1000, a=.8, r=.6):
    tt = t_(d); x = np.zeros(len(tt))
    for f in freqs:
        for det in (-.0035, 0, .0035): x += 2 * ((tt * f * (1 + det)) % 1) - 1
    return norm(lp(x, lpf, 2)) * env(d, a, r)


def glide(f0, f1, d):
    tt = t_(d); f = f0 * (f1 / f0) ** (tt / d); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / d) ** 1.5


def kpop(level):
    d = .16; tt = t_(d); f0 = 420 * 1.122 ** level; f = f0 * (1 + 1.1 * tt / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / .045)


def hat(): d = .035; return hp(noise(d), 7000) * np.exp(-t_(d) / .008)


def pulses(a, b, every, fn):
    t = a
    while t < b - 1e-6: fn(t); t += every


# ==================== voz ====================
for e in EV:
    if e['type'] != 'voice' or e.get('estimated'): continue
    p = os.path.join(HERE, 'voices', e['id'] + '.wav')
    if not os.path.exists(p): print('! falta', p); continue
    x, sr = sf.read(p, dtype='float64'); x = x if x.ndim == 1 else x.mean(1)
    if sr != SR: sys.exit(f'{p} debe estar a {SR} Hz (voice.py ya lo convierte)')
    add(voice, norm(x, .7), e['t'], 1.0)
for c in range(2): voice[:, c] = sfx.compress(voice[:, c], thr=.22, ratio=3.0, att=.003, rel=.15)

# ==================== música por secciones ====================
add(music, lp(brown(DUR), 280) * .012, 0, 1.0)                       # tono de cuarto: nunca silencio digital
if sec('hook'):
    a, b = sec('hook'); pulses(1.5, b, BEAT, lambda t: add(music, sfx.click(.55, 1.0), t, .06, .3))
    d = b - 1.0; tt = t_(d); add(music, (np.sin(2 * np.pi * 55 * tt) + .25 * np.sin(2 * np.pi * 110 * tt)) * env(d, 1.5, .4), 1.0, .06)
if sec('setup'):
    a, b = sec('setup'); add(music, pad(MINOR, b - a + .5, lpf=700, a=1.5, r=.4), a, .05, -.2)
if sec('climb'):
    a, b = sec('climb')
    add(music, pad(MINOR, b - a, lpf=950, a=1.0, r=.05) * np.linspace(.6, 1, len(t_(b - a))), a, .07, -.25)
    add(music, pad([220.0 * 1.003, 329.63, 392.0], b - a, lpf=800, a=1.0, r=.05), a, .045, .25)
    pulses(a, b - 2.0, BEAT, lambda t: (add(music, sfx.thump(.9, 52), t, .26), add(music, hat(), t + BEAT / 2, .05, .25)))
    marks = (ARR or [a]) + [b - 1.8]
    for i in range(len(marks) - 1):
        pulses(max(a, marks[i]), marks[i + 1], BEAT / 2, lambda t, i=i: add(music, tone(NOTES[min(i, 5)], .26, (1, .5, .25), r=.06, decay=.13), t, .13, -.1))
    d = 1.8; tt = t_(d); add(music, np.sin(2 * np.pi * 880 * tt) * (.6 + .4 * np.sin(2 * np.pi * 5 * tt)) * env(d, .5, .05), b - d, .018)
if sec('broken'):
    a, b = sec('broken'); d = b - (a + 1.2); tt = t_(d)
    add(music, (np.sin(2 * np.pi * 55 * tt) + np.sin(2 * np.pi * 55.7 * tt) + .3 * np.sin(2 * np.pi * 110.4 * tt)) * env(d, 1.2, .3), a + 1.2, .09)
if sec('resolve'):
    a, b = sec('resolve'); d = b - a
    add(music, pad(MAJOR, d, lpf=1300, a=1.0, r=.6), a, .07, -.25); add(music, pad([220.0 * 1.003, 329.63, 440.0], d, lpf=1100, a=1.0, r=.6), a, .045, .25)
    pulses(a + .8, b - .6, 2 * BEAT, lambda t: (add(music, sfx.thump(.7, 55), t, .18), add(music, tone(110, .45, (1, .45, .2), r=.15, decay=.25), t, .1)))
if sec('outro'):
    a, b = sec('outro'); d = b - a; add(music, pad(MAJOR + [659.25], d, lpf=1500, a=1.4, r=2.5) * np.exp(-t_(d) / 6), a, .075)

# ==================== foley ====================
for e in EV:
    ty, at, v = e['type'], e['t'], e.get('v', 1.0)
    if ty == 'key':
        ag = e.get('agent'); add(fol, sfx.click(1.75 if ag else 1.2, 1.0), at, (.15 if ag else .2) * (.85 + .3 * ((int(at * 1000) % 7) / 7)), .1)
    elif ty == 'snap': add(fol, sfx.clack(.85, 1.0), at, .3 * v); add(fol, sfx.thump(1.0, 85), at, .2 * v)
    elif ty == 'tick': add(fol, sfx.click(.75, 1.0), at, .12 * v)
    elif ty == 'pop': add(fol, kpop(e.get('level', 0)), at, .18)
    elif ty == 'whoosh': add(fol, sfx.whoosh(max(.3, e.get('d', .6)), 1.0), at, .1 * v)
    elif ty == 'knife':
        d = .2; tt = t_(d); x = bp(noise(d), 3000, 9000) * np.exp(-tt / .05) + np.sin(2 * np.pi * np.cumsum(2600 * (1 - .7 * tt / d)) / SR) * np.exp(-tt / .06) * .5
        add(fol, norm(x), at, .24, -.4)
    elif ty == 'cut': add(fol, sfx.thump(1.0, 44), at, .7); add(fol, lp(noise(.5), 500) * np.exp(-t_(.5) / .09), at, .22)
    elif ty == 'rise': add(fol, glide(220, 880, e['d']), at, .13); add(fol, bp(noise(e['d']), 2000, 6000) * np.linspace(0, 1, len(t_(e['d']))) ** 2, at, .04)
    elif ty == 'ding': add(fol, sfx.ding(1.0), at, .18 * v)

# ==================== ducking: la música baja cuando hay voz ====================
venv = np.abs(voice).max(1)
venv = uniform_filter1d(maximum_filter1d(venv, size=int(.25 * SR)), size=int(.12 * SR))
duck = 1 - (1 - 10 ** (GAIN['duck_db'] / 20)) * np.clip(venv / .08, 0, 1)
music *= duck[:, None]

mix = (voice * GAIN['voice'] + music * GAIN['music'] + fol * GAIN['foley'])[:int(DUR * SR)]
rms = np.sqrt(np.mean(mix ** 2)) + 1e-9
mix *= 10 ** (-17 / 20) / rms                                           # nivel cercano a -15 LUFS antes del mux
for c in range(2): mix[:, c] = limit(sfx.compress(mix[:, c], thr=.3, ratio=2.5, att=.002, rel=.12), .72)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
sf.write(os.path.join(HERE, 'out', 'mix.wav'), mix.astype(np.float32), SR, subtype='PCM_24')
print('mix.wav', f'{DUR:.2f}s', 'pico', round(float(np.abs(mix).max()), 3), '| voz:', sum(1 for e in EV if e['type'] == 'voice' and not e.get('estimated')), 'líneas')
