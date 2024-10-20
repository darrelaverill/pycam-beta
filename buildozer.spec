[app]

# (str) Title of your application
title = pycam

# (str) Package name
package.name = pycam

# (str) Package domain (needed for android/ios packaging)
package.domain = org.pycam

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directories to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy

# (str) Presplash of the application
presplash.filename = images/pycamicon.png

# (str) Icon of the application
icon.filename = images/pycamicon.png

# (list) Supported orientations
orientation = portrait

#
# OSX Specific
#

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 1.9.1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
#android.permissions = android.permission.INTERNET

# (int) Target Android API, should be as high as possible.
#android.api = 31

# (int) Minimum API your APK / AAB will support.
#android.minapi = 21

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
