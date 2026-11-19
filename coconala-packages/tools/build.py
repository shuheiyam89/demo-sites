# -*- coding: utf-8 -*-
"""ココナラ出品用の画像（見本・サムネイル）を、HTML を書いて Chrome のヘッドレスで撮って作る。
見本はすべて架空のお店（実在のお店・人の写真は使わない）。
使い方: python tools/build.py          （coconala-packages フォルダで実行）
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@600;800&family=Zen+Maru+Gothic:wght@500;700;900&'
         'family=Noto+Sans+JP:wght@400;700;900&family=Zen+Kaku+Gothic+New:wght@500;700;900&display=block" rel="stylesheet">')


def page(body, css, w, h):
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8">{FONTS}<style>'
            f'*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:{w}px;height:{h}px;overflow:hidden}}{css}</style></head>'
            f'<body>{body}</body></html>')


def shoot(rel_html, rel_png, w, h):
    src = os.path.join(HERE, rel_html)
    out = os.path.join(HERE, rel_png)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={w},{h}", "--virtual-time-budget=10000", f"--screenshot={out}",
                    "file:///" + src.replace("\\", "/")], check=True, capture_output=True)
    print("✓", rel_png)


def build(rel_html, rel_png, body, css, w, h):
    p = os.path.join(HERE, rel_html)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(page(body, css, w, h))
    shoot(rel_html, rel_png, w, h)


SAMPLE_NOTE = "※架空のお店で作った見本です"

# =====================================================================
# ① Instagram 投稿画像（架空のパン屋「麦とひだまり」）
# =====================================================================
IG_CSS = """
:root{--cream:#F7F0E4;--brown:#5E3F27;--orange:#D9822B;--green:#7C8B5B;--paper:#FFFBF4}
body{background:var(--cream);color:var(--brown);font-family:'Zen Maru Gothic',sans-serif;position:relative}
.min{font-family:'Shippori Mincho B1',serif}
.logo{position:absolute;right:56px;bottom:48px;display:flex;align-items:center;gap:14px;font-weight:700;font-size:30px}
.logo small{display:block;font-size:15px;letter-spacing:.3em;color:var(--orange)}
.note{position:absolute;left:56px;bottom:52px;font-size:18px;opacity:.55}
.tag{display:inline-block;background:var(--orange);color:#fff;font-weight:900;font-size:30px;padding:8px 26px;border-radius:999px;letter-spacing:.08em}
.frame{position:absolute;inset:28px;border:3px solid var(--brown);border-radius:36px;opacity:.18}
"""
WHEAT = ('<svg width="64" height="64" viewBox="0 0 64 64"><circle cx="32" cy="32" r="31" fill="#5E3F27"/>'
         '<path d="M32 50V18" stroke="#F7F0E4" stroke-width="3" stroke-linecap="round"/>'
         + "".join(f'<ellipse cx="{32 + s * 7}" cy="{y}" rx="4" ry="8" fill="#F2B45C" transform="rotate({s * 35} {32 + s * 7} {y})"/>'
                   for y in (22, 31, 40) for s in (-1, 1))
         + '<ellipse cx="32" cy="15" rx="4" ry="7" fill="#F2B45C"/></svg>')
LOGO = f'<div class="logo">{WHEAT}<div>麦とひだまり<small>BAKERY</small></div></div>'


def loaf(w=420, color="#C8803E", chunks=False):
    h = w * 0.62
    marks = "".join(f'<path d="M{w * x} {h * 0.22} q {w * 0.06} {h * 0.12} {w * 0.02} {h * 0.3}" stroke="#F3D4A2" stroke-width="{w * 0.025}" fill="none" stroke-linecap="round"/>'
                    for x in (0.3, 0.48, 0.66))
    ch = "".join(f'<rect x="{w * a}" y="{h * b}" width="{w * 0.07}" height="{w * 0.06}" rx="{w * 0.015}" fill="#8E4FA0" opacity=".85"/>'
                 for a, b in ((0.2, 0.55), (0.42, 0.62), (0.63, 0.5), (0.78, 0.66), (0.33, 0.78), (0.56, 0.8))) if chunks else ""
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><linearGradient id="g{w}{chunks}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{color}"/><stop offset="1" stop-color="#8A5126"/></linearGradient></defs>'
            f'<ellipse cx="{w / 2}" cy="{h * 0.95}" rx="{w * 0.46}" ry="{h * 0.05}" fill="#000" opacity=".08"/>'
            f'<rect x="{w * 0.04}" y="{h * 0.08}" width="{w * 0.92}" height="{h * 0.84}" rx="{h * 0.36}" fill="url(#g{w}{chunks})"/>'
            f'{marks}{ch}</svg>')


def croissant(w=300):
    h = w * 0.6
    parts = "".join(f'<ellipse cx="{w * x}" cy="{h * y}" rx="{w * rx}" ry="{h * 0.3}" fill="{c}" transform="rotate({r} {w * x} {h * y})"/>'
                    for x, y, rx, r, c in ((0.18, 0.62, 0.12, -35, "#B8702F"), (0.82, 0.62, 0.12, 35, "#B8702F"),
                                           (0.33, 0.5, 0.15, -18, "#D08E44"), (0.67, 0.5, 0.15, 18, "#D08E44"),
                                           (0.5, 0.45, 0.17, 0, "#E2A458")))
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">{parts}</svg>'


def round_bread(w=240, color="#D59A55"):
    return (f'<svg width="{w}" height="{w * 0.8}" viewBox="0 0 {w} {w * 0.8}"><ellipse cx="{w / 2}" cy="{w * 0.44}" rx="{w * 0.46}" ry="{w * 0.34}" fill="{color}"/>'
            f'<path d="M{w * 0.3} {w * 0.36} l{w * 0.4} {w * 0.12} M{w * 0.3} {w * 0.48} l{w * 0.4} -{w * 0.12}" stroke="#F6DDB0" stroke-width="{w * 0.03}" stroke-linecap="round"/></svg>')


IG_POSTS = [
    ("post-1-new", """<div class="frame"></div>
<div style="position:absolute;left:80px;top:96px"><span class="tag">NEW</span>
<p style="margin-top:34px;font-size:34px;font-weight:700;color:var(--green)">11月の新作</p>
<h1 class="min" style="font-size:118px;line-height:1.12;margin-top:10px">さつまいも<br>ブレッド</h1>
<p style="margin-top:30px;font-size:32px;line-height:1.7">ごろっと焼きいもを<br>もっちり生地で包みました</p></div>
<div style="position:absolute;right:60px;top:560px">""" + loaf(560, "#C98742", True) + """</div>
<div style="position:absolute;right:110px;top:410px;width:190px;height:190px;border-radius:50%;background:var(--orange);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(8deg)">
<span style="font-size:22px">1本</span><b style="font-size:54px;line-height:1">¥420</b><span style="font-size:18px">税込</span></div>"""),
    ("post-2-ranking", """<div class="frame"></div>
<div style="text-align:center;padding-top:92px"><p style="font-size:30px;letter-spacing:.3em;color:var(--orange);font-weight:700">RANKING</p>
<h1 class="min" style="font-size:86px;margin-top:6px">人気のパン TOP3</h1></div>
<div style="display:flex;justify-content:center;gap:34px;margin-top:120px">"""
     + "".join(f"""<div style="width:290px;height:500px;background:var(--paper);border-radius:32px;padding-top:40px;text-align:center;position:relative;{'margin-top:-30px;' if i == 0 else ''}box-shadow:0 10px 0 rgba(94,63,39,.08)">
<div style="position:absolute;left:-14px;top:-18px;width:76px;height:76px;border-radius:50%;background:{c};color:#fff;font-size:42px;font-weight:900;display:flex;align-items:center;justify-content:center">{i + 1}</div>
<div style="height:200px;display:flex;align-items:center;justify-content:center">{svg}</div>
<p class="min" style="font-size:38px;margin-top:20px">{name}</p><p style="font-size:26px;margin-top:10px;opacity:.7">{price}</p></div>"""
                for i, (c, svg, name, price) in enumerate((("#D9822B", croissant(230), "クロワッサン", "¥260"),
                                                            ("#7C8B5B", loaf(240), "山型食パン", "¥480"),
                                                            ("#A67B5B", round_bread(200), "塩バターパン", "¥180")))) + "</div>"),
    ("post-3-calendar", """<div class="frame"></div>
<div style="padding:92px 80px 0"><p style="font-size:30px;font-weight:700;color:var(--green)">お知らせ</p>
<h1 class="min" style="font-size:84px;margin-top:4px">12月の営業日</h1>
<div style="margin-top:44px;background:var(--paper);border-radius:32px;padding:36px 40px">
<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:10px;text-align:center;font-size:30px;font-weight:700">"""
     + "".join(f'<div style="padding:6px 0;color:{"#C0392B" if d == "日" else "var(--brown)"};opacity:.7;font-size:24px">{d}</div>' for d in "月火水木金土日")
     + '<div></div>' + "".join(f'<div style="height:66px;display:flex;align-items:center;justify-content:center;border-radius:50%;{"background:var(--orange);color:#fff;" if n in (7, 14, 21, 28, 30, 31) else ""}">{n}</div>' for n in range(1, 32))
     + """</div></div>
<p style="margin-top:30px;font-size:30px;display:flex;align-items:center;gap:14px"><span style="width:30px;height:30px;border-radius:50%;background:var(--orange);display:inline-block"></span>お休み　<span style="opacity:.75">毎週月曜と、年末年始（12/30〜1/3）はお休みです</span></p></div>"""),
    ("post-4-howto", """<div class="frame"></div>
<div style="padding:96px 80px 0"><p style="font-size:30px;font-weight:700;color:var(--orange)">おうちで、もっとおいしく</p>
<h1 class="min" style="font-size:84px;margin-top:4px;line-height:1.2">食パンの<br>トースト 3つのコツ</h1>
<ol style="list-style:none;margin-top:48px;display:grid;gap:22px">"""
     + "".join(f'<li style="display:flex;gap:26px;align-items:center;background:var(--paper);border-radius:26px;padding:26px 32px"><b style="flex:none;width:68px;height:68px;border-radius:50%;background:var(--green);color:#fff;font-size:36px;display:flex;align-items:center;justify-content:center">{i}</b><span style="font-size:34px;font-weight:700;line-height:1.45">{t}</span></li>'
               for i, t in ((1, "霧吹きで表面を軽く湿らせる"), (2, "トースターはしっかり予熱"), (3, "焼けたらすぐバターをのせる")))
     + "</ol></div>"),
    ("post-5-reserve", """<div class="frame"></div>
<div style="text-align:center;padding-top:110px"><span class="tag" style="background:var(--green)">お取り置き</span>
<h1 class="min" style="font-size:92px;line-height:1.25;margin-top:34px">前日までのご予約で<br>焼きたてを確実に</h1>
<p style="font-size:32px;margin-top:30px;opacity:.85">InstagramのDMで受け付けています</p></div>
<div style="display:flex;justify-content:center;gap:24px;margin-top:56px">"""
     + "".join(f'<div style="width:270px;background:var(--paper);border-radius:28px;padding:30px 20px;text-align:center"><b style="font-size:26px;color:var(--orange);letter-spacing:.15em">STEP {i}</b><p style="font-size:30px;font-weight:700;margin-top:12px;line-height:1.45">{t}</p></div>'
               for i, t in ((1, "DMで<br>パンと個数"), (2, "受け取りの<br>日時を送る"), (3, "お店で<br>お名前を")))
     + "</div>"),
]


