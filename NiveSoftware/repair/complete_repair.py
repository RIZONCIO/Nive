"""
Reparo Completo do Windows
Baseado no script do Ivo Dias
"""

import subprocess
import os
import threading
import shutil
from pathlib import Path
from tkinter import messagebox
import time


class CompleteWindowsRepair:
    """Classe para reparo completo do Windows"""

    def __init__(self, logger):
        self.logger = logger
        self.is_running = False
        self.progress_callback = None
        self.total_steps = 0
        self.current_step = 0

    def set_progress_callback(self, callback):
        """Definir callback para atualização de progresso"""
        self.progress_callback = callback

    def update_progress(self, step_description):
        """Atualizar progresso"""
        self.current_step += 1
        if self.progress_callback:
            progress = (self.current_step / self.total_steps) * 100
            self.progress_callback(progress, step_description)
        self.logger.log(f"[{self.current_step}/{self.total_steps}] {step_description}")

    def run_command_with_retry(self, command, description, max_retries=2):
        """Executar comando com tentativas"""
        for attempt in range(max_retries):
            try:
                self.logger.log(f"Executando: {description}")
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minutos por comando
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )

                if result.returncode == 0:
                    self.logger.log_success(f"✓ {description} - Sucesso")
                    return True, result.stdout
                else:
                    self.logger.log_warning(
                        f"⚠ {description} - Código: {result.returncode}"
                    )
                    if attempt == max_retries - 1:
                        self.logger.log_error(
                            f"✗ {description} - Falhou após {max_retries} tentativas"
                        )

            except subprocess.TimeoutExpired:
                self.logger.log_error(f"✗ {description} - Timeout (10min)")
                if attempt == max_retries - 1:
                    return False, "Timeout"

            except Exception as e:
                self.logger.log_error(f"✗ {description} - Erro: {str(e)}")
                if attempt == max_retries - 1:
                    return False, str(e)

        return False, "Falha após múltiplas tentativas"

    def step_1_dism_repairs(self):
        """Passo 1: Reparos DISM"""
        self.update_progress("Iniciando verificação DISM...")

        dism_commands = [
            (
                "DISM.exe /Online /Cleanup-image /Scanhealth",
                "Verificando integridade da imagem",
            ),
            (
                "Dism.exe /Online /Cleanup-Image /CheckHealth",
                "Verificando saúde dos componentes",
            ),
            (
                "Dism.exe /Online /Cleanup-Image /SpSuperseded",
                "Limpando componentes obsoletos",
            ),
            (
                "Dism.exe /Online /Cleanup-Image /startComponentCleanup",
                "Iniciando limpeza de componentes",
            ),
            (
                "DISM.exe /Online /Cleanup-image /Restorehealth",
                "Restaurando integridade da imagem",
            ),
        ]

        for command, description in dism_commands:
            self.run_command_with_retry(command, description)
            self.update_progress(description)

    def step_2_sfc_scan(self):
        """Passo 2: Verificação SFC"""
        self.update_progress("Executando verificação SFC...")
        self.run_command_with_retry(
            "sfc /scannow", "Verificação de arquivos do sistema"
        )

    def step_3_disk_check(self):
        """Passo 3: Verificação de disco"""
        self.update_progress("Agendando verificação de disco...")
        self.run_command_with_retry(
            "chkdsk /r /f", "Verificação de disco (será executada no próximo boot)"
        )

    def step_4_stop_services(self):
        """Passo 4: Parar serviços do Windows Update"""
        self.update_progress("Parando serviços do Windows Update...")

        services = ["bits", "wuauserv", "appidsvc", "cryptsvc"]
        for service in services:
            self.run_command_with_retry(
                f"net stop {service}", f"Parando serviço {service}"
            )

    def step_5_clean_update_files(self):
        """Passo 5: Limpar arquivos do Windows Update"""
        self.update_progress("Limpando arquivos do Windows Update...")

        # Deletar arquivos específicos
        commands = [
            (
                'Del "%ALLUSERSPROFILE%\\Application Data\\Microsoft\\Network\\Downloader\\qmgr*.dat"',
                "Limpando arquivos QMGR",
            ),
            (
                "Del c:\\windows\\SoftwareDistribution /f",
                "Limpando SoftwareDistribution",
            ),
        ]

        for command, description in commands:
            self.run_command_with_retry(command, description)

    def step_6_reset_services_security(self):
        """Passo 6: Resetar segurança dos serviços"""
        self.update_progress("Resetando segurança dos serviços...")

        security_commands = [
            (
                "sc.exe sdset bits D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;AU)(A;;CCLCSWRPWPDTLOCRRC;;;PU)",
                "Configurando segurança do BITS",
            ),
            (
                "sc.exe sdset wuauserv D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;AU)(A;;CCLCSWRPWPDTLOCRRC;;;PU)",
                "Configurando segurança do Windows Update",
            ),
        ]

        for command, description in security_commands:
            self.run_command_with_retry(command, description)

    def step_7_database_repair(self):
        """Passo 7: Reparar banco de dados do Windows Update"""
        self.update_progress("Reparando banco de dados...")

        # Mudar para diretório system32
        os.chdir(os.path.join(os.environ["windir"], "system32"))

        # Reparar banco de dados
        self.run_command_with_retry(
            "esentutl /d %windir%\\softwaredistribution\\datastore\\datastore.edb",
            "Reparando banco de dados do Windows Update",
        )

    def step_8_clean_registry(self):
        """Passo 8: Limpar registros problemáticos"""
        self.update_progress("Limpando registros problemáticos...")

        registry_commands = [
            (
                'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" /f',
                "Removendo políticas de update",
            ),
            (
                'reg delete "HKLM\\COMPONENTS\\PendingXmlIdentifier" /f',
                "Limpando componentes pendentes",
            ),
            (
                'reg delete "HKLM\\COMPONENTS\\NextQueueEntryIndex" /f',
                "Limpando índice de fila",
            ),
            (
                'reg delete "HKLM\\COMPONENTS\\AdvancedInstallersNeedResolving" /f',
                "Limpando instaladores avançados",
            ),
        ]

        for command, description in registry_commands:
            self.run_command_with_retry(command, description)

    def step_9_clean_temp_files(self):
        """Passo 9: Limpar arquivos temporários"""
        self.update_progress("Limpando arquivos temporários...")

        temp_path = os.environ.get("TEMP", "")
        if temp_path:
            self.run_command_with_retry(
                f"del {temp_path}\\*.* /s /f /q", "Limpando arquivos temporários"
            )

    def step_10_remove_pirate_software(self):
        """Passo 10: Remover software pirata"""
        self.update_progress("Verificando e removendo software ilícito...")

        # Matar processos
        processes = ["KMSPico.exe", "AutoKMS.exe"]
        for process in processes:
            self.run_command_with_retry(
                f"taskkill /f /im {process} /t", f"Finalizando processo {process}"
            )

        # Remover pastas
        pirate_folders = [
            os.path.join(os.environ.get("ProgramFiles", ""), "KMSpico"),
            "C:\\Windows\\AutoKMS",
            "C:\\Windows\\KMSPico",
            "C:\\Windows\\System32\\Tasks\\AutoKMS",
        ]

        for folder in pirate_folders:
            if os.path.exists(folder):
                try:
                    # Tomar posse e remover atributos
                    self.run_command_with_retry(
                        f'takeown /f "{folder}"', f"Tomando posse de {folder}"
                    )
                    self.run_command_with_retry(
                        f'attrib -r -s -h /s /d "{folder}"',
                        f"Removendo atributos de {folder}",
                    )
                    self.run_command_with_retry(
                        f'rmdir /s /q "{folder}"', f"Removendo pasta {folder}"
                    )
                except Exception as e:
                    self.logger.log_warning(
                        f"Não foi possível remover {folder}: {str(e)}"
                    )

    def step_11_network_reset(self):
        """Passo 11: Reset completo da rede"""
        self.update_progress("Executando reset completo da rede...")

        network_commands = [
            ("ipconfig /release", "Liberando configuração IP"),
            ("ipconfig /renew", "Renovando configuração IP"),
            ("ipconfig /flushdns", "Limpando cache DNS"),
            ("Netsh winsock reset", "Resetando Winsock"),
            ("nbtstat -rr", "Resetando NetBIOS"),
            ("netsh int ip reset resetlog.txt", "Resetando TCP/IP"),
            ("netsh winsock reset all", "Resetando Winsock completo"),
            ("netsh int 6to4 reset all", "Resetando 6to4"),
            ("netsh int ipv4 reset all", "Resetando IPv4"),
            ("netsh int ipv6 reset all", "Resetando IPv6"),
            ("netsh int httpstunnel reset all", "Resetando HTTP Tunnel"),
            ("netsh int isatap reset all", "Resetando ISATAP"),
            ("netsh int portproxy reset all", "Resetando Port Proxy"),
            ("netsh int tcp reset all", "Resetando TCP"),
            ("netsh int teredo reset all", "Resetando Teredo"),
        ]

        for command, description in network_commands:
            self.run_command_with_retry(command, description)
            self.update_progress(description)

    def step_12_fix_permissions(self):
        """Passo 12: Corrigir permissões"""
        self.update_progress("Corrigindo permissões do sistema...")

        permission_commands = [
            (
                "net localgroup administradores localservice /add",
                "Adicionando LocalService aos administradores",
            ),
            (
                "fsutil resource setautoreset true C:\\",
                "Configurando auto-reset do sistema de arquivos",
            ),
        ]

        for command, description in permission_commands:
            self.run_command_with_retry(command, description)

    def step_13_configure_services(self):
        """Passo 13: Configurar serviços"""
        self.update_progress("Configurando serviços do sistema...")

        service_commands = [
            (
                "sc config wuauserv start= auto",
                "Configurando Windows Update como automático",
            ),
            ("sc config bits start= auto", "Configurando BITS como automático"),
            (
                "sc config DcomLaunch start= auto",
                "Configurando DCOM Launch como automático",
            ),
        ]

        for command, description in service_commands:
            self.run_command_with_retry(command, description)

    def step_14_fix_registry_keys(self):
        """Passo 14: Corrigir chaves de registro"""
        self.update_progress("Corrigindo chaves de registro...")

        # Adicionar registros importantes (versão simplificada)
        registry_fixes = [
            (
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\BackupRestore\\FilesNotToBackup" /f',
                "Configurando backup",
            ),
            (
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate" /v "AllowOSUpgrade" /t REG_DWORD /d 1 /f',
                "Permitindo upgrade do OS",
            ),
        ]

        for command, description in registry_fixes:
            self.run_command_with_retry(command, description)

    def step_15_register_dlls(self):
        """Passo 15: Re-registrar DLLs críticas"""
        self.update_progress("Re-registrando DLLs críticas...")

        dlls = [
            "atl.dll",
            "urlmon.dll",
            "mshtml.dll",
            "shdocvw.dll",
            "browseui.dll",
            "jscript.dll",
            "vbscript.dll",
            "scrrun.dll",
            "msxml.dll",
            "msxml3.dll",
            "msxml6.dll",
            "actxprxy.dll",
            "softpub.dll",
            "wintrust.dll",
            "dssenh.dll",
            "rsaenh.dll",
            "gpkcsp.dll",
            "sccbase.dll",
            "slbcsp.dll",
            "cryptdlg.dll",
            "oleaut32.dll",
            "ole32.dll",
            "shell32.dll",
            "initpki.dll",
            "wuapi.dll",
            "wuaueng.dll",
            "wuaueng1.dll",
            "wucltui.dll",
            "wups.dll",
            "wups2.dll",
            "wuweb.dll",
            "qmgr.dll",
            "qmgrprxy.dll",
            "wucltux.dll",
            "muweb.dll",
            "wuwebv.dll",
        ]

        for dll in dlls:
            self.run_command_with_retry(f"regsvr32.exe {dll} /s", f"Registrando {dll}")

    def step_16_final_network_reset(self):
        """Passo 16: Reset final da rede"""
        self.update_progress("Executando reset final da rede...")

        final_commands = [
            ("netsh winsock reset", "Reset final do Winsock"),
            ("netsh winhttp reset proxy", "Reset do proxy HTTP"),
        ]

        for command, description in final_commands:
            self.run_command_with_retry(command, description)

    def step_17_restart_services(self):
        """Passo 17: Reiniciar serviços"""
        self.update_progress("Reiniciando serviços do sistema...")

        services = ["bits", "wuauserv", "appidsvc", "cryptsvc"]
        for service in services:
            self.run_command_with_retry(
                f"net start {service}", f"Iniciando serviço {service}"
            )

    def run_complete_repair(self, progress_callback=None):
        """Executar reparo completo do Windows"""
        if self.is_running:
            return False, "Reparo já está em execução"

        self.is_running = True
        self.progress_callback = progress_callback
        self.total_steps = 17  # Total de passos
        self.current_step = 0

        try:
            self.logger.log("=" * 60)
            self.logger.log("INICIANDO REPARO COMPLETO DO WINDOWS")
            self.logger.log("Baseado no script do Ivo Dias")
            self.logger.log("=" * 60)

            # Executar todos os passos
            self.step_1_dism_repairs()
            self.step_2_sfc_scan()
            self.step_3_disk_check()
            self.step_4_stop_services()
            self.step_5_clean_update_files()
            self.step_6_reset_services_security()
            self.step_7_database_repair()
            self.step_8_clean_registry()
            self.step_9_clean_temp_files()
            self.step_10_remove_pirate_software()
            self.step_11_network_reset()
            self.step_12_fix_permissions()
            self.step_13_configure_services()
            self.step_14_fix_registry_keys()
            self.step_15_register_dlls()
            self.step_16_final_network_reset()
            self.step_17_restart_services()

            self.logger.log("=" * 60)
            self.logger.log("REPARO COMPLETO FINALIZADO COM SUCESSO!")
            self.logger.log("RECOMENDA-SE REINICIAR O COMPUTADOR")
            self.logger.log("=" * 60)

            self.is_running = False
            return True, "Reparo completo executado com sucesso"

        except Exception as e:
            self.is_running = False
            error_msg = f"Erro durante reparo completo: {str(e)}"
            self.logger.log_error(error_msg)
            return False, error_msg

    def run_complete_repair_async(
        self, success_callback=None, error_callback=None, progress_callback=None
    ):
        """Executar reparo completo de forma assíncrona"""

        def run():
            try:
                success, message = self.run_complete_repair(progress_callback)
                if success:
                    if success_callback:
                        success_callback(message)
                else:
                    if error_callback:
                        error_callback(message)
            except Exception as e:
                if error_callback:
                    error_callback(str(e))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread


# Função auxiliar para uso no módulo commands.py
def get_complete_repair(logger):
    """Obter instância do reparo completo"""
    return CompleteWindowsRepair(logger)
