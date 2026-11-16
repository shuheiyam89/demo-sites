#!/usr/bin/env python3
"""おそうじ 宣伝リール（2026-11-17・v2形式）
cover 0.5 + before 5.0 + phone 3.0 + white 0.6 + result 3.6 + after 5.7 + end 1.5 = 19.9 秒
720x1280 / 30fps / H.264 High yuv420p / 音声は BGM（Carefree.mp3）＋カシャッ（合成）だけ

使い方: python build_1117.py   （このフォルダの素材を使い、osouji-reel-1117.mp4 と chk-*.jpg を書き出す）
必要: Python + Pillow、ffmpeg（PATH に無ければ WinGet のリンクを探す）
"""
import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "osouji-reel-1117.mp4")
W, H, FPS = 720, 1280, 30
TEAL = (31, 122, 153)
INK = (32, 48, 58)
RED = (214, 40, 40)

FF = shutil.which("ffmpeg") or os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe")


def font(names, size):
    """名前の候補から、最初に見つかったフォントを使う（Windows / Linux どちらでも動くように）"""
    dirs = [r"C:\Windows\Fonts", "/usr/share/fonts/opentype/noto", "/usr/share/fonts/truetype/dejavu"]
    for n in names:
        for d in dirs:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    raise SystemExit(f"フォントが見つかりません: {names}")


SANS = ["YuGothB.ttc", "BIZ-UDGothicB.ttc", "NotoSansCJK-Bold.ttc"]
SERIF = ["georgiab.ttf", "DejaVuSerif-Bold.ttf"]

before_img = Image.open(os.path.join(D, "before.png")).convert("RGB")
after_img = Image.open(os.path.join(D, "after.png")).convert("RGB")
lockup = Image.open(os.path.join(D, "lockup.png")).convert("RGBA")
icon = lockup.crop((0, 0, lockup.height, lockup.height))  # 左端の正方形がアイコン

# 透かし（左上・幅190px・不透明度65%）
wm = lockup.resize((190, round(190 * lockup.height / lockup.width)), Image.LANCZOS)
wm.putalpha(wm.getchannel("A").point(lambda v: int(v * 0.65)))


def cover_fit(img, w, h):
    """縦横比を保って w×h を埋めるように拡大し、中央で切り抜く"""
    s = max(w / img.width, h / img.height)
    r = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (r.width - w) // 2, (r.height - h) // 2
    return r.crop((x, y, x + w, y + h))


def zoom(img, z, cy=0.5):
    cw, ch = W / z, H / z
    x0 = (W - cw) / 2
    y0 = min(max(cy * H - ch / 2, 0), H - ch)
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)


def add_wm(fr):
    fr = fr.convert("RGBA")
    fr.alpha_composite(wm, (16, 16))
    return fr.convert("RGB")


