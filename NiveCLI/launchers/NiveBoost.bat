@ECHO OFF
:: NOME   : NiveBoost
:: AUTOR  : Ryan Vinicius Carvalho Pereira
:: VERSAO : 1.1.1
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
    echo  para aplicar as otimizacoes corretamente.
    echo.
    echo  Feche esta janela, clique com o botao direito no arquivo
    echo  NiveBoost.bat e escolha "Executar como administrador".
    echo ============================================================
    pause
    exit /b
)

title NiveBoost 1.1.1
set "NIVE_DIR=C:\Nive"

:menu
cls
color 9

echo Bem vindo o NiveBoost 1.1.1
echo пѕ 
echo ___      ___                         ________                                        
echo `MM\     `M' 68b                      `MMMMMMMb.                                      
echo  MMM\     M  Y89                       MM    `Mb                                /     
echo  M\MM\    M  ___  ____    ___   ____    MM     MM   _____     _____     ____    /M     
echo  M \MM\   M  `MM  `MM(    )M'  6MMMMb   MM    .M9  6MMMMMb   6MMMMMb   6MMMMb\ /MMMMM  
echo  M  \MM\  M   MM   `Mb    d'  6M'  `Mb  MMMMMMM(  6M'   `Mb 6M'   `Mb MM'    `  MM     
echo  M   \MM\ M   MM    YM.  ,P   MM    MM  MM    `Mb MM     MM MM     MM YM.       MM     
echo  M    \MM\M   MM     MM  M    MMMMMMMM  MM     MM MM     MM MM     MM  YMMMMb   MM     
echo  M     \MMM   MM     `Mbd'    MM        MM     MM MM     MM MM     MM      `Mb  MM     
echo  M      \MM   MM      YMP     YM    d9  MM    .M9 YM.   ,M9 YM.   ,M9 L    ,MM  YM.  , 
echo _M_      \M  _MM_      M       YMMMM9  _MMMMMMM9'  YMMMMM9   YMMMMM9  MYMMMM9    YMMM9 
echo пѕ 

date /t     
time /t 

echo Computador: %computername%        Usuario: %username%

echo ==========================================
echo *  N.Informação Sobre NiveBoost          *
echo *  C.Crédito Do NiveBoost                *
echo *  R.Recomendações Técnicas              *
echo *  S.Retornar ao ScriptNive              *
echo ==========================================               
			   
echo                         MENU OTIMIZADOR
echo ================================================================
echo * 1. Desabilitar Alguns Serviços Do Windows.                   *
echo * 2. Desabilitar Tweaks De Tarefas Agendadas.                  * 
echo * 3. Desabilitar Alguns Softwares do Windows.                  * 
echo * 4. Remover Telemetria e Coleta de Dados.                     *
echo * 5. Remover Features Não Usadas.                              *
echo * 6. Remover Animações Inuteis.                                *
echo * 7. Desabilitar Busca Web Na Barra De Pesquisa.               *
echo * 8. Desabilitar Escrita De Cache De Navegadores e Streaming.  *
echo * 9. Desabilitar propagandas na tela de bloqueio.              *
echo * 10. Otimizar o Edge.                                         *
echo * 11. Acelerar Windows.                                        *
echo * 12. Sair                                                     *
echo ================================================================

set /p opcao= Escolha uma opcao: 
echo ------------------------------
if %opcao% equ C goto opcaoC 
if %opcao% equ c goto opcaoc
if %opcao% equ N goto opcaoN
if %opcao% equ n goto opcaon
if %opcao% equ R goto opcaoR
if %opcao% equ r goto opcaor
if %opcao% equ S goto opcaoS
if %opcao% equ s goto opcaos
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

:opcaoN :opcaon
cls
start "" "%NIVE_DIR%\Documentação-Técnica-do-ScriptNive.pdf"
goto menu

:opcaoC :opcaoc
goto Credito 

:opcaoR :opcaor
cls
echo пѕ 
echo              ■━━━Recomendações Técnicas━━━□
echo         ╔══════════════════════════════════════╗
echo         ║1.Criar Um Ponto de Restauração.     ║
echo         ║2.Ler As Informação Do NiveBoost.    ║
echo         ║3.Não Ativar Caso Você Não Concorde. ║
echo         ║4.Não Ativar Mais De Uma Vez.        ║
echo         ╚══════════════════════════════════════╝ 
pause
goto menu

:opcaoS :opcaos
cls 
if exist "%NIVE_DIR%\ScriptNive.bat" (
    start "" "%NIVE_DIR%\ScriptNive.bat"
) else (
    start "" ScriptNive.bat
)
exit