def ig_posts():
    for name, body in IG_POSTS:
        build(f"01-instagram/src/{name}.html", f"01-instagram/{name}.png",
              body + LOGO + f'<div class="note">{SAMPLE_NOTE}</div>', IG_CSS, 1080, 1080)
    chips = (("ひだまりクリーム", "#F7F0E4", "背景"), ("こげ茶", "#5E3F27", "文字・ロゴ"), ("やきいろオレンジ", "#D9822B", "強調・値札"), ("麦のみどり", "#7C8B5B", "サブの強調"))
    rule = f"""<div style="padding:72px 72px 0">
<p style="font-size:26px;letter-spacing:.3em;color:var(--orange);font-weight:700">DESIGN RULE</p>
<h1 class="min" style="font-size:66px;margin-top:4px">色とフォントの統一ルール</h1>
<p style="font-size:26px;margin-top:14px;opacity:.75">この1枚があれば、次の投稿もお店の雰囲気のまま作れます</p>
<h2 style="font-size:30px;margin-top:46px">1. 色（この4色だけを使う）</h2>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:18px">""" + "".join(
        f'<div style="background:var(--paper);border-radius:22px;padding:16px"><div style="height:110px;border-radius:14px;background:{hx};border:2px solid rgba(94,63,39,.15)"></div><p style="font-size:22px;font-weight:700;margin-top:12px">{n}</p><p style="font-size:19px;opacity:.7">{hx}</p><p style="font-size:19px;opacity:.7">{u}</p></div>'
        for n, hx, u in chips) + """</div>
<h2 style="font-size:30px;margin-top:44px">2. フォント</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px">
<div style="background:var(--paper);border-radius:22px;padding:24px"><p class="min" style="font-size:56px">見出し</p><p style="font-size:22px;margin-top:8px;opacity:.75">しっぽり明朝 B1（太さ800）<br>パンの名前・タイトルに</p></div>
<div style="background:var(--paper);border-radius:22px;padding:24px"><p style="font-size:56px;font-weight:700">本文</p><p style="font-size:22px;margin-top:8px;opacity:.75">Zen 丸ゴシック（太さ500〜700）<br>説明・値段・お知らせに</p></div></div>
<h2 style="font-size:30px;margin-top:44px">3. レイアウト</h2>
<ul style="font-size:26px;line-height:1.9;margin-top:10px;padding-left:1.2em">
<li>ロゴはいつも右下。左下は「お知らせ」などの小さな文字だけ</li>
<li>外側から 80px は文字を置かない（スマホで切れないように）</li>
<li>1枚に伝えることは1つ。文字は3行まで</li>
<li>強調はオレンジを1か所だけ。値札は丸の中に</li></ul></div>"""
    build("01-instagram/src/style-rule.html", "01-instagram/style-rule.png",
          rule + LOGO + f'<div class="note">{SAMPLE_NOTE}</div>', IG_CSS + "body{background:var(--cream)}", 1080, 1350)


