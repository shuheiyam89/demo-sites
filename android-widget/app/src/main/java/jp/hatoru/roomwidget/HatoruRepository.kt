package jp.hatoru.roomwidget

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Log
import org.json.JSONException
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.time.Instant
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset

/** status.json の中身 */
data class HatoruStatus(
    val state: String,
    val task: String,
    val updatedAt: String,
)

/**
 * 状態JSONと部屋イラストの取得・キャッシュを担当する。
 * - 状態JSONは SharedPreferences に保存（取得失敗時は前回値を使う）
 * - 画像は filesDir/rooms/room-<state>.jpg に保存して再利用
 */
object HatoruRepository {
    private const val TAG = "HatoruRepository"

    const val BASE_URL = "https://shuheiyam89.github.io/demo-sites/hatoru-room/"
    private const val STATUS_URL = BASE_URL + "status.json"

    const val STATE_WORKING = "working"
    const val STATE_SLEEPING = "sleeping"
    const val STATE_THINKING = "thinking"
    const val STATE_RESEARCHING = "researching"
    val STATES = setOf(STATE_WORKING, STATE_SLEEPING, STATE_THINKING, STATE_RESEARCHING)

    /** updated_at から45分以上経過したら sleeping 扱い（Web版と同じルール） */
    const val SLEEP_AFTER_MILLIS = 45L * 60L * 1000L

    /** 画像キャッシュの再取得間隔（画像はめったに変わらないので7日） */
    private const val IMAGE_MAX_AGE_MILLIS = 7L * 24L * 60L * 60L * 1000L

    private const val PREFS = "hatoru_status"
    private const val KEY_STATE = "state"
    private const val KEY_TASK = "task"
    private const val KEY_UPDATED_AT = "updated_at"
    private const val KEY_LAST_FAILED = "last_failed"

    // ---------------- 状態JSON ----------------

    fun loadCached(context: Context): HatoruStatus? {
        val p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val state = p.getString(KEY_STATE, null) ?: return null
        return HatoruStatus(
            state = state,
            task = p.getString(KEY_TASK, "") ?: "",
            updatedAt = p.getString(KEY_UPDATED_AT, "") ?: "",
        )
    }

