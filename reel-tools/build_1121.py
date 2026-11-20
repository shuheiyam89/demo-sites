#!/usr/bin/env python3
"""宣伝リール 2026-11-21（おきがえ／おせんたく／おそうじ）の組み立て。
720x1280 / 30fps / H.264 High / yuv420p / AAC。音声は指定の BGM ＋カシャッ（shutter.wav）だけ（クリップの元音声は使わない）
透かし：各アプリのロゴ（ロックアップ）を左上・幅186px・不透明度65%で全編に入れる

おせんたく・おそうじ（build_v2.py の型）：
  cover 0.5 + before 5.0 + スマホ撮影 3.0 + 白 0.6 + 見立て結果 3.6 + after 5.7 + end 1.5 = 19.9 秒
おきがえ：
  cover 0.5 + before 5.0 + カシャッ白フラッシュ＋白い線スワイプ 0.6 + after 6.0 + 商品 2.0 + end 1.5 = 15.6 秒

使い方: python reel-tools/build_1121.py okigae|osentaku|osouji   （demo-sites フォルダで実行）
出力: <app>-reel/2026-11-21/ に reel.mp4・cover.jpg・frame-*.jpg
"""
import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 720, 1280, 30
INK = (32, 48, 58)
RED = (214, 40, 40)
FF = shutil.which("ffmpeg") or os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe")

APPS = {
    "okigae": dict(
        kind="okigae", music="Bossa_Antigua.mp3", color=(98, 72, 196), url="okigae.onrender.com",
        cover="普段着→デートの装い", before_start=0.0, after_start=1.5, after_sec=6.0,
        product_name="リボーン（Re-Bone）リボーンウォレット・改\nブラックリザード（リングトカゲ）",
        end_note="作品や商品、掲載しませんか？",
    ),
    "osentaku": dict(
        kind="v2", music="Quasi_Motion.mp3", color=(43, 111, 196), url="osentaku.onrender.com", name="おせんたく", icon="osentaku-icon.png",
        cover="ワインのシミ→真っ白", before_start=0.0, after_start=2.0,
        before_telop="お気に入りの白セーターにワインが…", after_telop="シミ抜きの手順がすぐ分かる",
        cards=[("見立て", "赤ワインのシミ／ニット（ウール混）"),
               ("手順", "①水で薄めた中性洗剤を付けて叩く\n②ぬるま湯ですすぐ\n③形を整えて陰干し"),
               ("使うもの", "中性洗剤／清潔な布／ぬるま湯")],
    ),
    "osouji": dict(
        kind="v2", music="Carefree.mp3", color=(31, 122, 153), url="osouji.onrender.com", name="おそうじ", icon="osouji-icon.png",
        cover="油汚れ→ピカピカ", before_start=0.0, after_start=2.5,
        before_telop="大掃除、レンジフードの油汚れが手強い…", after_telop="落とし方の手順がすぐ分かる",
        cards=[("見立て", "油汚れ／レンジフード（金属）"),
               ("手順", "①重曹ペーストを塗って置く\n②お湯で絞った布で拭く\n③乾拭きで仕上げ"),
               ("使うもの", "重曹／布／ゴム手袋")],
    ),
}

APP = sys.argv[1] if len(sys.argv) > 1 else ""
if APP not in APPS:
    raise SystemExit("使い方: python reel-tools/build_1121.py okigae|osentaku|osouji")
C = APPS[APP]
D = os.path.join(ROOT, f"{APP}-reel", "2026-11-21")


def font(names, size):
    for n in names:
        for d in [r"C:\Windows\Fonts", "/usr/share/fonts/opentype/noto", "/usr/share/fonts/truetype/dejavu"]:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    raise SystemExit(f"フォントが見つかりません: {names}")


SANS = ["YuGothB.ttc", "BIZ-UDGothicB.ttc", "NotoSansCJK-Bold.ttc"]
SANS_R = ["YuGothM.ttc", "NotoSansCJK-Regular.ttc"]
SERIF = ["georgiab.ttf", "DejaVuSerif-Bold.ttf"]


def cover_fit(img, w, h):
    s = max(w / img.width, h / img.height)
    r = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (r.width - w) // 2, (r.height - h) // 2
    return r.crop((x, y, x + w, y + h))


def zoom(img, z, cy=0.5):
    cw, ch = W / z, H / z
    x0 = (W - cw) / 2
    y0 = min(max(cy * H - ch / 2, 0), H - ch)
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)


