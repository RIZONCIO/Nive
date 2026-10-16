rem reg add "HKCU\Control Panel\Desktop" /v "UserPreferencesMask" /t REG_BINARY /d 9032078010000000 /f
rem reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" REG_SZ /d 0 /f
rem reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "TaskbarAnimations" /t REG_DWORD /d 0 /f
rem reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /V "IconsOnly" /T REG_DWORD /D 1 /F
rem reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /V "ListviewAlphaSelect" /T REG_DWORD /D 1 /F
rem reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v "DragFullWindows" /t REG_DWORD /d 0 /f
rem reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v "FontSmoothing" /t REG_SZ /d 2 /f
rem reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /V "ListviewShadow" /T REG_DWORD /D 1 /F
rem reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\DWM" /V "AlwaysHibernateThumbnails" /T REG_DWORD /D 0 /F