    fun lastFetchFailed(context: Context): Boolean =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_LAST_FAILED, false)

    /**
     * ネットワークから最新状態を取得してキャッシュを更新する（メインスレッドから呼ばないこと）。
     * 失敗した場合はキャッシュをそのまま残し false を返す。
     */
    @Synchronized
    fun refresh(context: Context): Boolean {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val now = System.currentTimeMillis()
        // GitHub Pages のキャッシュ（max-age=600）を避けるためクエリを付ける
        val bytes = httpGet("$STATUS_URL?t=$now", connectTimeoutMs = 5_000, readTimeoutMs = 6_000)
        val status = bytes?.let { parseStatus(String(it, Charsets.UTF_8)) }
        if (status == null) {
            prefs.edit().putBoolean(KEY_LAST_FAILED, true).commit()
            return false
        }
        prefs.edit()
            .putString(KEY_STATE, status.state)
            .putString(KEY_TASK, status.task)
            .putString(KEY_UPDATED_AT, status.updatedAt)
            .putBoolean(KEY_LAST_FAILED, false)
            .commit()

        val shown = displayState(status, now)
        ensureImage(context, shown)
        // 45分ルールでオフライン中に sleeping へ切り替わっても表示できるよう、sleeping 画像も確保しておく
        if (shown != STATE_SLEEPING) ensureImage(context, STATE_SLEEPING)
        return true
    }

    fun parseStatus(text: String): HatoruStatus? = try {
        val o = JSONObject(text)
        val state = if (o.isNull("state")) "" else o.optString("state", "").trim().lowercase()
        val task = if (o.isNull("task")) "" else o.optString("task", "").trim()
        val updatedAt = if (o.isNull("updated_at")) "" else o.optString("updated_at", "").trim()
        if (state.isEmpty()) null else HatoruStatus(state, task, updatedAt)
    } catch (e: JSONException) {
        Log.w(TAG, "status.json の解析に失敗", e)
        null
    }

    // ---------------- 表示ルール ----------------

    /** ISO8601 → epoch millis。オフセットが無い場合は +09:00 とみなす。解析できなければ null */
    fun parseUpdatedAt(value: String): Long? {
        if (value.isBlank()) return null
        return try {
            OffsetDateTime.parse(value).toInstant().toEpochMilli()
        } catch (e: Exception) {
            try {
                Instant.parse(value).toEpochMilli()
            } catch (e2: Exception) {
                try {
                    LocalDateTime.parse(value).atOffset(ZoneOffset.ofHours(9)).toInstant().toEpochMilli()
                } catch (e3: Exception) {
                    null
                }
            }
        }
    }

    /** updated_at が45分以上前（または不明）なら true */
    fun isStale(status: HatoruStatus, now: Long): Boolean {
        val t = parseUpdatedAt(status.updatedAt) ?: return true
        return now - t >= SLEEP_AFTER_MILLIS
    }

    /** 実際に表示する状態。古いデータや未知の state は sleeping にする */
    fun displayState(status: HatoruStatus, now: Long): String {
        if (isStale(status, now)) return STATE_SLEEPING
        return if (status.state in STATES) status.state else STATE_SLEEPING
    }

    fun label(context: Context, state: String): String = context.getString(
        when (state) {
            STATE_WORKING -> R.string.state_working
            STATE_THINKING -> R.string.state_thinking
            STATE_RESEARCHING -> R.string.state_researching
            else -> R.string.state_sleeping
        }
    )

    /** 例:「たった今」「3分前」「2時間前」「1日前」 */
    fun relativeTime(context: Context, updatedAt: String, now: Long): String {
        val t = parseUpdatedAt(updatedAt) ?: return context.getString(R.string.time_unknown)
        val minutes = (now - t).coerceAtLeast(0L) / 60_000L
        return when {
            minutes < 1 -> context.getString(R.string.time_just_now)
            minutes < 60 -> context.getString(R.string.time_minutes_ago, minutes)
            minutes < 60 * 24 -> context.getString(R.string.time_hours_ago, minutes / 60)
            else -> context.getString(R.string.time_days_ago, minutes / (60 * 24))
        }
    }

    // ---------------- 画像キャッシュ ----------------

    private fun imageFile(context: Context, state: String): File {
        val dir = File(context.filesDir, "rooms")
        if (!dir.exists()) dir.mkdirs()
        return File(dir, "room-$state.jpg")
    }

    /** 画像がキャッシュに無い（または古い）ときだけダウンロードする。失敗しても既存キャッシュは消さない */
    fun ensureImage(context: Context, state: String): Boolean {
        if (state !in STATES) return false
        val file = imageFile(context, state)
        val fresh = file.exists() && file.length() > 0 &&
            System.currentTimeMillis() - file.lastModified() < IMAGE_MAX_AGE_MILLIS
        if (fresh) return true

        val bytes = httpGet("${BASE_URL}room-$state.jpg", connectTimeoutMs = 5_000, readTimeoutMs = 10_000)
            ?: return file.exists()
        // 画像として読めるか確認してから保存（HTMLのエラーページなどを掴まないため）
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeByteArray(bytes, 0, bytes.size, bounds)
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return file.exists()

        return try {
            val tmp = File(file.parentFile, file.name + ".tmp")
            tmp.writeBytes(bytes)
            if (!tmp.renameTo(file)) {
                file.delete()
                tmp.renameTo(file)
            }
            true
        } catch (e: Exception) {
            Log.w(TAG, "画像の保存に失敗: $state", e)
            file.exists()
        }
    }

    /**
     * キャッシュ済み画像を読み込む。無ければ null。
     * @param maxWidth この幅(px)以下に縮小する
     * @param lowMemory true なら RGB_565 で読み込む（ウィジェット用。RemoteViews の転送サイズを抑える）
     */
    fun loadBitmap(context: Context, state: String, maxWidth: Int, lowMemory: Boolean): Bitmap? {
        val file = imageFile(context, state)
        if (!file.exists() || file.length() == 0L) return null
        return try {
            val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            BitmapFactory.decodeFile(file.path, bounds)
            if (bounds.outWidth <= 0) return null
            var sample = 1
            while (bounds.outWidth / (sample * 2) >= maxWidth) sample *= 2
            val opts = BitmapFactory.Options().apply {
                inSampleSize = sample
                if (lowMemory) inPreferredConfig = Bitmap.Config.RGB_565
            }
            val decoded = BitmapFactory.decodeFile(file.path, opts) ?: return null
            if (decoded.width <= maxWidth) {
                decoded
            } else {
                val h = (decoded.height.toLong() * maxWidth / decoded.width).toInt().coerceAtLeast(1)
                val scaled = Bitmap.createScaledBitmap(decoded, maxWidth, h, true)
                if (scaled !== decoded) decoded.recycle()
                scaled
            }
        } catch (e: Throwable) {
            Log.w(TAG, "画像の読み込みに失敗: $state", e)
            null
        }
    }

    // ---------------- 通信 ----------------

    private fun httpGet(url: String, connectTimeoutMs: Int, readTimeoutMs: Int): ByteArray? {
        var conn: HttpURLConnection? = null
        return try {
            conn = (URL(url).openConnection() as HttpURLConnection).apply {
                connectTimeout = connectTimeoutMs
                readTimeout = readTimeoutMs
                useCaches = false
                instanceFollowRedirects = true
                setRequestProperty("User-Agent", "HatoruRoomWidget/1.0 (Android)")
                setRequestProperty("Cache-Control", "no-cache")
            }
            if (conn.responseCode !in 200..299) {
                Log.w(TAG, "HTTP ${conn.responseCode}: $url")
                null
            } else {
                conn.inputStream.use { it.readBytes() }
            }
        } catch (e: Exception) {
            Log.w(TAG, "通信失敗: $url", e)
            null
        } finally {
            conn?.disconnect()
        }
    }
}
