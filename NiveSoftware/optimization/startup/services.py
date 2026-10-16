import subprocess
import sys
import os
from typing import Tuple, List, Dict


class DesabilitadorServicos:
    """Classe responsável por desabilitar serviços desnecessários do Windows"""

    def __init__(self, logger=None):
        """Inicializar o desabilitador de serviços"""
        self.logger = logger
        self.sucessos = []
        self.erros = []

        # Lista de serviços para parar e desabilitar
        self.servicos_para_desabilitar = [
            ("DiagTrack", "disabled", "Serviço de Telemetria Conectado"),
            (
                "diagnosticshub.standardcollector.service",
                "disabled",
                "Microsoft (R) Diagnostics Hub Standard Collector",
            ),
            (
                "dmwappushservice",
                "disabled",
                "Serviço de Roteamento de Mensagem Push WAP dmwappushservice",
            ),
            ("RemoteRegistry", "disabled", "Registro Remoto"),
            (
                "WMPNetworkSvc",
                "disabled",
                "Serviço de Compartilhamento de Rede do Windows Media Player",
            ),
            ("RetailDemo", "disabled", "Retail Demo Service"),
            ("HomeGroupListener", "disabled", "Ouvinte do Grupo Doméstico"),
            ("HomeGroupProvider", "disabled", "Provedor do Grupo Doméstico"),
        ]

    def log(self, message):
        """Método para log de mensagens"""
        if self.logger:
            self.logger.log(message)
        else:
            print(message)

    def _executar_comando_sc(
        self, comando: str, servico: str, parametro: str = ""
    ) -> bool:
        """Executar comando sc (Service Control) de forma segura"""
        try:
            if parametro:
                cmd = ["sc", comando, servico, parametro]
            else:
                cmd = ["sc", comando, servico]

            # Executar comando com timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            self.log(f"⏰ Timeout ao executar comando para serviço: {servico}")
            return False
        except FileNotFoundError:
            self.log("❌ Comando 'sc' não encontrado. Execute como Administrador.")
            return False
        except Exception as e:
            self.log(f"❌ Erro inesperado ao executar comando para {servico}: {str(e)}")
            return False

    def _parar_servico(self, servico: str, descricao: str) -> bool:
        """Parar um serviço específico"""
        self.log(f"🛑 Parando serviço: {servico} ({descricao})")

        if self._executar_comando_sc("stop", servico):
            self.log(f"✅ Serviço {servico} parado com sucesso")
            return True
        else:
            # Não consideramos erro se o serviço já estava parado
            self.log(f"⚠️ Serviço {servico} já estava parado ou não pôde ser parado")
            return True

    def _desabilitar_servico(
        self, servico: str, tipo_inicio: str, descricao: str
    ) -> bool:
        """Desabilitar um serviço específico"""
        self.log(f"🔧 Configurando serviço: {servico} para {tipo_inicio}")

        parametro = f"start= {tipo_inicio}"

        if self._executar_comando_sc("config", servico, parametro):
            self.log(f"✅ Serviço {servico} configurado para {tipo_inicio}")
            return True
        else:
            self.log(f"❌ Erro ao configurar serviço {servico}")
            return False

    def verificar_privilegios_admin(self) -> bool:
        """Verificar se o script está sendo executado como administrador"""
        try:
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def executar_desabilitacao_servicos(self) -> Tuple[bool, List[str], List[str]]:
        """Executar todo o processo de desabilitação de serviços"""
        self.sucessos.clear()
        self.erros.clear()
        self.log("🚀 Iniciando desabilitação de serviços desnecessários...")
        self.log("=" * 60)

        # Verificar privilégios de administrador
        if not self.verificar_privilegios_admin():
            error = "A operação exige privilégios administrativos; nenhum serviço foi alterado."
            self.log(f"❌ {error}")
            self.erros.append(error)
            return False, self.sucessos, self.erros

        total_servicos = len(self.servicos_para_desabilitar)
        self.log(f"📊 Total de serviços para processar: {total_servicos}")
        self.log("")

        # Primeira fase: Parar todos os serviços
        self.log("🛑 FASE 1: Parando serviços...")
        self.log("-" * 40)

        for i, (servico, tipo_inicio, descricao) in enumerate(
            self.servicos_para_desabilitar, 1
        ):
            self.log(f"[{i}/{total_servicos}] Processando: {servico}")

            # Parar o serviço
            if self._parar_servico(servico, descricao):
                # Não adicionamos aos sucessos ainda, apenas paramos
                pass

            self.log("")

        # Segunda fase: Desabilitar todos os serviços
        self.log("🔧 FASE 2: Desabilitando serviços...")
        self.log("-" * 40)

        for i, (servico, tipo_inicio, descricao) in enumerate(
            self.servicos_para_desabilitar, 1
        ):
            self.log(f"[{i}/{total_servicos}] Configurando: {servico}")

            # Desabilitar/configurar o serviço
            if self._desabilitar_servico(servico, tipo_inicio, descricao):
                self.sucessos.append(f"{servico} - {descricao}")
            else:
                self.erros.append(f"{servico} - {descricao}")

            self.log("")

        # Resultado final
        self.log("=" * 60)
        self.log("📊 RESULTADO FINAL:")
        self.log(f"✅ Sucessos: {len(self.sucessos)}")
        self.log(f"❌ Erros: {len(self.erros)}")

        if self.erros:
            self.log("")
            self.log("❌ Serviços com erro:")
            for erro in self.erros[:5]:  # Mostrar apenas os primeiros 5
                self.log(f"  • {erro}")
            if len(self.erros) > 5:
                self.log(f"  • ... e mais {len(self.erros) - 5} serviços")

        success = bool(self.sucessos) and not self.erros

        self.log("")
        if success:
            self.log("🎉 Desabilitação de serviços concluída com sucesso!")
        else:
            self.log("⚠️ Desabilitação concluída com alguns erros.")

        self.log("💡 Dica: Reinicie o computador para aplicar todas as alterações.")

        return success, self.sucessos, self.erros


def main():
    """Função principal para teste do módulo"""
    print("Testando módulo de desabilitação de serviços...")

    class SimpleLogger:
        def log(self, message):
            print(message)

    logger = SimpleLogger()
    desabilitador = DesabilitadorServicos(logger)

    success, sucessos, erros = desabilitador.executar_desabilitacao_servicos()

    print(f"\nResultado: {'Sucesso' if success else 'Erro'}")
    print(f"Sucessos: {len(sucessos)}")
    print(f"Erros: {len(erros)}")


if __name__ == "__main__":
    main()