:opcao1
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
    start "" "%NIVE_DIR%\Otimizadores\DesabilitarAlgunsServiços.bat"
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao2
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
    start "" "%NIVE_DIR%\Otimizadores\DesabilitarTweaks.bat"
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao3
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
    start "" "%NIVE_DIR%\Otimizadores\DesabilitarAlgunsSoftwares.bat"
) else (
    echo Cancelando.
    goto menu
)
goto menu

:opcao4
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
    start "" "%NIVE_DIR%\Otimizadores\RemoverTelemetria.bat"
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao5
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
    start "" "%NIVE_DIR%\Otimizadores\RemoverFeatures.bat"
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao6
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
    start "" "%NIVE_DIR%\Otimizadores\RemoverAnimacoes.bat"
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao7
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
REG ADD "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" /V BingSearchEnabled /T REG_DWORD /D 0 /F
REG ADD "HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Explorer" /V DisableSearchBoxSuggestions /T REG_DWORD /D 1 /F
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao8
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
    start "" "%NIVE_DIR%\Otimizadores\DesabilitaCacheNavegadoresStreaming.bat"
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao9
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /V "RotatingLockScreenOverlayEnabled" /T REG_DWORD /D 0 /F
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /V "SubscribedContent-338387Enabled" /T REG_DWORD /D 0 /F
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao10
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
    start "" "%NIVE_DIR%\Otimizadores\OtimizaroEdge.bat"
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao11
cls
echo OBS: Essas funções são irreversíveis a não ser que tenha criado um ponto de restauração!
set /p resposta=Deseja realmente continuar? (s/n): 
if /i "%resposta%"=="s" (
    echo Continuando...
    start "" "%NIVE_DIR%\Otimizadores\AcelerarWindows.bat"
) else (
    echo Cancelando.
    goto menu
)
goto menu 

:opcao12
cls
exit

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
echo пѕ 
echo ___      ___                         ________                                        
echo `MM\     `M' 68b                      `MMMMMMMb.                                      
echo  MMM\     M  Y89                       MM    `Mb                                /     
echo  M\MM\    M  ___  ____    ___   ____    MM     MM   _____     _____     ____    /M     
echo  M \MM\   M  `MM  `MM(    )M'  6MMMMb   MM    .M9  6MMMMMb   6MMMMMb   6MMMMb\ /MMMMM  
echo  M  \MM\  M   MM   `Mb    d'  6M'  `Mb  MMMMMMM(  6M'   `Mb 6M'   `Mb MM'    `  MM     
echo  M   \MM\ M   MM    YM.  ,P   MM    MM  MM    `Mb MM     MM MM     MM YM.       MM     
echo  M    \MM\M   MM     MM  M    MMMMMMMM  MM     MM MM     MM MM     MM  YMMMMb   MM     
echo  M     \MMM   MM     `Mbd'    MM        MM     MM MM     MM MM     MM      `Mb  MM     
echo  M      \MM   MM      YMP     YM    d9  MM    .M9 YM.   ,M9 YM.   ,M9 L    ,MM  YM.  , 
echo _M_      \M  _MM_      M       YMMMM9  _MMMMMMM9'  YMMMMM9   YMMMMM9  MYMMMM9    YMMM9 
echo пѕ 
echo ̏                                                                                               ̏ 
echo ▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄Créditos▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄
echo ̏                                                                                               ̏
echo     ▐━━━Criador do NiveBoost━━━▌            ▐━━━Sites Utilizando Para Criar o NiveBoost━━━▌
echo           ╔═════════════╗                                 ╔════════════════╗
echo           ╠Ryan Vinicius╣                                 ║1.Primeiro Site ║
echo           ╚═════════════╝                                 ║2.Segundo Site  ║ 
echo                                                           ║3.Terceiro Site ║
echo                                                           ║4.Quarto Site   ║
echo                                                           ╚════════════════╝                                            
echo  ̏                                                                                               ̏     
echo                            ▐━━━Criadores dos Scripts━━━▌ 
echo                          ╔══════════════════════════════╗
echo                          ║OtimizaroEdge   ➞     AFaustini║
echo                          ╚══════════════════════════════╝
echo  ̏                                                                                               ̏
echo     ▐━━━DATA DE LANÇAMENTO━━━▌                                        
echo         ╔════════════════╗ 
echo         ║  30/Jul./2024  ║
echo         ╚════════════════╝                               
echo  ̏                                                                                               ̏                                      
echo =======================
echo *  5.Menu Otimizador  *
echo =======================
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
goto menu 

pause >nul