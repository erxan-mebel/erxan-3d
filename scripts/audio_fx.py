"""Royalty-free background music and sound effects, synthesised with numpy.

music(seconds, path)          calm lo-fi groove (C - G - Am - F, 96 bpm) with fade in/out
sfx(events, seconds, path)    events = [(time, "whoosh" | "pop")] mixed into one track
"""
import wave

import numpy as np

SR = 48000


def _save(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def _note(freq, dur, amp=1.0, decay=3.0, harm=(1, 0.5, 0.25, 0.12)):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-decay * t) * np.minimum(1, t / 0.01)
    tone = sum(a * np.sin(2 * np.pi * freq * (i + 1) * t) for i, a in enumerate(harm))
    return amp * env * tone


def _mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def music(seconds, path, bpm=96, seed=7):
    rng = np.random.default_rng(seed)
    beat = 60 / bpm
    bar = 4 * beat
    n = int((seconds + 1) * SR)
    out = np.zeros(n)

    def add(sig, t):
        i = int(t * SR)
        j = min(n, i + len(sig))
        if i < n:
            out[i:j] += sig[: j - i]

    chords = [(60, 64, 67, 71), (55, 59, 62, 67), (57, 60, 64, 67), (53, 57, 60, 64)]  # Cmaj7 G Am7 Fmaj7
    roots = [36, 43, 45, 41]
    t, k = 0.0, 0
    while t < seconds:
        ch = chords[k % 4]
        for b in range(4):  # soft e-piano stabs
            for m in ch:
                add(_note(_mtof(m), beat * 1.6, 0.045, decay=2.2), t + b * beat + (0.0 if b % 2 == 0 else beat * 0.5))
        add(_note(_mtof(roots[k % 4]), bar, 0.22, decay=0.9, harm=(1, 0.3)), t)          # bass
        add(_note(_mtof(roots[k % 4] + 12), bar * 0.5, 0.08, decay=1.2, harm=(1,)), t + 2 * beat)
        for b in range(4):  # kick on 1 and 3, snare-ish on 2 and 4, hats on 8ths
            tb = t + b * beat
            if b % 2 == 0:
                kt = np.arange(int(0.25 * SR)) / SR
                add(0.5 * np.sin(2 * np.pi * (50 + 80 * np.exp(-30 * kt)) * kt) * np.exp(-12 * kt), tb)
            else:
                st = np.arange(int(0.18 * SR)) / SR
                add(0.12 * rng.standard_normal(len(st)) * np.exp(-25 * st), tb)
            for h in (0, 0.5):
                ht = np.arange(int(0.05 * SR)) / SR
                hat = rng.standard_normal(len(ht))
                hat = np.diff(hat, prepend=0)  # crude high-pass
                add(0.035 * hat * np.exp(-80 * ht), tb + h * beat)
        t += bar
        k += 1
    out = out[: int(seconds * SR)]
    fade = np.ones_like(out)
    fi, fo = int(1.0 * SR), int(2.0 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    out *= fade / (np.abs(out).max() + 1e-9) * 0.8
    _save(path, out)


def _whoosh(rng):
    d = 0.45
    t = np.arange(int(d * SR)) / SR
    noise = rng.standard_normal(len(t))
    # moving band-pass via two one-pole filters with swept coefficient
    out = np.zeros_like(noise)
    lp = hp = 0.0
    for i, x in enumerate(noise):
        a = 0.02 + 0.25 * (i / len(noise))
        lp += a * (x - lp)
        hp = lp - hp * 0.0
        out[i] = hp
    env = np.sin(np.pi * t / d) ** 2
    return 0.9 * out * env / (np.abs(out).max() + 1e-9)


def _pop():
    t = np.arange(int(0.12 * SR)) / SR
    f = 900 * np.exp(-18 * t) + 300
    return 0.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-30 * t)


def sfx(events, seconds, path, seed=3):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    out = np.zeros(n)
    for t, kind in events:
        sig = _whoosh(rng) if kind == "whoosh" else _pop()
        start = int(max(0, t - (0.3 if kind == "whoosh" else 0)) * SR)
        j = min(n, start + len(sig))
        out[start:j] += sig[: j - start]
    _save(path, out * 0.7)
