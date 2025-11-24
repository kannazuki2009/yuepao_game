[app]
title = 月抛大作战
package.name = yuepao
package.domain = org.yourname
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0
requirements = python3, kivy, android
orientation = portrait

# 添加这些Android特定设置
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25.1.8937393

[buildozer]
log_level = 2
warn_on_root = 1