# =====================================================================
# ③ バナー3サイズ（架空の花屋「花と器 こより」）
# =====================================================================
BN_CSS = """
:root{--bg:#F3EEE6;--ink:#2F3B33;--red:#B8473A;--green:#4F6B4F;--gold:#B89650}
body{background:var(--bg);color:var(--ink);font-family:'Zen Kaku Gothic New',sans-serif;position:relative;overflow:hidden}
.min{font-family:'Shippori Mincho B1',serif}
.off{background:var(--red);color:#fff;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:900;line-height:1}
.note{position:absolute;font-size:16px;opacity:.5}
"""


def swag(w=520):
    h = w * 1.35
    leaves = []
    import math
    for i in range(22):
        a = -60 + i * 120 / 21
        r = h * (0.35 + (i % 4) * 0.08)
        cx = w / 2 + math.sin(math.radians(a)) * r * 0.55
        cy = h * 0.42 + math.cos(math.radians(a)) * r * 0.9
        col = ("#4F6B4F", "#6E8A64", "#93A884", "#3E5641")[i % 4]
        leaves.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{w * 0.05:.0f}" ry="{w * 0.16:.0f}" fill="{col}" transform="rotate({-a * 0.8:.0f} {cx:.0f} {cy:.0f})"/>')
        leaves.append(f'<path d="M{w / 2} {h * 0.42} L{cx:.0f} {cy:.0f}" stroke="#6B5A3E" stroke-width="3"/>')
    berries = "".join(f'<circle cx="{w / 2 + dx:.0f}" cy="{h * 0.62 + dy:.0f}" r="{w * 0.025:.0f}" fill="#B8473A"/>'
                      for dx, dy in ((-60, 20), (-40, 50), (-75, 60), (50, 30), (70, 65), (35, 75), (0, 90), (-15, 120), (20, 115)))
    cotton = "".join(f'<circle cx="{w / 2 + dx:.0f}" cy="{h * 0.55 + dy:.0f}" r="{w * 0.045:.0f}" fill="#FBF8F2"/>' for dx, dy in ((-90, 100), (95, 110), (0, 40)))
    ribbon = (f'<path d="M{w / 2} {h * 0.42} l-{w * 0.18} -{w * 0.08} v{w * 0.16} z M{w / 2} {h * 0.42} l{w * 0.18} -{w * 0.08} v{w * 0.16} z" fill="#C9A86A"/>'
              f'<path d="M{w / 2} {h * 0.42} l-{w * 0.08} {w * 0.4} M{w / 2} {h * 0.42} l{w * 0.1} {w * 0.38}" stroke="#C9A86A" stroke-width="{w * 0.03}" stroke-linecap="round"/>'
              f'<circle cx="{w / 2}" cy="{h * 0.42}" r="{w * 0.04}" fill="#B89650"/>')
    stems = "".join(f'<path d="M{w / 2} {h * 0.42} L{w / 2 + dx} {h * 0.06}" stroke="#7A6A4E" stroke-width="4"/>' for dx in (-30, -10, 12, 30))
    return f'<svg width="{w}" height="{h:.0f}" viewBox="0 0 {w} {h:.0f}" style="transform:rotate(180deg)">{stems}{"".join(leaves)}{berries}{cotton}{ribbon}</svg>'


