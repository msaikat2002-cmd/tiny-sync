# Android Build Instructions

## Prerequisites

- Android Studio Arctic Fox (2020.3.1) or later
- JDK 8 or later
- Android SDK API 30

## Method 1: Android Studio

1. Open Android Studio
2. File > Open > Select `android` folder
3. Wait for Gradle sync to complete
4. Build > Build Bundle(s) / APK(s) > Build APK(s)
5. Output: `android/app/build/outputs/apk/release/app-release.apk`

## Method 2: Command Line (Gradle)

Ensure you have Gradle installed or use the wrapper:

```bash
cd android
chmod +x gradlew
./gradlew assembleRelease
```

Output: `app/build/outputs/apk/release/app-release.apk`

## Method 3: Command Line with Full Path

```bash
cd android
./gradlew :app:assembleRelease --release
```

## Signing for Release

### Create Keystore (First Time Only)

```bash
keytool -genkey -v -keystore my-release-key.keystore -alias clipboard_sync -keyalg RSA -keysize 2048 -validity 10000
```

### Configure Signing in build.gradle

Add to `app/build.gradle`:

```groovy
android {
    ...
    signingConfigs {
        release {
            storeFile file("path/to/my-release-key.keystore")
            storePassword "your-password"
            keyAlias "clipboard_sync"
            keyPassword "your-password"
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

### Generate Signed APK via Android Studio

1. Build > Generate Signed Bundle / APK
2. Select APK
3. Choose or create keystore
4. Select "release" variant
5. Click Finish

## Installation

### Via ADB

```bash
adb install app/build/outputs/apk/release/app-release.apk
```

### Direct on Device

Transfer APK to device and install (enable "Install from Unknown Sources")

## Verification

After installation:
1. App icon "Clipboard Sync" should appear
2. On first launch, setup screen appears
3. After entering IP, notification appears
4. Service runs in background

## Troubleshooting

### Gradle Sync Issues

```bash
./gradlew clean
./gradlew build --refresh-dependencies
```

### SDK Location

Create/edit `local.properties`:

```
sdk.dir=/path/to/android/sdk
```

### Out of Memory

Edit `gradle.properties`:

```
org.gradle.jvmargs=-Xmx1024m
```

### Build Cache Issues

```bash
rm -rf .gradle build app/build
./gradlew clean assembleRelease
```
