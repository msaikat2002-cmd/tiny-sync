package com.tinyclipboardsync

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.ClipboardManager
import android.content.ClipData
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import androidx.core.app.NotificationCompat
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.Socket
import kotlin.concurrent.thread

class ClipboardSyncService : Service() {

    companion object {
        private const val NOTIFICATION_ID = 1
        private const val CHANNEL_ID = "clipboard_sync_channel"
        private const val SERVER_PORT = 5555
        private const val PREFS_NAME = "ClipboardSyncPrefs"
        private const val KEY_SERVER_IP = "server_ip"
    }

    private var socket: Socket? = null
    private var writer: PrintWriter? = null
    private var reader: BufferedReader? = null
    private var isConnected = false
    private var clipboardManager: ClipboardManager? = null
    private var handler: Handler = Handler(Looper.getMainLooper())
    private var lastClipboardText = ""
    private var reconnectHandler = Handler(Looper.getMainLooper())
    private var reconnectRunnable: Runnable? = null
    private var isSettingClipboardFromNetwork = false
    private var clipboardListener: ClipboardManager.OnPrimaryClipChangedListener? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, createNotification(false))
        clipboardManager = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        connectToServer()
        setupClipboardListener()
        scheduleReconnect()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == "SEND_CLIPBOARD") {
            sendCurrentClipboard()
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        removeClipboardListener()
        disconnectFromServer()
        reconnectHandler.removeCallbacksAndMessages(null)
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                getString(R.string.notification_channel_name),
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(showButton: Boolean): Notification {
        val intent = Intent(this, SetupActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.notification_title))
            .setContentText(getString(R.string.notification_connected))
            .setSmallIcon(android.R.drawable.ic_menu_info_details)
            .setContentIntent(pendingIntent)
            .setOngoing(true)

        if (showButton) {
            val sendIntent = Intent(this, ClipboardSyncService::class.java).apply {
                action = "SEND_CLIPBOARD"
            }
            val sendPendingIntent = PendingIntent.getService(
                this, 1, sendIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            builder.addAction(
                android.R.drawable.ic_menu_send,
                getString(R.string.send_clipboard),
                sendPendingIntent
            )
        }

        return builder.build()
    }

    private fun getSavedServerIp(): String {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_SERVER_IP, "") ?: ""
    }

    private fun connectToServer() {
        thread {
            val ip = getSavedServerIp()
            if (ip.isEmpty()) return@thread

            try {
                socket = Socket(ip, SERVER_PORT)
                socket?.tcpNoDelay = true
                writer = PrintWriter(socket!!.getOutputStream(), true)
                reader = BufferedReader(InputStreamReader(socket!!.getInputStream()))

                isConnected = true
                updateNotification(true)

                while (isConnected && socket?.isClosed == false) {
                    val line = reader?.readLine()
                    if (line != null) {
                        handleIncomingMessage(line)
                    } else {
                        break
                    }
                }
            } catch (e: Exception) {
                isConnected = false
                updateNotification(false)
            }
        }
    }

    private fun handleIncomingMessage(json: String) {
        handler.post {
            try {
                if (json.startsWith("{") && json.endsWith("}")) {
                    val typeStart = json.indexOf("\"type\":") + 7
                    if (typeStart > 6) {
                        val typeEnd = json.indexOf(",", typeStart).let { 
                            if (it == -1) json.indexOf("}", typeStart) else it 
                        }
                        val type = json.substring(typeStart, typeEnd).trim().trim('"')

                        if (type == "clipboard") {
                            val contentStart = json.indexOf("\"content\":") + 10
                            if (contentStart > 9) {
                                val contentEnd = json.lastIndexOf("\"")
                                if (contentEnd > contentStart) {
                                    var content = json.substring(contentStart, contentEnd)
                                    content = unescapeJson(content)
                                    setClipboard(content)
                                }
                            }
                        }
                    }
                }
            } catch (e: Exception) { }
        }
    }

    private fun unescapeJson(s: String): String {
        return s.replace("\\n", "\n")
                .replace("\\r", "\r")
                .replace("\\t", "\t")
                .replace("\\\"", "\"")
                .replace("\\\\", "\\")
    }

    private fun setClipboard(text: String) {
        try {
            isSettingClipboardFromNetwork = true
            val clip = ClipData.newPlainText("", text)
            clipboardManager?.setPrimaryClip(clip)
            lastClipboardText = text
            isSettingClipboardFromNetwork = false
        } catch (e: Exception) {
            isSettingClipboardFromNetwork = false
        }
    }

    private fun getClipboardText(): String {
        return try {
            val clip = clipboardManager?.primaryClip
            if (clip != null && clip.itemCount > 0) {
                clip.getItemAt(0).text?.toString() ?: ""
            } else {
                ""
            }
        } catch (e: Exception) {
            ""
        }
    }

    private fun sendClipboard(text: String) {
        if (!isConnected || writer == null) return

        thread {
            try {
                val escaped = text.replace("\\", "\\\\")
                    .replace("\"", "\\\"")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t")

                val json = "{\"type\":\"clipboard\",\"content\":\"$escaped\"}"
                writer?.println(json)
                writer?.flush()
            } catch (e: Exception) {
                isConnected = false
            }
        }
    }

    private fun sendCurrentClipboard() {
        val text = getClipboardText()
        if (text.isNotEmpty()) {
            sendClipboard(text)
        }
    }

    private fun disconnectFromServer() {
        try {
            isConnected = false
            reader?.close()
            writer?.close()
            socket?.close()
            reader = null
            writer = null
            socket = null
        } catch (e: Exception) { }
    }

    private fun setupClipboardListener() {
        clipboardListener = ClipboardManager.OnPrimaryClipChangedListener {
            if (!isSettingClipboardFromNetwork) {
                val currentText = getClipboardText()
                if (currentText.isNotEmpty() && currentText != lastClipboardText) {
                    lastClipboardText = currentText
                    sendClipboard(currentText)
                }
            }
        }
        clipboardManager?.addPrimaryClipChangedListener(clipboardListener)
    }

    private fun removeClipboardListener() {
        clipboardListener?.let {
            clipboardManager?.removePrimaryClipChangedListener(it)
        }
        clipboardListener = null
    }

    private fun scheduleReconnect() {
        reconnectRunnable = Runnable {
            if (!isConnected) {
                connectToServer()
            }
            reconnectHandler.postDelayed(reconnectRunnable!!, 5000)
        }
        reconnectHandler.post(reconnectRunnable!!)
    }

    private fun updateNotification(connected: Boolean) {
        val notification = createNotification(connected)
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, notification)
    }
}
