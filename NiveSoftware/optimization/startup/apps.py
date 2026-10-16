# core/apps.py - Desabilitar alguns softwares do Windows

import subprocess
import os
import sys
import time
from typing import Dict, List, Tuple, Optional


class DisableSoftware:
    """Classe para desabilitar/remover softwares desnecessários do Windows"""

    def __init__(self, logger=None):
        """Inicializar com logger opcional"""
        self.logger = logger
        self.results = []

    def log(self, message: str, level: str = "INFO"):
        """Log de mensagens"""
        if self.logger:
            if hasattr(self.logger, "error") and level == "ERROR":
                self.logger.error(message)
            elif hasattr(self.logger, "info"):
                self.logger.info(message)
            else:
                self.logger.log(message)
        else:
            print(f"[{level}] {message}")

    def run_command(
        self,
        command: str,
        shell: bool = True,
        ignore_errors: bool = False,
        use_powershell: bool = False,
    ) -> Tuple[bool, str]:
        """Executar comando do sistema com melhor tratamento"""
        try:
            self.log(f"Executando: {command}")

            # Se usar PowerShell, ajustar comando
            if use_powershell:
                command = f'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "{command}"'

            # Executar comando
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=60,  # Reduzido para 60 segundos
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            # Verificar resultado
            if result.returncode == 0:
                self.log(f"Comando executado: {command}")
                return True, result.stdout.strip()
            error_msg = result.stderr.strip() or result.stdout.strip()
            if ignore_errors:
                self.log(f"Tentativa sem sucesso: {command} - {error_msg}", "WARNING")
            else:
                self.log(f"Erro ao executar: {command} - {error_msg}", "ERROR")
            return False, error_msg

        except subprocess.TimeoutExpired:
            self.log(f"Timeout ao executar: {command}", "ERROR")
            return False, "Timeout - comando demorou muito para executar"
        except FileNotFoundError:
            self.log(f"Comando não encontrado: {command}", "ERROR")
            return False, "Comando não encontrado no sistema"
        except Exception as e:
            self.log(f"Exceção ao executar {command}: {str(e)}", "ERROR")
            return False, str(e)

    def disable_hibernation(self) -> bool:
        """Desativar modo hibernação"""
        self.log("Desativando modo hibernação...")

        success, output = self.run_command("powercfg /h off")

        if success:
            self.results.append("✓ Modo hibernação desativado")
            return True
        else:
            self.results.append(
                "✗ Falha ao desativar hibernação (sem privilégios administrativos)"
            )
            return False

    def uninstall_paint(self) -> bool:
        """Desinstalar Paint usando winget"""
        self.log("Desinstalando Paint...")

        # Tentar diferentes formas de remover o Paint
        commands = [
            "winget uninstall 9PCFS5B6T72H --silent --accept-source-agreements",
            "winget uninstall Microsoft.Paint --silent --accept-source-agreements",
            'winget uninstall "Microsoft Paint" --silent --accept-source-agreements',
        ]

        for cmd in commands:
            success, output = self.run_command(cmd, ignore_errors=True)
            if success:
                self.results.append("✓ Paint desinstalado")
                return True
            time.sleep(2)  # Aguardar entre tentativas

        # Tentar via PowerShell como alternativa
        ps_cmd = "Get-AppxPackage *Microsoft.Paint* | Remove-AppxPackage"
        success, output = self.run_command(
            ps_cmd, use_powershell=True, ignore_errors=True
        )

        if success:
            self.results.append("✓ Paint removido via PowerShell")
            return True
        else:
            self.results.append(
                "✗ Paint não pôde ser removido (pode não estar instalado)"
            )
            return False

    def uninstall_phone_link(self) -> bool:
        """Desinstalar Vínculo com celular"""
        self.log("Desinstalando Vínculo com celular...")

        # Tentar diferentes métodos
        commands = [
            "winget uninstall Microsoft.YourPhone --silent --accept-source-agreements",
            'winget uninstall "Vínculo com o smartphone" --silent --accept-source-agreements',
        ]

        for cmd in commands:
            success, output = self.run_command(cmd, ignore_errors=True)
            if success:
                self.results.append("✓ Vínculo com celular desinstalado")
                return True
            time.sleep(2)

        # PowerShell como alternativa
        ps_cmd = "Get-AppxPackage *Microsoft.YourPhone* | Remove-AppxPackage"
        success, output = self.run_command(
            ps_cmd, use_powershell=True, ignore_errors=True
        )

        if success:
            self.results.append("✓ Vínculo com celular removido via PowerShell")
            return True
        else:
            self.results.append("✗ Vínculo com celular não pôde ser removido")
            return False

    def uninstall_cortana(self) -> bool:
        """Desinstalar Cortana"""
        self.log("Desinstalando Cortana...")

        # PowerShell para remover Cortana
        ps_commands = [
            "Get-AppxPackage *Microsoft.549981C3F5F10* | Remove-AppxPackage",
            "Get-AppxPackage -AllUsers *Cortana* | Remove-AppxPackage",
        ]

        success_count = 0
        for cmd in ps_commands:
            success, output = self.run_command(
                cmd, use_powershell=True, ignore_errors=True
            )
            if success:
                success_count += 1
            time.sleep(2)

        if success_count > 0:
            self.results.append("✓ Cortana desinstalada")
            return True
        else:
            self.results.append(
                "✗ Cortana não pôde ser removida (pode já estar removida)"
            )
            return False

    def uninstall_onedrive(self) -> bool:
        """Remoção do OneDrive"""
        self.log("Removendo OneDrive...")

        success_count = 0

        # 1. Matar processo do OneDrive
        kill_cmd = "taskkill /f /im OneDrive.exe /t"
        self.run_command(kill_cmd, ignore_errors=True)
        time.sleep(3)

        # 2. Tentar winget
        winget_commands = [
            "winget uninstall Microsoft.OneDrive --silent --accept-source-agreements",
            "winget uninstall OneDrive --silent --accept-source-agreements",
        ]

        for cmd in winget_commands:
            success, output = self.run_command(cmd, ignore_errors=True)
            if success:
                success_count += 1
            time.sleep(2)

        # 3. Tentar desinstaladores nativos
        uninstall_commands = [
            r'"%SystemRoot%\System32\OneDriveSetup.exe" /uninstall',
            r'"%SystemRoot%\SysWOW64\OneDriveSetup.exe" /uninstall',
        ]

        for cmd in uninstall_commands:
            success, output = self.run_command(cmd, ignore_errors=True)
            if success:
                success_count += 1
            time.sleep(2)

        if success_count > 0:
            self.results.append(
                f"✓ OneDrive removido ({success_count} operações bem-sucedidas)"
            )
            return True
        else:
            self.results.append("✗ OneDrive não pôde ser removido completamente")
            return False

    def remove_xbox_apps(self) -> bool:
        """Remover apps do Xbox"""
        self.log("Removendo aplicativos Xbox...")

        # PowerShell para remover Xbox apps
        ps_commands = [
            "Get-AppxPackage *Xbox* | Remove-AppxPackage",
            "Get-AppxPackage *Microsoft.XboxApp* | Remove-AppxPackage",
            "Get-AppxPackage *Microsoft.XboxGameOverlay* | Remove-AppxPackage",
        ]

        success_count = 0
        for cmd in ps_commands:
            success, output = self.run_command(
                cmd, use_powershell=True, ignore_errors=True
            )
            if success:
                success_count += 1
            time.sleep(2)

        if success_count > 0:
            self.results.append("✓ Aplicativos Xbox removidos")
            return True
        else:
            self.results.append("✗ Aplicativos Xbox não puderam ser removidos")
            return False

    def remove_store_apps(self) -> bool:
        """Remover alguns apps da Store (mantendo essenciais)"""
        self.log("Removendo apps desnecessários da Store...")

        # Apps específicos para remover
        apps_to_remove = [
            "*Microsoft.BingWeather*",
            "*Microsoft.GetHelp*",
            "*Microsoft.Getstarted*",
            "*Microsoft.Microsoft3DViewer*",
            "*Microsoft.MicrosoftOfficeHub*",
            "*Microsoft.MicrosoftSolitaireCollection*",
            "*Microsoft.MixedReality.Portal*",
            "*Microsoft.Office.OneNote*",
            "*Microsoft.People*",
            "*Microsoft.SkypeApp*",
            "*Microsoft.Wallet*",
            "*Microsoft.WindowsCamera*",
            "*Microsoft.WindowsMaps*",
            "*Microsoft.ZuneMusic*",
            "*Microsoft.ZuneVideo*",
        ]

        success_count = 0
        for app in apps_to_remove:
            cmd = f"Get-AppxPackage {app} | Remove-AppxPackage"
            success, output = self.run_command(
                cmd, use_powershell=True, ignore_errors=True
            )
            if success:
                success_count += 1
            time.sleep(1)

        if success_count > 0:
            self.results.append(f"✓ {success_count} apps da Store removidos")
            return True
        else:
            self.results.append("✗ Nenhum app da Store foi removido")
            return False

    def executar_desabilitacao_softwares(self):
        """Método principal que executa todas as operações"""
        self.log("Iniciando desabilitação de softwares...")

        sucessos = []
        erros = []

        # Dicionário com todas as operações
        operations = {
            "Modo Hibernação": self.disable_hibernation,
            "Microsoft Paint": self.uninstall_paint,
            "Vínculo com Celular": self.uninstall_phone_link,
            "Cortana": self.uninstall_cortana,
            "OneDrive": self.uninstall_onedrive,
            "Xbox Apps": self.remove_xbox_apps,
            "Apps da Store": self.remove_store_apps,
        }

        # Executar cada operação
        for name, operation in operations.items():
            try:
                self.log(f"Executando: {name}")
                if operation():
                    sucessos.append(name)
                    self.log(f"✓ {name} - Sucesso")
                else:
                    erros.append(f"{name} - Falha na operação")
                    self.log(f"✗ {name} - Falhou")
            except Exception as e:
                error_msg = f"{name} - Erro: {str(e)}"
                erros.append(error_msg)
                self.log(f"✗ {name} - Exceção: {str(e)}", "ERROR")

            # Pequena pausa entre operações
            time.sleep(1)

        # Determinar sucesso geral
        success = bool(sucessos) and not erros

        self.log(
            f"Operações concluídas - Sucessos: {len(sucessos)}, Erros: {len(erros)}"
        )
        return success, sucessos, erros

    def get_results_summary(self) -> List[str]:
        """Obter resumo dos resultados"""
        return self.results.copy()


def main():
    """Função principal para execução standalone"""
    print("NiveBoost - Desabilitador de Software v2.0")
    print("=" * 50)

    disabler = DisableSoftware()
    success, sucessos, erros = disabler.executar_desabilitacao_softwares()

    print("\nResumo das operações:")
    print("-" * 30)
    for result in disabler.get_results_summary():
        print(result)

    print(f"\nSucessos: {len(sucessos)}")
    print(f"Erros: {len(erros)}")

    if success:
        print("✓ Operação concluída com sucesso!")
    else:
        print("⚠ Operação concluída com alguns problemas")


if __name__ == "__main__":
    main()