def banner_body(kind):
    shop = '<p style="font-weight:700;letter-spacing:.2em">花と器 こより</p>'
    if kind == "square":
        return f"""<div style="position:absolute;right:-70px;top:150px">{swag(500)}</div>
<div style="position:absolute;left:84px;top:110px">{shop.replace('<p ', '<p style="font-size:30px" ', 1).replace('style="font-weight', 'data-x="').replace('<p style="font-size:30px" data-x="', '<p style="font-size:30px;font-weight')}
<p style="font-size:34px;margin-top:70px;color:var(--green);font-weight:700">冬のスワッグフェア</p>
<h1 class="min" style="font-size:112px;line-height:1.15;margin-top:12px">飾るだけで<br>冬じたく。</h1>
<p style="font-size:34px;margin-top:40px;line-height:1.6">11.22 SAT — 12.8 MON</p>
<div class="off" style="width:230px;height:230px;margin-top:40px"><span style="font-size:30px">全品</span><span style="font-size:92px">10<small style="font-size:44px">%</small></span><span style="font-size:36px">OFF</span></div></div>
<div class="note" style="left:84px;bottom:40px">{SAMPLE_NOTE}</div>"""
    if kind == "wide":
        return f"""<div style="position:absolute;right:60px;top:16px">{swag(440)}</div>
<div style="position:absolute;left:72px;top:64px">
<p style="font-size:26px;font-weight:700;letter-spacing:.2em">花と器 こより</p>
<p style="font-size:28px;margin-top:30px;color:var(--green);font-weight:700">冬のスワッグフェア</p>
<h1 class="min" style="font-size:84px;line-height:1.15;margin-top:6px">飾るだけで、<br>冬じたく。</h1>
<div style="display:flex;align-items:center;gap:34px;margin-top:34px">
<div class="off" style="width:170px;height:170px"><span style="font-size:24px">全品</span><span style="font-size:70px">10<small style="font-size:34px">%</small></span><span style="font-size:28px">OFF</span></div>
<p style="font-size:30px;line-height:1.6">11.22 SAT — 12.8 MON<br><span style="font-size:24px;opacity:.75">店頭・オンラインショップ</span></p></div></div>
<div class="note" style="left:72px;bottom:24px">{SAMPLE_NOTE}</div>"""
    return f"""<div style="position:absolute;left:50%;top:840px;transform:translateX(-50%)">{swag(520)}</div>
<div style="position:absolute;left:0;right:0;top:230px;text-align:center">
<p style="font-size:34px;font-weight:700;letter-spacing:.2em">花と器 こより</p>
<p style="font-size:40px;margin-top:70px;color:var(--green);font-weight:700">冬のスワッグフェア</p>
<h1 class="min" style="font-size:124px;line-height:1.2;margin-top:16px">飾るだけで<br>冬じたく。</h1>
<p style="font-size:40px;margin-top:40px">11.22 SAT — 12.8 MON</p></div>
<div class="off" style="position:absolute;right:70px;top:880px;width:230px;height:230px"><span style="font-size:32px">全品</span><span style="font-size:100px">10<small style="font-size:48px">%</small></span><span style="font-size:38px">OFF</span></div>
<div style="position:absolute;left:0;right:0;bottom:220px;text-align:center"><span style="display:inline-block;background:var(--ink);color:#fff;font-size:38px;font-weight:700;padding:22px 64px;border-radius:999px">オンラインショップを見る</span></div>
<div class="note" style="left:0;right:0;bottom:120px;text-align:center;font-size:22px">{SAMPLE_NOTE}</div>"""


