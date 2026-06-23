[app]

# (str) Title of your application
title = 成本估算软件

# (str) Package name
package.name = costestimation

# (str) Package domain (needed for android/ios packaging)
package.domain = org.costestimation

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let you add files/sharedfolders)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
source.include_patterns = cost_data.json

# (list) Source files to exclude (let you remove files/sharedfolders)
source.exclude_exts = spec

# (list) List of directory to exclude from the source
source.exclude_dirs = tests, bin

# (list) List of patterns to ignore
source.exclude_patterns = license,readme*.md,*.pyc

# (str) Application versioning (method 1)
version = 1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (str) Application entrypoint
main.py = main.py

# (list) List of requirements to install
requirements = python3,kivy

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of permissions to request
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 23b

# (bool) Use Android's private storage (recommended for new apps)
android.private_storage = True

# (str) Android log filter
android.log_filter = *:S python:V

# (str) Android additional author
# android.extra_author = None

# (str) Android AS project name (used for packaging)
# android.entitlements = None

# (str) Java package name for the auto-generated Java file
# android.java_package_name = org.test.cost

# (list) Python for android. Add dependencies to the APK
# android.add_src = 

# (str) A filename that includes the list of libraries to link the APK against
# android.libraries =

# (bool) Strip the debug symbols from the libraries
android.strip = True

# (str) The Android app category
android.category = PRODUCTIVITY

# (bool) Enable or disable the AndroidX support
android.enable_androidx = True

# (list) Add aar or jar files to the APK
# android.add_aars =

# (list) Gradle dependencies to compile
# android.gradle_dependencies =

# (bool) Enable R8 optimization for the APK
android.use_r8 = True

# (str) The path to your debug keystore (needed for building debug APK)
# android.debug_keystore = 

# (bool) Enable the debug mode for Android app
android.debug = True

# (bool) Enable the acceptance of all licenses
android.accept_sdk_license = True

# (str) Path to the buildozer local directory
buildozer.sdk.dir = 

# (str) Path to the buildozer android directory
buildozer.android_dir = 

# (int) Log level (0 = ERROR, 1 = WARNING, 2 = INFO, 3 = DEBUG)
log_level = 2

# (list) Android arch to build for
android.archs = arm64-v8a

# (str) The Android app theme
# android.apptheme = @android:style/Theme.DeviceDefault

# (str) The app locale
# android.applocale = 

# (str) Use the Gradle to build the APK
android.gradle = True

# (str) One of p4a (python-for-android) or we (wheels-engine) to use
android.bootstrap = sdl2

# (str) The branch of python-for-android to use
# android.p4a_branch = develop

# (int) Number of retries to download the dependencies
download.retries = 3

[buildozer]

# (int) Log level (0 = ERROR, 1 = WARNING, 2 = INFO, 3 = DEBUG)
log_level = 2

# (int) Number of threads to use for building
# parallel_builds = 1

# (str) Path to the buildozer temporary directory
# buildozer.build_dir = /.buildozer

# (str) Path to the buildozer binary directory
# buildozer.bin_dir = ./bin

# (str) The Android SDK directory
# android.sdk_path = ~/.buildozer/android/platform/android-sdk

# (str) The Android NDK directory
# android.ndk_path = ~/.buildozer/android/platform/android-ndk

# (str) The Ant executable directory
# android.ant_path = 

# (str) If set, use this as the Android SDK build tools version
# android.build_tools = 33.0.1

# (str) Python for android repo URL
# p4a.url = https://github.com/kivy/python-for-android.git

# (str) Python for android branch
# p4a.branch = develop
