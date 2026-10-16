@echo off
:: ============================================================
:: NOME   : NiveSoftwareAuxiliares.bat
:: AUTOR  : Inspirado no ScriptNive de Ryan Vinicius
:: VERSAO : 2.0
:: DESCR  : Instala/Desinstala softwares auxiliares via Winget/Choco
::          e organiza TODOS os atalhos em uma pasta unica central.
:: ============================================================

CHCP 65001 >nul

:: --------- Checagem de Administrador ---------
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo  [ERRO] Execute este script como ADMINISTRADOR.
    echo  Feche esta janela, clique com botao direito no arquivo
    echo  e escolha "Executar como administrador".
    echo ============================================================
    pause
    exit /b
)

setlocal enabledelayedexpansion

:: --------- Pasta central de ferramentas ---------
set "NIVE_FOLDER=C:\Nive\NiveFerramentas"
if not exist "%NIVE_FOLDER%" mkdir "%NIVE_FOLDER%" >nul 2>&1

:: Cria atalho unico na Area de Trabalho para a pasta central
if not exist "%USERPROFILE%\Desktop\Nive - Software Auxiliares.lnk" (
    powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%USERPROFILE%\Desktop\Nive - Software Auxiliares.lnk'); $sc.TargetPath = '%NIVE_FOLDER%'; $sc.Save()" >nul 2>&1
)

title NiveSoftwareAuxiliares 2.0

:menu
cls
color 9
echo ============================================================
echo    Nive Software Auxiliares - Gerenciador de Instalacao
echo ============================================================
echo    Pasta central: %NIVE_FOLDER%
echo ============================================================
echo.
echo  [1]  Rufus Portable     - Cria pen drives bootaveis (USB)
echo  [2]  Everything         - Busca arquivos instantaneamente
echo  [3]  HWiNFO             - Monitora hardware, temperaturas e sensores
echo  [4]  CPU-Z              - Informacoes detalhadas do processador
echo  [5]  GPU-Z              - Informacoes da placa de video
echo  [6]  CrystalDiskInfo    - Saude de HDs e SSDs (S.M.A.R.T.)
echo  [7]  CrystalDiskMark    - Teste de velocidade de disco
echo  [8]  WizTree            - Analisa espaco em disco rapidamente
echo  [9]  DDU                - Remove drivers de video completamente
echo  [10] AdwCleaner         - Remove adware e programas indesejados
echo  [11] TestDisk           - Recupera particoes e arquivos perdidos
echo  [12] Abrir pasta central de ferramentas
echo  [0]  Sair
echo ============================================================
set /p choice="Escolha uma opcao: "

if "%choice%"=="1"  goto set_rufus
if "%choice%"=="2"  goto set_everything
if "%choice%"=="3"  goto set_hwinfo
if "%choice%"=="4"  goto set_cpuz
if "%choice%"=="5"  goto set_gpuz
if "%choice%"=="6"  goto set_crystaldiskinfo
if "%choice%"=="7"  goto set_crystaldiskmark
if "%choice%"=="8"  goto set_wiztree
if "%choice%"=="9"  goto set_ddu
if "%choice%"=="10" goto set_adwcleaner
if "%choice%"=="11" goto set_testdisk
if "%choice%"=="12" ( start "" "%NIVE_FOLDER%" & goto menu )
if "%choice%"=="0"  exit /b

echo Opcao invalida!
timeout /t 2 >nul
goto menu


:: ============================================================
:: DEFINICAO DOS SOFTWARES
:: ============================================================
:set_rufus
set "software_name=Rufus Portable"
set "winget_id=Rufus.Rufus"
set "choco_pkg=rufus"
set "exe_search=rufus*.exe"
set "shortcut_name=Rufus"
goto check_software

:set_everything
set "software_name=Everything"
set "winget_id=voidtools.Everything"
set "choco_pkg=everything"
set "exe_search=Everything.exe"
set "shortcut_name=Everything"
goto check_software

:set_hwinfo
set "software_name=HWiNFO"
set "winget_id=REALiX.HWiNFO"
set "choco_pkg=hwinfo"
set "exe_search=HWiNFO64.exe"
set "shortcut_name=HWiNFO"
goto check_software

:set_cpuz
set "software_name=CPU-Z"
set "winget_id=CPUID.CPU-Z"
set "choco_pkg=cpu-z"
set "exe_search=cpuz*.exe"
set "shortcut_name=CPU-Z"
goto check_software

:set_gpuz
set "software_name=GPU-Z"
set "winget_id=TechPowerUp.GPU-Z"
set "choco_pkg=gpu-z"
set "exe_search=GPU-Z.exe"
set "shortcut_name=GPU-Z"
goto check_software

:set_crystaldiskinfo
set "software_name=CrystalDiskInfo"
set "winget_id=CrystalDewWorld.CrystalDiskInfo"
set "choco_pkg=crystaldiskinfo"
set "exe_search=DiskInfo64.exe"
set "shortcut_name=CrystalDiskInfo"
goto check_software

:set_crystaldiskmark
set "software_name=CrystalDiskMark"
set "winget_id=CrystalDewWorld.CrystalDiskMark"
set "choco_pkg=crystaldiskmark"
set "exe_search=DiskMark64.exe"
set "shortcut_name=CrystalDiskMark"
goto check_software

