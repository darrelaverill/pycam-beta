[app]
# (str) Title of your application
title = pycam

# (str) Package name
package.name = pycam

# (str) Package domain (needed for android packaging)
package.domain = com.pythonapp.pycam

# (str) Source code where the main.py lives
source.dir = .

# (list) Application requirements
requirements = python3, kivy, opencv-python, opencv-python-headless, numpy

# (str) Supported orientation (one of: landscape, sensorLandscape, portrait, sensorPortrait, all)
orientation = portrait

# (str) Icon of the application
icon.filename = %(source.dir)s/images/pycamicon.png

# (str) Version of your application
version = 0.1

# (list) Permissions
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (str) Minimum API your APK will support
android.minapi = 21

# (str) Presplash image
presplash.filename = %(source.dir)s/images/pycamicon.png

# Additional [buildozer] section
[buildozer]
# (str) Warn on root
warn_on_root = 1
