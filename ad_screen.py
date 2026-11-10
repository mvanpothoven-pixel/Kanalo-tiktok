"""Fake (invented) ad-break screen for a generic bad IPTV app. Usage: python3 ad_screen.py OUT.png [W H]"""
import sys, math
from PIL import Image, ImageDraw, ImageFilter
import kanalo_video as kv

W, H = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (756, 479)
S = 3  # supersample
w, h = W * S, H * S
img = Image.new("RGB", (w, h), (20, 20, 24))
d = ImageDraw.Draw(img)
# loud generic ad: yellow/red burst
for y in range(h):
    t = y / h
    d.line([(0, y), (w, y)], fill=(int(250 - 40 * t), int(200 - 120 * t), int(40 + 10 * t)))
cx, cy = w * 0.32, h * 0.52
for i in range(24):
    a0 = i * math.pi / 12; a1 = a0 + math.pi / 24
    d.polygon([(cx, cy), (cx + 3000 * math.cos(a0), cy + 3000 * math.sin(a0)), (cx + 3000 * math.cos(a1), cy + 3000 * math.sin(a1))], fill=(255, 225, 70))
d.ellipse([cx - 330, cy - 330, cx + 330, cy + 330], fill=(230, 40, 50))
f = kv.F(150, "Bold"); d.text((cx, cy - 40), "MEGA", font=f, fill="white", anchor="mm")
d.text((cx, cy + 110), "SALE!", font=f, fill="white", anchor="mm")
f2 = kv.F(84, "Bold")
d.rounded_rectangle([w * 0.58, h * 0.36, w * 0.95, h * 0.62], 40, fill=(255, 255, 255))
d.text((w * 0.765, h * 0.44), "-70%", font=kv.F(170, "Bold"), fill=(230, 40, 50), anchor="mm")
d.text((w * 0.765, h * 0.56), "ONLY TODAY", font=kv.F(60, "Bold"), fill=(30, 30, 30), anchor="mm")
# top-left AD badge and countdown, bottom progress bar
d.rounded_rectangle([60, 60, 60 + 360, 60 + 110], 24, fill=(0, 0, 0, 200))
d.text((60 + 180, 115), "AD  1 / 4", font=kv.F(64, "Bold"), fill=(255, 210, 0), anchor="mm")
d.rounded_rectangle([w - 60 - 420, 60, w - 60, 170], 24, fill=(0, 0, 0))
d.text((w - 60 - 210, 115), "Skip in 0:30", font=kv.F(56, "Bold"), fill="white", anchor="mm")
d.rectangle([0, h - 34, w, h], fill=(0, 0, 0))
d.rectangle([0, h - 34, int(w * 0.08), h], fill=(255, 210, 0))
img = img.resize((W, H), Image.LANCZOS)
img.save(sys.argv[1])
print(sys.argv[1], img.size)
