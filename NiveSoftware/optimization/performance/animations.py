# core/animations.py - Remoção de animações desnecessárias do Windows

import winreg
import os


class RemoverAnimacoes:
    """Classe para remover animações desnecessárias do Windows"""

    def __init__(self, logger=None):
        """Inicializar removedor de animações"""
        self.logger = logger

        # Configurações de registro para desabilitar animações
        self.configuracoes_animacoes = [
            {
                "hive": winreg.HKEY_CURRENT_USER,
                "path": r"Control Panel\Desktop",
                "name": "UserPreferencesMask",
                "type": winreg.REG_BINARY,
                "value": bytes.fromhex("9032078010000000"),
                "description": "Desabilita efeitos visuais avançados",
            },
            {
                "hive": winreg.HKEY_CURRENT_USER,
                "path": r"Control Panel\Desktop\WindowMetrics",
                "name": "MinAnimate",
                "type": winreg.REG_SZ,
                "value": "0",
                "description": "Desabilita animações de minimizar/maximizar janelas",
            },
            {
                "hive": winreg.HKEY_CURRENT_USER,
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "TaskbarAnimations",
                "type": winreg.REG_DWORD,
                "value": 0,
                "description": "Desabilita animações da barra de tarefas",
            },
            {
                "hive": winreg.HKEY_CURRENT_USER,
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "IconsOnly",
                "type": winreg.REG_DWORD,
                "value": 1,
                "description": "Mostrar apenas ícones (sem thumbnails)",
            },
            {
                "hive": winreg.HKEY_CURRENT_USER,
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "ListviewAlphaSelect",
                "type": winreg.REG_DWORD,
                "value": 1,
                "description": "Desabilita transparência na seleção de arquivos",
            },
            {
                "hive": winreg.HKEY_CURRENT_USER,
                "path": r"Control Panel\Desktop",
                "name": "DragFullWindows",
                "type": winreg.REG_DWORD,
                "value": 0,
                "description": "Desabilita arrastar janelas com conteúdo completo",
            },
            {
                "hive": winreg.HKEY_CURRENT_USER,
                "path": r"Control Panel\Desktop",
                "name": "FontSmoothing",
                "type": winreg.REG_SZ,
                "value": "2",
                "description": "Configura suavização de fontes otimizada",
            },
            {
                "hive": winreg.HKEY_CURRENT_USER,
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "ListviewShadow",
                "type": winreg.REG_DWORD,
                "value": 1,
                "description": "Desabilita sombras em visualizações de lista",
            },
            {
                "hive": winreg.HKEY_CURRENT_USER,
                "path": r"Software\Microsoft\Windows\DWM",
                "name": "AlwaysHibernateThumbnails",
                "type": winreg.REG_DWORD,
                "value": 0,
                "description": "Desabilita hibernação de thumbnails",
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

        except Exception as e:
            self.log(f"❌ Erro ao aplicar {config['description']}: {str(e)}")
            return False

    def executar_remocao_animacoes(self):
        """Executar remoção de todas as animações"""
        self.log("=== INICIANDO REMOÇÃO DE ANIMAÇÕES DESNECESSÁRIAS ===")

        sucessos = []
        erros = []

        self.log("\n--- Desabilitando Animações e Efeitos Visuais ---")

        for config in self.configuracoes_animacoes:
            try:
                if self.aplicar_configuracao_registro(config):
                    sucessos.append(f"Configuração aplicada: {config['description']}")
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
            self.log("\n🎉 ANIMAÇÕES DESABILITADAS COM SUCESSO!")
            self.log(
                "⚠️ IMPORTANTE: Reinicie o sistema ou faça logoff/login para aplicar todas as mudanças!"
            )
            self.log("\n📋 MELHORIAS APLICADAS:")
            self.log("• Animações de janelas desabilitadas")
            self.log("• Efeitos visuais reduzidos")
            self.log("• Animações da barra de tarefas removidas")
            self.log("• Transparências e sombras otimizadas")
            self.log("• Sistema mais responsivo")
        else:
            self.log("\n⚠️ REMOÇÃO CONCLUÍDA COM ERROS")
            self.log("Verifique as permissões de gravação do usuário atual")

        return sucesso_geral, sucessos, erros


# Função principal para teste
def main():
    """Função principal para testar o removedor"""
    print("=== TESTE DO REMOVEDOR DE ANIMAÇÕES ===")

    class SimpleLogger:
        def log(self, message):
            print(message)

    removedor = RemoverAnimacoes(logger=SimpleLogger())
    sucesso, sucessos, erros = removedor.executar_remocao_animacoes()

    print(f"\nResultado: {'Sucesso' if sucesso else 'Falhou'}")
    print(f"Sucessos: {len(sucessos)}, Erros: {len(erros)}")


if __name__ == "__main__":
    main()
