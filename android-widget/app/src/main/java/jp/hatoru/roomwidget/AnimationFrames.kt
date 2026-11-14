package jp.hatoru.roomwidget

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.Log
import org.json.JSONObject
import java.io.File

/**
 * コマ送りアニメーション用のコマ（フレーム）を用意する。
 *
 * - anime/frames.json（マニフェスト）を取得し、状態ごとのグリッド画像（例: 4列×2行＝8コマ）をダウンロードする
 * - グリッドを行優先（左→右、上→下）で切り分け、filesDir/frames/<state>/<version>/f<n>.jpg に保存する
 * - ネットワークを使うのは refresh() の中だけ（状態の再取得と同じタイミング）。コマの表示中は通信しない
 *
 * 表示側（ウィジェット）は frameUris() で得た content:// URI を ViewFlipper の各コマに渡す。
 * コマの切り替えはホーム画面アプリ（ランチャー）側の ViewFlipper が行うので、このアプリのサービスや
 * 常駐処理は不要で、OSに止められて表示が壊れることもない。
 */
object AnimationFrames {
    private const val TAG = "AnimationFrames"

    const val MANIFEST_URL = HatoruRepository.BASE_URL + "anime/frames.json"

    /** ウィジェットのレイアウトに用意しているコマの数（ViewFlipper の子） */
    const val MAX_FRAMES = 8

    const val DEFAULT_INTERVAL_MS = 900

    /** コマ画像の幅の上限(px)。ランチャーが読み込む画像を軽く保つ */
    private const val FRAME_MAX_WIDTH = 640

    /** マニフェストの再取得間隔（6時間）。グリッド画像の再取得間隔（7日） */
    private const val MANIFEST_MAX_AGE_MILLIS = 6L * 60L * 60L * 1000L
    private const val GRID_MAX_AGE_MILLIS = 7L * 24L * 60L * 60L * 1000L

    private const val PREFS = "hatoru_anime"
    private const val KEY_MANIFEST = "manifest"
    private const val KEY_MANIFEST_AT = "manifest_at"

    private data class Manifest(
        val intervalMs: Int,
        val cols: Int,
        val rows: Int,
        val frames: Int,
        val urls: Map<String, String>,
    )

    // ---------------- 表示側から使う ----------------

    /** コマを切り替える間隔(ms)。マニフェストが無ければ 900ms */
    fun intervalMs(context: Context): Int =
        loadManifest(context)?.intervalMs ?: DEFAULT_INTERVAL_MS

    /**
     * その状態のコマが揃っていれば、コマ画像の URI を順番どおりに返す（無ければ null）。
     * 端末内のファイルを見るだけで、通信はしない。
     */
    fun frameUris(context: Context, state: String): List<Uri>? {
        if (state !in HatoruRepository.STATES) return null
        val p = prefs(context)
        val version = p.getLong(keyVersion(state), 0L)
        val count = p.getInt(keyCount(state), 0)
        if (version <= 0L || count <= 0) return null
        val dir = versionDir(context, state, version)
        val uris = ArrayList<Uri>(count)
        for (i in 0 until count) {
            val f = File(dir, "f$i.jpg")
            if (!f.exists() || f.length() == 0L) return null
            uris.add(FrameProvider.uriFor(context, state, version, i))
        }
        return uris
    }

    // ---------------- 取得（バックグラウンドスレッドから呼ぶ） ----------------

    /**
     * 表示する状態のコマを用意する。失敗しても既存のコマは消さない。
     * @return コマが使える状態なら true
     */
    @Synchronized
    fun refresh(context: Context, state: String): Boolean {
        if (state !in HatoruRepository.STATES) return false
        val manifest = fetchManifestIfNeeded(context) ?: return frameUris(context, state) != null
        val url = manifest.urls[state] ?: return frameUris(context, state) != null

        val p = prefs(context)
        val sameUrl = p.getString(keyUrl(state), null) == url
        val version = p.getLong(keyVersion(state), 0L)
        val fresh = version > 0L && System.currentTimeMillis() - version < GRID_MAX_AGE_MILLIS
        if (sameUrl && fresh && frameUris(context, state) != null) return true

        val bytes = HatoruRepository.httpGet(url, connectTimeoutMs = 5_000, readTimeoutMs = 15_000)
            ?: return frameUris(context, state) != null
        val newVersion = System.currentTimeMillis()
        val count = splitAndSave(context, state, newVersion, bytes, manifest)
        if (count <= 0) return frameUris(context, state) != null

        p.edit()
            .putString(keyUrl(state), url)
            .putLong(keyVersion(state), newVersion)
            .putInt(keyCount(state), count)
            .commit()
        // 古い版のコマを片付ける
        stateDir(context, state).listFiles()?.forEach { if (it.name != newVersion.toString()) it.deleteRecursively() }
        return true
    }

