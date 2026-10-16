import tkinter as tk
from tkinter import messagebox
import winreg
import threading

# Importar módulos de otimização
try:
    from optimization.startup.boost_windows import AceleradorWindows
    from optimization.performance.telemetry import RemoverTelemetria
    from optimization.startup.features import RemoverFeatures
    from optimization.performance.animations import RemoverAnimacoes
    from optimization.performance.edge import OtimizadorEdge
    from optimization.startup.tasks import DesabilitadorTweaks
    from optimization.startup.apps import DisableSoftware
    from optimization.startup.services import DesabilitadorServicos
except ImportError:
    try:
        from core.boost_windows import AceleradorWindows
        from core.telemetry import RemoverTelemetria
        from core.features import RemoverFeatures
        from core.animations import RemoverAnimacoes
        from core.edge import OtimizadorEdge
        from core.tasks import DesabilitadorTweaks
        from core.apps import DisableSoftware
        from core.services import DesabilitadorServicos
    except ImportError:
        AceleradorWindows = None
        RemoverTelemetria = None
        RemoverFeatures = None
        RemoverAnimacoes = None
        OtimizadorEdge = None
        DesabilitadorTweaks = None
        DisableSoftware = None
        DesabilitadorServicos = None

# Importar módulo de resultados
from .boost_results import OptimizationResults
try:
    from core.permissions.admin import run_elevated_operation
except ImportError:
    try:
        from NiveSoftware.core.permissions.admin import run_elevated_operation
    except ImportError:
        from core.admin import run_elevated_operation


