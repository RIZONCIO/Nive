import winreg
import subprocess
import ctypes
import sys
from typing import List, Tuple, Optional


class AceleradorWindows:
    """Classe para aplicar otimizações de aceleração do Windows"""

    def __init__(self, logger=None):
        self.logger = logger
        self.errors = []
        self.successes = []

    def log(self, message: str):
        """Log das ações realizadas"""
        if self.logger:
            self.logger.log(message)
        else:
            print(message)

    def is_admin(self) -> bool:
        """Verifica se o script está rodando como administrador"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def add_registry_key(
        self,
        hive: int,
        key_path: str,
        value_name: str,
        value_type: int,
        value_data,
        description: str = "",
    ) -> bool:
        """Adiciona/modifica uma chave do registro"""
        try:
            with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                self.log(f"✓ {description}: {key_path}\\{value_name}")
                self.successes.append(description)
                return True
        except FileNotFoundError:
            # Tenta criar a chave se não existir
            try:
                with winreg.CreateKey(hive, key_path) as key:
                    winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                    self.log(
                        f"✓ {description} (chave criada): {key_path}\\{value_name}"
                    )
                    self.successes.append(description)
                    return True
            except Exception as e:
                self.log(f"✗ Erro ao criar {description}: {str(e)}")
                self.errors.append(f"{description}: {str(e)}")
                return False
        except Exception as e:
            self.log(f"✗ Erro em {description}: {str(e)}")
            self.errors.append(f"{description}: {str(e)}")
            return False

    def delete_registry_key(
        self, hive: int, key_path: str, description: str = ""
    ) -> bool:
        """Remove uma chave do registro"""
        try:
            winreg.DeleteKey(hive, key_path)
            self.log(f"✓ {description}: {key_path}")
            self.successes.append(description)
            return True
        except FileNotFoundError:
            self.log(f"? {description}: Chave não encontrada (já removida)")
            return True
        except Exception as e:
            self.log(f"✗ Erro ao remover {description}: {str(e)}")
            self.errors.append(f"{description}: {str(e)}")
            return False

    def execute_command(self, command: str, description: str = "") -> bool:
        """Executa um comando do sistema"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✓ {description}")
                self.successes.append(description)
                return True
            else:
                self.log(f"✗ Erro em {description}: {result.stderr}")
                self.errors.append(f"{description}: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"✗ Erro ao executar {description}: {str(e)}")
            self.errors.append(f"{description}: {str(e)}")
            return False

    def otimizar_boot(self) -> bool:
        """Otimização no Boot"""
        self.log("\n--- Otimizando Boot ---")
        success = True

        # Bootcfg timeout
        success &= self.execute_command(
            "bootcfg /timeout 10", "Configurar timeout do boot"
        )

        # Boot Optimization
        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Dfrg\BootOptimizeFunction",
            "Enable",
            winreg.REG_SZ,
            "Y",
            "Habilitar otimização de boot",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Dfrg\BootOptimizeFunction",
            "OptimizeComplete",
            winreg.REG_SZ,
            "Yes",
            "Marcar otimização como completa",
        )

        return success

    def acelerar_menu_iniciar(self) -> bool:
        """Menu Iniciar Mais Rápido"""
        self.log("\n--- Acelerando Menu Iniciar ---")
        success = True

        success &= self.add_registry_key(
            winreg.HKEY_CURRENT_USER,
            r"Control Panel\Desktop",
            "MenuShowDelay",
            winreg.REG_SZ,
            "100",
            "Acelerar menu (usuário atual)",
        )

        success &= self.add_registry_key(
            winreg.HKEY_USERS,
            r".DEFAULT\Control Panel\Desktop",
            "MenuShowDelay",
            winreg.REG_SZ,
            "100",
            "Acelerar menu (usuário padrão)",
        )

        return success

    def aumentar_taxa_upload(self) -> bool:
        """Aumentar a Taxa de Upload"""
        self.log("\n--- Aumentando Taxa de Upload ---")
        success = True

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Services\AFD\Parameters",
            "DefaultSendWindow",
            winreg.REG_DWORD,
            0x00018000,
            "Configurar janela de envio padrão",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
            "EnablePMTUDiscovery",
            winreg.REG_DWORD,
            0x00000001,
            "Habilitar descoberta de MTU",
        )

        return success

    def otimizar_limpeza_disco(self) -> bool:
        """Limpeza de Disco Mais Eficaz"""
        self.log("\n--- Otimizando Limpeza de Disco ---")

        return self.delete_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Compress old files",
            "Remover compressão de arquivos antigos",
        )

    def otimizar_tcp_ip(self) -> bool:
        """Otimização TCP/IP"""
        self.log("\n--- Otimizando TCP/IP ---")
        success = True

        # Lanmanserver parameters
        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Services\Lanmanserver\parameters",
            "SizReqBuf",
            winreg.REG_DWORD,
            0x00014596,
            "Otimizar buffer do servidor",
        )

        # TCP/IP Service Provider
        provider_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider"

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            provider_path,
            "class",
            winreg.REG_DWORD,
            0x00000001,
            "Configurar classe TCP/IP",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            provider_path,
            "DnsPriority",
            winreg.REG_DWORD,
            0x00000007,
            "Prioridade DNS",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            provider_path,
            "HostsPriority",
            winreg.REG_DWORD,
            0x00000006,
            "Prioridade Hosts",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            provider_path,
            "LocalPriority",
            winreg.REG_DWORD,
            0x00000005,
            "Prioridade Local",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            provider_path,
            "NetbtPriority",
            winreg.REG_DWORD,
            0x00000008,
            "Prioridade NetBT",
        )

        return success

    def otimizar_cache_dns(self) -> bool:
        """Otimização para o Cache de DNS"""
        self.log("\n--- Otimizando Cache de DNS ---")
        success = True

        dns_path = r"SYSTEM\CurrentControlSet\Services\Dnscache\Parameters"

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            dns_path,
            "CacheHashTableBucketSize",
            winreg.REG_DWORD,
            0x00000001,
            "Tamanho do bucket da tabela hash",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            dns_path,
            "CacheHashTableSize",
            winreg.REG_DWORD,
            0x00000180,
            "Tamanho da tabela hash do cache",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            dns_path,
            "MaxCacheEntryTtLimit",
            winreg.REG_DWORD,
            0x0000FA00,
            "Limite TTL máximo do cache",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            dns_path,
            "MaxSOACacheEntryTtLimit",
            winreg.REG_DWORD,
            0x0000012D,
            "Limite TTL SOA do cache",
        )

        return success

    def limpar_cache_ie(self) -> bool:
        """Limpar Arquivos Temporários do Internet Explorer"""
        self.log("\n--- Limpando Cache do IE ---")

        return self.add_registry_key(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\Cache",
            "Persistent",
            winreg.REG_DWORD,
            0x00000000,
            "Desabilitar cache persistente do IE",
        )

    def habilitar_gpu_scheduling(self) -> bool:
        """Habilitar agendamento de aceleração de GPU"""
        self.log("\n--- Habilitando GPU Scheduling ---")

        return self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
            "HwSchMode",
            winreg.REG_DWORD,
            2,
            "Habilitar agendamento de hardware da GPU",
        )

    def habilitar_modo_compacto(self) -> bool:
        """Habilitar modo compacto no Explorador de Arquivos"""
        self.log("\n--- Habilitando Modo Compacto ---")

        return self.add_registry_key(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "UseCompactMode",
            winreg.REG_DWORD,
            1,
            "Habilitar modo compacto no explorador",
        )

    def desabilitar_apps_background(self) -> bool:
        """Desabilitar Aplicativos em Segundo Plano"""
        self.log("\n--- Desabilitando Apps em Background ---")
        success = True

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Policies\Microsoft\Windows\AppPrivacy",
            "LetAppsRunInBackground",
            winreg.REG_DWORD,
            2,
            "Desabilitar apps em segundo plano",
        )

        # Remover chaves específicas (se existirem)
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\AppPrivacy",
                0,
                winreg.KEY_SET_VALUE,
            ) as key:
                try:
                    winreg.DeleteValue(
                        key, "LetAppsRunInBackground_UserInControlOfTheseApps"
                    )
                    self.log("✓ Removida chave UserInControlOfTheseApps")
                except FileNotFoundError:
                    pass

                try:
                    winreg.DeleteValue(
                        key, "LetAppsRunInBackground_ForceAllowTheseApps"
                    )
                    self.log("✓ Removida chave ForceAllowTheseApps")
                except FileNotFoundError:
                    pass

                try:
                    winreg.DeleteValue(key, "LetAppsRunInBackground_ForceDenyTheseApps")
                    self.log("✓ Removida chave ForceDenyTheseApps")
                except FileNotFoundError:
                    pass
        except Exception as e:
            self.log(f"⚠ Aviso ao limpar chaves de background: {str(e)}")

        return success

    def melhorar_qualidade_wallpaper(self) -> bool:
        """Melhorar qualidade papel de parede"""
        self.log("\n--- Melhorando Qualidade do Wallpaper ---")

        return self.add_registry_key(
            winreg.HKEY_CURRENT_USER,
            r"Control Panel\Desktop",
            "JPEGImportQuality",
            winreg.REG_DWORD,
            0x00000064,
            "Melhorar qualidade de importação JPEG",
        )

    def otimizar_agendador_jogos(self) -> bool:
        """Otimizar Agendador para Jogos"""
        self.log("\n--- Otimizando Agendador para Jogos ---")
        success = True

        games_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            games_path,
            "GPU Priority",
            winreg.REG_DWORD,
            8,
            "Prioridade de GPU para jogos",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            games_path,
            "Priority",
            winreg.REG_DWORD,
            6,
            "Prioridade geral para jogos",
        )

        success &= self.add_registry_key(
            winreg.HKEY_LOCAL_MACHINE,
            games_path,
            "Scheduling Category",
            winreg.REG_SZ,
            "High",
            "Categoria de agendamento para jogos",
        )

        return success

    def executar_todas_otimizacoes(self) -> Tuple[bool, List[str], List[str]]:
        """Executa todas as otimizações de aceleração"""

        self.successes.clear()
        self.errors.clear()
        if not self.is_admin():
            error = (
                "Ajustes de computador e usuário exigem elevação. "
                "Nenhuma alteração foi iniciada; execute o aplicativo como "
                "administrador usando a conta do usuário atual."
            )
            self.errors.append(error)
            self.log(f"❌ {error}")
            return False, self.successes, self.errors

        self.log("=== INICIANDO OTIMIZAÇÕES DE ACELERAÇÃO DO WINDOWS ===")

        # Lista de otimizações
        otimizacoes = [
            ("Otimização de Boot", self.otimizar_boot),
            ("Aceleração do Menu Iniciar", self.acelerar_menu_iniciar),
            ("Aumento da Taxa de Upload", self.aumentar_taxa_upload),
            ("Otimização da Limpeza de Disco", self.otimizar_limpeza_disco),
            ("Otimização TCP/IP", self.otimizar_tcp_ip),
            ("Otimização do Cache DNS", self.otimizar_cache_dns),
            ("Limpeza do Cache IE", self.limpar_cache_ie),
            ("GPU Scheduling", self.habilitar_gpu_scheduling),
            ("Modo Compacto", self.habilitar_modo_compacto),
            ("Desabilitar Apps Background", self.desabilitar_apps_background),
            ("Qualidade Wallpaper", self.melhorar_qualidade_wallpaper),
            ("Otimização para Jogos", self.otimizar_agendador_jogos),
        ]

        # Executar todas as otimizações
        overall_success = True
        for nome, funcao in otimizacoes:
            try:
                success = funcao()
                if not success:
                    overall_success = False
                    self.log(f"⚠ {nome}: Concluído com alguns erros")
            except Exception as e:
                overall_success = False
                error_msg = f"Erro crítico em {nome}: {str(e)}"
                self.log(f"✗ {error_msg}")
                self.errors.append(error_msg)

        self.log(f"\n=== RESULTADO FINAL ===")
        self.log(f"✓ Sucessos: {len(self.successes)}")
        self.log(f"✗ Erros: {len(self.errors)}")

        if overall_success and len(self.errors) == 0:
            self.log("🎉 TODAS AS OTIMIZAÇÕES FORAM APLICADAS COM SUCESSO!")
        elif len(self.successes) > len(self.errors):
            self.log("⚠ OTIMIZAÇÕES CONCLUÍDAS COM ALGUNS AVISOS")
        else:
            self.log("⚠ OTIMIZAÇÕES CONCLUÍDAS COM VÁRIOS ERROS")

        self.log("\n⚠ IMPORTANTE: Reinicie o sistema para aplicar todas as mudanças!")

        return overall_success, self.successes, self.errors


def main():
    """Função principal para teste independente"""
    acelerador = AceleradorWindows()
    success, sucessos, erros = acelerador.executar_todas_otimizacoes()

    if erros:
        print(f"\nErros encontrados:")
        for erro in erros:
            print(f"  - {erro}")

    return success


if __name__ == "__main__":
    main()