    private fun fetchManifestIfNeeded(context: Context): Manifest? {
        val p = prefs(context)
        val cached = loadManifest(context)
        val age = System.currentTimeMillis() - p.getLong(KEY_MANIFEST_AT, 0L)
        if (cached != null && age < MANIFEST_MAX_AGE_MILLIS) return cached

        val now = System.currentTimeMillis()
        val bytes = HatoruRepository.httpGet("$MANIFEST_URL?t=$now", connectTimeoutMs = 5_000, readTimeoutMs = 6_000)
        val text = bytes?.let { String(it, Charsets.UTF_8) }
        val parsed = text?.let { parseManifest(it) } ?: return cached
        p.edit().putString(KEY_MANIFEST, text).putLong(KEY_MANIFEST_AT, now).commit()
        return parsed
    }

    private fun loadManifest(context: Context): Manifest? =
        prefs(context).getString(KEY_MANIFEST, null)?.let { parseManifest(it) }

    private fun parseManifest(text: String): Manifest? = try {
        val o = JSONObject(text)
        val grid = o.getJSONObject("grid")
        val cols = grid.optInt("cols", 0)
        val rows = grid.optInt("rows", 0)
        val frames = grid.optInt("frames", cols * rows)
        val statesObj = o.getJSONObject("states")
        val urls = HashMap<String, String>()
        for (s in HatoruRepository.STATES) {
            val u = statesObj.optString(s, "").trim()
            if (u.startsWith("https://")) urls[s] = u
        }
        val interval = o.optInt("frame_interval_ms", DEFAULT_INTERVAL_MS).coerceIn(200, 10_000)
        if (cols <= 0 || rows <= 0 || frames <= 0 || urls.isEmpty()) null
        else Manifest(interval, cols, rows, frames.coerceAtMost(cols * rows), urls)
    } catch (e: Exception) {
        Log.w(TAG, "frames.json の解析に失敗", e)
        null
    }

    /** グリッドを行優先で切り分けて保存する。保存できたコマ数を返す（失敗時 0） */
    private fun splitAndSave(context: Context, state: String, version: Long, bytes: ByteArray, m: Manifest): Int {
        var grid: Bitmap? = null
        val dir = versionDir(context, state, version)
        return try {
            val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size, bounds)
            if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return 0
            // 1コマの幅が FRAME_MAX_WIDTH 程度になるまで縮小して読み込む
            var sample = 1
            while (bounds.outWidth / m.cols / (sample * 2) >= FRAME_MAX_WIDTH) sample *= 2
            val g = BitmapFactory.decodeByteArray(bytes, 0, bytes.size, BitmapFactory.Options().apply { inSampleSize = sample })
                ?: return 0
            grid = g
            val cellW = g.width / m.cols
            val cellH = g.height / m.rows
            if (cellW <= 0 || cellH <= 0) return 0

            if (!dir.exists()) dir.mkdirs()
            val count = m.frames.coerceAtMost(MAX_FRAMES)
            for (i in 0 until count) {
                val x = (i % m.cols) * cellW
                val y = (i / m.cols) * cellH
                val cell = Bitmap.createBitmap(g, x, y, cellW, cellH)
                val out = if (cell.width > FRAME_MAX_WIDTH) {
                    val h = (cell.height.toLong() * FRAME_MAX_WIDTH / cell.width).toInt().coerceAtLeast(1)
                    Bitmap.createScaledBitmap(cell, FRAME_MAX_WIDTH, h, true).also { if (it !== cell) cell.recycle() }
                } else cell
                File(dir, "f$i.jpg").outputStream().use { out.compress(Bitmap.CompressFormat.JPEG, 85, it) }
                out.recycle()
            }
            count
        } catch (e: Throwable) {
            Log.w(TAG, "コマの切り出しに失敗: $state", e)
            dir.deleteRecursively()
            0
        } finally {
            grid?.recycle()
        }
    }

    // ---------------- ファイルの場所 ----------------

    fun framesRoot(context: Context): File = File(context.filesDir, "frames")
    private fun stateDir(context: Context, state: String) = File(framesRoot(context), state)
    fun versionDir(context: Context, state: String, version: Long) = File(stateDir(context, state), version.toString())

    private fun prefs(context: Context) = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
    private fun keyUrl(state: String) = "url_$state"
    private fun keyVersion(state: String) = "ver_$state"
    private fun keyCount(state: String) = "count_$state"
}