class OptimizationHandlers:
    """Classe responsável pelos handlers das funções de otimização"""

    def __init__(self, optimization_tab):
        """Inicializar handlers"""
        self.parent = optimization_tab
        self.results = OptimizationResults(self)
        self._active_operations = set()
        self._active_operations_lock = threading.Lock()

    def _begin_operation(self, operation):
        with self._active_operations_lock:
            if operation in self._active_operations:
                messagebox.showwarning(
                    "Operação em andamento",
                    "Esta mesma operação já está em execução.",
                )
                return False
            self._active_operations.add(operation)
        return True

    def _end_operation(self, operation):
        with self._active_operations_lock:
            self._active_operations.discard(operation)

    def remove_telemetry(self):
        """Remover Telemetria usando o módulo RemoverTelemetria"""
        if not self.parent.confirm_operation(
            "Remover Telemetria",
            "Esta operação irá remover sistemas de telemetria e coleta de dados:\n\n"
            "• Desabilitar telemetria do Windows\n"
            "• Remover metadados de dispositivos da rede\n"
            "• Desabilitar Customer Experience Improvement Program\n"
            "• Desabilitar Application Compatibility tracking\n"
            "• Desabilitar AutoLoggers de diagnóstico\n"
            "• Desabilitar controle da Assistência Remota\n"
            "• Desabilitar ofertas do Malicious Software Removal Tool\n\n"
            "O Windows SmartScreen e os recursos de segurança não serão desabilitados.\n"
            "Esta operação requer autorização administrativa pelo UAC.\n\n"
            "Deseja continuar?",
        ):
            return

        # Verificar se o módulo está disponível
        if RemoverTelemetria is None:
            messagebox.showerror(
                "Erro",
                "Módulo de remoção de telemetria não encontrado!\n\n"
                "Verifique se o arquivo 'core/telemetry.py' existe.",
            )
            return

        # Criar janela de progresso
        progress_window, status_label, progress_bar, log_text = (
            self.parent.ui.show_progress_dialog("Removendo Telemetria")
        )

        def run_telemetry_removal():
            """Executar remoção de telemetria em thread separada"""
            try:
                result = self._run_elevated_optimization(
                    "optimization_telemetry",
                    progress_window,
                    status_label,
                    progress_bar,
                    log_text,
                )
                if result is None:
                    return
                success, sucessos, erros = result

                # Mostrar resultado final
                def show_result():
                    progress_bar.stop()
                    self.results.show_telemetry_result(
                        progress_window, status_label, success, sucessos, erros
                    )

                # Agendar para thread principal
                self.parent.logger.run_on_ui(
                    lambda: progress_window.after(500, show_result)
                )

            except Exception as e:
                self._handle_error(
                    progress_window,
                    progress_bar,
                    status_label,
                    e,
                    "remoção de telemetria",
                )

        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=run_telemetry_removal, daemon=True)
        thread.start()

    def disable_windows_services(self):
        """Desabilitar serviços desnecessários do Windows usando o módulo DesabilitadorServicos"""
        if not self.parent.confirm_operation(
            "Desabilitar Serviços do Windows",
            "Serão alterados apenas estes serviços opcionais:\n\n"
            "• DiagTrack e o coletor padrão do Diagnostics Hub\n"
            "• dmwappushservice e Registro Remoto\n"
            "• Compartilhamento de rede do Windows Media Player\n"
            "• Retail Demo e serviços legados de Grupo Doméstico\n\n"
            "Outros serviços de rede, atualização, backup, segurança, busca e hardware "
            "não serão alterados.\n"
            "Esta operação requer autorização administrativa pelo UAC.\n\n"
            "Deseja continuar?",
        ):
            return

        # Verificar se o módulo está disponível
        if DesabilitadorServicos is None:
            messagebox.showerror(
                "Erro",
                "Módulo de desabilitação de serviços não encontrado!\n\n"
                "Verifique se o arquivo 'core/services.py' existe.",
            )
            return

        # Criar janela de progresso
        progress_window, status_label, progress_bar, log_text = (
            self.parent.ui.show_progress_dialog("Desabilitando Serviços do Windows")
        )

        def run_services_disable():
            """Executar desabilitação de serviços em thread separada"""
            try:
                result = self._run_elevated_optimization(
                    "optimization_services",
                    progress_window,
                    status_label,
                    progress_bar,
                    log_text,
                )
                if result is None:
                    return
                success, sucessos, erros = result

                # Mostrar resultado final
                def show_result():
                    progress_bar.stop()
                    self.results.show_services_result(
                        progress_window, status_label, success, sucessos, erros
                    )

                # Agendar para thread principal
                self.parent.logger.run_on_ui(
                    lambda: progress_window.after(500, show_result)
                )

            except Exception as e:
                self._handle_error(
                    progress_window,
                    progress_bar,
                    status_label,
                    e,
                    "desabilitação de serviços",
                )

        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=run_services_disable, daemon=True)
        thread.start()

    def disable_windows_software(self):
        """Desabilitar softwares do Windows"""
        if not self.parent.confirm_operation(
            "Desabilitar Softwares do Windows",
            "Esta operação pode desativar a hibernação e tentar desinstalar Paint, "
            "Vínculo com Celular, Cortana, OneDrive e aplicativos Xbox/Store. "
            "Os aplicativos removidos poderão exigir reinstalação manual; a operação "
            "não cria um mecanismo próprio de restauração.\n\n"
            "Deseja continuar?",
        ):
            return

        if DisableSoftware is None:
            messagebox.showerror(
                "Erro",
                "Módulo de desabilitação de softwares não encontrado!\n\n"
                "Verifique se o arquivo 'core/apps.py' existe.",
            )
            return

        if not self._begin_operation("disable_windows_software"):
            return

        # Criar janela de progresso
        progress_window, status_label, progress_bar, log_text = (
            self.parent.ui.show_progress_dialog("Desabilitando Softwares do Windows")
        )

        def run_disable_software():
            """Executar desabilitação de softwares em thread separada"""
            try:
                progress_logger = self._create_progress_logger(log_text)
                desabilitador = DisableSoftware(logger=progress_logger)

                # Atualizar status
                self.parent.logger.run_on_ui(
                    lambda: status_label.config(text="Desabilitando softwares...")
                )

                # Executar desabilitação
                success, sucessos, erros = (
                    desabilitador.executar_desabilitacao_softwares()
                )

                # Mostrar resultado final
                def show_result():
                    progress_bar.stop()
                    self.results.show_disable_software_result(
                        progress_window, status_label, success, sucessos, erros
                    )

                # Agendar resultado para a thread principal
                self.parent.logger.run_on_ui(
                    lambda: progress_window.after(500, show_result)
                )

            except Exception as e:
                self._handle_error(
                    progress_window,
                    progress_bar,
                    status_label,
                    e,
                    "desabilitação de softwares",
                )
            finally:
                self._end_operation("disable_windows_software")

        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=run_disable_software, daemon=True)
        thread.start()

    def disable_web_search(self):
        """Desabilitar busca web na barra de pesquisa"""
        if self.parent.confirm_operation(
            "Desabilitar Busca Web",
            "Esta operação irá desabilitar a busca online na barra de pesquisa.\n\n"
            "A alteração é feita somente nas configurações do usuário atual.\n\n"
            "Deseja continuar?",
        ):
            try:
                # Desabilitar BingSearch
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Search",
                    0,
                    winreg.KEY_SET_VALUE,
                )
                winreg.SetValueEx(key, "BingSearchEnabled", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)

                # Desabilitar SearchBox Suggestions
                key = winreg.CreateKey(
                    winreg.HKEY_CURRENT_USER,
                    r"SOFTWARE\Policies\Microsoft\Windows\Explorer",
                )
                winreg.SetValueEx(
                    key, "DisableSearchBoxSuggestions", 0, winreg.REG_DWORD, 1
                )
                winreg.CloseKey(key)

                messagebox.showinfo("Sucesso", "Busca web desabilitada com sucesso!")
                self.parent.log_activity("Busca web na barra de pesquisa desabilitada")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao desabilitar busca web: {str(e)}")

    def disable_browser_cache(self):
        """Informar que a alteração de cache ainda não está implementada."""
        message = (
            "A alteração do cache de navegadores e streaming não está implementada. "
            "Nenhuma configuração foi modificada."
        )
        messagebox.showinfo("Opção indisponível", message)
        self.parent.log_activity("Cache de navegadores: opção não implementada")

    def disable_lock_screen_ads(self):
        """Desabilitar propagandas na tela de bloqueio"""
        if self.parent.confirm_operation(
            "Desabilitar Propagandas na Tela de Bloqueio",
            "Esta operação irá remover propagandas da tela de bloqueio.\n\n"
            "A alteração é feita somente nas configurações do usuário atual.\n\n"
            "Deseja continuar?",
        ):
            try:
                # Desabilitar RotatingLockScreenOverlay
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                    0,
                    winreg.KEY_SET_VALUE,
                )
                winreg.SetValueEx(
                    key, "RotatingLockScreenOverlayEnabled", 0, winreg.REG_DWORD, 0
                )
                winreg.SetValueEx(
                    key, "SubscribedContent-338387Enabled", 0, winreg.REG_DWORD, 0
                )
                winreg.CloseKey(key)

                messagebox.showinfo(
                    "Sucesso", "Propagandas na tela de bloqueio desabilitadas!"
                )
                self.parent.log_activity(
                    "Propagandas na tela de bloqueio desabilitadas"
                )

            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Erro ao desabilitar propagandas: {str(e)}"
                )

    # Métodos auxiliares privados
    def _run_elevated_optimization(
        self, operation, progress_window, status_label, progress_bar, log_text
    ):
        """Executar uma otimização administrativa pelo fluxo UAC existente."""
        self.parent.logger.run_on_ui(
            lambda: status_label.config(text="Aguardando autorização do Windows...")
        )
        elevated, results = run_elevated_operation(operation, timeout=7200)
        if not elevated:
            message = str(results)

            def show_elevation_error():
                progress_bar.stop()
                progress_window.destroy()
                if "recusada no UAC" in message:
                    messagebox.showinfo(
                        "Operação cancelada",
                        "A solicitação de privilégios foi cancelada. "
                        "Nenhuma alteração foi aplicada por esta operação.",
                    )
                else:
                    messagebox.showerror(
                        "Falha na elevação", f"Não foi possível executar:\n\n{message}"
                    )
                self.parent.log_activity(
                    f"Falha/cancelamento UAC em {operation}: {message}"
                )

            self.parent.logger.run_on_ui(show_elevation_error)
            return None

        if not isinstance(results, list) or not results:
            return False, [], ["O processo elevado não retornou um resultado."]

        result = results[0]
        if not isinstance(result, dict):
            return False, [], ["O processo elevado retornou dados inválidos."]
        data = result.get("data")
        if not isinstance(data, dict):
            data = {}
        successes = data.get("successes", [])
        errors = data.get("errors", [])
        if not isinstance(successes, list):
            successes = []
        if not isinstance(errors, list):
            errors = []

        output = result.get("stdout", "")
        if output:
            def append_output():
                for line in output.rstrip().splitlines():
                    log_text.insert(tk.END, line + "\n")
                log_text.see(tk.END)

            self.parent.logger.run_on_ui(append_output)

        if result.get("returncode") != 0 and not errors:
            errors = [result.get("stderr") or "A operação terminou com falha."]
        elif result.get("returncode") == 0 and not successes:
            errors = ["A operação terminou sem confirmar alterações aplicadas."]
        success = result.get("returncode") == 0 and bool(successes) and not errors
        return success, successes, errors

    def _create_progress_logger(self, log_widget):
        """Criar logger personalizado para capturar mensagens"""
        ui_logger = self.parent.logger

        class ProgressLogger:
            def __init__(self, log_widget):
                self.log_widget = log_widget
                self.ui_logger = ui_logger

            def log(self, message):
                self.ui_logger.run_on_ui(lambda: self.update_log(message))

            def info(self, message):
                # Alias para compatibilidade com módulos que usam logger.info()
                self.log(f"INFO: {message}")

            def warning(self, message):
                # Alias para compatibilidade com módulos que usam logger.warning()
                self.log(f"WARNING: {message}")

            def error(self, message):
                # Alias para compatibilidade com módulos que usam logger.error()
                self.log(f"ERROR: {message}")

            def update_log(self, message):
                self.log_widget.insert(tk.END, message + "\n")
                self.log_widget.see(tk.END)

        return ProgressLogger(log_widget)

    def _execute_optimization(self, optimization_type):
        """Executar otimização específica (método genérico para funções não implementadas)"""
        try:
            messagebox.showinfo(
                "Em Desenvolvimento",
                f"A otimização '{optimization_type}' será implementada em breve.\n\n"
                "Os scripts .bat correspondentes precisam ser convertidos para Python.",
            )
            self.parent.log_activity(f"Tentativa de execução: {optimization_type}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar otimização: {str(e)}")
            self.parent.log_activity(f"Erro em {optimization_type}: {str(e)}")

    def _handle_error(
        self, progress_window, progress_bar, status_label, error, operation_name
    ):
        """Tratar erros gerais"""

        def show_error():
            progress_bar.stop()
            status_label.config(text="❌ Erro crítico")
            progress_window.after(1000, progress_window.destroy)
            messagebox.showerror(
                "Erro Crítico",
                f"Erro crítico durante a {operation_name}:\n\n{str(error)}",
            )
            self.parent.log_activity(f"Erro crítico na {operation_name}: {str(error)}")

        self.parent.logger.run_on_ui(show_error)

    def remove_unused_features(self):
        """Remover Features Não Usadas usando o módulo RemoverFeatures"""
        if not self.parent.confirm_operation(
            "Remover Features Não Usadas",
            "Esta operação irá remover recursos e funcionalidades não utilizadas:\n\n"
            "• Desabilitar IIS e componentes web\n"
            "• Remover Message Queue (MSMQ)\n"
            "• Desabilitar WCF e recursos de desenvolvimento\n"
            "• Remover Hyper-V (se não utilizado)\n"
            "• Remover apps opcionais (WordPad, IE, etc.)\n"
            "• Desabilitar protocolo SMB1 (inseguro)\n"
            "• Remover recursos de rede avançados\n"
            "• E outras funcionalidades raramente usadas...\n\n"
            "Recursos removidos podem exigir reinstalação manual. "
            "O UAC será solicitado para esta operação.\n\n"
            "Deseja continuar?",
        ):
            return

        # Verificar se o módulo está disponível
        if RemoverFeatures is None:
            messagebox.showerror(
                "Erro",
                "Módulo de remoção de features não encontrado!\n\n"
                "Verifique se o arquivo 'core/features.py' existe.",
            )
            return

        # Criar janela de progresso
        progress_window, status_label, progress_bar, log_text = (
            self.parent.ui.show_progress_dialog("Removendo Features Não Usadas")
        )

        def run_features_removal():
            """Executar remoção de features em thread separada"""
            try:
                result = self._run_elevated_optimization(
                    "optimization_features",
                    progress_window,
                    status_label,
                    progress_bar,
                    log_text,
                )
                if result is None:
                    return
                success, sucessos, erros = result

                # Mostrar resultado final
                def show_result():
                    progress_bar.stop()
                    self.results.show_features_result(
                        progress_window, status_label, success, sucessos, erros
                    )

                # Agendar para thread principal
                self.parent.logger.run_on_ui(
                    lambda: progress_window.after(500, show_result)
                )

            except Exception as e:
                self._handle_error(
                    progress_window,
                    progress_bar,
                    status_label,
                    e,
                    "remoção de features",
                )

        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=run_features_removal, daemon=True)
        thread.start()

    def remove_animations(self):
        """Remover Animações usando o módulo RemoverAnimacoes"""
        if not self.parent.confirm_operation(
            "Remover Animações Desnecessárias",
            "Esta operação irá desabilitar animações e efeitos visuais:\n\n"
            "• Desabilitar animações de janelas\n"
            "• Remover efeitos visuais avançados\n"
            "• Desabilitar animações da barra de tarefas\n"
            "• Otimizar arrastar janelas\n"
            "• Desabilitar transparências desnecessárias\n"
            "• Remover sombras em listas\n"
            "• Otimizar suavização de fontes\n"
            "• E outras otimizações visuais...\n\n"
            "Altera somente preferências visuais do usuário atual e não oferece "
            "restauração automática.\n\n"
            "Deseja continuar?",
        ):
            return

        # Verificar se o módulo está disponível
        if RemoverAnimacoes is None:
            messagebox.showerror(
                "Erro",
                "Módulo de remoção de animações não encontrado!\n\n"
                "Verifique se o arquivo 'core/animations.py' existe.",
            )
            return

        if not self._begin_operation("remove_animations"):
            return

        # Criar janela de progresso
        progress_window, status_label, progress_bar, log_text = (
            self.parent.ui.show_progress_dialog("Removendo Animações")
        )

        def run_animations_removal():
            """Executar remoção de animações em thread separada"""
            try:
                progress_logger = self._create_progress_logger(log_text)
                removedor = RemoverAnimacoes(logger=progress_logger)

                # Atualizar status
                self.parent.logger.run_on_ui(
                    lambda: status_label.config(text="Desabilitando animações...")
                )

                # Executar remoção
                success, sucessos, erros = removedor.executar_remocao_animacoes()

                # Mostrar resultado final
                def show_result():
                    progress_bar.stop()
                    self.results.show_animations_result(
                        progress_window, status_label, success, sucessos, erros
                    )

                # Agendar para thread principal
                self.parent.logger.run_on_ui(
                    lambda: progress_window.after(500, show_result)
                )

            except Exception as e:
                self._handle_error(
                    progress_window,
                    progress_bar,
                    status_label,
                    e,
                    "remoção de animações",
                )
            finally:
                self._end_operation("remove_animations")

        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=run_animations_removal, daemon=True)
        thread.start()

    def optimize_edge(self):
        """Otimizar Microsoft Edge usando o módulo OtimizadorEdge"""
        if not self.parent.confirm_operation(
            "Otimizar Microsoft Edge",
            "Esta operação irá aplicar otimizações específicas para o Microsoft Edge:\n\n"
            "• Desabilitar sidebar/botão Bing\n"
            "• Desabilitar execução em segundo plano\n"
            "• Desabilitar inicialização automática\n"
            "• Remover botão de assinatura Acrobat\n"
            "• Desabilitar geolocalização por padrão\n"
            "• Desabilitar acesso a sensores\n"
            "• Desabilitar notificações de sites\n"
            "• E outras otimizações de privacidade...\n\n"
            "As políticas serão gravadas no Registro do computador. "
            "O UAC será solicitado para esta operação.\n\n"
            "Deseja continuar?",
        ):
            return

        # Verificar se o módulo está disponível
        if OtimizadorEdge is None:
            messagebox.showerror(
                "Erro",
                "Módulo de otimização do Edge não encontrado!\n\n"
                "Verifique se o arquivo 'core/edge.py' existe.",
            )
            return

        # Criar janela de progresso
        progress_window, status_label, progress_bar, log_text = (
            self.parent.ui.show_progress_dialog("Otimizando Microsoft Edge")
        )

        def run_edge_optimization():
            """Executar otimização do Edge em thread separada"""
            try:
                result = self._run_elevated_optimization(
                    "optimization_edge",
                    progress_window,
                    status_label,
                    progress_bar,
                    log_text,
                )
                if result is None:
                    return
                success, sucessos, erros = result

                # Mostrar resultado final
                def show_result():
                    progress_bar.stop()
                    self.results.show_edge_result(
                        progress_window, status_label, success, sucessos, erros
                    )

                # Agendar para thread principal
                self.parent.logger.run_on_ui(
                    lambda: progress_window.after(500, show_result)
                )

            except Exception as e:
                self._handle_error(
                    progress_window, progress_bar, status_label, e, "otimização do Edge"
                )

        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=run_edge_optimization, daemon=True)
        thread.start()

    def accelerate_windows(self):
        """Acelerar Windows usando o módulo AceleradorWindows"""
        if not self.parent.confirm_operation(
            "Aplicar Ajustes do Windows",
            "Esta operação irá aplicar 12 ajustes predefinidos de Registro e configuração. "
            "Não há garantia de ganho de desempenho; os efeitos variam conforme o sistema.\n\n"
            "• Otimização de Boot\n"
            "• Aceleração do Menu Iniciar\n"
            "• Aumento da Taxa de Upload\n"
            "• Otimização TCP/IP e DNS\n"
            "• GPU Hardware Scheduling\n"
            "• Modo Compacto no Explorer\n"
            "• Desabilitar Apps em Background\n"
            "• Otimização para Jogos\n"
            "• E outras melhorias...\n\n"
            "Alguns ajustes não têm restauração automática. "
            "Como a operação mistura Registro do computador e do usuário, ela não "
            "inicia um processo elevado separado. Execute o ScriptNive como "
            "administrador na conta atual; sem isso, nenhuma alteração será iniciada.\n\n"
            "Deseja continuar?",
        ):
            return

        # Verificar se o módulo está disponível
        if AceleradorWindows is None:
            messagebox.showerror(
                "Erro",
                "Módulo de aceleração não encontrado!\n\n"
                "Verifique se o arquivo 'core/boost_windows.py' existe.",
            )
            return

        if not self._begin_operation("accelerate_windows"):
            return

        # Criar janela de progresso
        progress_window, status_label, progress_bar, log_text = (
            self.parent.ui.show_progress_dialog("Aplicando Ajustes do Windows")
        )

        def run_acceleration():
            """Executar aceleração em thread separada"""
            try:
                progress_logger = self._create_progress_logger(log_text)
                acelerador = AceleradorWindows(logger=progress_logger)
                self.parent.logger.run_on_ui(
                    lambda: status_label.config(text="Aplicando ajustes...")
                )
                success, sucessos, erros = acelerador.executar_todas_otimizacoes()

                # Mostrar resultado final
                def show_result():
                    progress_bar.stop()
                    self.results.show_acceleration_result(
                        progress_window, status_label, success, sucessos, erros
                    )

                # Agendar para thread principal
                self.parent.logger.run_on_ui(
                    lambda: progress_window.after(500, show_result)
                )

            except Exception as e:
                self._handle_error(
                    progress_window, progress_bar, status_label, e, "aceleração"
                )
            finally:
                self._end_operation("accelerate_windows")

        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=run_acceleration, daemon=True)
        thread.start()

    def disable_scheduled_tasks(self):
        """Desabilitar Tarefas Agendadas usando o módulo DesabilitadorTweaks"""
        if not self.parent.confirm_operation(
            "Desabilitar Tarefas Agendadas",
            "Esta operação irá desabilitar tarefas agendadas desnecessárias:\n\n"
            "• Tarefas de telemetria e coleta de dados\n"
            "• Algumas tarefas de diagnóstico e avaliação do Windows\n\n"
            "Atualizações de aplicativos, Restauração do Sistema, Histórico de Arquivos, "
            "SmartScreen e recursos de segurança serão preservados.\n"
            "Tarefas ausentes ou que não puderem ser alteradas serão informadas como "
            "não aplicadas. Esta operação requer autorização administrativa pelo UAC.\n\n"
            "Deseja continuar?",
        ):
            return

        # Verificar se o módulo está disponível
        if DesabilitadorTweaks is None:
            messagebox.showerror(
                "Erro",
                "Módulo de desabilitação de tarefas não encontrado!\n\n"
                "Verifique se o arquivo 'core/tasks.py' existe.",
            )
            return

        # Criar janela de progresso
        progress_window, status_label, progress_bar, log_text = (
            self.parent.ui.show_progress_dialog("Desabilitando Tarefas Agendadas")
        )

        def run_scheduled_tasks_disable():
            """Executar desabilitação de tarefas em thread separada"""
            try:
                result = self._run_elevated_optimization(
                    "optimization_scheduled_tasks",
                    progress_window,
                    status_label,
                    progress_bar,
                    log_text,
                )
                if result is None:
                    return
                success, sucessos, erros = result

                # Mostrar resultado final
                def show_result():
                    progress_bar.stop()
                    self.results.show_tasks_result(
                        progress_window, status_label, success, sucessos, erros
                    )

                # Agendar para thread principal
                self.parent.logger.run_on_ui(
                    lambda: progress_window.after(500, show_result)
                )

            except Exception as e:
                self._handle_error(
                    progress_window,
                    progress_bar,
                    status_label,
                    e,
                    "desabilitação de tarefas",
                )

        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=run_scheduled_tasks_disable, daemon=True)
        thread.start()
