# -*- coding: utf-8 -*-
"""affiliate-humidifier（4L超音波加湿器 おまかせミスト／ブルーノ）の組み立て。「滑らか動画の標準」どおり。
構成: カバー0.5 + before 5.5（before-clip.mp4）+ after 6.5（after-clip.mp4）+ 商品カード4.0 + エンド3.0 = 19.5秒
1080x1920 / H.264 High / yuv420p / 30fps / AAC。テロップは白い丸い帯＋黒太字（下から330px）、PRバッジは全区間 118x68・右36px・上48px
音楽: "Peaceful Desolation" Kevin MacLeod (incompetech.com), CC BY 4.0
使い方: python build_humidifier.py   （このフォルダの素材を使う。途中のファイルは _work/ に作る）
"""
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
WK = os.path.join(D, "_work")
FF = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe")
W, H = 1080, 1920
FONT = "YuGothB.ttc"           # Muse 側の標準は Noto Sans CJK Bold。Windows にないので游ゴシック Bold で同じ大きさ・位置にする
FONT_R = "YuGothM.ttc"
LOCKUP = os.path.join(D, "..", "..", "..", "おかたずけアプリ", "public", "lockup.png")
INK = (25, 25, 25)
NORM = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30,format=yuv420p"

HOOK = ["冬の乾燥、", "肌も喉も限界"]
T1 = "朝起きると、喉がカラカラ…"
T2 = "ミストで、部屋がうるおう"
T3 = "4Lの大容量で、夜通し安心"
NAME = "4L超音波加湿器 おまかせミスト"
SUB = "（ブルーノ）"
PRICE = "6,930円"
RATING = "★4.56　レビュー118件"
ACCENT = (46, 120, 170)


def font(size, bold=True):
    return ImageFont.truetype(FONT if bold else FONT_R, size)


def pr_badge():
    img = Image.new("RGBA", (118, 68), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 2, 116, 66], radius=14, fill=(255, 255, 255, 235))
    d.text((59, 34), "PR", font=font(38), fill=(30, 30, 30, 255), anchor="mm")
    return img


def put_pr(img):
    img.alpha_composite(PR, (W - PR.width - 36, 48))