def banners():
    for kind, w, h in (("square", 1080, 1080), ("wide", 1200, 628), ("story", 1080, 1920)):
        build(f"03-banner/src/banner-{w}x{h}.html", f"03-banner/banner-{w}x{h}.png", banner_body(kind), BN_CSS, w, h)


# =====================================================================
# サムネイル（3商品で同じ型。1220×1240）
# =====================================================================
TH_CSS = """
:root{--ink:#1F2A44;--accent:#FF7A45;--soft:#EEF2FA}
body{background:#fff;color:var(--ink);font-family:'Zen Kaku Gothic New',sans-serif;position:relative}
.band{background:var(--accent);color:#fff;font-weight:900;font-size:40px;text-align:center;padding:22px 0;letter-spacing:.06em}
h1{font-size:84px;line-height:1.22;font-weight:900;text-align:center;margin-top:44px}
h1 em{font-style:normal;color:var(--accent)}
.sub{text-align:center;font-size:34px;margin-top:18px;font-weight:700;opacity:.8}
.prev{margin:40px auto 0;width:1120px;height:520px;background:var(--soft);border-radius:36px;display:flex;align-items:center;justify-content:center;gap:22px;overflow:hidden}
.prev img{border-radius:16px;box-shadow:0 8px 24px rgba(31,42,68,.18);object-fit:cover}
.foot{position:absolute;left:50px;right:50px;bottom:34px;display:flex;align-items:flex-end;justify-content:space-between}
.price{font-size:96px;font-weight:900;line-height:1}
.price small{font-size:40px}
.was{font-size:32px;font-weight:700;opacity:.7;margin-bottom:8px}
.pills{display:flex;gap:14px}
.pills span{background:var(--ink);color:#fff;font-weight:700;font-size:34px;padding:14px 26px;border-radius:999px}
.own{text-align:center;font-size:26px;font-weight:700;opacity:.7;margin-top:20px}
"""


