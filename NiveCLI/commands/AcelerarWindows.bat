Bootcfg /timeout 10

REM Optimização no Boot
REG ADD "HKLM\SOFTWARE\Microsoft\Dfrg\BootOptimizeFunction" /v Enable /t REG_SZ /d Y /f
REG ADD "HKLM\SOFTWARE\Microsoft\Dfrg\BootOptimizeFunction" /v OptimizeComplete /t REG_SZ /d Yes /f

REM Menu Iniciar Máis Rápido
REG ADD "HKCU\Control Panel\Desktop" /v MenuShowDelay /t REG_SZ /d 100 /f
REG ADD "HKU\.DEFAULT\Control Panel\Deskstop" /v MenuShowDelay /t REG_SZ /d 100 /f

REM Aumentar a Taxa de Upload
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters" /v DefaultSendWindow /t REG_DWORD /d 0x00018000 /f
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v EnablePMTUDiscovery /t REG_DWORD /d 0x00000001 /f

REM Limpeza de Disco Mais Eficaz (Prevenção contra Travamentos)
REG DELETE "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Compress old files" /f

REM Otimização TCP/IP
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Lanmanserver\parameters" /v SizReqBuf /t REG_DWORD /d 0x00014596 /f
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider" /v class /t REG_DWORD /d 0x00000001 /f
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider" /v DnsPriority /t REG_DWORD /d 0x00000007 /f
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider" /v HostsPriority /t REG_DWORD /d 0x00000006 /f
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider" /v LocalPriority /t REG_DWORD /d 0x00000005 /f
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider" /v NetbtPriority /t REG_DWORD /d 0x00000008 /f

REM Otimização para o Cache de DNS
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v CacheHashTableBucketSize /t REG_DWORD /d 0x00000001 /f
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v CacheHashTableSize /t REG_DWORD /d 0x00000180 /f
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v MaxCacheEntryTtLimit /t REG_DWORD /d 0x0000fa00 /f
REG ADD "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v MaxSOACacheEntryTtLimit /t REG_DWORD /d 0x0000012d /f

REM Limpar Arquivos Temporários do Internet Explorer
REG ADD "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Cache" /v Persistent /t REG_DWORD /d 0x00000000 /f

REM Habiltar agendamento de aceleração de GPU 

REG ADD "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /d 2 /t REG_DWORD /f

REM  Habiltar modo compacto no Explorador de Arquivos 

REG ADD "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v UseCompactMode /d 1 /t REG_DWORD /f

REM  Desabilitar Aplicativos em Segundo Plano 

reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy" /v "LetAppsRunInBackground" /t REG_DWORD /d 2 /f
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy" /V "LetAppsRunInBackground_UserInControlOfTheseApps" /F
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy" /V "LetAppsRunInBackground_ForceAllowTheseApps" /F
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy" /V "LetAppsRunInBackground_ForceDenyTheseApps" /F

REM  Melhorar qualidade papel de parede 

reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v "JPEGImportQuality" /t REG_DWORD /d 00000064 /f

REM *** Otimizar Agendador para Jogos ***
REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /V "GPU Priority" /T REG_DWORD /D 8 /F
REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /V Priority /T REG_DWORD /D 6 /F
REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /V "Scheduling Category" /T REG_SZ /D High /F

