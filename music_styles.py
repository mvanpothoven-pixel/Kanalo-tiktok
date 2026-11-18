"""Four distinct fully-synthesized backing tracks (no samples, no copyrighted music).
Usage: python3 music_styles.py STYLE OUT.wav DUR [seed]
STYLE: lofi | synthwave | phonk | afro"""
import sys, wave
import numpy as np

SR = 44100


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, cutoff):
    """vectorised-ish one-pole lowpass via scipy-free IIR (cutoff Hz)."""
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += a * (x[i] - s); y[i] = s
    return y


def env(n, a=0.005, d=0.2, s=0.6, r=0.1, hold=None):
    t = np.arange(n) / SR
    hold = hold if hold is not None else n / SR - r
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / d))
    rel = np.clip((t - hold) / r, 0, 1)
    return e * (1 - rel)


def add(out, sig, st):
    if st >= len(out): return
    e = min(len(sig), len(out) - st); out[st:st + e] += sig[:e]


def osc(kind, f, n, detune=0.0):
    t = np.arange(n) / SR
    out = 0
    for dt in ([0] if not detune else [-detune, 0, detune]):
        ph = (f * (1 + dt) * t) % 1
        if kind == "saw": out = out + (2 * ph - 1)
        elif kind == "sq": out = out + np.sign(ph - 0.5)
        elif kind == "tri": out = out + (4 * np.abs(ph - 0.5) - 1)
        else: out = out + np.sin(2 * np.pi * ph)
    return out / (1 if not detune else 3)


def kick(n_s=0.35, f0=150, f1=45, dec=8):
    n = int(n_s * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 28)) / SR) * np.exp(-t * dec)


def noise_hit(rng, n_s, dec, hp=True):
    n = int(n_s * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n) * np.exp(-t * dec)
    if hp: x = x - lp(x, 3000)
    return x


def snare(rng, dec=18, tone=190):
    n = int(0.25 * SR); t = np.arange(n) / SR
    return noise_hit(rng, 0.25, dec, hp=False) * 0.5 + np.sin(2 * np.pi * tone * t) * np.exp(-t * 25) * 0.5


def chord_pad(notes, n, kind="saw", cutoff=1600, detune=0.004):
    x = sum(osc(kind, mtof(m), n, detune) for m in notes) / len(notes)
    return lp(x, cutoff) * env(n, 0.04, 0.6, 0.7, 0.15)


# ---------------------------------------------------------------- styles
def lofi(dur, rng):
    bpm = 82; beat = 60 / bpm; n = int(dur * SR); out = np.zeros(n)
    prog = [[50, 53, 57, 60, 64], [55, 59, 62, 65], [48, 52, 55, 59, 62], [52, 55, 59, 62, 64]]  # Dm9 G7 Cmaj9 Em7
    bar = beat * 4; swing = 0.06
    for b in range(int(dur / bar) + 1):
        st = int(b * bar * SR); ch = prog[b % 4]
        # rhodes-ish: sine + soft tri, slightly strummed
        for k, m in enumerate(ch):
            nn = int(bar * SR); t = np.arange(nn) / SR
            v = (np.sin(2 * np.pi * mtof(m) * t) + 0.3 * osc("tri", mtof(m + 12), nn)) * np.exp(-t * 0.9)
            v *= 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)  # tremolo
            add(out, v * 0.10, st + int(k * 0.018 * SR))
        # bass
        bn = int(beat * 1.6 * SR)
        add(out, np.sin(2 * np.pi * mtof(ch[0] - 12) * np.arange(bn) / SR) * env(bn, 0.01, 0.4, 0.6, 0.1) * 0.35, st)
        add(out, np.sin(2 * np.pi * mtof(ch[0] - 12) * np.arange(bn) / SR) * env(bn, 0.01, 0.4, 0.6, 0.1) * 0.25, st + int(beat * 2.5 * SR))
        # drums (lazy boom bap)
        for p in range(8):
            ts = st + int((p * beat / 2 + (swing if p % 2 else 0)) * SR)
            if p in (0, 5): add(out, kick(0.3, 110, 48, 10) * 0.7, ts)
            if p in (2, 6): add(out, snare(rng, 14, 180) * 0.32, ts)
            add(out, noise_hit(rng, 0.04, 90) * (0.10 if p % 2 == 0 else 0.06), ts)
    # vinyl crackle + hiss, dusty lowpass
    crack = np.zeros(n); idx = rng.integers(0, n, int(dur * 25)); crack[idx] = rng.uniform(-0.4, 0.4, len(idx))
    out = lp(out, 5200); pk = np.max(np.abs(out)); out = out + lp(crack, 2500) * 0.08 * pk + rng.standard_normal(n) * 0.0012 * pk
    return out


