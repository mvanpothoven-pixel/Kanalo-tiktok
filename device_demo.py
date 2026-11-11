"""Simple 'real app on a device + music' TikToks (style of the 313K video).
Usage: python3 device_demo.py OUT_DIR [id ...]
Only real Kanalo demo screens from ./assets (fictional content)."""
import os, sys, math, subprocess
from PIL import Image, ImageDraw, ImageFilter
import kanalo_video as kv

W, H, FPS = 1080, 1920, 30
A = kv.ASSETS
A["iphone_gids"] = kv.load("iphone_gids.png")

VIDEOS = [
    dict(id="d1_bestscreen", dev="tv", screens=["atv_home", "atv_movies"], dur=8,
         hook="The IPTV player that fits\nyour best screen.", seed=11),
    dict(id="d2_zeroads", dev="phone", screens=["as_movies", "as_detail"], dur=8,
         hook="Your own playlist.\nZero ads.", seed=12),
    dict(id="d3_guide", dev="phone", screens=["iphone_gids"], scroll=True, dur=8,
         hook="A real TV guide\nfor your IPTV. Finally.", seed=13),
    dict(id="d4_detail", dev="phone", screens=["iphone_detail"], scroll=True, dur=8,
         hook="Every movie with poster,\ntrailer & cast.", seed=14),
    dict(id="d5_subs", dev="phone", screens=["as_subs"], dur=7,
         hook="Subtitles exactly\nhow you like them.", seed=15),
    dict(id="d6_manage", dev="phone", screens=["as_manage"], dur=7,
         hook="Hide the channels\nyou never watch.", seed=16),
    dict(id="d7_everywhere", dev="combo", screens=["atv_gids", "iphone_gids"], dur=8,
         hook="iPhone & Apple TV.\nOne app.", seed=17),
]

BGIMG = kv.glow_bg((110, 50, 200), cy=0.52, strength=0.75, r=1000).convert("RGB")


def shadow(img, box, r, blur=40, alpha=170):
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle(box, r, fill=alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste((0, 0, 0), (0, 0), sh)


def screen_content(src, sw, sh, scroll_k=None):
    """fit src to width sw; if taller, scroll (scroll_k 0..1) or top-align; if shorter, pad dark."""
    s = sw / src.width
    im = src.resize((sw, max(1, int(src.height * s))), Image.LANCZOS)
    if im.height >= sh:
        oy = int((im.height - sh) * (scroll_k if scroll_k is not None else 0))
        return im.crop((0, oy, sw, oy + sh))
    out = Image.new("RGB", (sw, sh), im.getpixel((sw // 2, im.height - 2)))
    out.paste(im, (0, 0))
    return out


def phone(img, cx, cy, sw, sh, content):
    bz = 16; r = 78
    box = (cx - sw // 2 - bz, cy - sh // 2 - bz, cx + sw // 2 + bz, cy + sh // 2 + bz)
    shadow(img, (box[0] + 10, box[1] + 30, box[2] + 10, box[3] + 30), r)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, r, fill=(28, 28, 32), outline=(90, 90, 100), width=3)
    m = Image.new("L", (sw, sh), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, sw - 1, sh - 1], r - bz, fill=255)
    img.paste(content, (cx - sw // 2, cy - sh // 2), m)


def tvset(img, cx, cy, sw, sh, content):
    bz = 14; r = 18
    box = (cx - sw // 2 - bz, cy - sh // 2 - bz, cx + sw // 2 + bz, cy + sh // 2 + bz)
    shadow(img, (box[0], box[1] + 30, box[2], box[3] + 30), r)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, r, fill=(16, 16, 20), outline=(70, 70, 80), width=2)
    d.rounded_rectangle((cx - 70, box[3], cx + 70, box[3] + 50), 6, fill=(40, 40, 46))
    d.rounded_rectangle((cx - 190, box[3] + 46, cx + 190, box[3] + 60), 7, fill=(52, 52, 60))
    img.paste(content, (cx - sw // 2, cy - sh // 2))


def frame(v, t):
    d = v["dur"]; img = BGIMG.copy()
    k_in = kv.ease(kv.prog(t, 0.0, 0.7))
    rise = int((1 - k_in) * 140)
    bob = int(math.sin(t * 1.6) * 8)
    scr = v["screens"]
    # which screen / crossfade
    def pick(sw, sh, scroll=False):
        if len(scr) == 1 or v["dev"] == "combo":
            return screen_content(A[scr[0]], sw, sh, kv.ease(kv.prog(t, 1.2, d - 1.2)) if scroll else None)
        sw_t = d * 0.5
        a = screen_content(A[scr[0]], sw, sh); b = screen_content(A[scr[1]], sw, sh)
        return Image.blend(a, b, kv.ease(kv.prog(t, sw_t - 0.25, sw_t + 0.25)))
    if v["dev"] == "tv":
        sw, sh = 980, int(980 * A[scr[0]].height / A[scr[0]].width)
        z = 1 + 0.05 * kv.prog(t, 0, d)
        c = pick(sw, sh)
        tvset(img, W // 2, 1000 + rise + bob, sw, sh, c)
    elif v["dev"] == "phone":
        sw, sh = 600, 1260
        phone(img, W // 2, 1110 + rise + bob, sw, sh, pick(sw, sh, v.get("scroll")))
    else:
        tw = 900; th = int(tw * A[scr[0]].height / A[scr[0]].width)
        tvset(img, W // 2 - 40, 820 + rise + bob, tw, th, screen_content(A[scr[0]], tw, th))
        k2 = kv.ease(kv.prog(t, 0.5, 1.3))
        sw, sh = 330, 700
        phone(img, W // 2 + 290, 1260 + int((1 - k2) * 900) - bob, sw, sh,
              screen_content(A[scr[1]], sw, sh, kv.ease(kv.prog(t, 1.5, d - 0.8))))
    # hook text
    ka = kv.ease(kv.prog(t, 0.15, 0.6))
    lines = v["hook"].split("\n")
    for i, ln in enumerate(lines):
        kv.text(img, ln, W // 2, 205 + i * 92, 74, alpha=ka)
    # brand footer
    kf = kv.ease(kv.prog(t, 0.9, 1.5))
    lab = "Kanalo · free on the App Store"; tw = kv.F(40, "SemiBold").getlength(lab)
    x0 = int(W / 2 - (tw + 84) / 2)
    kv.logo(img, x0 + 32, 1815, 64, alpha=kf)
    kv.text(img, lab, x0 + 84, 1815, 40, alpha=kf, w="SemiBold", anchor="lm")
    return img


def render(v, out):
    n = int(v["dur"] * FPS)
    tmp = os.path.join(out, v["id"] + "_v.mp4")
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "17", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(v, i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    mus = os.path.join(out, v["id"] + "_m.wav")
    subprocess.run([sys.executable, os.path.join(kv.HERE, "house_music.py"), mus, str(v["dur"] + 1), str(v["seed"])], check=True,
                   stdout=subprocess.DEVNULL)
    final = os.path.join(out, v["id"] + ".mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", tmp, "-i", mus, "-map", "0:v", "-map", "1:a",
                    "-af", f"afade=in:d=0.3,afade=out:st={v['dur'] - 0.8}:d=0.8", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", final], check=True)
    os.remove(tmp); os.remove(mus)
    return final


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    ids = sys.argv[2:]
    for v in VIDEOS:
        if ids and v["id"] not in ids: continue
        if "preview" in ids:
            pass
        print(render(v, out))
