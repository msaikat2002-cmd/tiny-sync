# Release Instructions

## Pre-release Checklist

### Windows
- [ ] Build in Release configuration
- [ ] Test on Windows 7 SP1 (32-bit)
- [ ] Verify memory usage < 10 MB
- [ ] Verify CPU usage ~0% when idle
- [ ] Test auto-start functionality
- [ ] Test firewall rule creation
- [ ] Verify no visible window/console

### Android
- [ ] Build signed release APK
- [ ] Test on Android 5.0 (API 21)
- [ ] Test on latest Android version
- [ ] Verify notification appears
- [ ] Test foreground service
- [ ] Verify clipboard sync works both directions
- [ ] Test reconnection after network loss

## Release Package Contents

### Windows Distribution
```
TinyClipboardSync-Windows/
├── TinyClipboardSync.exe
├── README.txt
└── setup-firewall.bat
```

Create `setup-firewall.bat`:
```batch
@echo off
netsh advfirewall firewall add rule name="Clipboard Sync" dir=in action=allow protocol=TCP localport=5555
echo Firewall rule added successfully.
pause
```

Create `README.txt`:
```
Tiny Clipboard Sync for Windows

1. Run TinyClipboardSync.exe
2. Firewall rule will be created automatically (or run setup-firewall.bat)
3. Note your IP address (run: ipconfig)
4. Enter this IP in the Android app
5. The application runs silently in background

To uninstall:
- Delete these files
- Remove from startup if needed

Requirements:
- Windows 7 SP1 or later
- .NET Framework 4.0 or later
```

### Android Distribution
```
TinyClipboardSync-Android/
├── app-release.apk
├── README.txt
└── installation-guide.txt
```

Create `installation-guide.txt`:
```
Installation Instructions:

Method 1 - Direct Install:
1. Transfer app-release.apk to your Android device
2. Enable "Install from Unknown Sources" in Settings
3. Open the APK file and install

Method 2 - ADB:
1. Connect device to computer
2. Run: adb install app-release.apk

First Use:
1. Open Clipboard Sync app
2. Enter your Windows PC IP address
3. Tap "Save and Start"
4. Service will start automatically

The app shows a persistent notification while running.
```

## Version Numbering

Use semantic versioning: MAJOR.MINOR.PATCH

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes only

Update version in:
- `windows/properties/AssemblyInfo.cs`
- `android/app/build.gradle` (versionCode, versionName)

## Git Tagging

```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

## Distribution Channels

### GitHub Releases
1. Create release on GitHub
2. Upload Windows ZIP package
3. Upload Android APK
4. Add changelog

### Direct Distribution
- Share via local network
- USB transfer
- Email/Cloud storage

## Post-release

### Documentation
- Update README with known issues
- Document troubleshooting steps
- Create FAQ if needed

### Support
- Monitor for bug reports
- Collect user feedback
- Plan improvements

## Rollback Procedure

If critical bug found:
1. Remove release from distribution
2. Create hotfix branch
3. Fix issue
4. Release new patch version
5. Notify users of update
