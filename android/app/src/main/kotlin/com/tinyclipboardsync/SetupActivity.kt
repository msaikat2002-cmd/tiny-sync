package com.tinyclipboardsync

import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity
import java.net.InetAddress

class SetupActivity : AppCompatActivity() {

    companion object {
        private const val PREFS_NAME = "ClipboardSyncPrefs"
        private const val KEY_SERVER_IP = "server_ip"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_setup)

        val ipInput = findViewById<EditText>(R.id.ipInput)
        val saveButton = findViewById<Button>(R.id.saveButton)

        val savedIp = getSavedServerIp()
        if (savedIp.isNotEmpty()) {
            ipInput.setText(savedIp)
        }

        saveButton.setOnClickListener {
            val ip = ipInput.text.toString().trim()
            if (validateIpAddress(ip)) {
                saveServerIp(ip)
                startService()
                finish()
            } else {
                ipInput.error = "Invalid IP address"
            }
        }
    }

    private fun validateIpAddress(ip: String): Boolean {
        return try {
            InetAddress.getByName(ip) != null
        } catch (e: Exception) {
            false
        }
    }

    private fun saveServerIp(ip: String) {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(KEY_SERVER_IP, ip).apply()
    }

    private fun getSavedServerIp(): String {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_SERVER_IP, "") ?: ""
    }

    private fun startService() {
        val serviceIntent = Intent(this, ClipboardSyncService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
    }
}
