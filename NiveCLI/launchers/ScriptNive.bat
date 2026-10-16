@ECHO OFF
:: NOME   : ScriptNive
:: AUTOR  : Ryan Vinicius Carvalho Pereira
:: VERSAO : 1.6.9
:: ============================================================

CHCP 65001 >nul

:: --------- Checagem de Administrador ---------
net session >nul 2>&1
if %errorlevel% neq 0 (
    cls
    color 4
    echo.
    echo ============================================================
    echo  [ERRO] Este script precisa ser executado como ADMINISTRADOR
    echo  para realizar diagnosticos e reparos corretamente.
    echo.
    echo  Feche esta janela, clique com o botao direito no arquivo
    echo  ScriptNive.bat e escolha "Executar como administrador".
    echo ============================================================
    pause
    exit /b
)

title ScriptNive 1.6.9

:: ============================================================
:: BOOTSTRAP - Verifica/instala arquivos em C:\Nive\
:: ============================================================
set "NIVE_DIR=C:\Nive"
set "GITHUB_ZIP=https://github.com/RIZONCIO/Script-Nive/releases/download/v1.6.9/Nive.zip"

call :bootstrap

:: Se o script nao estiver rodando de C:\Nive\, copia e relanca de la
if /i not "%~dp0"=="%NIVE_DIR%\" (
    if not exist "%NIVE_DIR%\ScriptNive.bat" copy /Y "%~f0" "%NIVE_DIR%\ScriptNive.bat" >nul 2>&1
    start "" "%NIVE_DIR%\ScriptNive.bat"
    exit /b
)

:menu
cls
color 9

echo Bem Vindo o ScriptNive 1.6.9

