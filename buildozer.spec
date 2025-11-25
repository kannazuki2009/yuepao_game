[app]
title = 月抛大作战
package.name = yuepaogame
package.domain = org.yuepao

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1
requirements = python3,kivy

# Kivy configuration
fullscreen = 0
orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1

# Android specific
android.permissions = INTERNET
android.api = 30
android.minapi = 21
android.sdk = 20
android.ndk = 23b
android.private_storage = True
android.accept_sdk_license = True

# Presplash and icon (optional)
# presplash.filename = assets/presplash.png
# icon.filename = assets/icon.png