def text_center(d, xy, s, f, fill, stroke=0, stroke_fill=None, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


def telop(fr, s, y, size=40):
    """白い角丸の帯に、濃い文字のテロップ"""
    d = ImageDraw.Draw(fr)
    f = font(SANS, size)
    tw = d.textlength(s, font=f)
    pad_x, h = 30, size + 34
    x0 = (W - tw) / 2 - pad_x
    d.rounded_rectangle([x0, y - h / 2, W - x0, y + h / 2], radius=h / 2, fill=(255, 255, 255))
    text_center(d, (W / 2, y), s, f, INK)
    return fr


def big_word(fr, word, color, alpha):
    """冒頭の大きなセリフ体の一言（Before / After）。alpha で消していく"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    text_center(d, (W / 2, H * 0.47), word, font(SERIF, 168), color + (255,), stroke=6, stroke_fill=(255, 255, 255, 255))
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    base = fr.convert("RGBA")
    base.alpha_composite(layer)
    return base.convert("RGB")


# ---------- 動きのクリップを 720x1280・30fps で1コマずつ読む（全部はメモリに載せない） ----------
def clip_frames(name, seconds):
    cmd = [FF, "-v", "error", "-i", os.path.join(D, name), "-t", str(seconds),
           "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    last = None
    for _ in range(round(seconds * FPS)):
        buf = p.stdout.read(n)
        if len(buf) == n:
            last = Image.frombytes("RGB", (W, H), buf)
        yield last
    p.stdout.close()
    p.wait()


# ---------- 1. カバー（前後を左右に並べる） ----------
def make_cover():
    fr = Image.new("RGB", (W, H))
    fr.paste(cover_fit(before_img, W // 2, H), (0, 0))
    fr.paste(cover_fit(after_img, W - W // 2, H), (W // 2, 0))
    d = ImageDraw.Draw(fr)
    d.rectangle([W // 2 - 3, 0, W // 2 + 3, H], fill=(255, 255, 255))
    f = font(SANS, 78)
    text_center(d, (W / 2, H * 0.5), "黒カビ→ピカピカ", f, (255, 255, 255), stroke=8, stroke_fill=INK)
    f2 = font(SANS, 34)
    text_center(d, (W * 0.25, H * 0.82), "Before", f2, (255, 255, 255), stroke=5, stroke_fill=INK)
    text_center(d, (W * 0.75, H * 0.82), "After", f2, (255, 255, 255), stroke=5, stroke_fill=INK)
    return add_wm(fr)


# ---------- 3. スマホで撮るカット ----------
def make_phone_scene():
    bg = ImageEnhance.Brightness(cover_fit(before_img, W, H).filter(ImageFilter.GaussianBlur(18))).enhance(0.7).convert("RGBA")
    pw, ph = 420, 840
    px, py = (W - pw) // 2, 150
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle([px + 10, py + 14, px + pw + 10, py + ph + 14], radius=62, fill=(0, 0, 0, 90))  # 影
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=62, fill=(21, 26, 31, 255))
    sx, sy, sw, sh = px + 16, py + 16, pw - 32, ph - 32
    screen = Image.new("RGBA", (sw, sh), (255, 255, 255, 255))
    band = 132
    shot = cover_fit(before_img, sw, sh - band)
    screen.paste(shot, (0, band))
    sd = ImageDraw.Draw(screen)
    ic = icon.resize((84, 84), Image.LANCZOS)
    screen.alpha_composite(ic, (26, (band - 84) // 2))
    sd.text((128, band // 2), "おそうじ", font=font(SANS, 50), fill=INK, anchor="lm")
    # 撮影ボタン（白い輪）
    cx, cy = sw // 2, sh - 70
    sd.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], outline=(255, 255, 255), width=7)
    sd.ellipse([cx - 27, cy - 27, cx + 27, cy + 27], fill=(255, 255, 255))
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw, sh], radius=48, fill=255)
    bg.paste(screen, (sx, sy), mask)
    d.rounded_rectangle([W // 2 - 50, py + 26, W // 2 + 50, py + 40], radius=7, fill=(21, 26, 31, 255))  # ノッチ
    return bg.convert("RGB")


# ---------- 5. 見立て結果のカード ----------
def wrap(d, s, f, maxw):
    """「 → 」の区切りで折り返す（言葉の途中では切らない）"""
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


def make_card(chip, text, cw=600):
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    ft = font(SANS, 34)
    lines = wrap(tmp, text, ft, cw - 56)
    ch = 92 + 46 * len(lines)
    card = Image.new("RGBA", (cw + 16, ch + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([8, 10, cw + 8, ch + 10], radius=28, fill=(0, 0, 0, 80))
    d.rounded_rectangle([0, 0, cw, ch], radius=28, fill=(255, 255, 255, 255))
    fc = font(SANS, 27)
    tw = d.textlength(chip, font=fc)
    d.rounded_rectangle([28, 24, 28 + tw + 32, 24 + 46], radius=23, fill=TEAL + (255,))
    d.text((28 + 16, 47), chip, font=fc, fill=(255, 255, 255), anchor="lm")
    for i, ln in enumerate(lines):
        d.text((28, 108 + 46 * i), ln, font=ft, fill=INK, anchor="lm")
    return card


CARDS = [
    (make_card("見立て", "洗面所の黒カビ・水アカ"), (36, 250)),
    (make_card("手順", "カビ取り剤を塗る → ラップで密閉 → 30分置いて流す"), (84, 520)),
    (make_card("使うもの", "カビ取り剤・ラップ・古歯ブラシ"), (46, 836)),
]
result_bg = ImageEnhance.Brightness(cover_fit(before_img, W, H)).enhance(0.62).filter(ImageFilter.GaussianBlur(1.2))
_rd = ImageDraw.Draw(result_bg)
_fn = font(SANS, 25)
_note = "塩素系の洗剤は混ぜない・換気して使ってください"
_tw = _rd.textlength(_note, font=_fn)
_rd.rounded_rectangle([(W - _tw) / 2 - 20, 1162, (W + _tw) / 2 + 20, 1210], radius=24, fill=(0, 0, 0))
text_center(_rd, (W / 2, 1186), _note, _fn, (255, 255, 255))


def result_frame(i):
    fr = result_bg.convert("RGBA")
    for (card, (x, y)), st in zip(CARDS, [6, 33, 60]):
        if i < st:
            continue
        p = min((i - st) / 12.0, 1.0)
        p = 1 - (1 - p) ** 2  # ゆっくり止まる
        c = card if p >= 1 else card.copy()
        if p < 1:
            c.putalpha(card.getchannel("A").point(lambda v: int(v * p)))
        fr.alpha_composite(c, (x, y + int((1 - p) * 18)))
    return add_wm(fr.convert("RGB"))


# ---------- 7. エンドカード ----------
def make_end():
    fr = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    lw = 540
    lk = lockup.resize((lw, round(lw * lockup.height / lockup.width)), Image.LANCZOS)
    fr.alpha_composite(lk, ((W - lw) // 2, 520))
    d = ImageDraw.Draw(fr)
    text_center(d, (W / 2, 520 + lk.height + 70), "osouji.onrender.com", font(SANS, 42), TEAL)
    return add_wm(fr.convert("RGB"))


# ---------- 組み立て ----------
CHK = {}


def build(emit):
    cover = make_cover()
    for _ in range(round(0.5 * FPS)):
        emit(cover)
    CHK["chk-cover.jpg"] = cover

    for i, f in enumerate(clip_frames("before-clip.mp4", 5.0)):
        fr = telop(f.copy(), "年末の大掃除、目地の黒カビが…", 200)
        if i < 40:
            fr = big_word(fr, "Before", (20, 20, 20), 1.0 if i < 26 else (40 - i) / 14)
        emit(add_wm(fr))

    phone = make_phone_scene()
    n = round(3.0 * FPS)
    last = None
    for i in range(n):
        fr = zoom(phone, 1.0 + 0.07 * i / (n - 1), cy=0.45)
        fr = telop(fr, "スマホで撮るだけ", 1120, 44)
        last = add_wm(fr)
        emit(last)

    white = Image.new("RGB", (W, H), (255, 255, 255))
    for i in range(round(0.6 * FPS)):
        emit(Image.blend(last, white, [0.35, 0.6, 0.85, 0.97][i]) if i < 4 else white)

    n = round(3.6 * FPS)
    for i in range(n):
        fr = result_frame(i)
        emit(fr)
        if i == n - 6:
            CHK["chk-cards.jpg"] = fr

    for i, f in enumerate(clip_frames("after-clip.mp4", 5.7)):
        fr = telop(f.copy(), "目地まで真っ白、気持ちいい", 1110)
        if i < 40:
            fr = big_word(fr, "After", RED, 1.0 if i < 26 else (40 - i) / 14)
        fr = add_wm(fr)
        emit(fr)
        if i == 12:
            CHK["chk-after.jpg"] = fr

    end = make_end()
    for _ in range(round(1.5 * FPS)):
        emit(end)


def main():
    if not os.path.exists(FF):
        raise SystemExit("ffmpeg が見つかりません")
    silent = os.path.join(D, "_video.mp4")
    cmd = [FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", silent]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    count = [0]

    def emit(fr):
        p.stdin.write(fr.convert("RGB").tobytes())
        count[0] += 1

    build(emit)
    p.stdin.close()
    if p.wait():
        raise SystemExit("映像の書き出しに失敗しました")
    dur = count[0] / FPS
    shutter_at = 0.5 + 5.0 + 3.0  # 白へフェードする瞬間
    print(f"映像: {count[0]} コマ = {dur:.2f} 秒", file=sys.stderr)

    # 音：BGM（頭0.6秒でフェードイン、最後1.5秒でフェードアウト）＋カシャッ（短いノイズ2発）
    shutter = (
        f"anoisesrc=d=0.05:c=white:a=0.9,highpass=f=1800,afade=t=out:st=0:d=0.05[s1];"
        f"anoisesrc=d=0.08:c=white:a=0.7,highpass=f=1200,afade=t=out:st=0:d=0.08,adelay=70|70[s2];"
        f"[s1][s2]amix=inputs=2:normalize=0,aformat=channel_layouts=stereo,adelay={int(shutter_at * 1000)}|{int(shutter_at * 1000)},apad[sh];"
    )
    graph = (
        shutter
        + f"[1:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,volume=0.85,"
        f"afade=t=in:st=0:d=0.6,afade=t=out:st={dur - 1.5:.3f}:d=1.5[bgm];"
        f"[bgm][sh]amix=inputs=2:duration=first:normalize=0[a]"
    )
    cmd = [FF, "-y", "-v", "error", "-i", silent, "-i", os.path.join(D, "Carefree.mp3"),
           "-filter_complex", graph, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", "-t", f"{dur:.3f}", OUT]
    if subprocess.call(cmd):
        raise SystemExit("音声の合成に失敗しました")
    os.remove(silent)
    for name, fr in CHK.items():
        fr.save(os.path.join(D, name), quality=88)
    print(f"完成: {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
