# Tiny Clipboard Sync

Minimal clipboard synchronization system over LAN.

## Features

- Synchronizes clipboard between Windows and Android
- Works over local network (Wi-Fi)
- No cloud, no internet required
- Minimal resource usage
- No GUI on Windows (background process)
- Minimal UI on Android (notification only)

## Requirements

### Windows
- Windows 7 SP1 or later (32-bit or 64-bit)
- .NET Framework 4.0 or later

### Android
- Android 5.0 (API 21) or later
- Wi-Fi connection to same network as Windows PC

## Project Structure

```
tiny-clipboard-sync/
├── windows/                    # Windows application
│   ├── TinyClipboardSync.csproj
│   ├── src/
│   │   ├── Program.cs
│   │   ├── ClipboardMonitor.cs
│   │   ├── NetworkClient.cs
│   │   └── RegistryHelper.cs
│   └── properties/
│       └── AssemblyInfo.cs
├── android/                    # Android application
│   ├── build.gradle
│   ├── settings.gradle
│   ├── gradle.properties
│   ├── app/
│   │   ├── build.gradle
│   │   ├── proguard-rules.pro
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       ├── kotlin/com/tinyclipboardsync/
│   │       │   ├── SetupActivity.kt
│   │       │   └── ClipboardSyncService.kt
│   │       └── res/
│   │           ├── layout/activity_setup.xml
│   │           ├── values/strings.xml
│   │           └── mipmap-*/ic_launcher.xml
│   └── gradle/wrapper/
│       └── gradle-wrapper.properties
└── README.md
```

## Build Instructions

### Windows Executable

1. Open Visual Studio (any version with .NET Framework 4.0 support)
2. Open `windows/TinyClipboardSync.csproj`
3. Build in Release configuration
4. Output: `windows/bin/Release/TinyClipboardSync.exe`

Or using MSBuild command line:
```batch
msbuild windows\TinyClipboardSync.csproj /p:Configuration=Release /p:Platform=x86
```

### Android APK

1. Open Android Studio
2. Import the `android` folder as a project
3. Wait for Gradle sync to complete
4. Build > Generate Signed Bundle / APK
5. Choose APK
6. Create or select keystore
7. Build release APK

Or using command line:
```bash
cd android
./gradlew assembleRelease
```

Output: `android/app/build/outputs/apk/release/app-release.apk`

## Usage

### First Time Setup

1. **Find Windows IP Address:**
   - On Windows, open Command Prompt
   - Run `ipconfig`
   - Note the IPv4 address (e.g., 192.168.1.100)

2. **Run Windows Application:**
   - Copy `TinyClipboardSync.exe` to desired location
   - Run the executable
   - It will run silently in background
   - Auto-start is enabled automatically

3. **Setup Android App:**
   - Install the APK on Android device
   - Open the app
   - Enter the Windows PC IP address
   - Tap "Save and Start"
   - Service will start and show notification

### Normal Operation

- Both devices must be on the same Wi-Fi network
- Clipboard changes are automatically synchronized
- Android shows persistent notification with status
- Windows runs silently in background

### Reconnection

- If connection is lost, Android automatically reconnects every 5 seconds
- Windows automatically attempts to connect on startup

## Protocol

The application uses a simple JSON protocol over TCP port 5555:

```json
{"type":"clipboard","content":"text content"}
```

Special characters are escaped:
- `\` becomes `\\`
- `"` becomes `\"`
- newline becomes `\n`
- carriage return becomes `\r`
- tab becomes `\t`

## Technical Details

### Windows
- Uses `AddClipboardFormatListener` for efficient clipboard monitoring
- No polling - uses Windows clipboard change notifications
- Runs as message-only window (no taskbar entry)
- Single instance enforced via Mutex
- Auto-start via Registry Run key

### Android
- Foreground service for reliable operation
- Notification channel for Android 8.0+
- SharedPreferences for IP storage
- Automatic reconnection on disconnect

## Troubleshooting

### Connection Issues
1. Ensure both devices are on same Wi-Fi network
2. Check Windows Firewall - allow port 5555
3. Verify Windows IP address is correct
4. Try pinging Windows from Android

### Windows Firewall Rule
```batch
netsh advfirewall firewall add rule name="Clipboard Sync" dir=in action=allow protocol=TCP localport=5555
```

### Clipboard Not Syncing
1. Ensure service is running on Android (check notification)
2. Check Windows application is running (Task Manager)
3. Try copying text again after connection established

## License

Public Domain / MIT License
