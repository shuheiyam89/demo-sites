package jp.hatoru.roomwidget

import android.app.Activity
import android.graphics.Bitmap
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import kotlin.concurrent.thread

/** ランチャー画面: 現在の状態プレビュー、「今すぐ更新」ボタン、ウィジェットの置き方 */
class MainActivity : Activity() {

    private lateinit var previewImage: ImageView
    private lateinit var previewLabel: TextView
    private lateinit var previewTask: TextView
    private lateinit var previewUpdated: TextView
    private lateinit var refreshButton: Button

    private var loading = false

    // プレビューのコマ送り（アプリ画面を開いている間だけ動かす）
    private val handler = Handler(Looper.getMainLooper())
    private var frames: List<Bitmap> = emptyList()
    private var frameIndex = 0
    private var frameIntervalMs = AnimationFrames.DEFAULT_INTERVAL_MS
    private val tick = object : Runnable {
        override fun run() {
            if (frames.size > 1) {
                frameIndex = (frameIndex + 1) % frames.size
                previewImage.setImageBitmap(frames[frameIndex])
                handler.postDelayed(this, frameIntervalMs.toLong())
            }
        }
    }

    override fun onResume() {
        super.onResume()
        startPreviewAnimation()
    }

    override fun onPause() {
        super.onPause()
        handler.removeCallbacks(tick)
    }

    private fun startPreviewAnimation() {
        handler.removeCallbacks(tick)
        if (frames.size > 1) handler.postDelayed(tick, frameIntervalMs.toLong())
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        previewImage = findViewById(R.id.preview_image)
        previewLabel = findViewById(R.id.preview_label)
        previewTask = findViewById(R.id.preview_task)
        previewUpdated = findViewById(R.id.preview_updated)
        refreshButton = findViewById(R.id.refresh_button)

        refreshButton.setOnClickListener { refresh(showToast = true) }

        loadAndRender(null)
        if (savedInstanceState == null) refresh(showToast = false)
    }

    private fun refresh(showToast: Boolean) {
        if (loading) return
        loading = true
        refreshButton.isEnabled = false
        refreshButton.setText(R.string.status_refreshing)

        val appContext = applicationContext
        thread(name = "hatoru-activity-refresh") {
            val ok = try {
                HatoruRepository.refresh(appContext)
            } catch (e: Throwable) {
                false
            }
            // ホーム画面のウィジェットも最新のキャッシュで描き直す
            HatoruWidgetProvider.updateAllWidgets(appContext)
            runOnUiThread {
                if (isFinishing || isDestroyed) return@runOnUiThread
                loading = false
                refreshButton.isEnabled = true
                refreshButton.setText(R.string.button_refresh_now)
                loadAndRender(ok)
                if (showToast) {
                    Toast.makeText(
                        this,
                        if (ok) R.string.toast_refreshed else R.string.toast_failed,
                        Toast.LENGTH_SHORT,
                    ).show()
                }
            }
        }
    }

    /** 画像のデコードは裏スレッドで行い、UIに反映する */
    private fun loadAndRender(lastResult: Boolean?) {
        val appContext = applicationContext
        thread(name = "hatoru-activity-render") {
            val status = HatoruRepository.loadCached(appContext)
            val now = System.currentTimeMillis()
            val state = status?.let { HatoruRepository.displayState(it, now) }
            val bitmap: Bitmap? = state?.let {
                HatoruRepository.loadBitmap(appContext, it, maxWidth = 1200, lowMemory = false)
            }
            val newFrames = state?.let { AnimationFrames.frameBitmaps(appContext, it, maxWidth = 640, lowMemory = false) }.orEmpty()
            val interval = AnimationFrames.intervalMs(appContext)
            runOnUiThread {
                if (isFinishing || isDestroyed) return@runOnUiThread
                if (status == null || state == null) {
                    previewLabel.setText(R.string.preview_no_data)
                    previewTask.visibility = View.GONE
                    previewUpdated.text = if (lastResult == false) getString(R.string.status_fetch_failed) else ""
                    return@runOnUiThread
                }
                frames = newFrames
                frameIndex = 0
                frameIntervalMs = interval
                if (frames.isNotEmpty()) previewImage.setImageBitmap(frames[0])
                else if (bitmap != null) previewImage.setImageBitmap(bitmap)
                startPreviewAnimation()
                previewLabel.text = HatoruRepository.label(this, state)
                val showTask = status.task.isNotEmpty() && !HatoruRepository.isStale(status, now)
                previewTask.text = status.task
                previewTask.visibility = if (showTask) View.VISIBLE else View.GONE
                var updated = getString(
                    R.string.updated_prefix,
                    HatoruRepository.relativeTime(this, status.updatedAt, now),
                )
                if (HatoruRepository.lastFetchFailed(this)) {
                    updated += " ・ " + getString(R.string.status_fetch_failed)
                }
                // コマの準備状況（ウィジェットが動かないときの確認用）
                updated += "\n" + if (frames.isNotEmpty()) getString(R.string.anime_ready, frames.size)
                    else getString(R.string.anime_not_ready)
                previewUpdated.text = updated
            }
        }
    }
}
