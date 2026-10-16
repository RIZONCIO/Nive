REM  Desativar modo hibernação
powercfg -h off

REM Paint

winget uninstall 9PCFS5B6T72H

REM Vínculo com celular

winget uninstall MSIX\Microsoft.YourPhone_1.24062.101.0_x64__8wekyb3d8bbwe

REM Microsoft Edge

winget uninstall Microsoft.Edge
winget uninstall ARP\Machine\X86\Microsoft Edge Update
winget uninstall Microsoft.EdgeWebView2Runtime
winget uninstall MSIX\Microsoft.MicrosoftEdge.Stable_126.0.2592.113_neutral__8we…

REM Desinstalar COMPLETAMENTE a Cortana

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-AppxPackage -allusers Microsoft.549981C3F5F10 | Remove-AppxPackage"

REM Remoção OneDrive

winget uninstall MSIX\Microsoft.OneDriveSync_24116.609.5.0_neutral__8wekyb3d8bbwe
winget uninstall Microsoft.OneDrive
taskkill /f /im OneDrive.exe
%SystemRoot%\System32\OneDriveSetup.exe /uninstall 
%SystemRoot%\SysWOW64\OneDriveSetup.exe /uninstall

REM  Remoção Apps Store 

Powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "Get-AppxPackage | where-object {$_.name -notlike '*GamingApp*'} | where-object {$_.name -notlike '*Winget*'} |where-object {$_.name -notlike '*store*'} |  where-object {$_.name -notlike '*DesktopAppInstaller*'} |where-object {$_.name -notlike '*xbox*'} | where-object {$_.name -notlike '*terminal*'} |Remove-AppxPackage"