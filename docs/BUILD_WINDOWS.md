# Windows Build Instructions

## Prerequisites

- Visual Studio 2010 or later (Express Edition works)
- OR .NET Framework 4.0 SDK + MSBuild

## Method 1: Visual Studio

1. Open `windows/TinyClipboardSync.csproj` in Visual Studio
2. Set configuration to "Release"
3. Set platform to "x86"
4. Build > Build Solution
5. Output: `windows/bin/Release/TinyClipboardSync.exe`

## Method 2: MSBuild Command Line

Open Developer Command Prompt for Visual Studio or ensure MSBuild is in PATH:

```batch
cd windows
msbuild TinyClipboardSync.csproj /p:Configuration=Release /p:Platform=x86
```

Output: `windows/bin/Release/TinyClipboardSync.exe`

## Method 3: csc (C# Compiler Direct)

If you have the .NET Framework installed:

```batch
cd windows\src
csc /target:winexe /out:../TinyClipboardSync.exe ^
    /reference:System.dll ^
    /reference:System.Core.dll ^
    /reference:System.Windows.Forms.dll ^
    Program.cs ClipboardMonitor.cs NetworkClient.cs RegistryHelper.cs
```

## Verification

The executable should be approximately 8-12 KB in size.

Run the executable - it should start silently with no visible window.

Check Task Manager for "TinyClipboardSync.exe" process.

## Creating Windows Firewall Rule

Required for Android to connect:

```batch
netsh advfirewall firewall add rule name="Clipboard Sync" dir=in action=allow protocol=TCP localport=5555
```

## Auto-Start Configuration

The application automatically adds itself to Windows startup via Registry.

To verify:
1. Press Win+R
2. Type `shell:startup`
3. Or check Registry: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`

## Uninstall

1. Delete the executable
2. Remove from startup: Run `regedit`, navigate to above key, delete "TinyClipboardSync" value
3. Remove firewall rule: `netsh advfirewall firewall delete rule name="Clipboard Sync"`
