"""'I broke up with my IPTV app' — chat-style TikTok (1080x1920, 30fps) with music + message pops.
Usage: python3 chat_breakup.py LANG OUT.mp4"""
import os, sys, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import kanalo_video as kv
import kanalo_music as km

W, H, FPS = 1080, 1920, 30
EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
BLUE = (10, 132, 255); GREY = (38, 38, 41); BG = (0, 0, 0)

T = {
 "en": dict(hook=("I broke up with", "my IPTV app 💔"), name="My IPTV app", online="online", read="Read", deleted="My IPTV app was deleted",
   msgs=[("a", "hey 😊 ready for the match tonight?"), ("m", "we need to talk."), ("a", "sure! right after this short ad 📺"),
         ("m", "THAT. that's the problem."), ("m", "you interrupt me every time it gets good"), ("a", "but you pay me every month 🥺"),
         ("m", "exactly."), ("m", "my playlist works in any player btw"), ("a", "…who is he"), ("img", None), ("m", "his name is Kanalo. no ads. ever. bye 👋")]),
 "nl": dict(hook=("Ik heb het uitgemaakt", "met mijn IPTV-app 💔"), name="Mijn IPTV-app", online="online", read="Gelezen", deleted="Mijn IPTV-app is verwijderd",
   msgs=[("a", "hoi 😊 zin in de wedstrijd vanavond?"), ("m", "we moeten praten."), ("a", "tuurlijk! na deze korte reclame 📺"),
         ("m", "DAT. dat is het probleem."), ("m", "je onderbreekt me altijd op het mooiste moment"), ("a", "maar je betaalt me elke maand 🥺"),
         ("m", "precies."), ("m", "mijn playlist werkt in elke speler trouwens"), ("a", "…wie is hij"), ("img", None), ("m", "hij heet Kanalo. geen reclame. nooit. doei 👋")]),
}


def is_emo(c): return ord(c) > 0x2190 and c not in "…·"


def runs(s):
    out, cur, emo = [], "", None
    for c in s:
        e = is_emo(c) or c == "️"
        if emo is None or e == emo: cur += c
        else: out.append((emo, cur)); cur = c
        emo = e
    if cur: out.append((emo, cur))
    return out


_ec = {}
def emoji_img(ch, size):
    k = (ch, size)
    if k not in _ec:
        im = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((6, 6), ch, font=EMO, embedded_color=True)
        bb = im.getbbox() or (0, 0, 1, 1); im = im.crop(bb)
        s = size / im.height; _ec[k] = im.resize((max(1, int(im.width * s)), size), Image.LANCZOS)
    return _ec[k]


def text_w(s, f, size):
    w = 0; d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for e, part in runs(s):
        if e: w += sum(emoji_img(c, int(size * 1.05)).width + 4 for c in part if c != "️")
        else: w += d.textlength(part, font=f)
    return w


def draw_rich(img, xy, s, f, size, fill):
    x, y = xy; d = ImageDraw.Draw(img)
    for e, part in runs(s):
        if e:
            for c in part:
                if c == "️": continue
                em = emoji_img(c, int(size * 1.05)); img.paste(em, (int(x), int(y - size * 0.86)), em); x += em.width + 4
        else:
            d.text((x, y), part, font=f, fill=fill, anchor="ls"); x += d.textlength(part, font=f)


def wrap(s, f, size, maxw):
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, f, size) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines


FS = 58; FNT = kv.F(FS, "Regular"); LH = 74; PADX, PADY = 42, 28; MAXW = 700


def bubble(kind, s):
    lines = wrap(s, FNT, FS, MAXW)
    tw = max(text_w(l, FNT, FS) for l in lines)
    bw, bh = int(tw + 2 * PADX), int(len(lines) * LH + 2 * PADY - 8)
    im = Image.new("RGBA", (bw + 20, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = BLUE if kind == "m" else GREY
    x0 = 0 if kind == "m" else 20
    d.rounded_rectangle([x0, 0, x0 + bw, bh], 44, fill=col)
    # tail
    if kind == "m": d.polygon([(bw - 30, bh - 30), (bw + 16, bh), (bw - 50, bh - 4)], fill=col)
    else: d.polygon([(50, bh - 30), (4, bh), (70, bh - 4)], fill=col)
    for i, l in enumerate(lines):
        draw_rich(im, (x0 + PADX, PADY + 46 + i * LH), l, FNT, FS, (255, 255, 255))
    return im


def img_bubble(lang="en"):
    scr = Image.open(os.path.join(kv.HERE, "overlays", f"screen_gids_{lang}.png")).convert("RGB")
    w = 430; h = int(w * scr.height / scr.width); h = min(h, 760)
    s = scr.resize((w, int(w * scr.height / scr.width)), Image.LANCZOS).crop((0, 0, w, h))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 40, fill=255); im.paste(s, (0, 0), m)
    return im


def build(lang):
    L = T[lang]; items = []; t = 1.6
    for kind, s in L["msgs"]:
        if kind == "a":
            items.append(dict(kind="typing", t0=t, t1=t + 0.6)); t += 0.6
        im = img_bubble(lang) if kind == "img" else bubble(kind, s)
        items.append(dict(kind=kind, im=im, t0=t)); t += 1.1 if kind != "img" else 1.5
        if kind == "m" and len(s) < 22: t -= 0.35
    return items, t


def header(img, L):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 330], fill=(18, 18, 20))
    d.line([(0, 330), (W, 330)], fill=(45, 45, 50), width=2)
    d.text((60, 250), "‹", font=kv.F(96, "Regular"), fill=BLUE, anchor="lm")
    cx = W // 2
    d.ellipse([cx - 58, 130, cx + 58, 246], fill=(90, 90, 98))
    d.rounded_rectangle([cx - 30, 166, cx + 30, 204], 6, outline="white", width=5)
    d.line([(cx - 12, 216), (cx + 12, 216)], fill="white", width=5)
    d.text((cx, 288), L["name"], font=kv.F(40, "Medium"), fill="white", anchor="mm")


