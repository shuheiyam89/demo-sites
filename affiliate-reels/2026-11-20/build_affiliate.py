# -*- coding: utf-8 -*-
"""アフィリエイト（商品紹介）リール 2026-11-20 を3本組み立てる（@okatazuke.onrender 向け）
1080x1920 / 30fps / H.264 High + yuv420p / 約19.5秒 / テロップのみ（ナレーションなし）
cover 0.5 → before 5.5（2ポーズを行き来）→ after 6.5（3ポーズをつなぐ）→ 商品カード 4.0 → エンドカード 3.0
人物の動き：同じ場面・同じ人物の少し違うポーズの画像（src/*-b1,b2 / *-a1,a2,a3）を、ゆっくりズームしながら重ねて切り替える
音楽：Kevin MacLeod（incompetech.com, CC BY 4.0）
使い方: python build_affiliate.py [warm|christmas|storage]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(D, "src")
W, H, FPS = 1080, 1920, 30
FF = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe")
INK = (40, 36, 32)
ORANGE = (240, 120, 40)
LOCKUP = os.path.join(D, "..", "..", "..", "おかたずけアプリ", "public", "lockup.png")

REELS = {
    "warm": dict(
        out="affiliate-warm", music="Carefree.mp3", prefix="warm", prod="prod-warm.jpg",
        hook="寒い夜のエアコン代、\nもったいない",
        before=["エアコンを強めても、まだ寒い…"],
        after=["羽織るだけで、ぬくぬく", "そのままソファでくつろげる"],
        name="着る毛布 グルーニー", sub="（ルームウェア）", price="3,490円", rating="4.5", reviews="46,927",
        accent=(214, 120, 70),
    ),
    "christmas": dict(
        out="affiliate-christmas", music="Jingle_Bells.mp3", prefix="xmas", prod="prod-christmas.jpg",
        hook="ツリーに巻くだけで\n一気にクリスマス",
        before=["ツリーはあるのに、なんだか地味…"],
        after=["巻いて点けるだけで、この雰囲気", "タイマー付きで、消し忘れにくい"],
        name="LEDツリーライト 12m", sub="（タイマー付き・1年保証）", price="1,480円", rating="4.58", reviews="618",
        accent=(196, 52, 52),
    ),
    "storage": dict(
        out="affiliate-storage", music="Bossa_Antigua.mp3", prefix="stor", prod="prod-storage.jpg",
        hook="衣類の山、\n5面開くボックスで解決",
        before=["衣類の山、どこにしまう…？"],
        after=["5面が開くから、出し入れしやすい", "キャスター付きで、そのまま移動"],
        name="収納ボックス", sub="木天板・キャスター付き", price="4,280円", rating="4.5", reviews="5,691",
        accent=(150, 110, 70),
    ),
}

_fonts = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _fonts:
        for n in (["YuGothB.ttc", "meiryob.ttc"] if bold else ["YuGothM.ttc", "meiryo.ttc"]):
            try:
                _fonts[key] = ImageFont.truetype(n, size)
                break
            except OSError:
                continue
    return _fonts[key]


def cover_fit(img, w=W, h=H):
    s = max(w / img.width, h / img.height)
    im = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def zoomed(img, z):
    """img は W x H より少し大きい元画像。z（1.0〜）で中心から拡大して W x H を切り出す"""
    cw, ch = img.width / z, img.height / z
    x0, y0 = (img.width - cw) / 2, (img.height - ch) / 2
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def load_scene(name):
    return cover_fit(Image.open(os.path.join(S, f"{name}.png")).convert("RGB"), int(W * 1.12), int(H * 1.12))


def pr_badge(d):
    f = font(30)
    d.rounded_rectangle([W - 120, 56, W - 40, 104], radius=10, fill=(255, 255, 255))
    d.text((W - 80, 80), "PR", font=f, fill=INK, anchor="mm")


def telop(fr, s, y=1580):
    d = ImageDraw.Draw(fr)
    f = font(54)
    tw = d.textlength(s, font=f)
    pad, h = 44, 108
    x0 = (W - tw) / 2 - pad
    d.rounded_rectangle([x0, y - h / 2, W - x0, y + h / 2], radius=h / 2, fill=(255, 255, 255))
    d.text((W / 2, y), s, font=f, fill=INK, anchor="mm")


def ease(t):
    return t * t * (3 - 2 * t)


def scene_frames(imgs, seconds, telops, z0, z1, hold_pattern):
    """imgs を hold_pattern（各ポーズの番号の並び）の順に、0.7秒の重ね合わせでつなぐ。ゆっくりズーム"""
    n = round(seconds * FPS)
    seg = n / len(hold_pattern)
    fade = int(0.7 * FPS)
    for i in range(n):
        k = min(int(i / seg), len(hold_pattern) - 1)
        a = imgs[hold_pattern[k]]
        into = i - k * seg
        z = z0 + (z1 - z0) * (i / max(1, n - 1))
        fr = zoomed(a, z)
        if k + 1 < len(hold_pattern) and into > seg - fade:
            t = ease((into - (seg - fade)) / fade)
            fr = Image.blend(fr, zoomed(imgs[hold_pattern[k + 1]], z), t)
        ti = min(int(i / (n / len(telops))), len(telops) - 1)
        telop(fr, telops[ti])
        pr_badge(ImageDraw.Draw(fr))
        yield fr


def make_cover(img, hook):
    fr = zoomed(img, 1.0)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rectangle([0, 0, W, H], fill=(0, 0, 0, 70))
    fr = Image.alpha_composite(fr.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(fr)
    f = font(92)
    lines = hook.split("\n")
    y = H * 0.40 - (len(lines) - 1) * 66
    for ln in lines:
        d.text((W / 2, y), ln, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=(30, 26, 22))
        y += 132
    pr_badge(d)
    return fr


def make_card(bg, cfg):
    fr = bg.filter(ImageFilter.GaussianBlur(28))
    fr = Image.blend(fr, Image.new("RGB", (W, H), (250, 246, 240)), 0.45)
    d = ImageDraw.Draw(fr)
    x0, y0, x1, y1 = 90, 300, W - 90, 1560
    d.rounded_rectangle([x0 + 6, y0 + 12, x1 + 6, y1 + 12], radius=48, fill=(222, 214, 204))
    d.rounded_rectangle([x0, y0, x1, y1], radius=48, fill=(255, 255, 255))
    prod = Image.open(os.path.join(S, cfg["prod"])).convert("RGB").resize((680, 680), Image.LANCZOS)
    fr.paste(prod, ((W - 680) // 2, y0 + 60))
    d = ImageDraw.Draw(fr)
    y = y0 + 60 + 680 + 70
    d.text((W / 2, y), cfg["name"], font=font(62), fill=INK, anchor="mm")
    y += 70
    d.text((W / 2, y), cfg["sub"], font=font(36, False), fill=(110, 104, 96), anchor="mm")
    y += 104
    f_price = font(96)
    f_note = font(38)
    pw = d.textlength(cfg["price"], font=f_price)
    nw = d.textlength("（投稿時点）", font=f_note)
    px = (W - pw - nw) / 2
    d.text((px, y), cfg["price"], font=f_price, fill=cfg["accent"], anchor="lm")
    d.text((px + pw + 4, y + 18), "（投稿時点）", font=f_note, fill=(110, 104, 96), anchor="lm")
    y += 100
    d.text((W / 2, y), f"★{cfg['rating']}　レビュー{cfg['reviews']}件", font=font(46), fill=(230, 160, 20), anchor="mm")
    d.text((W / 2, y1 - 44), "投稿時点の価格です（価格・在庫は変わることがあります）", font=font(30, False), fill=(140, 134, 126), anchor="mm")
    pr_badge(d)
    return fr


def make_end():
    fr = Image.new("RGB", (W, H), (250, 246, 240))
    d = ImageDraw.Draw(fr)
    try:
        lk = Image.open(LOCKUP).convert("RGBA")
        s = 640 / lk.width
        lk = lk.resize((640, round(lk.height * s)), Image.LANCZOS)
        fr.paste(lk, ((W - lk.width) // 2, 560), lk)
        y = 560 + lk.height + 150
    except OSError:
        y = 800
    for ln in ("商品のリンクは", "プロフィールとストーリーズにあります"):
        d.text((W / 2, y), ln, font=font(56), fill=INK, anchor="mm")
        y += 84
    y += 60
    d.rounded_rectangle([W / 2 - 330, y - 52, W / 2 + 330, y + 52], radius=52, fill=ORANGE)
    d.text((W / 2, y), "@okatazuke.onrender", font=font(50), fill=(255, 255, 255), anchor="mm")
    pr_badge(d)
    return fr


def build(key):
    cfg = REELS[key]
    p = cfg["prefix"]
    b = [load_scene(f"{p}-b1"), load_scene(f"{p}-b2")]
    a = [load_scene(f"{p}-a1"), load_scene(f"{p}-a2"), load_scene(f"{p}-a3")]
    silent = os.path.join(D, f"_{key}_video.mp4")
    enc = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "19", silent],
                           stdin=subprocess.PIPE)
    count = [0]

    def emit(fr):
        enc.stdin.write(fr.tobytes())
        count[0] += 1

    cover = make_cover(b[0], cfg["hook"])
    for _ in range(round(0.5 * FPS)):
        emit(cover)
    chk = {}
    for i, fr in enumerate(scene_frames(b, 5.5, cfg["before"], 1.0, 1.05, [0, 1, 0])):
        emit(fr)
        if i == 60:
            chk["before"] = fr
    last = None
    for i, fr in enumerate(scene_frames(a, 6.5, cfg["after"], 1.0, 1.06, [0, 1, 2])):
        emit(fr)
        last = fr
        if i == 70:
            chk["after"] = fr
    chk["after-end"] = last
    card = make_card(zoomed(a[2], 1.06), cfg)
    for _ in range(round(4.0 * FPS)):
        emit(card)
    chk["card"] = card
    end = make_end()
    for _ in range(round(3.0 * FPS)):
        emit(end)
    chk["end"] = end
    enc.stdin.close()
    enc.wait()
    dur = count[0] / FPS
    out = os.path.join(D, cfg["out"] + ".mp4")
    af = f"atrim=0:{dur:.2f},afade=t=in:st=0:d=0.4,afade=t=out:st={dur - 1.5:.2f}:d=1.5,volume=0.85"
    subprocess.run([FF, "-y", "-v", "error", "-i", silent, "-i", os.path.join(S, cfg["music"]), "-filter:a", af,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(silent)
    cover.save(os.path.join(D, cfg["out"] + "-cover.jpg"), quality=92)
    for k, fr in chk.items():
        fr.resize((540, 960)).save(os.path.join(S, f"chk-{key}-{k}.jpg"), quality=85)
    print(f"✓ {cfg['out']}.mp4（{dur:.1f}秒）")


if __name__ == "__main__":
    for k in (sys.argv[1:] or REELS):
        build(k)
