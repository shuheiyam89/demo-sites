package jp.hatoru.roomwidget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.os.Bundle
import android.view.View
import android.widget.RemoteViews
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.concurrent.thread

/**
 * ホーム画面ウィジェット。
 * - 30分ごと（updatePeriodMillis）に onUpdate → 再取得
 * - タップで ACTION_REFRESH → 即時再取得
 * - 取得失敗時はキャッシュ（前回表示）のまま描画する
 * - コマが用意できていれば、ViewFlipper でコマ送りアニメーションを表示する
 *   （コマの切り替えはランチャー側の ViewFlipper が行う。コマが無いときは静止画）
 *   コマは Bitmap で渡す（URI で渡すとランチャーが読み込めない端末があるため）
 */
class HatoruWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        // まずキャッシュで即描画（真っ白にしない）→ 裏で再取得
        updateAllWidgets(context, refreshing = true)
        refreshAsync(context)
    }

    override fun onAppWidgetOptionsChanged(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int,
        newOptions: Bundle,
    ) {
        updateAllWidgets(context, refreshing = refreshing.get())
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        if (intent.action == ACTION_REFRESH) {
            updateAllWidgets(context, refreshing = true)
            refreshAsync(context)
        }
    }

    private fun refreshAsync(context: Context) {
        if (!refreshing.compareAndSet(false, true)) return // 取得中なら二重に走らせない
        val appContext = context.applicationContext
        val pending = goAsync()
        thread(name = "hatoru-refresh") {
            try {
                HatoruRepository.refresh(appContext)
            } catch (e: Throwable) {
                // 何があってもウィジェットは前回表示で描き直す
            } finally {
                refreshing.set(false)
                try {
                    updateAllWidgets(appContext, refreshing = false)
                } finally {
                    pending.finish()
                }
            }
        }
    }

    companion object {
        const val ACTION_REFRESH = "jp.hatoru.roomwidget.ACTION_REFRESH"

        /** ウィジェット用の画像幅上限(px)。RemoteViews の転送上限を超えないよう控えめにする */
        private const val WIDGET_IMAGE_MAX_WIDTH = 640

        /** アニメーションの1コマの幅上限(px)。8コマ分を1回で送るので、静止画より小さくする */
        private const val FRAME_MAX_WIDTH = 400

        private val refreshing = AtomicBoolean(false)

        /** 配置済みの全ウィジェットをキャッシュの内容で描き直す */
        fun updateAllWidgets(context: Context, refreshing: Boolean = false) {
            val manager = AppWidgetManager.getInstance(context)
            val ids = manager.getAppWidgetIds(ComponentName(context, HatoruWidgetProvider::class.java))
            if (ids.isEmpty()) return
            manager.updateAppWidget(ids, buildViews(context, refreshing))
        }

        /** ランチャー画面などから呼ぶ: 全ウィジェットに再取得を依頼する */
        fun requestRefresh(context: Context) {
            context.sendBroadcast(refreshIntent(context))
        }

        private fun refreshIntent(context: Context): Intent =
            Intent(context, HatoruWidgetProvider::class.java).setAction(ACTION_REFRESH)

        private fun refreshPendingIntent(context: Context): PendingIntent =
            PendingIntent.getBroadcast(
                context,
                0,
                refreshIntent(context),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )

        private val FRAME_VIEW_IDS = intArrayOf(
            R.id.frame_0, R.id.frame_1, R.id.frame_2, R.id.frame_3,
            R.id.frame_4, R.id.frame_5, R.id.frame_6, R.id.frame_7,
        )

        /**
         * コマ送りアニメーションを設定する。コマが無ければ ViewFlipper を隠して静止画だけにする。
         * コマは RGB_565・幅400px の Bitmap で渡す（8コマで約1.7MB。RemoteViews の画像上限より十分小さい）。
         * コマ数が8未満のときは、先頭から繰り返して8枠を埋める（同じ Bitmap は1回しか送られない）。
         */
        private fun applyAnimation(context: Context, views: RemoteViews, frames: List<Bitmap>?) {
            if (frames.isNullOrEmpty()) {
                views.setViewVisibility(R.id.room_flipper, View.GONE)
                return
            }
            FRAME_VIEW_IDS.forEachIndexed { i, id -> views.setImageViewBitmap(id, frames[i % frames.size]) }
            views.setInt(R.id.room_flipper, "setFlipInterval", AnimationFrames.intervalMs(context))
            views.setViewVisibility(R.id.room_flipper, View.VISIBLE)
        }

        private fun buildViews(context: Context, refreshing: Boolean): RemoteViews {
            val views = RemoteViews(context.packageName, R.layout.widget_hatoru)
            val status = HatoruRepository.loadCached(context)
            val now = System.currentTimeMillis()

            if (status == null) {
                // まだ一度も取得できていない
                views.setViewVisibility(R.id.room_flipper, View.GONE)
                views.setTextViewText(R.id.state_label, context.getString(R.string.app_name))
                views.setTextViewText(R.id.task_text, context.getString(R.string.widget_tap_to_load))
                views.setViewVisibility(R.id.task_text, View.VISIBLE)
                views.setTextViewText(
                    R.id.updated_text,
                    if (refreshing) context.getString(R.string.status_refreshing) else "",
                )
            } else {
                val state = HatoruRepository.displayState(status, now)
                // 静止画は常に下に敷いておく（コマが読めなかったときもここが見える）
                HatoruRepository.loadBitmap(context, state, WIDGET_IMAGE_MAX_WIDTH, lowMemory = true)
                    ?.let { views.setImageViewBitmap(R.id.room_image, it) }
                applyAnimation(
                    context,
                    views,
                    AnimationFrames.frameBitmaps(context, state, FRAME_MAX_WIDTH, lowMemory = true),
                )

                views.setTextViewText(R.id.state_label, HatoruRepository.label(context, state))

                // 45分ルールで「おやすみ中」にした場合、古い task は出さない
                val showTask = status.task.isNotEmpty() && !HatoruRepository.isStale(status, now)
                views.setTextViewText(R.id.task_text, if (showTask) status.task else "")
                views.setViewVisibility(R.id.task_text, if (showTask) View.VISIBLE else View.GONE)

                val sb = StringBuilder(
                    context.getString(
                        R.string.updated_prefix,
                        HatoruRepository.relativeTime(context, status.updatedAt, now),
                    )
                )
                if (refreshing) {
                    sb.append(" ・ ").append(context.getString(R.string.status_refreshing))
                } else if (HatoruRepository.lastFetchFailed(context)) {
                    sb.append(" ・ ").append(context.getString(R.string.status_fetch_failed))
                }
                views.setTextViewText(R.id.updated_text, sb.toString())
            }

            views.setOnClickPendingIntent(R.id.widget_root, refreshPendingIntent(context))
            return views
        }
    }
}
