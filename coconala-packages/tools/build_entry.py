# -*- coding: utf-8 -*-
"""ココナラの「入口商品」3つ（04〜06）の見本とサムネイルを作る。2026-11-20 追加。
見本はすべて架空のお店。build.py の build()/TH_CSS を使う。
使い方: python tools/build_entry.py   （coconala-packages フォルダで実行）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import build, TH_CSS, SAMPLE_NOTE  # noqa: E402


def thumb2(folder, title_html, sub, preview, price, was, pills):
    body = f"""<div class="band">実績づくり価格・先着3名さま</div>
<h1>{title_html}</h1><p class="sub">{sub}</p>
<div class="prev">{preview}</div>
<p class="own">本番稼働中のWebアプリ4本を自社で企画・運営しています</p>
<div class="foot"><div><p class="was">4人目からは {was}</p><p class="price">{price}<small>円</small></p></div>
<div class="pills">{''.join(f'<span>{p}</span>' for p in pills)}</div></div>"""
    build(f"{folder}/src/thumbnail.html", f"{folder}/thumbnail.png", body, TH_CSS, 1220, 1240)


# =====================================================================
# ④ バナー3サイズ（入口価格）：③の見本をそのまま使う
# =====================================================================
def banner_entry():
    bn = ('<img src="../../03-banner/banner-1080x1080.png" style="width:330px;height:330px">'
          '<img src="../../03-banner/banner-1200x628.png" style="width:480px;height:251px">'
          '<img src="../../03-banner/banner-1080x1920.png" style="width:236px;height:420px">')
    thumb2("04-banner-entry", "告知バナー<em>3サイズ</em><br>まとめて5,000円", "インスタ投稿・ストーリーズ・Web広告に",
           bn, "5,000", "8,000円", ("納期2日", "修正1回"))


# =====================================================================
# ⑤ ホームページ改善レポート（架空のカフェ「山と珈琲 となり」）
# =====================================================================
RP_CSS = """
:root{--ink:#1F2A44;--accent:#FF7A45;--soft:#F3F5FA;--green:#2E8B57;--red:#D9534F;--line:#DCE1EC}
body{background:#fff;color:var(--ink);font-family:'Zen Kaku Gothic New',sans-serif;position:relative}
.hd{background:var(--ink);color:#fff;padding:40px 64px}
.hd p{font-size:24px;opacity:.75;letter-spacing:.1em}.hd h1{font-size:54px;margin-top:6px}
.wrap{padding:44px 64px}
h2{font-size:36px;margin:0 0 22px;display:flex;align-items:center;gap:14px}
h2 b{background:var(--accent);color:#fff;border-radius:12px;padding:4px 16px;font-size:28px}
.card{background:var(--soft);border-radius:24px;padding:28px 32px}
.note{position:absolute;left:64px;bottom:30px;font-size:18px;opacity:.5}
.pg{position:absolute;right:64px;bottom:30px;font-size:18px;opacity:.5}
"""


def bar(label, score, comment):
    col = "var(--green)" if score >= 4 else ("var(--accent)" if score == 3 else "var(--red)")
    return (f'<div style="display:grid;grid-template-columns:300px 1fr 70px;align-items:center;gap:20px;padding:16px 0;border-bottom:2px solid var(--line)">'
            f'<b style="font-size:28px">{label}</b><div><div style="height:22px;background:#E6EAF2;border-radius:99px"><div style="width:{score * 20}%;height:100%;background:{col};border-radius:99px"></div></div>'
            f'<p style="font-size:21px;margin-top:8px;opacity:.75">{comment}</p></div><b style="font-size:36px;color:{col};text-align:right">{score}<small style="font-size:20px">/5</small></b></div>')


def phone(inner, w=300, h=500):
    return (f'<div style="width:{w}px;height:{h}px;border:10px solid #1F2A44;border-radius:40px;overflow:hidden;background:#fff;position:relative">{inner}</div>')


BEFORE = phone("""<div style="height:44px;background:#fff;display:flex;align-items:center;padding:0 16px;font-size:15px;font-weight:700;border-bottom:1px solid #eee">山と珈琲 となり <span style="margin-left:auto">≡</span></div>
<div style="height:330px;background:linear-gradient(160deg,#8C6A4F,#4A3A2E);display:flex;align-items:flex-end;padding:16px;color:#fff;font-size:15px">WELCOME</div>
<div style="padding:14px;font-size:13px;line-height:1.7;color:#666">当店は2019年にオープンしました。店主が山歩きの途中で出会った…</div>""")
AFTER = phone("""<div style="height:44px;background:#fff;display:flex;align-items:center;padding:0 16px;font-size:15px;font-weight:700;border-bottom:1px solid #eee">山と珈琲 となり <span style="margin-left:auto;background:#FF7A45;color:#fff;border-radius:99px;padding:3px 10px;font-size:12px">予約</span></div>
<div style="height:200px;background:linear-gradient(160deg,#8C6A4F,#4A3A2E);padding:18px;color:#fff"><p style="font-size:13px;opacity:.85">駅から徒歩3分・自家焙煎</p><p style="font-size:24px;font-weight:900;line-height:1.35;margin-top:8px">山の朝みたいな<br>やさしい一杯を</p></div>
<div style="padding:14px"><div style="background:#FF7A45;color:#fff;font-weight:900;text-align:center;border-radius:12px;padding:14px;font-size:17px">席を予約する（30秒）</div>
<div style="display:flex;gap:8px;margin-top:10px;font-size:12px;text-align:center"><span style="flex:1;background:#F3F5FA;border-radius:8px;padding:8px">営業時間</span><span style="flex:1;background:#F3F5FA;border-radius:8px;padding:8px">メニュー</span><span style="flex:1;background:#F3F5FA;border-radius:8px;padding:8px">地図</span></div></div>""")


def report():
    head = '<div class="hd"><p>ホームページ改善レポート（見本）</p><h1>山と珈琲 となり 様</h1></div>'
    p1 = head + """<div class="wrap"><h2><b>1</b>5つの項目の点数</h2><div>""" + "".join((
        bar("スマホの見やすさ", 4, "文字の大きさは十分。ボタンが小さく押しにくい所が2か所"),
        bar("最初の画面で伝わるか", 2, "写真だけで、何のお店か・どこにあるかが分からない"),
        bar("予約・問い合わせまで", 2, "予約ボタンがページの一番下にしかない"),
        bar("検索に出やすいか", 3, "ページの題名が「HOME」。地名と業種が入っていない"),
        bar("表示の速さ", 3, "最初の写真が4MBあり、スマホで表示が遅い"),
    )) + """</div>
<h2 style="margin-top:40px"><b>2</b>先に直すと効果が大きい3つ</h2>
<div class="card" style="font-size:28px;line-height:1.8"><b>① 最初の画面に「何の店か・どこか」と予約ボタンを置く</b><br><b>② ページの題名を「〇〇駅のカフェ｜山と珈琲 となり」にする</b><br><b>③ 最初の写真を軽くする（4MB → 300KBほど）</b></div></div>
<p class="note">""" + SAMPLE_NOTE + "</p><p class=\"pg\">1 / 3</p>"
    build("05-hp-report/src/report-1.html", "05-hp-report/report-1.png", p1, RP_CSS, 1080, 1350)

    p2 = head + """<div class="wrap"><h2><b>①</b>最初の画面の直し方（イメージ）</h2>
<div style="display:flex;justify-content:center;gap:60px;align-items:flex-start">
<div style="text-align:center"><p style="font-size:30px;font-weight:900;color:var(--red);margin-bottom:14px">今</p>""" + BEFORE + """</div>
<div style="font-size:70px;color:var(--accent);margin-top:220px">→</div>
<div style="text-align:center"><p style="font-size:30px;font-weight:900;color:var(--green);margin-bottom:14px">直したあと</p>""" + AFTER + """</div></div>
<div class="card" style="margin-top:36px;font-size:26px;line-height:1.75">
<b>なぜ？</b> スマホで来た人は、最初の画面で「自分に関係あるか」を数秒で判断します。<br>
<b>どう直す？</b> 写真の上に「駅から徒歩3分・自家焙煎」と短い一言を重ね、予約ボタンを最初の画面に置きます。<br>
<b>手間：</b>小（文字とボタンの追加だけ。ホームページ作成サービスの編集画面で直せます）</div></div>
<p class="note">""" + SAMPLE_NOTE + "</p><p class=\"pg\">2 / 3</p>"
    build("05-hp-report/src/report-2.html", "05-hp-report/report-2.png", p2, RP_CSS, 1080, 1350)

    rows = (("トップ", "予約ボタンが一番下だけ", "上部とメニューにも置く", "大", "小"),
            ("トップ", "何の店か伝わらない", "写真に一言を重ねる", "大", "小"),
            ("全ページ", "題名が「HOME」", "地名＋業種＋店名に", "中", "小"),
            ("トップ", "写真が重い（4MB）", "圧縮して300KBほどに", "中", "小"),
            ("メニュー", "値段が画像の中だけ", "文字で書く（検索にも出る）", "中", "中"),
            ("アクセス", "地図がない", "Googleマップを埋め込む", "小", "小"),
            ("お問い合わせ", "入力欄が9個", "名前・連絡先・内容の3つに", "中", "中"))
    p3 = head + """<div class="wrap"><h2><b>3</b>直す所の一覧（優先順）</h2>
<table style="width:100%;border-collapse:collapse;font-size:24px">
<tr style="background:var(--ink);color:#fff"><th style="padding:14px;text-align:left">場所</th><th style="text-align:left">今の問題</th><th style="text-align:left">直し方</th><th>効果</th><th>手間</th></tr>""" + "".join(
        f'<tr style="border-bottom:2px solid var(--line);background:{"#fff" if i % 2 else "var(--soft)"}"><td style="padding:16px 14px;font-weight:700">{a}</td><td>{b}</td><td>{c}</td>'
        f'<td style="text-align:center;font-weight:900;color:{"var(--accent)" if d == "大" else "inherit"}">{d}</td><td style="text-align:center">{e}</td></tr>'
        for i, (a, b, c, d, e) in enumerate(rows)) + """</table>
<div class="card" style="margin-top:36px;font-size:26px;line-height:1.75"><b>おすすめの進め方</b><br>
上の4つは、どれも編集画面で1〜2時間ほどで直せます。まず4つを直して、1か月後に予約の数を比べてみてください。<br>
ご自分で直すのが難しい場合は、別のサービスで直す作業もお受けできます。</div></div>
<p class="note">""" + SAMPLE_NOTE + "</p><p class=\"pg\">3 / 3</p>"
    build("05-hp-report/src/report-3.html", "05-hp-report/report-3.png", p3, RP_CSS, 1080, 1350)

    pv = "".join(f'<img src="../report-{i}.png" style="width:{w}px;height:{w * 1.25:.0f}px">' for i, w in ((2, 300), (1, 380), (3, 300)))
    thumb2("05-hp-report", "ホームページの<br><em>改善点レポート</em>", "URLを送るだけ・電話や打ち合わせなし",
           pv, "3,000", "5,000円", ("納期3日", "PDFで納品"))


# =====================================================================
# ⑥ ブログ記事・コラム1本（架空の花屋「花と器 こより」）
# =====================================================================
BG_CSS = """
:root{--ink:#2F3B33;--green:#4F6B4F;--soft:#F3EEE6;--red:#B8473A;--line:#E2DBCF}
body{background:#fff;color:var(--ink);font-family:'Zen Kaku Gothic New',sans-serif;position:relative}
.top{display:flex;align-items:center;padding:26px 56px;border-bottom:2px solid var(--line);font-weight:700;font-size:26px;letter-spacing:.15em}
.wrap{padding:36px 56px}
.min{font-family:'Shippori Mincho B1',serif}
h2.s{font-size:38px;border-left:10px solid var(--green);padding-left:18px;margin:34px 0 18px}
p.t{font-size:27px;line-height:1.9}
.box{background:var(--soft);border-radius:22px;padding:24px 30px}
.note{position:absolute;left:56px;bottom:26px;font-size:18px;opacity:.5}
"""


def vase(w=360):
    stems = "".join(f'<path d="M{w / 2} {w * 0.95} Q{w / 2 + dx * 0.4} {w * 0.6} {w / 2 + dx} {w * 0.25}" stroke="#4F6B4F" stroke-width="5" fill="none"/>' for dx in (-110, -50, 0, 60, 120))
    flowers = "".join(f'<g transform="translate({w / 2 + dx} {w * 0.25 + dy})">' + "".join(f'<ellipse cx="0" cy="-16" rx="12" ry="20" fill="{c}" transform="rotate({a})"/>' for a in range(0, 360, 60)) + '<circle r="10" fill="#E8C35A"/></g>'
                      for dx, dy, c in ((-110, 10, "#E9A5A0"), (-50, -40, "#F4D6C8"), (0, 0, "#B8473A"), (60, -30, "#F4D6C8"), (120, 20, "#E9A5A0")))
    body = f'<path d="M{w * 0.36} {w * 0.85} h{w * 0.28} l{w * 0.04} {w * 0.55} q0 {w * 0.08} -{w * 0.08} {w * 0.08} h-{w * 0.2} q-{w * 0.08} 0 -{w * 0.08} -{w * 0.08} z" fill="#C9D4CB" opacity=".9"/>'
    return f'<svg width="{w}" height="{w * 1.5:.0f}" viewBox="0 0 {w} {w * 1.5:.0f}">{stems}{flowers}{body}</svg>'


def blog():
    top = '<div class="top">花と器 こより<span style="margin-left:auto;font-size:20px;opacity:.6;letter-spacing:0">コラム</span></div>'
    p1 = top + """<div class="wrap"><p style="font-size:22px;opacity:.6">2026年11月20日</p>
<h1 class="min" style="font-size:52px;line-height:1.4;margin-top:10px">切り花を長持ちさせる5つのコツ｜<br>買った日から始める水替えと切り戻し</h1>
<div style="display:flex;align-items:center;gap:40px;margin-top:26px;background:var(--soft);border-radius:24px;padding:20px 36px">""" + vase(250) + """
<p class="t" style="font-size:26px">せっかく選んだ花束、できるだけ長く楽しみたいですよね。切り花は、水の清潔さと茎の切り口で、もちが大きく変わります。この記事では、今日からできる5つのコツを紹介します。</p></div>
<div class="box" style="margin-top:28px"><p style="font-size:28px;font-weight:700">目次</p><ol style="font-size:25px;line-height:1.9;margin-top:6px;padding-left:1.4em">
<li>買ったらすぐ「水切り」をする</li><li>水は毎日替え、花瓶も洗う</li><li>水に浸かる葉は取る</li><li>置き場所は涼しい所に</li><li>2〜3日に一度「切り戻し」</li><li>よくある質問</li></ol></div></div>
<p class="note">""" + SAMPLE_NOTE + "（記事1本・約3,000字の冒頭）</p>"
    build("06-blog/src/article-1.html", "06-blog/article-1.png", p1, BG_CSS, 1080, 1350)

    p2 = top + """<div class="wrap" style="padding-top:10px"><h2 class="s">1. 買ったらすぐ「水切り」をする</h2>
<p class="t">茎の先は、持ち帰るあいだに乾いて、水を吸いにくくなっています。ボウルに水をはり、水の中で茎を斜めに1〜2cm切りましょう。切り口が空気にふれないので、水を吸い上げやすくなります。</p>
<h2 class="s">2. 水は毎日替え、花瓶も洗う</h2>
<p class="t">水がにごるのは、雑菌が増えているしるしです。雑菌は茎の切り口をふさぎ、花が早くしおれる原因になります。水は毎日替え、花瓶の内側もスポンジで洗うと、もちが変わります。</p>
<div class="box" style="margin-top:24px;font-size:25px;line-height:1.8"><b>ポイント</b>　水の量は、花瓶の3分の1ほどで十分です。多すぎると茎がいたみやすくなります。</div>
<h2 class="s">お店から</h2>
<p class="t">花と器 こよりでは、季節の花を1本からお選びいただけます。長持ちのコツも、お気軽にスタッフへお声がけください。</p></div>
<p class="note">""" + SAMPLE_NOTE + "（本文の一部）</p>"
    build("06-blog/src/article-2.html", "06-blog/article-2.png", p2, BG_CSS, 1080, 1350)

    pv = ''.join(f'<img src="../article-{i}.png" style="width:{w}px;height:{w * 1.25:.0f}px">' for i, w in ((1, 380), (2, 380)))
    thumb2("06-blog", "お店のブログ記事<br><em>1本</em>書きます", "検索で読まれやすい構成・約3,000字・見出し付き",
           pv, "4,000", "6,000円", ("納期3日", "修正1回"))


if __name__ == "__main__":
    banner_entry()
    report()
    blog()
