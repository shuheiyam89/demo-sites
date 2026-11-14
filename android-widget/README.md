# ハトルの仕事部屋ウィジェット（Android）

AIアシスタント「ハトル」（チワワ）の今の状態（お仕事中／おやすみ中／考え中／調べもの中）を、部屋のイラストと一言でホーム画面に表示する Android ウィジェットです。Web版（GitHub Pages）で公開している状態データと画像をそのまま読みに行く、表示専用のアプリです。

- applicationId: `jp.hatoru.roomwidget` ／ アプリ名: ハトルの仕事部屋
- minSdk 26（Android 8.0）／ targetSdk 34
- Kotlin、`AppWidgetProvider` + `RemoteViews`（Glance は不使用）
- 外部ライブラリなし（通信は `HttpURLConnection`、JSON は `org.json`）
- 権限は `INTERNET` のみ。アカウント・広告・トラッキングなし

## 表示するもの

| 項目 | 内容 |
|---|---|
| イラスト | `room-<state>.jpg`（3:2） |
| 状態ラベル | working=お仕事中／sleeping=おやすみ中／thinking=考え中／researching=調べもの中 |
| 一言 | `task`（ある場合だけ） |
| 最終更新 | `updated_at` からの相対時刻（例「更新: 3分前」） |

データソース（認証不要）:
- 状態JSON: https://shuheiyam89.github.io/demo-sites/hatoru-room/status.json
- 画像: https://shuheiyam89.github.io/demo-sites/hatoru-room/room-working.jpg ほか

### 表示ルール
- `updated_at` から **45分以上**たっていたら、`state` に関係なく「おやすみ中」とその画像を表示します（Web版と同じ）。このとき古い `task` は表示しません。
- `state` が4種類のどれでもない場合、または `updated_at` が読めない場合も「おやすみ中」として表示します。
- 取得に失敗したときは**前回の表示をそのまま残し**、「通信できませんでした」と小さく出します（真っ白にはしません）。
- 画像は端末内（アプリ専用領域）にキャッシュして再利用します（7日ごとに取り直し）。

## 更新のしくみ
- **自動**: `updatePeriodMillis = 1800000`（30分）。Android が約30分ごとにウィジェットを更新し、そのタイミングで最新の状態を取得します（端末の省電力状態によっては遅れることがあります）。
- **タップ**: ウィジェットをタップするとその場で再取得して描き直します（取得中は「更新中…」と表示）。
- **アプリ画面**: アプリを開くと自動で取得し、「今すぐ更新」ボタンでも再取得できます。結果はホーム画面のウィジェットにも反映されます。
- `status.json` は GitHub Pages のキャッシュを避けるため `?t=<時刻>` を付けて取得します。

## ビルド手順

### 必要なもの
- JDK 17
- Android SDK（Platform 34 / Build-Tools）… Android Studio を入れれば揃います
- インターネット接続（Gradle 8.9・Android Gradle Plugin 8.5.2・Kotlin 1.9.24 を初回にダウンロード）

### 注意: `gradle-wrapper.jar` について
このリポジトリには `gradle/wrapper/gradle-wrapper.properties`（Gradle 8.9 指定）は入っていますが、**`gradlew` スクリプトと `gradle-wrapper.jar` は入っていません**（作成した環境ではバイナリ生成・コマンド実行ができなかったため）。最初に一度、次のどちらかで生成してください。

- Android Studio でこのフォルダを開く（自動で同期・生成されます）
- または Gradle をインストール済みなら、このフォルダで:
  ```sh
  gradle wrapper --gradle-version 8.9
  ```

生成後は通常どおり:
```sh
./gradlew assembleDebug
```
APK の出力先: `app/build/outputs/apk/debug/app-debug.apk`

SDK の場所が見つからないと言われたら、`local.properties` に `sdk.dir=/path/to/Android/sdk` を書いてください（コミット不要）。

### GitHub Actions でビルドする（PC に SDK が無い場合）
`demo-sites` リポジトリ直下の `.github/workflows/android-widget-apk.yml` で、`android-widget/` を変更して push すると GitHub 上で自動ビルドされます（Actions タブ → 「Build hatoru widget APK」→ 「Run workflow」で手動実行も可）。
完了した実行結果ページ下部の **Artifacts → `hatoru-widget-debug-apk`** から zip をダウンロードし、中の `app-debug.apk` を使います。

## Pixel へのインストール手順
1. Pixel で `app-debug.apk` をダウンロードします（Artifacts の zip の場合は、ファイルアプリで zip を開いて展開）。
2. 「ファイル」アプリ（Files by Google）→「ダウンロード」から `app-debug.apk` をタップします。
3. 「提供元不明のアプリ」の確認が出たら **設定** → 「この提供元のアプリを許可」をオンにして戻ります。
4. 「インストール」をタップします。Play プロテクトの警告が出た場合は「詳細」→「インストールする」を選びます。

> debug APK はビルドした環境ごとに署名鍵が違います。別の環境（例: 別の Actions 実行）でビルドした APK で上書きしようとして「アプリはインストールされていません」と出たら、いったん古いアプリをアンインストールしてから入れ直してください。

## ウィジェットの置き方
1. ホーム画面の何もないところを長押し
2. 「ウィジェット」をタップ
3. 一覧から「ハトルの仕事部屋」を探し、ウィジェットを長押ししてホーム画面に置く
4. 置いたウィジェットを長押しすると、枠をドラッグして大きさを変えられます（2×2〜4×3 がおすすめ）

## ファイル構成
```
android-widget/
├─ settings.gradle.kts / build.gradle.kts / gradle.properties
├─ gradle/wrapper/gradle-wrapper.properties
└─ app/
   ├─ build.gradle.kts
   └─ src/main/
      ├─ AndroidManifest.xml
      ├─ java/jp/hatoru/roomwidget/
      │  ├─ HatoruRepository.kt      … 取得・キャッシュ・45分ルール・相対時刻
      │  ├─ HatoruWidgetProvider.kt  … ウィジェット本体（30分更新＋タップ更新）
      │  └─ MainActivity.kt          … ランチャー画面
      └─ res/ … レイアウト・文字列・アイコン（ベクター）・ウィジェット定義
```

## v1 でやっていないこと
- 朝昼夜の色味演出・アニメーション（静止画＋テキストのみ）
- 相対時刻は描画した時点の値です（次の自動更新またはタップまでは「3分前」のまま）
