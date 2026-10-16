# core/tasks.py - Desabilitar tarefas agendadas do Windows

import subprocess
import os
import sys
from typing import List, Tuple


class DesabilitadorTweaks:
    """Classe responsável por desabilitar tarefas agendadas desnecessárias do Windows"""

    def __init__(self, logger=None):
        """Inicializar desabilitador de tweaks"""
        self.logger = logger
        self.sucessos = []
        self.erros = []

    def log(self, message: str):
        """Registrar mensagem no log"""
        if self.logger:
            self.logger.log(message)
        else:
            print(message)

    def verificar_privilegios_admin(self) -> bool:
        """Verificar se está executando como administrador"""
        try:
            return os.getuid() == 0
        except AttributeError:
            # Windows
            import ctypes

            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False

    def desabilitar_tarefa(self, task_name: str) -> bool:
        """Desabilitar uma tarefa agendada específica"""
        try:
            self.log(f"Desabilitando tarefa: {task_name}")

            # Executar comando schtasks
            result = subprocess.run(
                ["schtasks", "/Change", "/TN", task_name, "/Disable"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                self.log(f"✅ Tarefa desabilitada: {task_name}")
                self.sucessos.append(f"Tarefa desabilitada: {task_name}")
                return True
            else:
                error_msg = (
                    result.stderr.strip() if result.stderr else "Erro desconhecido"
                )
                if (
                    "não foi encontrada" in error_msg.lower()
                    or "cannot find" in error_msg.lower()
                ):
                    self.log(f"⚠️ Tarefa não encontrada (não alterada): {task_name}")
                    self.erros.append(f"Tarefa não encontrada: {task_name}")
                    return False
                else:
                    self.log(f"❌ Erro ao desabilitar {task_name}: {error_msg}")
                    self.erros.append(f"Erro em {task_name}: {error_msg}")
                    return False

        except subprocess.TimeoutExpired:
            error_msg = f"Timeout ao desabilitar tarefa: {task_name}"
            self.log(f"❌ {error_msg}")
            self.erros.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Erro crítico ao desabilitar {task_name}: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.erros.append(error_msg)
            return False

    def obter_tarefas_para_desabilitar(self) -> List[str]:
        """Obter lista de tarefas que devem ser desabilitadas"""
        return [
            # Tarefas de telemetria e coleta de dados
            "Microsoft\\Windows\\Application Experience\\ProgramDataUpdater",
            # Customer Experience Improvement Program
            "Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator",
            "Microsoft\\Windows\\Customer Experience Improvement Program\\KernelCeipTask",
            "Microsoft\\Windows\\Customer Experience Improvement Program\\UsbCeip",
            "Microsoft\\Windows\\Customer Experience Improvement Program\\Uploader",
            # Avaliação de desempenho não utilizada pela maioria dos usuários
            "Microsoft\\Windows\\Maintenance\\WinSAT",
            "Microsoft\\Windows\\Power Efficiency Diagnostics\\AnalyzeSystem",
        ]

    def executar_desabilitacao_tweaks(self) -> Tuple[bool, List[str], List[str]]:
        """Executar desabilitação de todas as tarefas agendadas desnecessárias"""

        # Limpar listas
        self.sucessos.clear()
        self.erros.clear()

        self.log("=" * 60)
        self.log("🔧 INICIANDO DESABILITAÇÃO DE TAREFAS AGENDADAS")
        self.log("=" * 60)

        # Verificar se é Windows
        if not sys.platform.startswith("win"):
            error_msg = "Este módulo funciona apenas no Windows"
            self.log(f"❌ {error_msg}")
            self.erros.append(error_msg)
            return False, self.sucessos, self.erros

        # Verificar privilégios de administrador
        if not self.verificar_privilegios_admin():
            error_msg = (
                "A operação exige privilégios administrativos; "
                "nenhuma tarefa foi alterada."
            )
            self.log(f"❌ {error_msg}")
            self.erros.append(error_msg)
            return False, self.sucessos, self.erros

        # Obter lista de tarefas
        tarefas = self.obter_tarefas_para_desabilitar()
        self.log(f"📋 Tarefas a serem desabilitadas: {len(tarefas)}")
        self.log("")

        # Desabilitar cada tarefa
        total_desabilitadas = 0
        for i, tarefa in enumerate(tarefas, 1):
            self.log(f"[{i:02d}/{len(tarefas):02d}] Processando: {tarefa}")

            if self.desabilitar_tarefa(tarefa):
                total_desabilitadas += 1

            self.log("")

        # Resumo final
        self.log("=" * 60)
        self.log("📊 RESUMO DA DESABILITAÇÃO")
        self.log("=" * 60)
        self.log(f"✅ Sucessos: {len(self.sucessos)}")
        self.log(f"❌ Erros: {len(self.erros)}")
        self.log(f"📋 Total processado: {len(tarefas)}")

        if len(self.erros) == 0 and self.sucessos:
            self.log("🎉 Todas as tarefas foram processadas com sucesso!")
            success = True
        elif self.sucessos and self.erros:
            self.log(
                "⚠️ Operação parcial: algumas tarefas não foram alteradas"
            )
            success = False
        else:
            self.log(
                "❌ Nenhuma tarefa foi desabilitada; verifique os erros e as permissões"
            )
            success = False

        self.log("")
        self.log("⚠️ IMPORTANTE:")
        self.log("• Reinicie o sistema para aplicar todas as mudanças")
        self.log("• Algumas tarefas podem não existir em todas as versões do Windows")
        self.log("• Execute como Administrador para obter melhores resultados")

        return success, self.sucessos, self.erros

    def listar_tarefas_ativas(self) -> List[str]:
        """Listar tarefas agendadas ativas no sistema"""
        try:
            self.log("📋 Listando tarefas ativas do sistema...")

            result = subprocess.run(
                ["schtasks", "/query", "/fo", "csv"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                # Primeira linha é cabeçalho
                tarefas = []
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split(",")
                        if len(parts) >= 2:
                            nome_tarefa = parts[0].strip('"')
                            status = parts[2].strip('"') if len(parts) > 2 else ""
                            if status == "Ready":  # Tarefa ativa
                                tarefas.append(nome_tarefa)

                self.log(f"✅ Encontradas {len(tarefas)} tarefas ativas")
                return tarefas
            else:
                self.log(f"❌ Erro ao listar tarefas: {result.stderr}")
                return []

        except Exception as e:
            self.log(f"❌ Erro ao listar tarefas: {str(e)}")
            return []

    def verificar_status_tarefa(self, task_name: str) -> str:
        """Verificar status atual de uma tarefa específica"""
        try:
            result = subprocess.run(
                ["schtasks", "/query", "/TN", task_name],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                if "Disabled" in result.stdout:
                    return "Desabilitada"
                elif "Ready" in result.stdout:
                    return "Ativa"
                else:
                    return "Status desconhecido"
            else:
                return "Não encontrada"

        except Exception:
            return "Erro ao verificar"


def main():
    """Função principal para teste"""
    print("🔧 Desabilitador de Tarefas Agendadas - Teste")
    print("=" * 50)

    # Criar desabilitador
    desabilitador = DesabilitadorTweaks()

    # Executar desabilitação
    success, sucessos, erros = desabilitador.executar_desabilitacao_tweaks()

    # Mostrar resultado
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    print(f"✅ Sucessos: {len(sucessos)}")
    print(f"❌ Erros: {len(erros)}")
    print(f"🎯 Status: {'Sucesso' if success else 'Com erros'}")


if __name__ == "__main__":
    main()