# ---------- ロゴ（ロックアップ）と透かし ----------
def lockup_for():
    if APP == "okigae":
        # okigae-lockup.png は白い背景つき（RGB）なので、白に近い所を透明にする
        im = Image.open(os.path.join(D, "okigae-lockup.png")).convert("RGB")
        a = im.convert("L").point(lambda v: 0 if v > 246 else (255 if v < 200 else int((246 - v) * 255 / 46)))
        lk = im.convert("RGBA")
        lk.putalpha(a)
        return lk.crop(lk.getbbox())
    icon = Image.open(os.path.join(D, C["icon"])).convert("RGBA")
    f = font(SANS, 104)
    tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(C["name"], font=f))
    lk = Image.new("RGBA", (192 + 28 + tw + 8, 192), (0, 0, 0, 0))
    lk.alpha_composite(icon.resize((192, 192), Image.LANCZOS), (0, 0))
    ImageDraw.Draw(lk).text((192 + 28, 96), C["name"], font=f, fill=(35, 60, 80, 255), anchor="lm")
    return lk


LOCKUP = lockup_for()
WM = LOCKUP.resize((186, round(186 * LOCKUP.height / LOCKUP.width)), Image.LANCZOS)
WM.putalpha(WM.getchannel("A").point(lambda v: int(v * 0.65)))


def add_wm(fr):
    fr = fr.convert("RGBA")
    fr.alpha_composite(WM, (16, 16))
    return fr.convert("RGB")


def text_center(d, xy, s, f, fill, stroke=0, stroke_fill=None):
    d.text(xy, s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=stroke_fill)


def fit_font(names, s, maxw, size):
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while size > 30 and tmp.textlength(s, font=font(names, size)) > maxw:
        size -= 2
    return font(names, size)


def telop(fr, s, y, size=40):
    d = ImageDraw.Draw(fr)
    f = fit_font(SANS, s, W - 100, size)
    tw = d.textlength(s, font=f)
    h = f.size + 34
    x0 = (W - tw) / 2 - 30
    d.rounded_rectangle([x0, y - h / 2, W - x0, y + h / 2], radius=h / 2, fill=(255, 255, 255))
    text_center(d, (W / 2, y), s, f, INK)
    return fr