def typing_im(t):
    im = Image.new("RGBA", (190, 104), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 0, 180, 100], 44, fill=GREY); d.polygon([(50, 70), (4, 100), (70, 96)], fill=GREY)
    for i in range(3):
        a = 0.45 + 0.55 * max(0, np.sin((t * 6) - i * 0.9))
        c = int(150 * a + 60); d.ellipse([60 + i * 36 - 12, 38, 60 + i * 36 + 12, 62], fill=(c, c, c))
    return im


def frame(t, items, L, total):
    img = Image.new("RGB", (W, H), BG)
    vis = []
    for it in items:
        if it["kind"] == "typing":
            if it["t0"] <= t < it["t1"]: vis.append(("a", typing_im(t), it["t0"]))
        elif t >= it["t0"]: vis.append((it["kind"], it["im"], it["t0"]))
    TOP, BOT, GAP = 380, 1440, 22
    hs = sum(v[1].height + GAP for v in vis)
    off = max(0, hs - (BOT - TOP))
    y = TOP - off
    for kind, im, t0 in vis:
        p = kv.ease(kv.prog(t, t0, t0 + 0.18)); sc = 0.85 + 0.15 * kv.back(kv.prog(t, t0, t0 + 0.22))
        if y + im.height > TOP - 60:
            w2, h2 = max(1, int(im.width * sc)), max(1, int(im.height * sc))
            im2 = im.resize((w2, h2)) if sc != 1 else im
            if p < 1: a = im2.split()[3].point(lambda v: int(v * p)); im2 = im2.copy(); im2.putalpha(a)
            x = W - 40 - w2 if kind in ("m", "img") else 30
            img.paste(im2, (int(x), int(y + (im.height - h2))), im2)
        y += im.height + GAP
    last_m = max([it["t0"] for it in items if it["kind"] in ("m", "img")])
    if t > last_m + 0.6:
        d = ImageDraw.Draw(img); d.text((W - 50, min(y + 4, BOT + 30)), L["read"], font=kv.F(32, "Medium"), fill=(140, 140, 150), anchor="ra")
    if t > last_m + 1.3:
        d = ImageDraw.Draw(img); yy = min(y + 70, BOT + 90)
        d.text((W / 2, yy), L["deleted"], font=kv.F(34, "Medium"), fill=(140, 140, 150), anchor="ma")
    header(img, L)
    # hook banner (cover frame) for the first 3.2s
    if t < 3.4:
        a = 1 - kv.prog(t, 3.0, 3.4)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        d.rounded_rectangle([60, 470, W - 60, 760], 40, fill=(255, 255, 255, int(245 * a)))
        img.paste(Image.new("RGB", (W, H)), (0, 0), ov.split()[3].point(lambda v: 0))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        if a > 0.05:
            l1, l2 = L["hook"]
            f = kv.F(70, "Bold")
            for i, s in enumerate((l1, l2)):
                tw = text_w(s, f, 70); tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                draw_rich(tmp, ((W - tw) / 2, 590 + i * 100), s, f, 70, (15, 15, 20, 255))
                tmp.putalpha(tmp.split()[3].point(lambda v: int(v * a)))
                img = Image.alpha_composite(img.convert("RGBA"), tmp).convert("RGB")
    return img


def blips(path, times, dur, sr=44100):
    n = int(dur * sr); out = np.zeros(n)
    for t, kind in times:
        s = int(t * sr); ln = int(0.09 * sr)
        if s + ln > n: continue
        tt = np.arange(ln) / sr; f = 1350 if kind == "m" else 880
        out[s:s + ln] += np.sin(2 * np.pi * f * tt * (1 + 0.6 * tt)) * np.exp(-tt * 45) * 0.35
    data = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(data.tobytes())


def main(lang, out, endpng):
    L = T[lang]; items, t_end = build(lang)
    total = t_end + 1.6; end_len = 2.4; dur = total + end_len
    end = Image.open(endpng).convert("RGB")
    tmp = tempfile.mkdtemp()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", f"{tmp}/v.mp4"], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        t = i / FPS
        im = end if t >= total else frame(t, items, L, total)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    km.make_music(f"{tmp}/m.wav", dur, seed=17)
    blips(f"{tmp}/b.wav", [(it["t0"], it["kind"]) for it in items if it["kind"] != "typing"], dur)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{tmp}/v.mp4", "-i", f"{tmp}/m.wav", "-i", f"{tmp}/b.wav", "-filter_complex",
                    "[1]volume=0.55[m];[2]volume=1.0[b];[m][b]amix=inputs=2:normalize=0,afade=t=out:st=%.2f:d=0.6[a]" % (dur - 0.6),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    print(out, round(dur, 2))


if __name__ == "__main__":
    lang = sys.argv[1]; main(lang, sys.argv[2], os.path.join(kv.HERE, "overlays", f"end_{lang}.png"))
