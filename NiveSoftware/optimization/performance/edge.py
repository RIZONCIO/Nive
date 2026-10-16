# core/edge.py - Otimizações para o Microsoft Edge

import winreg
import os


class OtimizadorEdge:
    """Classe para aplicar otimizações específicas do Microsoft Edge"""

    def __init__(self, logger=None):
        """Inicializar otimizador do Edge"""
        self.logger = logger

        # Configurações de registro para otimizar o Edge
        self.configuracoes_edge = [
            {
                "hive": winreg.HKEY_LOCAL_MACHINE,
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "HubsSidebarEnabled",
                "type": winreg.REG_DWORD,
                "value": 0,
                "description": "Desabilitar sidebar do Edge (botão Bing)",
            },
            {
                "hive": winreg.HKEY_LOCAL_MACHINE,
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "BackgroundModeEnabled",
                "type": winreg.REG_DWORD,
                "value": 0,
                "description": "Desabilitar Edge executando em segundo plano",
            },
            {
                "hive": winreg.HKEY_LOCAL_MACHINE,
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "StartupBoostEnabled",
                "type": winreg.REG_DWORD,
                "value": 0,
                "description": "Desabilitar Edge iniciar automaticamente com Windows",
            },
            {
                "hive": winreg.HKEY_LOCAL_MACHINE,
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "EfficiencyMode",
                "type": winreg.REG_DWORD,
                "value": 0,
                "description": "Desabilitar modo de eficiência automático",
            },
            {
                "hive": winreg.HKEY_LOCAL_MACHINE,
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "ShowAcrobatSubscriptionButton",
                "type": winreg.REG_DWORD,
                "value": 0,
                "description": "Remover botão de assinatura do Acrobat",
            },
            {
                "hive": winreg.HKEY_LOCAL_MACHINE,
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "DefaultGeolocationSetting",
                "type": winreg.REG_DWORD,
                "value": 2,
                "description": "Desabilitar geolocalização por padrão",
            },
            {
                "hive": winreg.HKEY_LOCAL_MACHINE,
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "DefaultSensorsSetting",
                "type": winreg.REG_DWORD,
                "value": 2,
                "description": "Desabilitar acesso a sensores por padrão",
            },
            {
                "hive": winreg.HKEY_LOCAL_MACHINE,
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "DefaultNotificationsSetting",
                "type": winreg.REG_DWORD,
                "value": 2,
                "description": "Desabilitar notificações de sites por padrão",
            },
        ]

    def log(self, message):
        """Registrar mensagem no log"""
        if self.logger:
            self.logger.log(message)
        else:
            print(message)

    def verificar_permissoes_admin(self):
        """Verificar se está executando como administrador"""
        try:
            return os.getuid() == 0
        except AttributeError:
            # Windows
            try:
                return os.access(
                    os.path.join(
                        os.environ.get("SystemRoot", "C:\\Windows"), "system32"
                    ),
                    os.W_OK,
                )
            except:
                return False

    def criar_chave_se_necessario(self, hive, path):
        """Criar chave de registro se não existir"""
        try:
            # Tentar abrir a chave primeiro
            key = winreg.OpenKey(hive, path, 0, winreg.KEY_WRITE)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            # Chave não existe, tentar criar
            try:
                key = winreg.CreateKey(hive, path)
                winreg.CloseKey(key)
                return True
            except Exception as e:
                self.log(f"❌ Erro ao criar chave {path}: {str(e)}")
                return False
        except Exception as e:
            self.log(f"❌ Erro ao acessar chave {path}: {str(e)}")
            return False

    def aplicar_configuracao_registro(self, config):
        """Aplicar uma configuração específica no registro"""
        try:
            hive = config["hive"]
            path = config["path"]
            name = config["name"]
            reg_type = config["type"]
            value = config["value"]
            description = config["description"]

            self.log(f"Aplicando: {description}")

            # Criar chave se necessário
            if not self.criar_chave_se_necessario(hive, path):
                return False

            # Abrir chave para escrita
            with winreg.OpenKey(hive, path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, name, 0, reg_type, value)

            self.log(f"✅ {description} - aplicada com sucesso")
            return True

        except PermissionError:
            self.log(f"❌ Sem permissão para modificar: {config['description']}")
            self.log("   Execute como Administrador para aplicar esta configuração")
            return False
        except Exception as e:
            self.log(f"❌ Erro ao aplicar {config['description']}: {str(e)}")
            return False

    def verificar_edge_instalado(self):
        """Verificar se o Microsoft Edge está instalado"""
        try:
            # Verificar se existe a chave do Edge no registro
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Edge",
                0,
                winreg.KEY_READ,
            ):
                return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def executar_otimizacao_edge(self):
        """Executar otimização completa do Microsoft Edge"""
        self.log("=== INICIANDO OTIMIZAÇÃO DO MICROSOFT EDGE ===")

        # Verificar se Edge está instalado
        if not self.verificar_edge_instalado():
            self.log("⚠️ AVISO: Microsoft Edge não foi detectado no sistema")
            self.log("As configurações serão aplicadas mesmo assim para uso futuro")

        if not self.verificar_permissoes_admin():
            error = "A operação exige privilégios administrativos; nenhuma política foi alterada."
            self.log(f"❌ {error}")
            return False, [], [error]

        sucessos = []
        erros = []

        self.log("\n--- Aplicando Otimizações do Microsoft Edge ---")

        for config in self.configuracoes_edge:
            try:
                if self.aplicar_configuracao_registro(config):
                    sucessos.append(f"Otimização aplicada: {config['description']}")
                else:
                    erros.append(f"Falha em: {config['description']}")
            except Exception as e:
                erros.append(f"Erro crítico em {config['description']}: {str(e)}")

        # Relatório final
        self.log("\n=== RELATÓRIO FINAL ===")
        self.log(f"✅ Sucessos: {len(sucessos)}")
        self.log(f"❌ Erros: {len(erros)}")

        if len(erros) > 0:
            self.log("\n--- Detalhes dos Erros ---")
            for erro in erros:
                self.log(f"• {erro}")

        sucesso_geral = bool(sucessos) and not erros

        if sucesso_geral:
            self.log("\n🎉 MICROSOFT EDGE OTIMIZADO COM SUCESSO!")
            self.log("⚠️ IMPORTANTE: Reinicie o Edge para aplicar todas as mudanças!")
            self.log("\n📋 OTIMIZAÇÕES APLICADAS:")
            self.log("• Sidebar/botão Bing desabilitado")
            self.log("• Execução em segundo plano desabilitada")
            self.log("• Inicialização automática desabilitada")
            self.log("• Botão Acrobat removido")
            self.log("• Permissões de privacidade otimizadas")
            self.log("• Geolocalização desabilitada por padrão")
            self.log("• Notificações de sites desabilitadas")
        else:
            self.log("\n⚠️ OTIMIZAÇÃO CONCLUÍDA COM ERROS")
            self.log("Execute como Administrador e verifique se o Edge está instalado")

        return sucesso_geral, sucessos, erros


# Função principal para teste
def main():
    """Função principal para testar o otimizador"""
    print("=== TESTE DO OTIMIZADOR DO EDGE ===")

    class SimpleLogger:
        def log(self, message):
            print(message)

    otimizador = OtimizadorEdge(logger=SimpleLogger())
    sucesso, sucessos, erros = otimizador.executar_otimizacao_edge()

    print(f"\nResultado: {'Sucesso' if sucesso else 'Falhou'}")
    print(f"Sucessos: {len(sucessos)}, Erros: {len(erros)}")


if __name__ == "__main__":
    main()
