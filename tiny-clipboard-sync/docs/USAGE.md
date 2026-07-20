# Usage Guide

## Quick Start

### Step 1: Find Windows IP Address

On your Windows PC:
1. Press `Win + R`
2. Type `cmd` and press Enter
3. In the command prompt, type: `ipconfig`
4. Look for "IPv4 Address" under your network adapter
5. Note this address (e.g., `192.168.1.100`)

### Step 2: Run Windows Application

1. Copy `TinyClipboardSync.exe` to a folder on your Windows PC
2. Double-click to run
3. No window will appear - it runs silently
4. Check Task Manager to verify it's running

### Step 3: Setup Android App

1. Install the APK on your Android device
2. Open the app
3. Enter the Windows IP address you noted earlier
4. Tap "Save and Start"
5. A notification will appear showing "Clipboard Sync - Connected"

### Step 4: Test Synchronization

1. Copy text on Windows (Ctrl+C)
2. Wait 1-2 seconds
3. Paste on Android (long-press in any text field)
4. The text should appear!

5. Copy text on Android (long-press, select, copy)
6. Wait 1-2 seconds
7. Paste on Windows (Ctrl+V)
8. The text should appear!

## How It Works

### Windows Side

- Runs as a background process
- Monitors clipboard using Windows API (no polling)
- When clipboard changes, sends text to Android
- Receives text from Android and updates clipboard
- Automatically starts with Windows

### Android Side

- Runs as a foreground service
- Shows persistent notification
- Checks clipboard every second for changes
- Sends changed text to Windows
- Receives text from Windows and updates clipboard
- Automatically reconnects if connection is lost

## Network Requirements

- Both devices must be on the same Wi-Fi network
- TCP port 5555 must be allowed through Windows Firewall
- The firewall rule is created automatically on first run

## Troubleshooting

### "Connected" but not syncing

1. Try copying text again
2. Check that both devices are on same Wi-Fi
3. Restart the Android service (open app, tap Save and Start)

### Cannot connect

1. Verify Windows IP address is correct
2. Check Windows Firewall allows port 5555
3. Try pinging Windows from Android
4. Restart Windows application

### Windows Firewall Rule

To manually create firewall rule:
```batch
netsh advfirewall firewall add rule name="Clipboard Sync" dir=in action=allow protocol=TCP localport=5555
```

To remove firewall rule:
```batch
netsh advfirewall firewall delete rule name="Clipboard Sync"
```

### Android Service Stopped

If the notification disappears:
1. Open the app again
2. Tap "Save and Start"
3. Service will restart

## Tips

### Battery Optimization

Some Android devices may kill background services. To prevent this:
1. Go to Settings > Apps > Clipboard Sync
2. Tap Battery
3. Select "Unrestricted" or "Don't optimize"

### Static IP for Windows

For reliable connection, consider setting a static IP for your Windows PC:
1. Open Control Panel > Network and Sharing Center
2. Click your network connection
3. Properties > Internet Protocol Version 4 (TCP/IPv4)
4. Set a static IP address

### Multiple Devices

The system supports one Windows PC and one Android device at a time.

## Security Notes

- Communication is unencrypted (local network only)
- Only use on trusted networks
- Do not expose port 5555 to the internet
- Text content is visible in network traffic

## Uninstalling

### Windows
1. Delete `TinyClipboardSync.exe`
2. Remove from startup (optional):
   - Press `Win + R`
   - Type `shell:startup`
   - Delete shortcut if present
3. Remove firewall rule (optional)

### Android
1. Long-press app icon
2. Drag to Uninstall
3. Or go to Settings > Apps > Clipboard Sync > Uninstall
