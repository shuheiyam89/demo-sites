package jp.hatoru.roomwidget

import android.content.ContentProvider
import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.net.Uri
import android.os.ParcelFileDescriptor
import java.io.File
import java.io.FileNotFoundException

/**
 * ウィジェットのコマ画像を、ホーム画面アプリ（ランチャー）に読ませるための読み取り専用プロバイダー。
 *
 * RemoteViews に画像を Bitmap で8枚渡すと、プロセス間の転送上限（約1MB）を超えて失敗しやすい。
 * そこで画像は URI で渡し、ランチャーがここからファイルを読む。
 * 公開するのは filesDir/frames/<state>/<version>/f<n>.jpg（公開済みのイラストを切り分けたもの）だけで、
 * 書き込みや一覧の取得には応じない。
 *
 * URI: content://jp.hatoru.roomwidget.frames/<state>/<version>/f<n>.jpg
 *   版（version）をパスに含めるので、コマを作り直すと URI も変わり、ランチャー側で古い画像が残らない。
 */
class FrameProvider : ContentProvider() {

    override fun onCreate(): Boolean = true

    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor {
        if (mode != "r") throw SecurityException("read only")
        val ctx = context ?: throw FileNotFoundException()
        val file = resolve(ctx, uri) ?: throw FileNotFoundException(uri.toString())
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
    }

    override fun getType(uri: Uri): String = "image/jpeg"

    override fun query(uri: Uri, projection: Array<out String>?, selection: String?, selectionArgs: Array<out String>?, sortOrder: String?): Cursor? = null
    override fun insert(uri: Uri, values: ContentValues?): Uri? = throw UnsupportedOperationException()
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<out String>?): Int = throw UnsupportedOperationException()
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<out String>?): Int = throw UnsupportedOperationException()

    companion object {
        private const val AUTHORITY_SUFFIX = ".frames"
        private val NAME = Regex("^f[0-7]\\.jpg$")
        private val VERSION = Regex("^[0-9]{1,19}$")

        fun uriFor(context: Context, state: String, version: Long, index: Int): Uri =
            Uri.Builder()
                .scheme("content")
                .authority(context.packageName + AUTHORITY_SUFFIX)
                .appendPath(state)
                .appendPath(version.toString())
                .appendPath("f$index.jpg")
                .build()

        /** 決まった形の URI だけをファイルに対応させる（それ以外は null） */
        private fun resolve(context: Context, uri: Uri): File? {
            if (uri.authority != context.packageName + AUTHORITY_SUFFIX) return null
            val seg = uri.pathSegments
            if (seg.size != 3) return null
            val (state, version, name) = seg
            if (state !in HatoruRepository.STATES || !VERSION.matches(version) || !NAME.matches(name)) return null
            val file = File(AnimationFrames.versionDir(context, state, version.toLong()), name)
            // 念のため、frames フォルダの外を指していないことを確かめる
            val root = AnimationFrames.framesRoot(context).canonicalPath + File.separator
            if (!file.canonicalPath.startsWith(root) || !file.isFile) return null
            return file
        }
    }
}
