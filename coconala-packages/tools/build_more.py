# -*- coding: utf-8 -*-
"""ココナラの入口商品 09〜14 の見本とサムネイルを作る。2026-11-20 追加。
見本はすべて架空のお店・物件。build.py / build_entry.py の部品を使う。
使い方: PYTHONIOENCODING=utf-8 python tools/build_more.py [sheet|flyer|cal|rewrite|estate|reel]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import build, SAMPLE_NOTE  # noqa: E402
from build_entry import thumb2, RP_CSS  # noqa: E402

CSS = RP_CSS + """
.post{background:#fff;border:2px solid var(--line);border-radius:20px;padding:18px 22px}
.chip{display:inline-block;background:var(--soft);border-radius:99px;padding:2px 14px;font-size:20px;font-weight:700}
"""


def head(kind, name):
    return f'<div class="hd"><p>{kind}（見本）</p><h1>{name}</h1></div>'


def foot(page=""):
    return f'<p class="note">{SAMPLE_NOTE}</p>' + (f'<p class="pg">{page}</p>' if page else "")


def two(folder):
    return "".join(f'<img src="../sample-{i}.png" style="width:380px;height:475px">' for i in (1, 2))


# ⑨ スプレッドシート・Excel
def sheet():
    rows = (("11/1", "ブレンド豆", "2", "1,600"), ("11/1", "ホットサンド", "3", "2,250"), ("11/2", "ブレンド豆", "1", "800"),
            ("11/2", "カフェラテ", "4", "2,200"), ("11/3", "ホットサンド", "2", "1,500"))
    tbl = lambda extra="": ('<table style="width:100%;border-collapse:collapse;font-size:22px;background:#fff">'
                            '<tr style="background:#E8F0E8"><th style="padding:8px">日付</th><th>商品</th><th>数</th><th>売上</th></tr>'
                            + "".join(f'<tr style="border-bottom:1px solid #ddd"><td style="padding:8px">{a}</td><td>{b}</td><td style="text-align:right">{c}</td><td style="text-align:right;padding-right:10px">{d}</td></tr>' for a, b, c, d in rows)
                            + extra + '</table>')
    p1 = head("スプレッドシート自動化", "山と珈琲 となり 様") + """<div class="wrap">
<h2><b>今</b>毎日の売上を手で足し算している</h2>""" + tbl() + """
<p style="font-size:24px;margin:14px 0 0;color:var(--red);font-weight:700">→ 月末に電卓で商品ごとに集計。1時間以上かかり、まちがいも出る</p>
<h2 style="margin-top:36px"><b>後</b>入力するだけで、集計表が自動で埋まる</h2>
<table style="width:100%;border-collapse:collapse;font-size:24px;background:#fff">
<tr style="background:var(--ink);color:#fff"><th style="padding:10px;text-align:left">商品</th><th>今月の数</th><th>今月の売上</th></tr>
<tr style="border-bottom:1px solid #ddd"><td style="padding:10px">ブレンド豆</td><td style="text-align:center">3</td><td style="text-align:right;padding-right:14px">2,400</td></tr>
<tr style="border-bottom:1px solid #ddd"><td style="padding:10px">ホットサンド</td><td style="text-align:center">5</td><td style="text-align:right;padding-right:14px">3,750</td></tr>
<tr><td style="padding:10px">カフェラテ</td><td style="text-align:center">4</td><td style="text-align:right;padding-right:14px">2,200</td></tr></table>
<div class="card" style="margin-top:20px;font-family:monospace;font-size:22px">=SUMIFS(売上!D:D, 売上!B:B, A2, 売上!A:A, "&gt;="&amp;$F$1)</div>
<p style="font-size:22px;margin-top:10px;opacity:.75">式には、何をしているかの説明を日本語で付けてお渡しします</p></div>""" + foot("1 / 2")
    build("09-sheet/src/sample-1.html", "09-sheet/sample-1.png", p1, CSS, 1080, 1350)
    items = (("集計・計算", "売上・在庫・勤怠を、入力するだけで自動集計"), ("見やすく", "期限切れを赤く・合計行・並べ替え・プルダウン"),
             ("転記をなくす", "フォームの回答を、決まった表へ自動でまとめる"), ("自動で知らせる", "毎朝、在庫が少ない商品をメールで知らせる（GAS）"),
             ("データの整理", "名簿の重複を消す・全角半角をそろえる"), ("グラフ", "月ごとの売上を自動でグラフに"))
    p2 = head("スプレッドシート自動化", "こんなことができます") + '<div class="wrap"><div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">' + "".join(
        f'<div class="post"><span class="chip">{t}</span><p style="font-size:25px;line-height:1.6;margin-top:10px">{x}</p></div>' for t, x in items) + """</div>
<div class="card" style="margin-top:28px;font-size:25px;line-height:1.8"><b>お届けの形</b><br>・作った表（コピー）と、使い方のメモ<br>・式やプログラムには、日本語の説明を付けます<br>・Googleスプレッドシート／Excel のどちらでも</div></div>""" + foot("2 / 2")
    build("09-sheet/src/sample-2.html", "09-sheet/sample-2.png", p2, CSS, 1080, 1350)
    thumb2("09-sheet", "スプレッドシート・Excel<br>の<em>面倒な作業を自動化</em>", "関数・集計・GAS 1つから・電話なし",
           two("09-sheet"), "3,000", "5,000円", ("納期2日", "修正1回"))


# ⑩ チラシ・メニュー表（架空のパン屋「麦とひだまり」）
FLY_CSS = """
:root{--cream:#F7F0E4;--brown:#5E3F27;--orange:#D9822B;--green:#7C8B5B;--paper:#FFFBF4}
body{background:var(--cream);color:var(--brown);font-family:'Zen Maru Gothic',sans-serif;position:relative}
.min{font-family:'Shippori Mincho B1',serif}
.note{position:absolute;left:80px;bottom:56px;font-size:20px;opacity:.55}
"""


def flyer():
    from build import loaf, croissant, round_bread, LOGO
    p1 = """<div style="position:absolute;inset:36px;border:4px solid var(--brown);border-radius:40px;opacity:.2"></div>
<div style="text-align:center;padding-top:110px"><p style="font-size:40px;font-weight:700;color:var(--orange);letter-spacing:.2em">GRAND OPEN 1st ANNIVERSARY</p>
<h1 class="min" style="font-size:150px;line-height:1.15;margin-top:30px">1周年<br>ありがとう祭</h1>
<p style="font-size:52px;font-weight:700;margin-top:40px">12.6 SAT — 12.8 MON</p></div>
<div style="display:flex;justify-content:center;align-items:flex-end;gap:40px;margin-top:70px">""" + croissant(330) + loaf(460, "#C98742", True) + round_bread(260) + """</div>
<div style="display:flex;justify-content:center;gap:36px;margin-top:80px">""" + "".join(
        f'<div style="width:300px;background:var(--paper);border-radius:30px;padding:36px 20px;text-align:center"><b style="font-size:34px;color:var(--orange)">{a}</b><p style="font-size:38px;font-weight:700;margin-top:12px;line-height:1.4">{b}</p></div>'
        for a, b in (("その1", "食パン<br>全品10%OFF"), ("その2", "先着50名に<br>ミニラスク"), ("その3", "スタンプ<br>2倍"))) + """</div>
<p style="text-align:center;font-size:32px;margin-top:70px;line-height:1.7">〇〇駅 東口 徒歩5分 ／ 7:00〜18:00（月曜定休）</p>""" + LOGO.replace("bottom:48px", "bottom:60px") + f'<div class="note">{SAMPLE_NOTE}</div>'
    build("10-flyer/src/sample-1.html", "10-flyer/sample-1.png", p1, FLY_CSS + ".logo{position:absolute;right:70px;bottom:60px;display:flex;align-items:center;gap:14px;font-weight:700;font-size:30px}.logo small{display:block;font-size:15px;letter-spacing:.3em;color:var(--orange)}", 1240, 1754)
    menu = (("食パン", (("山型食パン", "480"), ("角食パン", "450"), ("さつまいもブレッド", "420"))),
            ("おかずパン", (("カレーパン", "260"), ("ベーコンエピ", "300"), ("たまごサンド", "350"))),
            ("甘いパン", (("クロワッサン", "260"), ("あんバター", "280"), ("シナモンロール", "290"))))
    p2 = """<div style="padding:110px 110px 0"><p style="font-size:34px;letter-spacing:.3em;color:var(--orange);font-weight:700">MENU</p>
<h1 class="min" style="font-size:110px;margin-top:6px">パンのメニュー</h1>""" + "".join(
        f'<h2 style="font-size:46px;margin-top:64px;border-bottom:4px solid var(--brown);padding-bottom:10px">{cat}</h2>'
        + "".join(f'<div style="display:flex;font-size:42px;margin-top:26px"><span>{n}</span><span style="flex:1;border-bottom:3px dotted rgba(94,63,39,.4);margin:0 18px 14px"></span><b>¥{p}</b></div>' for n, p in items)
        for cat, items in menu) + """<p style="font-size:30px;margin-top:60px;opacity:.75">価格はすべて税込です。焼き上がり時間は店頭でご確認ください。</p></div>""" + f'<div class="note">{SAMPLE_NOTE}</div>'
    build("10-flyer/src/sample-2.html", "10-flyer/sample-2.png", p2, FLY_CSS, 1240, 1754)
    pv = "".join(f'<img src="../sample-{i}.png" style="width:330px;height:467px">' for i in (1, 2))
    thumb2("10-flyer", "<em>チラシ・メニュー表</em><br>1枚デザインします", "印刷用PDF＋SNS用画像つき・A4/B5",
           pv, "5,000", "8,000円", ("納期3日", "修正1回"))


# ⑪ Instagram投稿ネタ30日分
def cal():
    topics = ["新作紹介", "店内の様子", "スタッフのおすすめ", "焼き上がり時間", "お客さまの質問に答える", "定休日のお知らせ", "豆知識",
              "人気TOP3", "季節の素材", "作り方の裏側", "予約のしかた", "保存のコツ", "セットのおすすめ", "週末の予定",
              "ラッピング", "朝の仕込み", "限定メニュー", "よくある質問", "道案内", "おうちで楽しむコツ", "スタンプカード",
              "材料のこだわり", "雨の日のお知らせ", "ギフト向け", "新作の試作", "月末のふりかえり", "お店の歴史", "来月の予告", "感謝の投稿", "まとめ"]
    p1 = head("Instagram投稿ネタ30日分", "麦とひだまり 様（12月）") + '<div class="wrap" style="padding-top:30px"><div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px">' + "".join(
        f'<div style="background:{"#FFF3EC" if i % 7 in (5, 6) else "var(--soft)"};border-radius:14px;padding:10px 10px 12px;min-height:150px"><b style="font-size:22px;color:var(--accent)">{i + 1}</b><p style="font-size:20px;line-height:1.45;margin-top:4px;font-weight:700">{t}</p></div>'
        for i, t in enumerate(topics)) + "</div></div>" + foot("1 / 2")
    build("11-ig-calendar/src/sample-1.html", "11-ig-calendar/sample-1.png", p1, CSS, 1080, 1350)
    caps = (("1日・新作紹介", "12月の新作は「りんごとくるみのカンパーニュ」。甘く煮たりんごを、香ばしいくるみと一緒に焼き込みました。薄く切って、トーストするのがおすすめです。", "#麦とひだまり #〇〇駅パン屋 #カンパーニュ"),
            ("4日・焼き上がり時間", "よく聞かれる焼き上がり時間をまとめました。食パンは8時と11時、クロワッサンは9時ごろです。お取り置きはDMでどうぞ。", "#〇〇駅パン屋 #焼きたてパン"),
            ("12日・保存のコツ", "食パンが余ったら、1枚ずつラップして冷凍に。凍ったままトースターで焼くと、もっちり感が戻ります。", "#パンの保存 #食パン"))
    p2 = head("Instagram投稿ネタ30日分", "投稿文の例（30日分）") + '<div class="wrap"><div style="display:grid;gap:20px">' + "".join(
        f'<div class="post"><span class="chip">{t}</span><p style="font-size:25px;line-height:1.75;margin-top:10px">{x}</p><p style="font-size:21px;color:#3B6FB6;margin-top:8px">{h}</p></div>' for t, x, h in caps) + """</div>
<div class="card" style="margin-top:26px;font-size:24px;line-height:1.8">・1日1つのテーマと、そのまま使える投稿文<br>・写真の撮り方のひとこと（何をどう撮るか）<br>・スプレッドシートで納品。コピーして貼るだけ</div></div>""" + foot("2 / 2")
    build("11-ig-calendar/src/sample-2.html", "11-ig-calendar/sample-2.png", p2, CSS, 1080, 1350)
    thumb2("11-ig-calendar", "Instagram投稿ネタ<br><em>30日分</em>まとめて作ります", "テーマ＋投稿文＋撮り方メモ・毎日のネタ探しを楽に",
           two("11-ig-calendar"), "3,000", "5,000円", ("納期3日", "修正1回"))


# ⑫ ホームページの文章の書き直し（架空のハウスクリーニング「きらり清掃」）
def rewrite():
    p1 = head("ホームページの文章の書き直し", "きらり清掃 様（トップページ）") + """<div class="wrap">
<h2><b>前</b>今の文章</h2><div class="card" style="font-size:25px;line-height:1.85;color:#666">当社は2015年創業以来、地域の皆様に支えられ、お客様第一をモットーに、高品質なサービスを提供してまいりました。スタッフ一同、誠心誠意努めてまいりますので、何卒よろしくお願い申し上げます。</div>
<p style="font-size:23px;color:var(--red);font-weight:700;margin-top:12px">→ 何をしてくれる会社か、いくらか、どこまで来てくれるかが分からない</p>
<h2 style="margin-top:34px"><b>後</b>書き直した文章</h2><div class="card" style="font-size:26px;line-height:1.85;background:#FFF6F1">
<b style="font-size:34px">エアコン・お風呂・キッチンの掃除を、<br>〇〇市内なら最短翌日にうかがいます。</b><br><br>
エアコン1台 9,800円から。作業前に見積もりをお伝えし、追加料金がかかる場合は、必ず作業の前にご相談します。<br>
女性スタッフの指名もできます。<br><br><span style="background:var(--accent);color:#fff;border-radius:10px;padding:8px 18px;font-weight:900">空いている日を見る</span></div></div>""" + foot("1 / 2")
    build("12-rewrite/src/sample-1.html", "12-rewrite/sample-1.png", p1, CSS, 1080, 1350)
    pts = (("1文目で「何を・どこで」", "読む人がいちばん知りたいことを先に書きます"), ("値段と範囲を書く", "「〇円から」「〇〇市内」があると、問い合わせの不安が減ります"),
           ("不安への答えを入れる", "追加料金・スタッフなど、聞かれることを先回りして書きます"), ("行動を1つに決める", "最後のボタンは1つ。「何をすればいいか」を迷わせません"),
           ("盛らない", "「地域No.1」など根拠のない言葉は使いません"))
    p2 = head("ホームページの文章の書き直し", "書き直しの考え方") + '<div class="wrap"><div style="display:grid;gap:16px">' + "".join(
        f'<div class="post"><span class="chip">{i + 1}. {t}</span><p style="font-size:25px;line-height:1.6;margin-top:8px">{x}</p></div>' for i, (t, x) in enumerate(pts)) + """</div>
<div class="card" style="margin-top:24px;font-size:24px;line-height:1.8">・1ページ分（約1,500字まで）を書き直します<br>・見出し・本文・ボタンの文言まで。変えた理由のメモ付き</div></div>""" + foot("2 / 2")
    build("12-rewrite/src/sample-2.html", "12-rewrite/sample-2.png", p2, CSS, 1080, 1350)
    thumb2("12-rewrite", "ホームページの<br><em>文章を書き直します</em>", "伝わらない文章を、問い合わせにつながる文章に・1ページ",
           two("12-rewrite"), "4,000", "6,000円", ("納期3日", "修正1回"))


# ⑬ 不動産の物件紹介文（架空の物件）
def estate():
    props = (("〇〇駅 徒歩6分・1K・25㎡", "南向きの明るいお部屋です。バス・トイレ別、独立洗面台つき。駅までの道は商店街を通るので、夜も明るく歩けます。2階の角部屋で、窓が2面あります。", ("一人暮らし", "バス・トイレ別", "角部屋")),
             ("〇〇駅 徒歩12分・2LDK・58㎡", "リビングと続く6畳の洋室は、扉を開ければ広い一つの空間として使えます。徒歩3分にスーパー、7分に小学校があります。駐車場1台分あり（月額8,000円）。", ("ファミリー", "駐車場あり", "スーパー近く")),
             ("〇〇駅 徒歩4分・店舗・32㎡", "大通りに面した1階の店舗区画です。前面ガラスで、通りから店内がよく見えます。飲食店の相談可（重飲食は要相談）。", ("1階路面", "飲食相談可", "駅近")))
    p1 = head("不動産の物件紹介文", "架空の物件 3件") + '<div class="wrap"><div style="display:grid;gap:22px">' + "".join(
        f'<div class="post"><b style="font-size:29px">{t}</b><p style="font-size:24px;line-height:1.75;margin-top:10px">{x}</p><p style="margin-top:10px">' + " ".join(f'<span class="chip">{c}</span>' for c in cs) + "</p></div>"
        for t, x, cs in props) + "</div></div>" + foot("1 / 2")
    build("13-estate/src/sample-1.html", "13-estate/sample-1.png", p1, CSS, 1080, 1350)
    pts = ("1件ごとに、長い紹介文（200字ほど）と、ポータル用の短い文（60字ほど）",
           "誰に向いた部屋かを先に書き、その人が気にすること（駅・買い物・学校）を入れる",
           "「最高」「格安」「日本一」など、不動産の広告で使えない言葉は使わない",
           "間取り・面積・距離は、いただいた資料の数字だけを使う",
           "バーチャルステージングの画像と一緒に頼むと、写真と文章の雰囲気がそろう")
    p2 = head("不動産の物件紹介文", "書き方と、お届けするもの") + '<div class="wrap"><div class="card" style="font-size:26px;line-height:1.9"><ol style="padding-left:1.3em">' + "".join(f"<li>{p}</li>" for p in pts) + """</ol></div>
<div class="card" style="margin-top:24px;font-size:25px;line-height:1.8;background:#FFF6F1"><b>ご用意いただくもの</b><br>物件の資料（間取り図・募集図面など）と、写真があれば写真。周辺のことは、地図で分かる範囲で調べて書きます。</div></div>""" + foot("2 / 2")
    build("13-estate/src/sample-2.html", "13-estate/sample-2.png", p2, CSS, 1080, 1350)
    thumb2("13-estate", "<em>物件の紹介文</em>を<br>3件分書きます", "ポータル用の短文つき・広告の決まりに配慮",
           two("13-estate"), "3,000", "5,000円", ("納期2日", "修正1回"))


# ⑭ ショート動画（リール）1本の編集
def reel():
    scenes = (("0〜2秒", "生地をこねる手元", "毎朝4時から"), ("2〜5秒", "オーブンから出す", "焼きたて、こんな音"), ("5〜8秒", "パンを切る断面", "中はもっちり"),
              ("8〜11秒", "棚に並べる", "8時に並びます"), ("11〜15秒", "店の外観", "〇〇駅 徒歩5分"))
    cols = ("#C98742", "#8A5126", "#D9A35C", "#7C8B5B", "#5E3F27")
    p1 = head("ショート動画（リール）の編集", "麦とひだまり 様・15秒") + '<div class="wrap"><div style="display:flex;gap:14px;justify-content:center">' + "".join(
        f'<div style="width:184px"><div style="height:327px;border-radius:18px;background:linear-gradient(170deg,{c},#2a1b10);position:relative;overflow:hidden">'
        f'<p style="position:absolute;left:10px;right:10px;bottom:40px;color:#fff;font-weight:900;font-size:22px;text-align:center;text-shadow:0 2px 6px rgba(0,0,0,.5)">{cap}</p>'
        f'<div style="position:absolute;left:50%;top:40%;transform:translate(-50%,-50%);width:54px;height:54px;border-radius:50%;background:rgba(255,255,255,.85)"><div style="margin:15px 0 0 21px;width:0;height:0;border-left:18px solid #5E3F27;border-top:12px solid transparent;border-bottom:12px solid transparent"></div></div></div>'
        f'<p style="font-size:20px;font-weight:700;margin-top:8px">{t}</p><p style="font-size:19px;opacity:.75">{s}</p></div>'
        for (t, s, cap), c in zip(scenes, cols)) + """</div>
<div class="card" style="margin-top:30px;font-size:25px;line-height:1.85"><b>やること</b><br>・お送りいただいた動画（スマホで撮ったもの）を、15〜30秒にまとめる<br>・テロップ（字幕）・BGM（使ってよい音源）・切り替え<br>・縦長 1080×1920。Instagramリール・TikTok・YouTubeショートに</div>
<div class="card" style="margin-top:18px;font-size:24px;line-height:1.8;background:#FFF6F1">写真をつなげるだけのスライドショーではなく、<b>動いている映像</b>で作ります。そのため、動画の素材をご用意ください（1カット5秒ほど、5〜10本）。</div></div>""" + foot()
    build("14-reel/src/sample-1.html", "14-reel/sample-1.png", p1, CSS, 1080, 1350)
    pv = '<img src="../sample-1.png" style="width:1080px;height:500px;object-fit:cover;object-position:50% 30%">'
    thumb2("14-reel", "ショート動画を<br><em>1本編集</em>します", "スマホの動画を、テロップ・BGM付きのリールに",
           pv, "5,000", "8,000円", ("納期3日", "修正1回"))


ALL = {"sheet": sheet, "flyer": flyer, "cal": cal, "rewrite": rewrite, "estate": estate, "reel": reel}
if __name__ == "__main__":
    for k in (sys.argv[1:] or ALL):
        ALL[k]()