def thumb(folder, title_html, sub, preview, price, was, days):
    body = f"""<div class="band">実績づくり価格・先着3名さま</div>
<h1>{title_html}</h1><p class="sub">{sub}</p>
<div class="prev">{preview}</div>
<p class="own">本番稼働中のWebアプリ4本を自社で企画・運営しています</p>
<div class="foot"><div><p class="was">4人目からは {was}</p><p class="price">{price}<small>円</small></p></div>
<div class="pills"><span>納期{days}</span><span>修正2回</span></div></div>"""
    build(f"{folder}/src/thumbnail.html", f"{folder}/thumbnail.png", body, TH_CSS, 1220, 1240)


def thumbs():
    ig = "".join(f'<img src="../{n}.png" style="width:{s}px;height:{s}px">' for n, s in
                 (("post-2-ranking", 240), ("post-1-new", 330), ("post-5-reserve", 240)))
    thumb("01-instagram", "Instagram投稿画像<em>5枚</em><br>お店の色でそろえます",
          "文字入れ込み＋色とフォントの統一ルール付き", ig + '<img src="../style-rule.png" style="width:190px;height:238px">', "15,000", "25,000円", "3日")
    lp = ('<img src="../sample-lp-mobile.png" style="width:220px;height:470px;object-position:top">'
          '<img src="../sample-lp-pc.png" style="width:760px;height:428px;object-position:top">')
    thumb("02-lp", "スマホで見やすい<br><em>1ページLP</em>を公開まで",
          "構成案・文章のたたき台・問い合わせフォーム込み", lp, "30,000", "50,000円", "7日")
    bn = ('<img src="../banner-1080x1080.png" style="width:330px;height:330px">'
          '<img src="../banner-1200x628.png" style="width:480px;height:251px">'
          '<img src="../banner-1080x1920.png" style="width:236px;height:420px">')
    thumb("03-banner", "広告・SNS用<br>バナー<em>3サイズ</em>セット", "同じデザインで正方形・横長・縦長", bn, "15,000", "20,000円", "2日")


def lp_shots():
    shoot("02-lp/sample/index.html", "02-lp/sample-lp-pc.png", 1440, 900)
    # ページ全体：ページの外側を緑にした一時コピーを縦長で撮り、緑の部分を切り落とす
    src = os.path.join(HERE, "02-lp", "sample", "index.html")
    tmp = os.path.join(HERE, "02-lp", "sample", "_capture.html")
    html = open(src, encoding="utf-8").read().replace("html{background:#21324A}", "html{background:#00ff00}").replace("position:sticky", "position:relative").replace("<style>", "<style>html,body{width:390px}", 1)
    open(tmp, "w", encoding="utf-8").write(html)
    shoot("02-lp/sample/_capture.html", "02-lp/sample-lp-mobile-full.png", 600, 9000)
    os.remove(tmp)
    from PIL import Image
    p = os.path.join(HERE, "02-lp", "sample-lp-mobile-full.png")
    im = Image.open(p).convert("RGB")
    y = im.height
    while y > 1 and im.getpixel((5, y - 1)) == (0, 255, 0):
        y -= 1
    im.crop((0, 0, 390, y)).save(p)
    im.crop((0, 0, 390, 844)).save(os.path.join(HERE, "02-lp", "sample-lp-mobile.png"))   # スマホの1画面目
    print("  ページの高さ", y)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "ig"):
        ig_posts()
    if what in ("all", "banner"):
        banners()
    if what in ("all", "lp"):
        lp_shots()
    if what in ("all", "thumb"):
        thumbs()