echo                  _________-----_____
echo        ____------           __      ----_
echo  ___----             ___------              \
echo     ----________        ----                 \
echo                -----__    ^|             _____)
echo                     __-                /     \
echo         _______-----    ___--          \    /)\
echo   ------_______      ---____            \__/  /
echo                -----__    \ --    _          /\
echo                       --__--__     \_____/   \_/\
echo                               ---^|   /          ^|
echo                                  ^| ^|___________^|
echo                                  ^| ^| ((_(_)^| )_)
echo                                  ^|  \_((_(_)^|/(_)
echo                                   \             (
echo                                    \_____________)

date /t     
time /t 

echo Computador: %computername%        Usuario: %username%

echo ==========================================
echo *  S.Informação Sobre ScriptNive         *
echo *  I.Informações gerais do Computador    *
echo *  C.Crédito Do ScriptNive               *
echo *  E.Verificar diagnóstico de erro       *
echo *  O.Otimizar Windows                    *
echo *  A.Nive Software Auxiliares            *
echo ==========================================
                   
echo            MENU TAREFAS
echo =========================================
echo * 1. Esvaziar a Lixeira                  *
echo * 2. Ativar GodMode no PC                *
echo * 3. Solucionar Erros no HD/SSD          *
echo * 4. Verificar Erros na RAM              *
echo * 5. Reparador Do Sistema                *
echo * 6. Limpar Arquivos Temporários e HD    *
echo * 7. Limpar o Cache DNS                  *
echo * 8. Painel de Controle                  *
echo * 9. Gerenciador de Tarefas              * 
echo * 10. Iniciar o MRT                      *
echo * 11. Atualizador de Programas           *
echo * 12. Resolvendo Problemas de Som        *
echo * 13. Reinstalar Software Problemático   *
echo * 14. Deletar Pastas Corrompidas         *
echo * 15. Reparo Completo do Windows         *
echo * 16. Sair                               *
echo * 17.          *
echo ==========================================

set /p opcao= Escolha uma opcao: 
echo ------------------------------
if %opcao% equ C goto opcaoC 
if %opcao% equ c goto opcaoc
if %opcao% equ I goto opcaoI
if %opcao% equ i goto opcaoi
if %opcao% equ E goto opcaoE
if %opcao% equ e goto opcaoe
if %opcao% equ S goto opcaoS
if %opcao% equ s goto opcaos
if %opcao% equ O goto opcaoO 
if %opcao% equ o goto opcaoo
if %opcao% equ A goto opcaoA
if %opcao% equ a goto opcaoa
if %opcao% equ 1 goto opcao1
if %opcao% equ 2 goto opcao2
if %opcao% equ 3 goto opcao3
if %opcao% equ 4 goto opcao4
if %opcao% equ 5 goto opcao5
if %opcao% equ 6 goto opcao6 
if %opcao% equ 7 goto opcao7
if %opcao% equ 8 goto opcao8
if %opcao% equ 9 goto opcao9
if %opcao% equ 10 goto opcao10
if %opcao% equ 11 goto opcao11
if %opcao% equ 12 goto opcao12
if %opcao% equ 13 goto opcao13
if %opcao% equ 14 goto opcao14
if %opcao% equ 15 goto opcao15
if %opcao% equ 16 goto opcao16


:opcaoS :opcaos
cls
start "" "%NIVE_DIR%\Documentação-Técnica-do-ScriptNive.pdf"
goto menu

:opcaoI :opcaoi
cls
start "" "%NIVE_DIR%\INFPC.bat"
goto menu

:opcaoC :opcaoc
goto Credito 

:opcaoE :opcaoe
cls
start perfmon /rel
goto menu

:opcaoO :opcaoo
cls 
if exist "%NIVE_DIR%\NiveBoost.bat" (
    start "" "%NIVE_DIR%\NiveBoost.bat"
) else (
    echo [ERRO] NiveBoost.bat nao encontrado em %NIVE_DIR%.
    pause
)
goto menu

:opcao1
cls
rd /S /Q c:\$Recycle.bin
echo ===================================
echo *      Lixeira Esvaziada          *
echo ===================================
pause
goto menu

:opcao2
cls
set "folderName=GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}"
set "desktopPath=%USERPROFILE%\Desktop"
mkdir "%desktopPath%\%folderName%"
echo A pasta "GodMode" foi criada na Área de Trabalho.
pause
goto menu


:opcao3
cls
WMIC diskdrive get status & WMIC diskdrive get model,status
CHKDSK /R & shutdown -r -t 30 
echo ===================================
echo *   Verificado com Sucesso        *
echo *   Erros do HD Corrigidas        *
echo ===================================
pause
goto menu

:opcao4
cls
mdsched
pause
goto menu 

:opcao5
cls
sfc /scannow &  Dism /Online /Cleanup-Image /ScanHealth & Dism /Online /Cleanup-Image /RestoreHealth & shutdown -r -t 30 
pause
goto menu

:opcao6
cls
start cleanmgr.exe & del /q /f /s "%temp%\*" & del /q/f/s "C:\Windows\Temp\*" & del /q /f /s "%windir%\Prefetch\*" & del /q /f /s "%appdata%\Microsoft\Windows\Recent\*"
echo ==================================
echo *      Temp Limpo com sucesso  *  
echo *      HD  Limpo com sucesso   *
echo ==================================
pause
goto menu

:opcao7
cls
netsh winsock reset
netsh int ip reset
ipconfig /release 
ipconfig /renew 
ipconfig /flushdns 
ipconfig /registerdns
pause
goto menu

:opcao8
cls
control.exe
goto menu

:opcao9
cls
taskmgr.exe 
goto menu

:opcao10
cls
echo Iniciando verificação do MRT...
powershell.exe -command "Start-Process 'C:\Windows\System32\MRT.exe'"
timeout /t 2 >nul
goto menu

:opcao11
cls
winget upgrade & winget upgrade --all
pause
goto menu

:opcao12
CLS
echo Reiniciando o Serviço de Áudio...
net stop audiosrv & timeout /t 5 & net start audiosrv

echo Verificando o Status dos Serviços de Áudio...
for %%S in (audiosrv AudioEndpointBuilder wuauserv) do net start %%S

echo Processo Concluído. Verifique se os problemas de áudio foram resolvidos.
pause
goto menu

:opcao13
cls
echo -------------------------------
echo  Reinstalar Software com Problema
echo -------------------------------

set "script1=%~dp0Opcao13.ps1"
set "script2=%NIVE_DIR%\Opcao13.ps1"

if exist "%script1%" (
    start "" powershell -ExecutionPolicy Bypass -NoProfile -File "%script1%"
) else if exist "%script2%" (
    start "" powershell -ExecutionPolicy Bypass -NoProfile -File "%script2%"
) else (
    echo.
    echo [ERRO] Script Opcao13.ps1 nao encontrado.
    pause
)
goto menu

:opcao14
cls
echo.
echo ==========================================
echo      DELETAR PASTA CORROMPIDA (FORÇADO)
echo ==========================================
echo.

set /p pasta=Digite o caminho COMPLETO da pasta que deseja deletar: 

if not "%pasta:~0,1%"=="\"" set "pasta=%pasta%"
set "pasta=%pasta:"=%"

if not exist "%pasta%" (
    echo.
    echo [ERRO] Caminho nao encontrado: "%pasta%"
    pause
    goto menu
)

echo.
echo Removendo atributos de protecao...
attrib -R -S -H "%pasta%" /S /D >nul 2>&1

echo.
echo Tomando posse da pasta...
takeown /f "%pasta%" /r /d y >nul 2>&1

echo.
echo Garantindo permissoes administrativas...
icacls "%pasta%" /grant administrators:F /t >nul 2>&1

echo.
echo Tentando apagar a pasta normalmente...
rd /s /q "%pasta%" >nul 2>&1

start explorer.exe >nul 2>&1

if exist "%pasta%" (
    echo.
    echo [AVISO] Pasta ainda existe... Iniciando modo ZUMBI!
    
    echo.
    echo Criando pasta temporária para forçar exclusao...
    md "%temp%\vazio" >nul 2>&1

    echo.
    echo Sobrescrevendo e sincronizando com pasta vazia...
    robocopy "%temp%\vazio" "%pasta%" /MIR >nul

    echo.
    echo Tentando apagar a pasta zumbi...
    rd /s /q "%pasta%" >nul 2>&1

    rd "%temp%\vazio" /s /q >nul 2>&1

    if exist "%pasta%" (
        echo.
        echo [FALHA] Ainda nao foi possivel excluir a pasta.
        echo Tente reiniciar o PC em modo de seguranca e usar esta opcao novamente.
    ) else (
        echo.
        echo [SUCESSO] Pasta zumbi deletada com sucesso!
    )

) else (
    echo.
    echo [SUCESSO] Pasta excluída com sucesso!
)

echo.
set /p repetir=Deseja deletar outra pasta? (s/n): 
if /i "%repetir%"=="s" (
    goto :opcao14
) else (
    goto menu
)

:opcao15
cls
if exist "%NIVE_DIR%\Reparo completo do Windows.bat" (
    start "" "%NIVE_DIR%\Reparo completo do Windows.bat"
) else (
    echo [ERRO] "Reparo completo do Windows.bat" nao encontrado em %NIVE_DIR%.
    pause
)
goto menu

:opcao16
cls
exit

:opcaoA :opcaoa
cls
echo ============================================================
echo    Abrindo Nive Software Auxiliares...
echo ============================================================
echo.

if exist "%NIVE_DIR%\NiveSoftwareAuxiliares.bat" (
    start "" "%NIVE_DIR%\NiveSoftwareAuxiliares.bat"
    goto menu
)

echo [ERRO] NiveSoftwareAuxiliares.bat nao encontrado em %NIVE_DIR%.
pause
goto menu


:: ============================================================
:: ROTINA : BOOTSTRAP
:: Verifica arquivos em C:\Nive\ e baixa do GitHub se faltar
:: ============================================================
:bootstrap
cls
color 9
echo ============================================================
echo    ScriptNive - Verificacao de Ambiente
echo ============================================================
echo.

:: Garante pasta base
if not exist "%NIVE_DIR%" mkdir "%NIVE_DIR%" >nul 2>&1

:: Verifica arquivos essenciais
set "MISSING=0"
if not exist "%NIVE_DIR%\ScriptNive.bat"                set "MISSING=1"
if not exist "%NIVE_DIR%\NiveBoost.bat"                 set "MISSING=1"
if not exist "%NIVE_DIR%\NiveSoftwareAuxiliares.bat"    set "MISSING=1"
if not exist "%NIVE_DIR%\INFPC.bat"                     set "MISSING=1"
if not exist "%NIVE_DIR%\Opcao13.ps1"                   set "MISSING=1"
if not exist "%NIVE_DIR%\pacotes.json"                  set "MISSING=1"
if not exist "%NIVE_DIR%\Otimizadores\AcelerarWindows.bat" set "MISSING=1"

if "%MISSING%"=="0" (
    echo [OK] Todos os arquivos ja estao presentes em %NIVE_DIR%.
    timeout /t 1 >nul
    goto :eof
)

echo [INFO] Arquivos ausentes detectados. Iniciando download...
echo.

set "ZIP=%TEMP%\Nive.zip"
set "EXTRACT=%TEMP%\NiveExtract"

if exist "%ZIP%" del /q "%ZIP%" >nul 2>&1
if exist "%EXTRACT%" rd /s /q "%EXTRACT%" >nul 2>&1

echo [..] Baixando pacote do GitHub...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { [Net.ServicePointManager]::SecurityProtocol='Tls12'; Invoke-WebRequest -Uri '%GITHUB_ZIP%' -OutFile '%ZIP%' -UseBasicParsing } catch { exit 1 }"

if not exist "%ZIP%" (
    echo.
    echo [ERRO] Falha ao baixar o pacote. Verifique sua conexao com a internet.
    echo        URL: %GITHUB_ZIP%
    pause
    goto :eof
)

echo [OK] Download concluido.
echo [..] Extraindo arquivos...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Expand-Archive -Path '%ZIP%' -DestinationPath '%EXTRACT%' -Force"

if not exist "%EXTRACT%" (
    echo [ERRO] Falha ao extrair o pacote.
    pause
    goto :eof
)

echo [..] Copiando arquivos para %NIVE_DIR%...
:: O comando abaixo copia TUDO que está dentro da pasta extraída para C:\Nive\
xcopy /E /Y /I /Q "%EXTRACT%\*" "%NIVE_DIR%\" >nul 2>&1

echo [..] Limpando arquivos temporarios...
rd /s /q "%EXTRACT%" >nul 2>&1
del /q "%ZIP%" >nul 2>&1

echo.
echo [OK] Ambiente configurado com sucesso em %NIVE_DIR%.
timeout /t 2 >nul
goto :eof


@echo off
cls
:Credito
cls
color 4                                                                                                   
echo                                   .  .                                                             
echo                                  .^.::                      .~^:                                   
echo                           ...:^7!7~^:                       ..:?!~7^::                             
echo                           ^^7!7?~^:                            .^~?77?~~                           
echo                        .:?77?7!~:.                               .~!!?777.                         
echo                    .   !!?7J7!~:                                  ^~~?!!?!!...                     
echo                  :.^..:!777J?^^                                    ^~?!!?7!~...                    
echo                  :^?^:.!!77!?^^                                    .:?!!?!!^:^7.                   
echo                .:7!?..^!!77??.                                      .?!!?!! ^!?!!                  
echo               ..~??7!~~!!77J?                                       .?!!77J^~!7!Y~.                
echo               ^~?7!77~.!!77J?:.                                     .?!!?!!^!77!J?^.               
echo               .:77!77~~!!77!?:.                                    ::7!!?!!!!777J7^.               
echo               :^?7!?7!?7!77??!~                                    .:?!!?!7?!77!Y7^^               
echo               ~~77!?7!77J77J?~~           .^.            ^         ^~?!!?!7?!77!Y7.                
echo              .::!7!77!?77777?^:          :~:. ... ...  ::^         :^7!!?!!?!77!7~.                
echo             .~~^:!!?7!?!!7!!7^:          ..?~!^.:  :::~?~~         ..7!!?!!?!7?~~.^!               
echo             .~7!7^^77!?7!77!7::^           !~7?~~!^^7!?7^.        ^..~!!?!!?!7~..!!7               
echo             .^!!?!~~~~?7J77?!~~^.          ~~7?~!7~!7!7~:         ^::^!!?!7?^:!~7?!7               
echo               7!77!?!~!!777J7~!?^:.         :77~!^^7!~7..      ..:?^^7!!?!!^~!?!Y7!7               
echo               ~~?7!77!?!!77!?^^?!~^..       .:^~77!?!^:      ..^!!?::?!!?!7?777!77~~               
echo               :^?7!77?77?77?7~~!!7?^^:        ~^7~~7!:       ^^?7!~:^?!!?!777J7!J?^~               
echo                .~7!7?J77J77Y77?!~!?!7~::^.    ^^7:^7^.    ::7???^^!77?!!77J7!Y?!J~.                
echo                 ::^!7!77J?7J?!7?~!!!7?!7!^:.  .^?!~?:.  .^7!?7!^~!?!!?!!?!777?!^~:                 
echo                  ..:^^^^^!~!!!!7777~!7!7?~~^  7~77!77: :^?7!?!~77!J7!7!!7^~^:^^                     
echo                    :!~?~!~~!~~!?!7?!77!77!J7^!?!7?!77!!7!7?777!?7!J7!7~~!~~?^^.                     
echo                     ^^77??7Y?7J?!7?!7?!77!J?!57!77!77!?7!7?J?7!?7!?77?77?77~::                      
echo                       ^^^?!77!7?~!?!7?!77!77!J7!77!77!77!77777!7!!?!!?!!?~~:                        
echo                        ..^~!7777!!^^~7!7?!77!Y7!77!77!77!?7!!7~^!!?777~~~                          
echo                           .::~~!!!~..:^~!!77!57!77!77!?7!!~^^:^!7!!~^:..                           
echo                             .  ::~?^:^. :~77!J7!77!77~~~::^..~~?~^^  .                             
echo                                    .:      ~~77!77!77~~    .:::                                    
echo                                            .^77!77!77^.                                             
echo                                            ?!?7!?7!77~?                                             
echo                                         ::~?!57!57!77!?~^:                                         
echo                                         ^~77~J7!J7!7??7?~^                                         
echo                                        .?!77!77!77!77!7!!?:.                                       
echo                                       :^7~~?!??!77!77!?:^?:.                                       
echo                                       ..7^^7!Y!~77~~7!7~^7..                                       
echo                                         ^~77!Y^^77~~7!77~^                                         
echo                                         .~77!Y~~77~^7!77~^                                         
echo                                         ^~!7!7^^77~^7!77~^                                         
echo                                          .^7!7^^77^^7~7~:.                                         
echo                                            !~!^^77^ 7~~                                            
echo                                             :~ :!7: ~::                                            
echo                                             .: .^^. :.                                             
echo                                                .^^.                                                
echo                                                 ...      
echo ̏                                                                                               ̏ 
echo ▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄Créditos▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄
echo ̏                                                                                               ̏
echo     ▐━━━Criador do ScripNive━━━▌            ▐━━━Criador do Reparo completo do Windows━━━▌
echo           ╔═════════════╗                                 ╔════════╗
echo           ╠Ryan Vinicius╣                                 ╠Ivo Dias╣ 
echo           ╚═════════════╝                                 ╚════════╝    
echo ̏                                                                                               ̏  
echo                       ▐━━━Sites Utilizando Para Criar o ScripNive━━━▌
echo                                  ╔════════════════╗
echo                                  ║1.Primeiro Site ║
echo                                  ║2.Segundo Site  ║
echo                                  ║3.Terceiro Site ║
echo                                  ║4.Quarto Site   ║
echo                                  ╚════════════════╝                                            
echo  ̏                                                                                               ̏     
echo     ▐━━━DATA DE LANÇAMENTO━━━▌                                        
echo         ╔════════════════╗ 
echo         ║  10/Set./2022  ║
echo         ╚════════════════╝                               
echo  ̏                                                                                               ̏                                      
echo ===================
echo *  5.Menu Tarefas *
echo ===================
set /p opcao= Escolha uma opcao: 
echo ------------------------------
if %opcao% equ 1 goto opcao1
if %opcao% equ 2 goto opcao2
if %opcao% equ 3 goto opcao3
if %opcao% equ 4 goto opcao4
if %opcao% equ 5 goto opcao5

:opcao1
start https://docs.microsoft.com/pt-br/windows-server/administration/windows-commands/cmd
goto Credito

:opcao2
start https://www.dostips.com/
goto Credito

:opcao3
start https://www.text-image.com/
goto Credito

:opcao4
start https://github.com/RIZONCIO/Script-Nive
goto Credito

:opcao5
cls
goto menu 

pause >nul