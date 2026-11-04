"""Royalty-free background music generator for Kanalo videos (lo-fi / chill).

make_music(path, dur, seed) writes a stereo 48 kHz WAV of `dur` seconds.
Everything is synthesised here, so there are no rights issues.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000

# chord progressions as semitone offsets from the key root (root, 3rd, 5th, 7th, 9th)
PROGS = [
    [[0, 4, 7, 11, 14], [-3, 0, 4, 7, 11], [5, 9, 12, 16, 19], [7, 11, 14, 17, 21]],   # Imaj7 vi7 IVmaj7 V7
    [[2, 5, 9, 12, 16], [7, 11, 14, 17, 21], [0, 4, 7, 11, 14], [-3, 0, 4, 7, 11]],    # ii7 V7 Imaj7 vi7
    [[5, 9, 12, 16, 19], [4, 7, 11, 14, 17], [2, 5, 9, 12, 16], [0, 4, 7, 11, 14]],    # IV iii ii I
]
KEYS = [53, 55, 57, 58, 60]  # MIDI roots: F, G, A, Bb, C


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lowpass(x, fc):
    return sosfilt(butter(2, fc, btype="low", fs=SR, output="sos"), x)


def highpass(x, fc):
    return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)


def rhodes(freq, n):
    t = np.arange(n) / SR
    env = np.exp(-t * 1.6) * (1 - np.exp(-t * 60))
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    tone = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t)
            + 0.12 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 6))
    return tone * env * trem


def make_music(path, dur, seed=0, bpm=None):
    rng = np.random.default_rng(seed)
    bpm = bpm or int(rng.choice([76, 80, 84, 88]))
    beat = 60.0 / bpm
    bar = beat * 4
    n = int(dur * SR)
    out = np.zeros(n)
    prog = PROGS[seed % len(PROGS)]
    key = KEYS[seed % len(KEYS)] - 12

    # chords: one hit per bar + a soft re-hit on beat 3
    nbars = int(np.ceil(dur / bar)) + 1
    for b in range(nbars):
        chord = prog[b % len(prog)]
        for off in (0.0, beat * 2.5):
            start = int((b * bar + off) * SR)
            if start >= n:
                continue
            ln = min(int(bar * SR * 1.2), n - start)
            vel = 1.0 if off == 0 else 0.45
            for i, s in enumerate(chord):
                out[start:start + ln] += rhodes(mtof(key + s), ln)[:ln] * 0.16 * vel * (0.85 if i else 1.0)
        # bass: root on beat 1 and 3
        for off in (0.0, beat * 2):
            start = int((b * bar + off) * SR)
            if start >= n:
                continue
            ln = min(int(beat * 1.8 * SR), n - start)
            t = np.arange(ln) / SR
            f = mtof(key + chord[0] - 12)
            out[start:start + ln] += np.sin(2 * np.pi * f * t) * np.exp(-t * 2.5) * 0.30

    out = lowpass(out, 2600)

    # drums
    drums = np.zeros(n)
    nbeats = int(dur / beat) + 2
    for k in range(nbeats):
        start = int(k * beat * SR)
        if start >= n:
            continue
        if k % 4 in (0, 2) or (k % 8 == 7):  # kick
            ln = min(int(0.35 * SR), n - start)
            t = np.arange(ln) / SR
            f = 45 + 70 * np.exp(-t * 30)
            drums[start:start + ln] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.55
        if k % 4 in (1, 3):  # soft snare / rim
            ln = min(int(0.18 * SR), n - start)
            t = np.arange(ln) / SR
            noise = highpass(rng.standard_normal(ln), 1800)
            drums[start:start + ln] += noise * np.exp(-t * 28) * 0.10
        for h in (0.0, 0.5):  # hats on 8ths
            hs = int((k + h) * beat * SR) + int(rng.integers(0, 400))
            if hs >= n:
                continue
            ln = min(int(0.05 * SR), n - hs)
            t = np.arange(ln) / SR
            hat = highpass(rng.standard_normal(ln), 7000) * np.exp(-t * 90)
            drums[hs:hs + ln] += hat * (0.035 if h else 0.05)
    out += lowpass(drums, 9000)

    # vinyl crackle + hiss
    crackle = np.zeros(n)
    idx = rng.integers(0, n, size=int(dur * 6))
    crackle[idx] = rng.uniform(-0.25, 0.25, size=idx.size)
    out += lowpass(crackle, 4000) * 0.4 + lowpass(rng.standard_normal(n), 3000) * 0.004

    # fades and level
    fade_in, fade_out = int(0.4 * SR), int(1.2 * SR)
    out[:fade_in] *= np.linspace(0, 1, fade_in)
    out[-fade_out:] *= np.linspace(1, 0, fade_out)
    out = np.tanh(out * 1.2)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.5
    # light stereo width: delayed copy on the right
    d = int(0.012 * SR)
    right = np.concatenate([np.zeros(d), out[:-d]])
    st = np.stack([out, 0.85 * out + 0.15 * right], axis=1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    return path


if __name__ == "__main__":
    import sys
    make_music(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 0)
