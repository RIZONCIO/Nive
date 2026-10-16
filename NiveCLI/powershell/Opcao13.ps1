chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "ScriptNive 1.6.8"

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$pastaScript = Split-Path -Parent $MyInvocation.MyCommand.Definition
$caminhoJson = Join-Path $pastaScript "pacotes.json"

try {
    $mapaPacotes = Get-Content -Raw -Path $caminhoJson | ConvertFrom-Json
} catch {
    Write-Host "[ERRO] Não foi possível carregar o 'pacotes.json'."
    pause
    exit
}

if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "`nChocolatey não encontrado. Instalando..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "[ERRO] Falha na instalação do Chocolatey."
        pause
        exit
    }
    Write-Host "Chocolatey instalado com sucesso."
}

function Buscar-NomeNoChocolatey {
    param([string]$nomeDisplay)

    $nomeLimpo = ($nomeDisplay -replace '[^a-zA-Z0-9\s]', '') -replace '\s+', ' '
    $palavraChave = $nomeLimpo.Split(' ')[0].ToLower()

    Write-Host "`n[INFO] Tentando identificar '$palavraChave' no Chocolatey..."
    $resultado = choco search $palavraChave --exact

    if ($resultado -match "$palavraChave\s+[0-9]") {
        return $palavraChave
    } else {
        return $null
    }
}

do {
    Clear-Host
    Write-Host "Listando softwares instalados..."

    $apps = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
            Where-Object { $_.DisplayName -and $_.UninstallString } |
            Select-Object DisplayName, UninstallString

    for ($i = 0; $i -lt $apps.Count; $i++) {
        Write-Host "$i - $($apps[$i].DisplayName)"
    }

    $escolha = Read-Host "`nDigite o número do software que deseja desinstalar"
    $appSelecionado = $apps[$escolha]

    if ($appSelecionado) {
        $nomeDisplay = $appSelecionado.DisplayName
        $uninstallCmd = $appSelecionado.UninstallString

        # Tenta encontrar no JSON
        $pacoteChoco = $null
        foreach ($chave in $mapaPacotes.PSObject.Properties.Name) {
            if ($nomeDisplay -like "*$chave*") {
                $pacoteChoco = $mapaPacotes.$chave
                break
            }
        }

        Write-Host "`nDesinstalando: $nomeDisplay"
        try {
            Start-Process "cmd.exe" "/c $uninstallCmd" -Wait -Verb RunAs
        } catch {
            Write-Host "[ERRO] Falha ao desinstalar: $_"
        }

        Start-Sleep -Seconds 5

        $programaAindaExiste = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
                               Where-Object { $_.DisplayName -like "*$nomeDisplay*" }

        if (-not $programaAindaExiste) {
            if (-not $pacoteChoco) {
                $pacoteChoco = Buscar-NomeNoChocolatey -nomeDisplay $nomeDisplay
            }

            if ($pacoteChoco) {
                $pastaRaiz = "C:\ProgramData\chocolatey\lib"
                $nomeBase = ($pacoteChoco -split '\.')[0].ToLower()

                $pastasRelacionadas = Get-ChildItem -Path $pastaRaiz -Directory | Where-Object {
                    $_.Name.ToLower() -like "*$nomeBase*"
                }

                foreach ($pasta in $pastasRelacionadas) {
                    Write-Host "`n[INFO] Limpando cache: $($pasta.FullName)"
                    try {
                        Remove-Item -Recurse -Force $pasta.FullName
                    } catch {
                        Write-Host "[ERRO] Não foi possível remover: $($pasta.FullName)"
                    }
                }

                Write-Host "`n[SUCCESSO] Reinstalando '$pacoteChoco' via Chocolatey..."
                choco install $pacoteChoco -y --force
            } else {
                Write-Host "`n[ERRO] Nome '$nomeDisplay' não encontrado no JSON e não identificado automaticamente no Chocolatey."
            }

        } else {
            Write-Host "`n[ALERTA] O programa ainda está instalado. Reinstalação abortada."
        }

    } else {
        Write-Host "[ERRO] Número inválido!"
    }

    Write-Host ""
    Write-Host "[1] Voltar para a lista"
    Write-Host "[S] Sair"
    $resposta = Read-Host "Escolha (1/S)"
    if ($resposta -eq 'S' -or $resposta -eq 's') { break }

} while ($true)