def synthwave(dur, rng):
    bpm = 100; beat = 60 / bpm; n = int(dur * SR); out = np.zeros(n)
    prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    bar = beat * 4
    for b in range(int(dur / bar) + 1):
        st = int(b * bar * SR); ch = prog[b % 4]
        add(out, chord_pad(ch, int(bar * SR), "saw", 1400, 0.006) * 0.16, st)
        # 16th arp
        for s in range(16):
            m = ch[s % 3] + 12 * (1 + (s // 3) % 2)
            an = int(beat / 4 * SR)
            v = lp(osc("sq", mtof(m), an), 2600) * env(an, 0.002, 0.05, 0.2, 0.02)
            add(out, v * 0.07, st + int(s * beat / 4 * SR))
        # driving 8th bass
        for e in range(8):
            bn = int(beat / 2 * SR)
            add(out, lp(osc("saw", mtof(ch[0] - 24), bn), 700) * env(bn, 0.003, 0.1, 0.5, 0.03) * 0.30, st + int(e * beat / 2 * SR))
        # drums: kick on 1&3, big gated snare on 2&4
        for q in range(4):
            ts = st + int(q * beat * SR)
            if q % 2 == 0: add(out, kick(0.4, 140, 50, 7) * 0.85, ts)
            else:
                sn = snare(rng, 6, 200)[: int(0.22 * SR)]  # gated
                add(out, sn * 0.42, ts)
            add(out, noise_hit(rng, 0.05, 60) * 0.07, ts + int(beat / 2 * SR))
    # simple echo for 80s space
    d = int(beat * 0.75 * SR); echo = np.zeros(n); echo[d:] = out[:-d] * 0.25
    return out + echo


def phonk(dur, rng):
    bpm = 130; beat = 60 / bpm; n = int(dur * SR); out = np.zeros(n)
    bar = beat * 4; root = 37  # C#
    bell = [61, 64, 66, 64, 61, 59, 61, 56]
    for b in range(int(dur / bar) + 1):
        st = int(b * bar * SR)
        # cowbell melody (two detuned squares through bandpass-ish)
        for s, m in enumerate(bell):
            cn = int(0.22 * SR); t = np.arange(cn) / SR
            v = (osc("sq", mtof(m) * 1.0, cn) + osc("sq", mtof(m) * 1.48, cn)) * np.exp(-t * 14)
            v = lp(v, 3500) - lp(v, 600)
            add(out, v * 0.11, st + int(s * beat / 2 * SR))
        # 808 with glide
        for pos, ln, m2 in [(0, 1.5, 0), (1.75, 0.75, 0), (2.5, 1.5, 3 if b % 2 else -2)]:
            nn = int(ln * beat * SR); t = np.arange(nn) / SR
            f = mtof(root) * 2 ** ((m2 * np.clip(t / 0.12, 0, 1)) / 12 if pos == 2.5 else 0)
            v = np.sin(2 * np.pi * np.cumsum(f) / SR); v = np.tanh(v * 2.2) * env(nn, 0.003, 0.5, 0.8, 0.06)
            add(out, v * 0.42, st + int(pos * beat * SR))
            add(out, kick(0.12, 180, 60, 30) * 0.5, st + int(pos * beat * SR))
        # snare/clap on 3 (half-time feel) + rolling hats
        add(out, snare(rng, 16, 220) * 0.45, st + int(2 * beat * SR))
        for h in range(16):
            ts = st + int(h * beat / 4 * SR)
            add(out, noise_hit(rng, 0.03, 120) * 0.08, ts)
            if b % 2 and h >= 12:  # triplet roll at end of bar
                add(out, noise_hit(rng, 0.02, 160) * 0.07, ts + int(beat / 12 * SR))
    return np.tanh(out * 1.4) / 1.2


def afro(dur, rng):
    bpm = 108; beat = 60 / bpm; n = int(dur * SR); out = np.zeros(n)
    prog = [[54, 57, 61, 64], [52, 56, 59, 62], [57, 61, 64, 68], [59, 62, 66, 69]]  # F#m7 E A Bm-ish
    bar = beat * 4
    for b in range(int(dur / bar) + 1):
        st = int(b * bar * SR); ch = prog[b % 4]
        # plucky guitar-like stabs on the offbeats
        for p in [0.5, 1.5, 1.75, 2.5, 3.5]:
            nn = int(0.25 * SR); t = np.arange(nn) / SR
            v = sum(osc("tri", mtof(m + 12), nn) for m in ch[1:]) / 3 * np.exp(-t * 16)
            add(out, v * 0.12, st + int(p * beat * SR))
        # warm marimba-ish lead
        for k, p in enumerate([0, 0.75, 1.5, 2.25, 3]):
            m = ch[(k + b) % 4] + 12; nn = int(0.4 * SR); t = np.arange(nn) / SR
            add(out, (np.sin(2 * np.pi * mtof(m) * t) + 0.25 * np.sin(2 * np.pi * mtof(m) * 4 * t)) * np.exp(-t * 7) * 0.10,
                st + int(p * beat * SR))
        # bass
        for p, ln in [(0, 0.75), (1.5, 0.5), (2, 0.75), (3.25, 0.5)]:
            nn = int(ln * beat * SR)
            add(out, np.sin(2 * np.pi * mtof(ch[0] - 24) * np.arange(nn) / SR) * env(nn, 0.005, 0.2, 0.7, 0.04) * 0.38, st + int(p * beat * SR))
        # drums: kick 4otf-ish but syncopated, rim + shaker
        for p in [0, 1, 2, 3]: add(out, kick(0.3, 120, 50, 11) * 0.7, st + int(p * beat * SR))
        for p in [0.75, 1.5, 2.75, 3.5]:
            rn = int(0.06 * SR); t = np.arange(rn) / SR
            add(out, np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 80) * 0.18, st + int(p * beat * SR))
        add(out, snare(rng, 20, 210) * 0.25, st + int(1 * beat * SR)); add(out, snare(rng, 20, 210) * 0.25, st + int(3 * beat * SR))
        for h in range(16):
            add(out, noise_hit(rng, 0.05, 50) * (0.07 if h % 2 else 0.04), st + int(h * beat / 4 * SR))
    return out


STYLES = dict(lofi=lofi, synthwave=synthwave, phonk=phonk, afro=afro)


def make(style, path, dur, seed=1):
    rng = np.random.default_rng(seed)
    x = STYLES[style](dur, rng)
    x = x - 0.55 * lp(x, 140)  # tame sub-bass so it carries on phone speakers
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, 220) * 0.96 + x * 0.04], 1)  # tiny stereo width
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 1)
