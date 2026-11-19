# アフィリエイト（商品紹介）リール 2026-11-20（@okatazuke.onrender 向け）

| 動画 | カバー | 商品 | BGM |
|---|---|---|---|
| affiliate-warm.mp4 | affiliate-warm-cover.jpg | 着る毛布 グルーニー 3,490円 ★4.5 レビュー46,927件 | Carefree |
| affiliate-christmas.mp4 | affiliate-christmas-cover.jpg | LEDツリーライト 12m 1,480円 ★4.58 レビュー618件 | Jingle Bells |
| affiliate-storage.mp4 | affiliate-storage-cover.jpg | 収納ボックス 木天板・キャスター付き 4,280円 ★4.5 レビュー5,691件 | Bossa Antigua |

- 1080x1920・30fps・H.264 High・yuv420p・AAC・19.5秒。テロップのみ。全編の右上に「PR」。
- 構成：カバー0.5秒 → 困っている場面5.5秒 → 解決した場面6.5秒 → 商品カード4秒 → エンドカード3秒。
- 人物の動き：同じ人物・同じ部屋の少し違うポーズの画像（OpenAI gpt-image-2 で生成。ビフォー1枚目から編集で作り、同じ人物に見えるようにした）を、ゆっくりズームしながら重ねて切り替えている（動画生成ではない）。
- 商品カードの写真は楽天の商品画像（各商品ページの画像URL）。価格・評価は投稿時点の数字。
- 組み立て：`python build_affiliate.py`（素材は src/。src/ はリポジトリに入れていない）

## 音楽のクレジット（投稿のキャプションに入れてください）
- "Carefree" Kevin MacLeod (incompetech.com) Licensed under Creative Commons: By Attribution 4.0 License http://creativecommons.org/licenses/by/4.0/
- "Jingle Bells" Kevin MacLeod (incompetech.com) Licensed under Creative Commons: By Attribution 4.0 License http://creativecommons.org/licenses/by/4.0/
- "Bossa Antigua" Kevin MacLeod (incompetech.com) Licensed under Creative Commons: By Attribution 4.0 License http://creativecommons.org/licenses/by/4.0/

## ⚠ この3本は不採用（静止画＋クロスフェード）→「滑らか動画の標準」に従う
この3本は「動きがコマ撮りすぎる」として社長に却下されました。次回からは `affiliate-reels/smooth-standard/滑らか動画の標準.md` に従います。要点：
- **シーン（ビフォー・アフター）は、本物の動きのある動画クリップを使う。**
- **静止画のポーズ違い＋クロスフェードで代用しない。**
- **動画クリップが渡されていない（自分の環境でも作れない）ときは、組み立てに入る前に報告する。** 静止画で埋めて納品しない。
- **音楽は毎回別の曲にする**（同じ曲を使い回さない）。Kevin MacLeod（CC BY 4.0）で、キャプションにクレジットを入れる。
- 分担：ハトル（Muse側）が写真・動画クリップ・音楽ファイルを用意し、Claude Code は組み立て（テロップ・PR・商品カード・エンドカード・音楽付け）を担当する。
- 組み立ては `smooth-standard/build_warm.py`・`build_two.py` の形：
  - 構成：カバー0.5秒 → ビフォー5.5秒 → アフター6.5秒 → 商品カード4秒 → エンドカード3秒（計19.5秒）
  - テロップの位置：白い丸い帯＋黒の太字。下から330pxの位置。アフターは3.4秒でテロップを切り替える
  - PRバッジ：全編の右上（右36px・上48px）
- 完成見本：`smooth-standard/affiliate-warm-smooth.mp4`