:set_wiztree
set "software_name=WizTree"
set "winget_id=AntibodySoftware.WizTree"
set "choco_pkg=wiztree"
set "exe_search=WizTree64.exe"
set "shortcut_name=WizTree"
goto check_software

:set_ddu
set "software_name=DDU (Display Driver Uninstaller)"
set "winget_id=Wagnardsoft.DisplayDriverUninstaller"
set "choco_pkg=ddu"
set "exe_search=Display Driver Uninstaller.exe"
set "shortcut_name=DDU"
goto check_software

:set_adwcleaner
set "software_name=AdwCleaner"
set "winget_id=Malwarebytes.AdwCleaner"
set "choco_pkg=adwcleaner"
set "exe_search=AdwCleaner.exe"
set "shortcut_name=AdwCleaner"
goto check_software

:set_testdisk
set "software_name=TestDisk"
set "winget_id=CGSecurity.TestDisk"
set "choco_pkg=testdisk"
set "exe_search=testdisk_win.exe"
set "shortcut_name=TestDisk"
goto check_software


:: ============================================================
:: VERIFICA SE ESTA INSTALADO E PERGUNTA O QUE FAZER
:: ============================================================
:check_software
cls
echo ============================================================
echo    %software_name%
echo ============================================================
echo.
echo Verificando status no sistema, aguarde...
winget list --id %winget_id% 2>nul | findstr /i "%winget_id%" >nul
if !errorlevel! equ 0 (
    set "installed=1"
) else (
    set "installed=0"
)

cls
echo ============================================================
echo    %software_name%
echo ============================================================
echo.
if "!installed!"=="1" (
    echo STATUS: [INSTALADO]
    echo.
    echo O que deseja fazer?
    echo   [D] Desinstalar
    echo   [V] Voltar ao menu
    echo.
    set /p acao="Escolha: "
    if /i "!acao!"=="d" goto uninstall_software
    goto menu
) else (
    echo STATUS: [NAO INSTALADO]
    echo.
    echo O que deseja fazer?
    echo   [I] Instalar
    echo   [V] Voltar ao menu
    echo.
    set /p acao="Escolha: "
    if /i "!acao!"=="i" goto install_software
    goto menu
)


:: ============================================================
:: INSTALACAO (Winget -> Choco) + ATALHO CENTRALIZADO
:: ============================================================
:install_software
cls
echo ============================================================
echo    Instalando: %software_name%
echo ============================================================
echo.

echo [1/3] Tentando instalar via WINGET...
winget install --id %winget_id% -e --accept-package-agreements --accept-source-agreements --silent
if !errorlevel! equ 0 (
    echo.
    echo [OK] Instalado via Winget.
    goto after_install
)

echo.
echo [AVISO] Winget falhou. Tentando via Chocolatey...
where choco >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERRO] Chocolatey nao esta instalado. Nao foi possivel continuar.
    pause
    goto menu
)
choco install %choco_pkg% -y
if !errorlevel! equ 0 (
    echo.
    echo [OK] Instalado via Chocolatey.
    goto after_install
) else (
    echo.
    echo [ERRO] Nao foi possivel instalar %software_name%.
    pause
    goto menu
)

:after_install
echo.
echo [2/3] Procurando executavel para criar atalho na pasta central...
call :create_shortcut "%exe_search%" "%shortcut_name%"

echo.
echo [3/3] Concluido. Verifique a pasta: %NIVE_FOLDER%
echo.
pause
goto menu


:: ============================================================
:: DESINSTALACAO
:: ============================================================
:uninstall_software
cls
echo ============================================================
echo    Desinstalando: %software_name%
echo ============================================================
echo.
winget uninstall --id %winget_id% -e --silent
if !errorlevel! neq 0 (
    echo.
    echo [AVISO] Winget falhou. Tentando via Chocolatey...
    where choco >nul 2>&1
    if !errorlevel! equ 0 (
        choco uninstall %choco_pkg% -y
    )
)

:: Remove atalho da pasta central
if exist "%NIVE_FOLDER%\%shortcut_name%.lnk" del /q "%NIVE_FOLDER%\%shortcut_name%.lnk" >nul 2>&1

echo.
echo [OK] Processo de desinstalacao concluido.
pause
goto menu


:: ============================================================
:: ROTINA: CRIA ATALHO NA PASTA CENTRAL PROCURANDO O .EXE
:: Args: %1 = padrao do exe (aceita *)   %2 = nome do atalho
:: ============================================================
:create_shortcut
set "exe_path="
for %%D in ("C:\Program Files" "C:\Program Files (x86)" "%LOCALAPPDATA%\Programs" "%ProgramData%\chocolatey\bin") do (
    if not defined exe_path (
        if exist "%%~D" (
            for /f "delims=" %%F in ('dir /b /s "%%~D\%~1" 2^>nul') do (
                if not defined exe_path set "exe_path=%%F"
            )
        )
    )
)

if defined exe_path (
    echo Executavel encontrado: !exe_path!
    powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%NIVE_FOLDER%\%~2.lnk'); $sc.TargetPath = '!exe_path!'; $sc.WorkingDirectory = Split-Path '!exe_path!'; $sc.Save()" >nul 2>&1
    echo Atalho criado em: %NIVE_FOLDER%\%~2.lnk
) else (
    echo [AVISO] Nao foi possivel localizar o executavel "%~1" automaticamente.
    echo Abra o menu iniciar e crie o atalho manualmente se necessario.
)
exit /b