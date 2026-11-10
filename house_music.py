"""Upbeat feel-good house loop (no samples, fully synthesized). Usage: python3 house_music.py OUT.wav DUR [seed]"""
import sys, wave
import numpy as np

SR = 44100


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, a):  # one-pole lowpass, a in (0,1)
    y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s += a * (x[i] - s); y[i] = s
    return y


def make(path, dur, seed=5, bpm=122):
    rng = np.random.default_rng(seed)
    n = int(dur * SR); out = np.zeros(n); beat = 60 / bpm; step = beat / 4
    key = 57  # A minor-ish
    prog = [[0, 3, 7, 10], [-4, 0, 3, 7], [-2, 2, 5, 9], [-7, -3, 0, 3]]  # Am7 Fmaj7 G(add) Em7-ish
    nsteps = int(dur / step) + 1
    # kick four on the floor
    kl = int(0.28 * SR); kt = np.arange(kl) / SR
    kick = np.sin(2 * np.pi * (45 + 120 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9)
    # clap
    cl = int(0.18 * SR); ct = np.arange(cl) / SR
    clap = rng.standard_normal(cl) * np.exp(-ct * 22) * 0.35
    hat_l = int(0.05 * SR); ht = np.arange(hat_l) / SR
    for s in range(nsteps):
        st = int(s * step * SR); bar = s // 16; pos = s % 16
        if st >= n: break
        if pos % 4 == 0 and bar >= 1 or (bar == 0 and pos % 4 == 0 and s >= 8):
            e = min(kl, n - st); out[st:st + e] += kick[:e] * 0.9
        if pos in (4, 12):
            e = min(cl, n - st); out[st:st + e] += clap[:e]
        if pos % 4 == 2:
            e = min(hat_l, n - st)
            h = rng.standard_normal(hat_l) * np.exp(-ht * 70); h = h - lp(h, 0.5)
            out[st:st + e] += h[:e] * 0.22
        chord = prog[bar % 4]
        # plucky arp on 16ths
        note = key + 12 + chord[[0, 1, 2, 3, 2, 1, 3, 2][pos % 8]]
        pl = int(step * 1.6 * SR); e = min(pl, n - st); t = np.arange(e) / SR
        f = mtof(note)
        saw = 2 * ((t * f) % 1) - 1
        pluck = (0.6 * saw + 0.4 * np.sin(2 * np.pi * f * t)) * np.exp(-t * 14)
        out[st:st + e] += pluck * 0.12
        # offbeat bass
        if pos % 4 == 2:
            bl = int(step * 1.8 * SR); e = min(bl, n - st); t = np.arange(e) / SR
            fb = mtof(key - 24 + chord[0])
            out[st:st + e] += np.sin(2 * np.pi * fb * t) * np.minimum(1, t * 200) * np.exp(-t * 6) * 0.45
        # pad on bar start
        if pos == 0:
            pdl = int(16 * step * SR); e = min(pdl, n - st); t = np.arange(e) / SR
            pad = sum(np.sin(2 * np.pi * mtof(key + c) * t * (1 + 0.002 * k)) for k, c in enumerate(chord))
            out[st:st + e] += pad * np.minimum(1, t * 3) * np.exp(-t * 0.6) * 0.05
    # gentle sidechain pump
    tt = np.arange(n) / SR; ph = (tt % beat) / beat
    out *= 0.55 + 0.45 * np.minimum(1, ph * 4)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.85
    fade = int(0.02 * SR); out[:fade] *= np.linspace(0, 1, fade)
    data = (out * 32767).astype(np.int16)
    st = np.stack([data, data], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())


if __name__ == "__main__":
    make(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 5)