def big_word(fr, word, color, alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    text_center(ImageDraw.Draw(layer), (W / 2, H * 0.47), word, font(SERIF, 168), color + (255,), stroke=6, stroke_fill=(255, 255, 255, 255))
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    base = fr.convert("RGBA")
    base.alpha_composite(layer)
    return base.convert("RGB")


def clip_frames(name, seconds, start=0.0):
    cmd = [FF, "-v", "error", "-ss", str(start), "-i", os.path.join(D, name), "-t", str(seconds),
           "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-an", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n, last = W * H * 3, None
    for _ in range(round(seconds * FPS)):
        buf = p.stdout.read(n)
        if len(buf) == n:
            last = Image.frombytes("RGB", (W, H), buf)
        if last is None:
            raise SystemExit(f"{name} を読めませんでした")
        yield last
    p.stdout.close()
    p.wait()


before_img = Image.open(os.path.join(D, "before.jpg")).convert("RGB")
after_img = Image.open(os.path.join(D, "after.jpg")).convert("RGB")


def make_cover():
    fr = Image.new("RGB", (W, H))
    fr.paste(cover_fit(before_img, W // 2, H), (0, 0))
    fr.paste(cover_fit(after_img, W - W // 2, H), (W // 2, 0))
    d = ImageDraw.Draw(fr)
    d.rectangle([W // 2 - 3, 0, W // 2 + 3, H], fill=(255, 255, 255))
    text_center(d, (W / 2, H * 0.5), C["cover"], fit_font(SANS, C["cover"], W - 60, 78), (255, 255, 255), stroke=8, stroke_fill=INK)
    f2 = font(SANS, 34)
    text_center(d, (W * 0.25, H * 0.82), "Before", f2, (255, 255, 255), stroke=5, stroke_fill=INK)
    text_center(d, (W * 0.75, H * 0.82), "After", f2, (255, 255, 255), stroke=5, stroke_fill=INK)
    return add_wm(fr)


def make_end(note=None):
    fr = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    lw = 520
    lk = LOCKUP.resize((lw, round(lw * LOCKUP.height / LOCKUP.width)), Image.LANCZOS)
    y0 = 500
    fr.alpha_composite(lk, ((W - lw) // 2, y0))
    d = ImageDraw.Draw(fr)
    y = y0 + lk.height + 70
    text_center(d, (W / 2, y), C["url"], font(SANS, 42), C["color"])
    if note:
        text_center(d, (W / 2, y + 62), note, font(SANS_R, 28), (110, 110, 110))
    return add_wm(fr.convert("RGB"))


# ---------- おせんたく・おそうじ（build_v2.py の型） ----------
def make_phone_scene(shot, icon):
    bg = ImageEnhance.Brightness(cover_fit(shot, W, H).filter(ImageFilter.GaussianBlur(18))).enhance(0.7).convert("RGBA")
    pw, ph = 420, 840
    px, py = (W - pw) // 2, 150
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle([px + 10, py + 14, px + pw + 10, py + ph + 14], radius=62, fill=(0, 0, 0, 90))
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=62, fill=(21, 26, 31, 255))
    sx, sy, sw, sh = px + 16, py + 16, pw - 32, ph - 32
    screen = Image.new("RGBA", (sw, sh), (255, 255, 255, 255))
    band = 132
    screen.paste(cover_fit(shot, sw, sh - band), (0, band))
    sd = ImageDraw.Draw(screen)
    screen.alpha_composite(icon.resize((84, 84), Image.LANCZOS), (26, (band - 84) // 2))
    sd.text((128, band // 2), C["name"], font=font(SANS, 46), fill=INK, anchor="lm")
    cx, cy = sw // 2, sh - 70
    sd.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], outline=(255, 255, 255), width=7)
    sd.ellipse([cx - 27, cy - 27, cx + 27, cy + 27], fill=(255, 255, 255))
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw, sh], radius=48, fill=255)
    bg.paste(screen, (sx, sy), mask)
    d.rounded_rectangle([W // 2 - 50, py + 26, W // 2 + 50, py + 40], radius=7, fill=(21, 26, 31, 255))
    return bg.convert("RGB")


def wrap(d, s, f, maxw):
    """「 → 」と「／」の区切りで折り返す（言葉の途中では切らない）"""
    parts = s.split(" → ")
    lines, cur = [], ""
    for i, p in enumerate(parts):
        piece = p if i == 0 else " → " + p
        if cur and d.textlength(cur + piece, font=f) > maxw:
            lines.append(cur + " →")
            cur = p
        else:
            cur += piece
    lines.append(cur)
    return lines


def make_card(chip, text, cw=620):
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    ft = font(SANS, 32)
    lines = [ln for part in text.split("\n") for ln in wrap(tmp, part, ft, cw - 56)]
    ch = 92 + 44 * len(lines)
    card = Image.new("RGBA", (cw + 16, ch + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([8, 10, cw + 8, ch + 10], radius=28, fill=(0, 0, 0, 80))
    d.rounded_rectangle([0, 0, cw, ch], radius=28, fill=(255, 255, 255, 255))
    fc = font(SANS, 27)
    tw = d.textlength(chip, font=fc)
    d.rounded_rectangle([28, 24, 28 + tw + 32, 24 + 46], radius=23, fill=C["color"] + (255,))
    d.text((28 + 16, 47), chip, font=fc, fill=(255, 255, 255), anchor="lm")
    for i, ln in enumerate(lines):
        d.text((28, 106 + 44 * i), ln, font=ft, fill=INK, anchor="lm")
    return card


def build_v2(emit, chk):
    shot = Image.open(os.path.join(D, "photo.jpg")).convert("RGB")
    icon = Image.open(os.path.join(D, C["icon"])).convert("RGBA")
    cover = make_cover()
    for _ in range(round(0.5 * FPS)):
        emit(cover)
    chk["cover"] = cover
    for i, f in enumerate(clip_frames("before_clip.mp4", 5.0, C["before_start"])):
        fr = telop(f.copy(), C["before_telop"], 200)
        if i < 40:
            fr = big_word(fr, "Before", (20, 20, 20), 1.0 if i < 26 else (40 - i) / 14)
        emit(add_wm(fr))
    phone = make_phone_scene(shot, icon)
    n, last = round(3.0 * FPS), None
    for i in range(n):
        last = add_wm(telop(zoom(phone, 1.0 + 0.07 * i / (n - 1), cy=0.45), "スマホで撮るだけ", 1120, 44))
        emit(last)
    chk["phone"] = last
    white = Image.new("RGB", (W, H), (255, 255, 255))
    for i in range(round(0.6 * FPS)):
        emit(Image.blend(last, white, [0.35, 0.6, 0.85, 0.97][i]) if i < 4 else white)
    cards = [make_card(a, b) for a, b in C["cards"]]
    ys, y = [], 230
    for c in cards:
        ys.append(y)
        y += c.height + 40
    xs = [30, 70, 40]
    bg = ImageEnhance.Brightness(cover_fit(shot, W, H)).enhance(0.62).filter(ImageFilter.GaussianBlur(1.2))
    n = round(3.6 * FPS)
    for i in range(n):
        fr = bg.convert("RGBA")
        for card, x, yy, st in zip(cards, xs, ys, [6, 33, 60]):
            if i < st:
                continue
            p = 1 - (1 - min((i - st) / 12.0, 1.0)) ** 2
            c = card if p >= 1 else card.copy()
            if p < 1:
                c.putalpha(card.getchannel("A").point(lambda v, p=p: int(v * p)))
            fr.alpha_composite(c, (x, yy + int((1 - p) * 18)))
        fr = add_wm(fr.convert("RGB"))
        emit(fr)
        if i == n - 6:
            chk["cards"] = fr
    for i, f in enumerate(clip_frames("after_clip.mp4", 5.7, C["after_start"])):
        fr = telop(f.copy(), C["after_telop"], 1110)
        if i < 40:
            fr = big_word(fr, "After", RED, 1.0 if i < 26 else (40 - i) / 14)
        fr = add_wm(fr)
        emit(fr)
        if i == 60:
            chk["after"] = fr
    end = make_end()
    for _ in range(round(1.5 * FPS)):
        emit(end)
    chk["end"] = end
    return 0.5 + 5.0 + 3.0  # カシャッの位置（秒）


# ---------- おきがえ ----------
def make_product():
    fr = Image.new("RGB", (W, H), (255, 255, 255))
    p = Image.open(os.path.join(D, "product.jpg")).convert("RGB")
    s = 600 / max(p.width, p.height)
    p = p.resize((round(p.width * s), round(p.height * s)), Image.LANCZOS)
    fr.paste(p, ((W - p.width) // 2, 300 + (600 - p.height) // 2))
    d = ImageDraw.Draw(fr)
    y = 1010
    for ln in C["product_name"].split("\n"):
        text_center(d, (W / 2, y), ln, fit_font(SANS_R, ln, W - 80, 28), (70, 70, 70))
        y += 42
    return add_wm(fr)


def build_okigae(emit, chk):
    cover = make_cover()
    for _ in range(round(0.5 * FPS)):
        emit(cover)
    chk["cover"] = cover
    last = None
    for i, f in enumerate(clip_frames("before_clip.mp4", 5.0, C["before_start"])):
        last = add_wm(f)
        emit(last)
        if i == 75:
            chk["before"] = last
    afters = clip_frames("after_clip.mp4", C["after_sec"], C["after_start"])
    first_after = add_wm(next(afters))
    white = Image.new("RGB", (W, H), (255, 255, 255))
    # カシャッ：白へフラッシュ（0.2秒）→ 白い線が左から右へ動き、後の姿を見せる（0.4秒）
    for k in range(6):
        emit(Image.blend(last, white, [0.5, 0.85, 1, 1, 1, 1][k]))
    for k in range(12):
        x = round(W * (k + 1) / 12)
        fr = white.copy()
        fr.paste(first_after.crop((0, 0, x, H)), (0, 0))
        d = ImageDraw.Draw(fr)
        d.rectangle([x - 5, 0, x + 5, H], fill=(255, 255, 255))
        d.rectangle([x - 7, 0, x - 5, H], fill=(210, 210, 210))
        emit(fr)
    emit(first_after)
    for i, f in enumerate(afters):
        fr = add_wm(f)
        emit(fr)
        if i == 70:
            chk["after"] = fr
    prod = make_product()
    for _ in range(round(2.0 * FPS)):
        emit(prod)
    chk["product"] = prod
    end = make_end(C["end_note"])
    for _ in range(round(1.5 * FPS)):
        emit(end)
    chk["end"] = end
    return 0.5 + 5.0  # カシャッの位置（秒）


def main():
    silent = os.path.join(D, "_video.mp4")
    p = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", silent], stdin=subprocess.PIPE)
    count = [0]

    def emit(fr):
        p.stdin.write(fr.convert("RGB").tobytes())
        count[0] += 1

    chk = {}
    shutter_at = build_okigae(emit, chk) if C["kind"] == "okigae" else build_v2(emit, chk)
    p.stdin.close()
    if p.wait():
        raise SystemExit("映像の書き出しに失敗しました")
    dur = count[0] / FPS
    ms = int(shutter_at * 1000)
    graph = (f"[2:a]aformat=channel_layouts=stereo,adelay={ms}|{ms},apad[sh];"
             f"[1:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,volume=0.85,"
             f"afade=t=in:st=0:d=0.6,afade=t=out:st={dur - 1.5:.3f}:d=1.5[bgm];"
             f"[bgm][sh]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=disabled[a]")
    out = os.path.join(D, "reel.mp4")
    if subprocess.call([FF, "-y", "-v", "error", "-i", silent, "-i", os.path.join(D, C["music"]), "-i", os.path.join(TOOLS, "shutter.wav"),
                        "-filter_complex", graph, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                        "-movflags", "+faststart", "-t", f"{dur:.3f}", out]):
        raise SystemExit("音声の合成に失敗しました")
    os.remove(silent)
    chk["cover"].save(os.path.join(D, "cover.jpg"), quality=92)
    for k, fr in chk.items():
        fr.save(os.path.join(D, f"frame-{k}.jpg"), quality=85)
    print(f"✓ {APP}: reel.mp4（{dur:.1f}秒）")


if __name__ == "__main__":
    main()
