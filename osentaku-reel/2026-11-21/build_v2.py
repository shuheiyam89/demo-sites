#!/usr/bin/env python3
"""Osouji promo reel v2: adds a result scene (3 cards fading in staggered)
between the white transition and the after clip.
cover 0.5 + before 5.0 + phone 3.0 + white 0.6 + result 3.6 + after 5.7 = 18.4s (+ end card 1.5 = 19.9s)"""
import subprocess, sys, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

D = "/home/hatch/workspace/instagram/osouji-promo-1116"
W, H, FPS = 720, 1280, 30
SANS = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
TEAL = (31, 122, 153)
INK = (32, 48, 58)

phone_img = Image.open(f"{D}/phone.png").convert("RGB")
cover = Image.open(f"{D}/cover.jpg").convert("RGB")
before_img = Image.open(f"{D}/before.png").convert("RGB")

wm = Image.open(f"{D}/lockup.png").convert("RGBA")
wm = wm.resize((190, int(190 * wm.height / wm.width)), Image.LANCZOS)
wm.putalpha(wm.getchannel("A").point(lambda v: int(v * 0.65)))

def frame_at(img, z, cx=0.5, cy=0.46):
    iw, ih = img.size
    cw, ch = iw / z, ih / z
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)

def add_wm(fr):
    fr.paste(wm, (16, 16), wm)
    return fr

bframes = sorted(glob.glob(f"{D}/before_frames/f*.png"))
aframes = sorted(glob.glob(f"{D}/after_frames/f*.png"))
print(f"frames: before {len(bframes)}, after {len(aframes)}", file=sys.stderr)

# ---------- result scene cards ----------
def make_card(chip, text):
    cw_, ch_ = 520, 128
    card = Image.new("RGBA", (cw_ + 16, ch_ + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([8, 8, cw_ + 8, ch_ + 8], radius=26, fill=(0, 0, 0, 70))  # shadow
    d.rounded_rectangle([0, 0, cw_, ch_], radius=26, fill=(255, 255, 255, 255))
    fchip = ImageFont.truetype(SANS, 27)
    tw = d.textlength(chip, font=fchip)
    d.rounded_rectangle([26, 24, 26 + tw + 28, 24 + 44], radius=22, fill=TEAL + (255,))
    d.text((26 + 14, 46), chip, font=fchip, fill=(255, 255, 255), anchor='lm')
    size = 30
    ftext = ImageFont.truetype(SANS, size)
    while d.textlength(text, font=ftext) > cw_ - 52 and size > 20:
        size -= 2
        ftext = ImageFont.truetype(SANS, size)
    d.text((26, 96), text, font=ftext, fill=INK + (255,), anchor='lm')
    return card

cards = [
    (make_card('見立て', 'コンロの焦げ付き・油汚れ'), (46, 268)),
    (make_card('手順', '重曹ペースト→こする→拭き上げ'), (150, 540)),
    (make_card('使うもの', '重曹とスポンジ（家にあるもの）'), (46, 812)),
]
backdrop = frame_at(before_img, 1.0)
backdrop = ImageEnhance.Brightness(backdrop).enhance(0.8).filter(ImageFilter.GaussianBlur(1.1)).convert("RGBA")

def result_frame(i, total):
    fr = backdrop.copy()
    starts = [9, 36, 63]
    for (card, (x, y)), st in zip(cards, starts):
        if i < st:
            continue
        p = min((i - st) / 12.0, 1.0)
        if p < 1.0:
            c = card.copy()
            alpha = c.getchannel("A").point(lambda v: int(v * p))
            c.putalpha(alpha)
            fr.paste(c, (x, y + int((1 - p) * 16)), c)
        else:
            fr.paste(card, (x, y), card)
    return add_wm(fr.convert("RGB"))

# ---------- assemble part1 v2 ----------
def stream_to(path, emit_fn):
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    count = [0]
    def emit(fr):
        proc.stdin.write(fr.convert("RGB").tobytes()); count[0] += 1
    emit_fn(emit)
    proc.stdin.close(); proc.wait()
    print(f"{path}: {count[0]} frames = {count[0]/FPS:.2f}s rc={proc.returncode}", file=sys.stderr)

def build(emit):
    for _ in range(int(0.5 * FPS)):
        emit(cover)
    n = int(5.0 * FPS)
    for i in range(n):
        emit(add_wm(Image.open(bframes[min(i, len(bframes) - 1)]).convert("RGB")))
    n = int(3.0 * FPS)
    phone_frames = [frame_at(phone_img, 1.00 + 0.07 * (i / (n - 1)), cy=0.44) for i in range(n)]
    for f in phone_frames:
        emit(add_wm(f))
    last = phone_frames[-1]
    white = Image.new("RGB", (W, H), (255, 255, 255))
    n = int(0.6 * FPS)
    for i in range(n):
        emit(Image.blend(last, white, [0.3, 0.55, 0.8, 0.95][i]) if i < 4 else white)
    n = int(3.6 * FPS)
    for i in range(n):
        emit(result_frame(i, n))
    n = int(5.7 * FPS)
    for i in range(n):
        emit(add_wm(Image.open(aframes[min(i, len(aframes) - 1)]).convert("RGB")))

stream_to(f"{D}/part1v2.mp4", build)
print("done", file=sys.stderr)
