"""
Comandos do Sistema ScriptNive
core/commands.py
"""

import subprocess
import os
import threading
from pathlib import Path
from tkinter import messagebox

try:
    from core.permissions.admin import run_elevated_command, run_elevated_operation
except ImportError:
    try:
        from NiveSoftware.core.permissions.admin import (
            run_elevated_command,
            run_elevated_operation,
        )
    except ImportError:
        from core.admin import run_elevated_command, run_elevated_operation


class SystemCommands:
    """Classe para executar comandos do sistema"""

    def __init__(self, logger):
        """Inicializar comandos do sistema"""
        self.logger = logger
        self.is_running = False
        self._active_async_operations = set()
        self._active_async_operations_lock = threading.Lock()

    def run_command_sync(self, command, shell=True):
        """Executar comando sincronamente"""
        try:
            self.logger.log(f"Executando comando: {command}")
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=300,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )

            if result.returncode == 0:
                self.logger.log_success(f"Comando executado com sucesso")
                return True, result.stdout
            else:
                self.logger.log_error(f"Erro no comando. Código: {result.returncode}")
                self.logger.log_error(f"Stderr: {result.stderr}")
                return False, result.stderr

        except subprocess.TimeoutExpired:
            self.logger.log_error("Comando excedeu tempo limite (5 minutos)")
            return False, "Timeout"
        except Exception as e:
            self.logger.log_error(f"Erro ao executar comando: {str(e)}")
            return False, str(e)

    def run_command_async(
        self,
        command,
        success_callback=None,
        error_callback=None,
        elevated_operation=None,
        operation_key=None,
        elevated_timeout=300,
    ):
        """Executar comando assincronamente"""
        operation_key = operation_key or elevated_operation
        if operation_key:
            with self._active_async_operations_lock:
                if operation_key in self._active_async_operations:
                    error = "Esta operação já está em execução."
                    self.logger.log_warning(
                        f"Execução duplicada ignorada: {operation_key}"
                    )
                    if error_callback:
                        self.logger.run_on_ui(
                            lambda: error_callback(error)
                        )
                    return None
                self._active_async_operations.add(operation_key)

        def run():
            try:
                self.is_running = True
                if elevated_operation:
                    success, output = run_elevated_command(
                        elevated_operation, timeout=elevated_timeout
                    )
                    if success:
                        self.logger.log_success("Comando elevado executado com sucesso")
                    elif "solicitação de privilégios foi recusada no UAC" in str(
                        output
                    ):
                        self.logger.log_warning(
                            "Operação elevada cancelada pelo usuário no UAC"
                        )
                    else:
                        self.logger.log_error(f"Falha no comando elevado: {output}")
                else:
                    success, output = self.run_command_sync(command)

                if success:
                    if elevated_operation and output:
                        self.logger.log_info(output.strip())
                    if success_callback:
                        self.logger.run_on_ui(lambda: success_callback(output))
                else:
                    if error_callback:
                        self.logger.run_on_ui(lambda: error_callback(output))

            except Exception as e:
                self.logger.log_error(f"Erro em thread assíncrona: {str(e)}")
                if error_callback:
                    error = str(e)
                    self.logger.run_on_ui(lambda: error_callback(error))
            finally:
                self.is_running = False
                if operation_key:
                    with self._active_async_operations_lock:
                        self._active_async_operations.discard(operation_key)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def _show_operation_error(self, title, description, error):
        if "solicitação de privilégios foi recusada no UAC" in str(error):
            messagebox.showinfo(
                "Operação cancelada",
                "A solicitação de privilégios foi recusada. Nenhuma operação foi executada.",
            )
            return

        self.logger.log_error(f"{description}: {error}")
        messagebox.showerror(title, f"{description}:\n{error}")

    def empty_recycle_bin(self):
        """Esvaziar lixeira"""
        command = (
            'powershell -NoProfile -Command "'
            "try { Clear-RecycleBin -Force -ErrorAction Stop } "
            "catch { Write-Error $_.Exception.Message; exit 1 }"
            '"'
        )

        def success_callback(output):
            self.logger.log_success("Lixeira esvaziada com sucesso")
            messagebox.showinfo("Sucesso", "Lixeira esvaziada com sucesso!")

        def error_callback(error):
            self.logger.log_error("Erro ao esvaziar lixeira")
            self.logger.log(f"Detalhe do erro na lixeira: {error}")
            message = (
                "Não foi possível esvaziar totalmente a lixeira. "
                "Alguns itens podem estar em uso ou exigir privilégios elevados."
            )
            messagebox.showwarning("Atenção", message)

        return self.run_command_async(command, success_callback, error_callback)

    def activate_godmode(self):
        """Ativar GodMode"""
        try:
            desktop_path = Path.home() / "Desktop"
            godmode_path = (
                desktop_path / "GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}"
            )

            godmode_path.mkdir(exist_ok=True)

            self.logger.log_success("GodMode criado na Área de Trabalho")
            messagebox.showinfo("Sucesso", "GodMode foi criado na Área de Trabalho!")

        except Exception as e:
            self.logger.log_error(f"Erro ao criar GodMode: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao criar GodMode:\n{str(e)}")

    def check_disk_errors(self):
        """Verificar a unidade do sistema com CHKDSK online."""
        if not messagebox.askyesno(
            "Confirmar",
            "Será feita uma verificação online da unidade C: com CHKDSK. "
            "A verificação pode corrigir erros do sistema de arquivos, mas "
            "não forçará a reinicialização do computador.\nDeseja continuar?",
        ):
            self.logger.log_info("Verificação de disco cancelada pelo usuário")
            return

        def success_callback(_output):
            self.logger.log_success("Comando CHKDSK concluído sem erro de execução")
            messagebox.showinfo(
                "Verificação concluída",
                "O CHKDSK terminou sem retornar erro de execução. "
                "Consulte o log para ver a saída do comando; isso não representa "
                "uma confirmação de que todos os discos estão íntegros.",
            )

        def error_callback(error):
            self._show_operation_error(
                "Erro na verificação de disco",
                "Não foi possível concluir o CHKDSK",
                error,
            )

        return self.run_command_async(
            "chkdsk C: /scan",
            success_callback,
            error_callback,
            elevated_operation="disk_check",
            elevated_timeout=7200,
        )

    def check_ram(self):
        """Verificar RAM"""
        command = "mdsched"

        def success_callback(_output):
            self.logger.log_success("Diagnóstico de Memória do Windows aberto")
            messagebox.showinfo(
                "Diagnóstico de memória",
                "O Diagnóstico de Memória do Windows foi aberto. "
                "Escolha a opção de execução na janela do Windows; o teste "
                "e seus resultados só estarão disponíveis após a reinicialização "
                "que você confirmar no próprio Windows.",
            )

        def error_callback(error):
            self._show_operation_error(
                "Erro no diagnóstico de memória",
                "Não foi possível abrir o Diagnóstico de Memória",
                error,
            )

        return self.run_command_async(
            command,
            success_callback,
            error_callback,
            operation_key="memory_check",
        )

    def repair_system(self):
        """Reparar sistema"""
        if not messagebox.askyesno(
            "Confirmar",
            "Esta operação executará SFC e DISM, pode demorar bastante e "
            "requer privilégios de administrador. Se uma etapa falhar, as "
            "etapas seguintes não serão executadas. O ScriptNive não reiniciará "
            "o computador automaticamente.\nDeseja continuar?",
        ):
            self.logger.log_info("Reparo SFC/DISM cancelado pelo usuário")
            return

        def success_callback(_output):
            self.logger.log_success("Sequência SFC/DISM concluída sem erro de execução")
            messagebox.showinfo(
                "SFC e DISM concluídos",
                "Todos os comandos da sequência terminaram sem erro de execução. "
                "Consulte o log para a saída detalhada. O computador não será "
                "reiniciado automaticamente.",
            )

        def error_callback(error):
            self._show_operation_error(
                "Erro no reparo do sistema",
                "A sequência SFC/DISM foi interrompida",
                error,
            )

        return self.run_command_async(
            "sfc /scannow",
            success_callback,
            error_callback,
            elevated_operation="system_repair",
            elevated_timeout=7200,
        )

    def clean_temp_files(self):
        """Limpar arquivos temporários"""
        def run():
            try:
                elevated, results = run_elevated_operation("clean_temp_files")
            except Exception as e:
                error = str(e)
                self.logger.log_error(f"Falha ao limpar arquivos temporários: {error}")
                self.logger.run_on_ui(
                    lambda: messagebox.showerror("Erro", error)
                )
                return

            if not elevated:
                self.logger.log_error(f"Falha ao limpar arquivos temporários: {results}")
                self.logger.run_on_ui(
                    lambda: messagebox.showerror("Erro", str(results))
                )
                return

            failures = [
                result["stderr"] or f"Código {result['returncode']}"
                for result in results
                if result["returncode"] != 0
            ]
            for failure in failures:
                self.logger.log_warning(
                    f"Uma etapa de limpeza não foi concluída: {failure}"
                )

            try:
                subprocess.Popen("cleanmgr.exe", shell=True)
            except OSError as e:
                error = str(e)
                self.logger.log_error(
                    f"Não foi possível abrir a Limpeza de Disco: {error}"
                )
                self.logger.run_on_ui(
                    lambda: messagebox.showerror(
                        "Erro",
                        f"Arquivos tratados, mas não foi possível abrir cleanmgr:\n{error}",
                    )
                )
                return

            self.logger.log_success("Etapas de limpeza temporária concluídas")
            message = "Etapas de limpeza temporária concluídas."
            if failures:
                message += "\nAlgumas pastas continham arquivos em uso ou não puderam ser limpas."
            self.logger.run_on_ui(
                lambda: messagebox.showinfo("Limpeza", message)
            )

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def clean_dns_cache(self):
        """Limpar cache DNS - Versão corrigida"""

        # Comandos de limpeza DNS separados para melhor controle
        dns_commands = [
            (
                "Resetando Winsock (repara catálogo de sockets)...",
                "netsh winsock reset",
            ),
            (
                "Resetando pilha TCP/IP (repara configurações IP)...",
                "netsh int ip reset",
            ),
            (
                "Limpando cache NetBIOS (purga nomes locais)...",
                "nbtstat -R",
            ),  # Extra: útil para problemas de nomes de rede
            (
                "Liberando nomes NetBIOS (atualiza registro)...",
                "nbtstat -RR",
            ),  # Extra: complementa o anterior
            (
                "Limpando cache ARP (remove mapeamentos de IP para MAC)...",
                "arp -d *",
            ),  # Extra: bom para conflitos de hardware na rede
            (
                "Parando serviço DNS Client...",
                "net stop dnscache",
            ),  # Da sua lista, opcional mas ajuda em flushes mais profundos
            ("Limpando cache DNS...", "ipconfig /flushdns"),
            ("Reiniciando serviço DNS Client...", "net start dnscache"),  # Da sua lista
            ("Liberando IP atual...", "ipconfig /release"),
            ("Renovando IP...", "ipconfig /renew"),
            ("Registrando DNS...", "ipconfig /registerdns"),
        ]

        def execute_dns_cleanup():
            try:
                success, results = run_elevated_operation("dns_cleanup", timeout=60)
                if not success:
                    return False, results

                success_count = 0
                descriptions = [description for description, _ in dns_commands]
                descriptions.extend(["Reset adicional do Winsock", "Reset adicional TCP/IP"])
                for description, result in zip(descriptions, results):
                    self.logger.log(description)
                    if result.get("aborted"):
                        return False, result["stderr"]
                    if result["returncode"] == 0:
                        success_count += 1
                        self.logger.log_success(f"✓ {description} - Sucesso")
                    else:
                        self.logger.log_warning(
                            f"⚠ {description} - Código: {result['returncode']}"
                        )

                return (
                    success_count > 0,
                    f"Executados {success_count} comandos com sucesso",
                )

            except subprocess.TimeoutExpired:
                return False, "Timeout - Operação demorou muito para completar"
            except Exception as e:
                return False, f"Erro inesperado: {str(e)}"

        def success_callback(output):
            self.logger.log_success("Cache DNS limpo com sucesso!")
            messagebox.showinfo(
                "Sucesso",
                "Cache DNS limpo com sucesso!\n\n"
                "Recomenda-se reiniciar o navegador para aplicar as mudanças.\n\n"
                "Detalhes no log.",
            )

        def error_callback(error):
            self.logger.log_error(f"Erro ao limpar cache DNS: {error}")
            messagebox.showerror(
                "Erro",
                f"Erro ao limpar cache DNS:\n\n{error}\n\n"
                "Possíveis soluções:\n"
                "• Execute como Administrador\n"
                "• Verifique sua conexão de rede\n"
                "• Tente novamente em alguns minutos",
            )

        # Executar de forma assíncrona
        def run():
            try:
                self.is_running = True
                self.logger.log("Iniciando limpeza de cache DNS...")

                success, output = execute_dns_cleanup()
                self.is_running = False

                if success:
                    self.logger.run_on_ui(lambda: success_callback(output))
                else:
                    self.logger.run_on_ui(lambda: error_callback(output))

            except Exception as e:
                self.is_running = False
                error = str(e)
                self.logger.run_on_ui(lambda: error_callback(error))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def fix_audio(self):
        """Reparar som - Exatamente como no .bat"""
        commands = [
            "net stop audiosrv",
            "timeout /t 5",
            "net start audiosrv",
            "net start AudioEndpointBuilder",
            "net start wuauserv",
        ]

        full_command = " & ".join(commands)

        def success_callback(output):
            self.logger.log_success("Serviços de áudio reiniciados")
            messagebox.showinfo(
                "Sucesso",
                "Serviços de áudio reiniciados!\nVerifique se os problemas foram resolvidos.",
            )

        def error_callback(error):
            self.logger.log_error("Erro ao reparar áudio")
            messagebox.showerror("Erro", f"Erro ao reparar áudio:\n{error}")

        return self.run_command_async(
            full_command,
            success_callback,
            error_callback,
            elevated_operation="audio_repair",
        )

    def update_programs(self):
        """Atualizar programas com winget"""
        command = "winget upgrade --all"

        def success_callback(output):
            self.logger.log_success("Programas atualizados")
            messagebox.showinfo("Sucesso", "Atualização de programas concluída!")

        def error_callback(error):
            self.logger.log_error("Erro ao atualizar programas")
            messagebox.showerror("Erro", f"Erro ao atualizar programas:\n{error}")

        return self.run_command_async(command, success_callback, error_callback)

    def delete_corrupted_folder(self, folder_path):
        """Deletar pasta corrompida - Exatamente como no .bat"""
        if not folder_path or not os.path.exists(folder_path):
            self.logger.log_error("Caminho da pasta inválido")
            return False

        commands = [
            f'attrib -R -S -H "{folder_path}" /S /D',
            f'takeown /f "{folder_path}" /r /d y',
            f'icacls "{folder_path}" /grant administrators:F /t',
            f'rd /s /q "{folder_path}"',
        ]

        self.logger.log(f"Tentando deletar pasta: {folder_path}")

        for cmd in commands:
            success, output = self.run_command_sync(cmd)

        # Verificar se pasta ainda existe
        if not os.path.exists(folder_path):
            self.logger.log_success(f"Pasta deletada com sucesso: {folder_path}")
            return True
        else:
            # Tentar método "zumbi" como no .bat original
            self.logger.log_warning(
                "Pasta ainda existe, tentando método alternativo..."
            )

            try:
                import tempfile

                temp_dir = tempfile.mkdtemp()

                # Usar robocopy para sobrescrever com pasta vazia
                robocopy_cmd = f'robocopy "{temp_dir}" "{folder_path}" /MIR'
                success, output = self.run_command_sync(robocopy_cmd)

                # Tentar deletar novamente
                success, output = self.run_command_sync(f'rd /s /q "{folder_path}"')

                # Limpar pasta temporária
                os.rmdir(temp_dir)

                if not os.path.exists(folder_path):
                    self.logger.log_success(
                        "Pasta corrompida deletada com método alternativo"
                    )
                    return True
                else:
                    self.logger.log_error(
                        "Não foi possível deletar a pasta mesmo com método alternativo"
                    )
                    return False

            except Exception as e:
                self.logger.log_error(f"Erro no método alternativo: {str(e)}")
                return False

    def delete_corrupted_folder_async(
        self, folder_path, success_callback=None, error_callback=None
    ):
        def run():
            try:
                elevated, results = run_elevated_operation(
                    "delete_corrupted_folder", arguments={"path": folder_path}
                )
                if not elevated:
                    self.logger.log_error(f"Falha ao elevar remoção da pasta: {results}")
                    if error_callback:
                        self.logger.run_on_ui(lambda: error_callback(str(results)))
                    return

                result = results[0]
                if result["returncode"] == 0:
                    self.logger.log_success(f"Pasta deletada: {folder_path}")
                    if success_callback:
                        self.logger.run_on_ui(
                            lambda: success_callback(result["stdout"])
                        )
                else:
                    self.logger.log_warning(
                        f"Falha ao deletar pasta {folder_path}: {result['stderr']}"
                    )
                    if error_callback:
                        self.logger.run_on_ui(
                            lambda: error_callback(result["stderr"])
                        )
            except Exception as e:
                self.logger.log_error(f"Erro ao deletar pasta {folder_path}: {e}")
                if error_callback:
                    error = str(e)
                    self.logger.run_on_ui(lambda: error_callback(error))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def schedule_reboot_async(self, error_callback=None):
        def run():
            try:
                success, output = run_elevated_command("schedule_reboot")
                if not success:
                    self.logger.log_error(
                        f"Falha ao agendar reinicialização: {output}"
                    )
                    if error_callback:
                        self.logger.run_on_ui(
                            lambda: error_callback(str(output))
                        )
                    return
                self.logger.log_info("Reinicialização agendada pelo usuário")
            except Exception as e:
                error = str(e)
                self.logger.log_error(
                    f"Falha ao agendar reinicialização: {error}"
                )
                if error_callback:
                    self.logger.run_on_ui(lambda: error_callback(error))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def open_system_tools(self):
        """Métodos para abrir ferramentas do sistema"""

        def open_control_panel(self):
            subprocess.Popen("control.exe")
            self.logger.log("Painel de Controle aberto")

        def open_task_manager(self):
            subprocess.Popen("taskmgr.exe")
            self.logger.log("Gerenciador de Tarefas aberto")

        def start_mrt(self):
            command = "powershell.exe -command \"Start-Process 'C:\\Windows\\System32\\MRT.exe'\""

            def success_callback(output):
                self.logger.log_success(
                    "MRT (Malicious Software Removal Tool) iniciado"
                )

            def error_callback(error):
                self.logger.log_error("Erro ao iniciar MRT")
                messagebox.showerror("Erro", f"Erro ao iniciar MRT:\n{error}")

            return self.run_command_async(command, success_callback, error_callback)

        def check_diagnostics():
            subprocess.Popen(["perfmon.exe", "/rel"])
            self.logger.log("Monitor de Confiabilidade (perfmon) aberto")

        return {
            "control_panel": open_control_panel,
            "task_manager": open_task_manager,
            "mrt": start_mrt,
            "diagnostics": check_diagnostics,
        }

    # Adicione no final da classe SystemCommands no módulo commands.py:

    def complete_windows_repair(
        self,
        progress_callback=None,
        success_callback=None,
        error_callback=None,
    ):
        """Executar reparo completo do Windows (baseado no script do Ivo Dias)"""
        from tkinter import messagebox

        if success_callback is None and error_callback is None:
            if not messagebox.askyesno(
                "ATENÇÃO - Reparo Completo do Windows",
                "Esta operação irá:\n\n"
                "• Executar reparos profundos no sistema\n"
                "• Resetar configurações de rede\n"
                "• Limpar arquivos do Windows Update\n"
                "• Remover software pirata (se encontrado)\n"
                "• Re-registrar DLLs críticas\n"
                "• Agendar verificação de disco\n\n"
                "ESTE PROCESSO PODE DEMORAR MUITO TEMPO!\n"
                "Deseja continuar?",
            ):
                return

        def default_success_callback(message):
            self.logger.log_success("Reparo completo finalizado com sucesso!")
            messagebox.showinfo(
                "Reparo Concluído",
                "Reparo completo do Windows finalizado!\n\n"
                "RECOMENDA-SE REINICIAR O COMPUTADOR AGORA.\n\n"
                "Deseja reiniciar agora?",
            )

            if messagebox.askyesno("Reiniciar", "Reiniciar o computador agora?"):
                self.schedule_reboot_async(
                    lambda error: messagebox.showerror(
                        "Erro", f"Não foi possível agendar a reinicialização:\n{error}"
                    )
                )

        def default_error_callback(error):
            self.logger.log_error(f"Erro durante reparo completo: {error}")
            messagebox.showerror(
                "Erro no Reparo",
                f"Ocorreu um erro durante o reparo completo:\n\n{error}\n\n"
                "Verifique o log para mais detalhes.",
            )

        if success_callback is None:
            success_callback = default_success_callback
        if error_callback is None:
            error_callback = default_error_callback

        def run():
            try:
                self.is_running = True

                def report_progress(percentage, description):
                    if progress_callback:
                        self.logger.run_on_ui(
                            lambda: progress_callback(percentage, description)
                        )

                elevated, results = run_elevated_operation(
                    "complete_repair",
                    progress_callback=report_progress,
                )
                if not elevated:
                    self.logger.run_on_ui(lambda: error_callback(results))
                    return

                result = results[0]
                if result["returncode"] == 0:
                    self.logger.run_on_ui(
                        lambda: success_callback(result["stdout"])
                    )
                else:
                    self.logger.run_on_ui(lambda: error_callback(result["stderr"]))
            except Exception as e:
                self.logger.log_error(f"Erro no processo de reparo elevado: {e}")
                error = str(e)
                self.logger.run_on_ui(lambda: error_callback(error))
            finally:
                self.is_running = False

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def is_command_running(self):
        """Verificar se algum comando está em execução"""
        return self.is_running