def make_telop(text, name):
    f = font(54)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = d.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 44, 26
    img = Image.new("RGBA", (tw + pad_x * 2, th + pad_y * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=(th + pad_y * 2) // 2, fill=(255, 255, 255, 242))
    d.text((pad_x - bbox[0], pad_y - bbox[1]), text, font=f, fill=INK + (255,))
    img.save(os.path.join(WK, name))


def cover_fit(src):
    s = max(W / src.width, H / src.height)
    src = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    x, y = (src.width - W) // 2, (src.height - H) // 2
    return src.crop((x, y, x + W, y + H))


def make_cover():
    img = cover_fit(Image.open(os.path.join(D, "before.jpg")).convert("RGB")).convert("RGBA")
    d = ImageDraw.Draw(img)
    f = font(96)
    ty = 620
    for line in HOOK:
        d.text((W // 2, ty), line, font=f, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0, 255), anchor="ma")
        ty += 128
    put_pr(img)
    img = img.convert("RGB")
    img.save(os.path.join(WK, "cover.png"))
    img.save(os.path.join(D, "affiliate-humidifier-cover.jpg"), quality=92)


def make_card():
    bg = cover_fit(Image.open(os.path.join(D, "after.jpg")).convert("RGB")).filter(ImageFilter.GaussianBlur(28))
    fr = Image.blend(bg, Image.new("RGB", (W, H), (246, 248, 250)), 0.45).convert("RGBA")
    d = ImageDraw.Draw(fr)
    x0, y0, x1, y1 = 90, 300, W - 90, 1560
    d.rounded_rectangle([x0 + 6, y0 + 12, x1 + 6, y1 + 12], radius=48, fill=(214, 220, 226, 255))
    d.rounded_rectangle([x0, y0, x1, y1], radius=48, fill=(255, 255, 255, 255))
    prod = Image.open(os.path.join(D, "product.jpg")).convert("RGB").resize((680, 680), Image.LANCZOS)
    fr.paste(prod, ((W - 680) // 2, y0 + 60))
    d = ImageDraw.Draw(fr)
    y = y0 + 60 + 680 + 70
    d.text((W / 2, y), NAME, font=font(56), fill=INK, anchor="mm")
    y += 66
    d.text((W / 2, y), SUB, font=font(36, False), fill=(110, 110, 110), anchor="mm")
    y += 104
    fp, fn = font(96), font(38)
    pw, nw = d.textlength(PRICE, font=fp), d.textlength("（投稿時点）", font=fn)
    px = (W - pw - nw) / 2
    d.text((px, y), PRICE, font=fp, fill=ACCENT, anchor="lm")
    d.text((px + pw + 4, y + 18), "（投稿時点）", font=fn, fill=(110, 110, 110), anchor="lm")
    y += 100
    d.text((W / 2, y), RATING, font=font(46), fill=(230, 160, 20), anchor="mm")
    d.text((W / 2, y1 - 44), "投稿時点の価格です（価格・在庫は変わることがあります）", font=font(30, False), fill=(140, 140, 140), anchor="mm")
    put_pr(fr)
    fr.convert("RGB").save(os.path.join(WK, "card.png"))


def make_end():
    fr = Image.new("RGBA", (W, H), (250, 246, 240, 255))
    d = ImageDraw.Draw(fr)
    lk = Image.open(LOCKUP).convert("RGBA")
    lk = lk.resize((640, round(lk.height * 640 / lk.width)), Image.LANCZOS)
    fr.alpha_composite(lk, ((W - lk.width) // 2, 560))
    y = 560 + lk.height + 150
    for ln in ("商品のリンクは", "プロフィールとストーリーズにあります"):
        d.text((W / 2, y), ln, font=font(56), fill=(40, 36, 32), anchor="mm")
        y += 84
    y += 60
    d.rounded_rectangle([W / 2 - 330, y - 52, W / 2 + 330, y + 52], radius=52, fill=(240, 120, 40))
    d.text((W / 2, y), "@okatazuke.onrender", font=font(50), fill=(255, 255, 255), anchor="mm")
    put_pr(fr)
    fr.convert("RGB").save(os.path.join(WK, "end.png"))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr[-3000:])
        sys.exit(1)


def still(png, sec, out):
    run([FF, "-y", "-v", "error", "-loop", "1", "-i", os.path.join(WK, png), "-t", str(sec), "-vf", "format=yuv420p", "-r", "30",
         "-c:v", "libx264", "-profile:v", "high", "-crf", "18", os.path.join(WK, out)])


if __name__ == "__main__":
    os.makedirs(WK, exist_ok=True)
    PR = pr_badge()
    PR.save(os.path.join(WK, "pr.png"))
    make_telop(T1, "telop1.png")
    make_telop(T2, "telop2.png")
    make_telop(T3, "telop3.png")
    make_cover()
    make_card()
    make_end()
    w = lambda n: os.path.join(WK, n)
    still("cover.png", 0.5, "seg_cover.mp4")
    run([FF, "-y", "-v", "error", "-i", os.path.join(D, "before-clip.mp4"), "-i", w("pr.png"), "-i", w("telop1.png"), "-filter_complex",
         f"[0:v]{NORM}[v];[v][1:v]overlay=W-w-36:48[a];[a][2:v]overlay=(W-w)/2:H-h-330:enable='between(t,0.3,5.5)'[out]",
         "-map", "[out]", "-t", "5.5", "-c:v", "libx264", "-profile:v", "high", "-crf", "18", w("seg_before.mp4")])
    run([FF, "-y", "-v", "error", "-i", os.path.join(D, "after-clip.mp4"), "-i", w("pr.png"), "-i", w("telop2.png"), "-i", w("telop3.png"), "-filter_complex",
         f"[0:v]{NORM}[v];[v][1:v]overlay=W-w-36:48[a];[a][2:v]overlay=(W-w)/2:H-h-330:enable='between(t,0.3,3.4)'[b];"
         f"[b][3:v]overlay=(W-w)/2:H-h-330:enable='between(t,3.4,6.5)'[out]",
         "-map", "[out]", "-t", "6.5", "-c:v", "libx264", "-profile:v", "high", "-crf", "18", w("seg_after.mp4")])
    still("card.png", 4.0, "seg_card.mp4")
    still("end.png", 3.0, "seg_end.mp4")
    with open(w("concat.txt"), "w", encoding="utf-8") as fh:
        for s in ["seg_cover", "seg_before", "seg_after", "seg_card", "seg_end"]:
            fh.write(f"file '{w(s + '.mp4')}'\n".replace("\\", "/"))
    run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", w("concat.txt"), "-c", "copy", w("video_only.mp4")])
    run([FF, "-y", "-v", "error", "-i", w("video_only.mp4"), "-i", os.path.join(D, "music.mp3"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-af", "afade=t=in:st=0:d=0.4,afade=t=out:st=18.0:d=1.5", "-c:a", "aac", "-b:a", "160k", "-t", "19.5", "-movflags", "+faststart",
         os.path.join(D, "affiliate-humidifier.mp4")])
    shutil.rmtree(WK)
    print("DONE")
