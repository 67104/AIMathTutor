# Building the Android APK (Phase 9)

> **Read this first — Android Studio cannot build this app on its own.**
> Android Studio builds Java/Kotlin projects with Gradle; it has no idea how to
> compile a Python/Kivy app. A Kivy app **must** be packaged by Buildozer /
> python-for-android, which is POSIX-only (Linux / WSL2 / Docker).
>
> **The right division of labour:**
> * **Android Studio** → install the SDK + NDK, run the emulator, use `adb` /
>   `logcat`, and sign releases. (You can also open the Gradle project that
>   python-for-android generates — see "Using Android Studio" below.)
> * **Buildozer (in WSL2/Docker)** → does the actual Python → APK compile.
>
> Develop/test on Windows with `python main.py`; package with the steps below.

---

## Using Android Studio in this workflow

Android Studio does the parts it's good at; Buildozer does the Python compile.

1. **Install Android Studio** (Windows). In **Settings → SDK Manager** install:
   - Android SDK Platform **34**, Build-Tools **34.x**
   - **NDK (Side by side) 25.x** and **CMake** (SDK Tools tab)
   - An emulator image (Device Manager) or enable USB debugging on a phone.

2. **Point Buildozer at Android Studio's SDK/NDK** (so it doesn't re-download).
   In WSL, the Windows SDK is visible under `/mnt/c/Users/Admin/AppData/Local/Android/Sdk`,
   but builds are far more reliable using a **Linux-side** SDK. Easiest: let
   Buildozer manage its own SDK/NDK in WSL (Option A), and use Android Studio only
   for the **emulator, adb, logcat, and signing**.

3. **Open the generated Gradle project in Android Studio (optional).**
   After a Buildozer run, python-for-android leaves a Gradle project at:
   ```
   .buildozer/android/platform/build-*/dists/aimathtutor/
   ```
   Open that folder in Android Studio to build/run/debug/sign it with the IDE,
   inspect the manifest, or step through native crashes with logcat. You still
   needed Buildozer once to *generate* it.

4. **Run + debug on the emulator/device** launched from Android Studio:
   ```bash
   adb install -r bin/aimathtutor-*-debug.apk
   adb logcat | grep -i python      # watch app logs / tracebacks
   ```

---

## Option A — WSL2 (does the Python→APK compile; pair with Android Studio above)

1. **Install WSL2 + Ubuntu** (PowerShell, admin), then reboot:
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

2. **Inside Ubuntu**, install the toolchain:
   ```bash
   sudo apt update && sudo apt install -y \
       git zip unzip openjdk-17-jdk python3-pip python3-venv \
       autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
       libffi-dev libssl-dev build-essential ccache libltdl-dev
   python3 -m pip install --user --upgrade buildozer Cython==0.29.36
   ```

3. **Copy the project into the WSL filesystem** (building on `/mnt/c` is slow and
   can hit permission issues — use the native Linux fs):
   ```bash
   cp -r /mnt/c/Users/Admin/AIMathTutor ~/AIMathTutor
   cd ~/AIMathTutor
   ```

4. **Build** (first build downloads the SDK/NDK — 20–40 min; later builds are minutes):
   ```bash
   buildozer -v android debug
   ```
   Output: `bin/aimathtutor-0.1.0-arm64-v8a_armeabi-v7a-debug.apk`
   Install/run/debug it via Android Studio's emulator or `adb` (see above).

5. **Install on a phone** (USB debugging on) from Windows or WSL:
   ```bash
   adb install -r bin/aimathtutor-*-debug.apk
   ```

---

## Option B — Docker (most reproducible; good for CI)

From the project root on any Docker host (including Docker Desktop on Windows):
```bash
docker run --rm -v "${PWD}:/home/user/app" -w /home/user/app \
    kivy/buildozer:latest android debug
```
The `kivy/buildozer` image ships the full toolchain. The APK lands in `bin/`.

> On Windows PowerShell use `${PWD}`; the volume mount makes `bin/` appear in your
> project folder.

---

## Option C — GitHub Actions (hands-off cloud build)
Use the community action `ArtemSBulgakov/buildozer-action@v1` (or run the Docker
image above in a `ubuntu-latest` job) and upload `bin/*.apk` as an artifact. This
avoids maintaining a local Linux toolchain entirely.

---

## Signing a release build
Debug APKs are auto-signed with a throwaway key. For a Play-Store release:
```bash
buildozer android release
# then sign bin/*-release-unsigned.apk with your keystore:
keytool -genkey -v -keystore my.keystore -alias aimt -keyalg RSA -keysize 2048 -validity 10000
$ANDROID_HOME/build-tools/34.0.0/apksigner sign --ks my.keystore bin/*-release-unsigned.apk
```

---

## On-device OCR options (Tesseract is omitted on Android)
The desktop app uses the Tesseract binary; bundling it into an APK is heavy and
fiddly. `buildozer.spec` therefore leaves it out and the app **degrades to typed
input** (the recognised-text field is always editable). To add real mobile OCR,
pick one:

| Option | How | Trade-off |
|---|---|---|
| **Google ML Kit Text Recognition** | via `pyjnius` calling the Android ML Kit API | Best accuracy, on-device, free; needs Java bridging code |
| **tesseract via `tesseract` p4a recipe** | add a Tesseract recipe + bundle `eng.traineddata` | Large APK, slower, weakest on math |
| **Cloud OCR** | POST image to an API | Conflicts with the offline/no-paid-cloud requirement |

Recommended: ML Kit through pyjnius, behind the existing `ocr_service` interface
so the rest of the app is unchanged. Keep the editable-draft UX regardless.

---

## Common first-build failures & fixes

| Symptom | Cause | Fix |
|---|---|---|
| `Command failed: ... aidl` / SDK licence | SDK licences not accepted | `yes | ~/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager --licenses` |
| Build hangs at "Downloading Android SDK" | first-run downloads | Let it finish (20–40 min); don't kill it |
| `opencv` recipe fails to compile | wrong NDK / low RAM | Use `android.ndk = 25b`; give the VM/container ≥ 4 GB RAM |
| `Cython` errors | Cython too new | Pin `Cython==0.29.36` (as above) |
| APK installs but crashes on launch | a `requirements` lib has no working recipe | Check `adb logcat`; remove/replace the offending lib (matplotlib is the usual suspect) |
| Huge APK (>100 MB) | OpenCV + Matplotlib + both ABIs | Drop `armeabi-v7a`; consider replacing Matplotlib with a Kivy-drawn chart |
| Black screen / no window | `.kv` not bundled | Ensure `kv` is in `source.include_exts` (it is) |
| Permissions do nothing | runtime grant not requested | Handled in `app/utils/platform_utils.py` (called from CameraScreen) |

See also [PROBLEMS.md](PROBLEMS.md) for the wider risk register (APK size,
battery, memory, Android compatibility).
