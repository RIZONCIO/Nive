import os
import sys
import json
import subprocess
import winreg
import time
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class SoftwareManager:
    def __init__(self, packages_json_path: str = None):
        """
        Inicializa o gerenciador de software

        Args:
            packages_json_path: Caminho para o arquivo pacotes.json
        """
        if packages_json_path:
            self.packages_json_path = Path(packages_json_path)
        else:
            candidates = [
                Path(__file__).resolve().parent / "pacotes.json",
                Path(__file__).resolve().parents[1] / "config" / "pacotes.json",
                Path(__file__).resolve().parents[2] / "shared" / "config" / "pacotes.json",
                Path(__file__).resolve().parents[3] / "data" / "pacotes.json",
                Path(__file__).resolve().parents[3] / "NiveCLI" / "config" / "pacotes.json",
                Path("C:/Nive/pacotes.json"),
            ]
            self.packages_json_path = next((c for c in candidates if c.exists()), candidates[1])
        self.script_dir = self.packages_json_path.parent
        self.packages_map = {}
        self.load_packages_json()

    def load_packages_json(self) -> bool:
        """Carrega o mapeamento de pacotes do arquivo JSON"""
        try:
            if self.packages_json_path.exists():
                with open(self.packages_json_path, "r", encoding="utf-8") as f:
                    self.packages_map = json.load(f)
                return True
            else:
                print(f"[AVISO] Arquivo {self.packages_json_path} não encontrado.")
                return False
        except Exception as e:
            print(f"[ERRO] Não foi possível carregar o 'pacotes.json': {e}")
            return False

    def check_admin_privileges(self) -> bool:
        """Verifica se o script está rodando com privilégios de administrador"""
        try:
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        """Executa o script com privilégios de administrador"""
        if not self.check_admin_privileges():
            try:
                import ctypes

                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                return True
            except:
                print("[ERRO] Não foi possível obter privilégios de administrador.")
                return False
        return True

    def check_chocolatey_installed(self) -> bool:
        """Verifica se o Chocolatey está instalado"""
        try:
            result = subprocess.run(
                ["choco", "--version"], capture_output=True, text=True, shell=True
            )
            return result.returncode == 0
        except:
            return False

    def install_chocolatey(self) -> bool:
        """Instala o Chocolatey"""
        try:
            print("\nChocolatey não encontrado. Instalando...")

            # Comando PowerShell para instalar Chocolatey
            cmd = [
                "powershell.exe",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "Set-ExecutionPolicy Bypass -Scope Process -Force; "
                + "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
                + "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

            if result.returncode == 0 and self.check_chocolatey_installed():
                print("Chocolatey instalado com sucesso.")
                return True
            else:
                print(f"[ERRO] Falha na instalação do Chocolatey: {result.stderr}")
                return False

        except Exception as e:
            print(f"[ERRO] Falha na instalação do Chocolatey: {e}")
            return False

    def get_installed_software(self) -> List[Dict[str, str]]:
        """Obtém lista de software instalado do registro do Windows"""
        software_list = []

        try:
            # Registro para programas 64-bit
            reg_paths = [
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            ]

            with winreg.OpenKey(reg_paths[0], reg_paths[1]) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                display_name = winreg.QueryValueEx(
                                    subkey, "DisplayName"
                                )[0]
                                uninstall_string = winreg.QueryValueEx(
                                    subkey, "UninstallString"
                                )[0]

                                software_list.append(
                                    {
                                        "display_name": display_name,
                                        "uninstall_string": uninstall_string,
                                        "registry_key": subkey_name,
                                    }
                                )
                            except FileNotFoundError:
                                # Algumas entradas podem não ter DisplayName ou UninstallString
                                pass
                        i += 1
                    except OSError:
                        break

        except Exception as e:
            print(f"[ERRO] Erro ao acessar registro: {e}")

        return software_list

    def search_chocolatey_package(self, display_name: str) -> Optional[str]:
        """Busca um pacote no Chocolatey baseado no nome de exibição"""
        try:
            # Remove caracteres especiais e pega a primeira palavra
            clean_name = re.sub(r"[^a-zA-Z0-9\s]", "", display_name)
            clean_name = re.sub(r"\s+", " ", clean_name).strip()

            if not clean_name:
                return None

            keyword = clean_name.split()[0].lower()

            print(f"\n[INFO] Tentando identificar '{keyword}' no Chocolatey...")

            result = subprocess.run(
                ["choco", "search", keyword, "--exact"],
                capture_output=True,
                text=True,
                shell=True,
            )

            if result.returncode == 0:
                # Procura por linha que contenha o nome do pacote e versão
                for line in result.stdout.split("\n"):
                    if re.search(rf"{re.escape(keyword)}\s+[0-9]", line, re.IGNORECASE):
                        return keyword

            return None

        except Exception as e:
            print(f"[ERRO] Erro ao buscar no Chocolatey: {e}")
            return None

    def uninstall_software(self, uninstall_string: str) -> bool:
        """Desinstala software usando a string de desinstalação"""
        try:
            # Executa comando de desinstalação
            result = subprocess.run(
                f"cmd.exe /c {uninstall_string}",
                shell=True,
                capture_output=True,
                text=True,
            )

            return result.returncode == 0

        except Exception as e:
            print(f"[ERRO] Falha ao desinstalar: {e}")
            return False

    def check_software_exists(self, display_name: str) -> bool:
        """Verifica se o software ainda existe no registro"""
        software_list = self.get_installed_software()
        for software in software_list:
            if display_name.lower() in software["display_name"].lower():
                return True
        return False

    def clean_chocolatey_cache(self, package_name: str):
        """Limpa cache do Chocolatey para um pacote específico"""
        try:
            chocolatey_lib_path = Path("C:/ProgramData/chocolatey/lib")
            if not chocolatey_lib_path.exists():
                return

            # Remove parte da versão do nome do pacote se existir
            base_name = package_name.split(".")[0].lower()

            # Procura por pastas relacionadas
            for folder in chocolatey_lib_path.iterdir():
                if folder.is_dir() and base_name in folder.name.lower():
                    print(f"\n[INFO] Limpando cache: {folder}")
                    try:
                        import shutil

                        shutil.rmtree(folder)
                    except Exception as e:
                        print(f"[ERRO] Não foi possível remover: {folder} - {e}")

        except Exception as e:
            print(f"[ERRO] Erro ao limpar cache: {e}")

    def reinstall_with_chocolatey(self, package_name: str) -> bool:
        """Reinstala software usando Chocolatey"""
        try:
            print(f"\n[SUCESSO] Reinstalando '{package_name}' via Chocolatey...")

            result = subprocess.run(
                ["choco", "install", package_name, "-y", "--force"],
                capture_output=True,
                text=True,
                shell=True,
            )

            if result.returncode == 0:
                print(f"[SUCESSO] {package_name} reinstalado com sucesso!")
                return True
            else:
                print(f"[ERRO] Falha ao reinstalar {package_name}: {result.stderr}")
                return False

        except Exception as e:
            print(f"[ERRO] Erro ao reinstalar com Chocolatey: {e}")
            return False

    def find_chocolatey_package(self, display_name: str) -> Optional[str]:
        """Encontra nome do pacote Chocolatey para um software"""
        # Primeiro, tenta encontrar no JSON
        for key in self.packages_map:
            if key.lower() in display_name.lower():
                return self.packages_map[key]

        # Se não encontrar no JSON, tenta buscar automaticamente
        return self.search_chocolatey_package(display_name)

    def process_software_reinstall(
        self, software_info: Dict[str, str]
    ) -> Tuple[bool, str]:
        """
        Processa desinstalação e reinstalação de um software

        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        display_name = software_info["display_name"]
        uninstall_string = software_info["uninstall_string"]

        print(f"\nDesinstalando: {display_name}")

        # Desinstala o software
        if not self.uninstall_software(uninstall_string):
            return False, f"Falha ao desinstalar {display_name}"

        # Aguarda um pouco para o sistema processar
        time.sleep(5)

        # Verifica se o programa foi realmente desinstalado
        if self.check_software_exists(display_name):
            return (
                False,
                f"O programa {display_name} ainda está instalado. Reinstalação abortada.",
            )

        # Tenta encontrar o pacote Chocolatey correspondente
        package_name = self.find_chocolatey_package(display_name)

        if not package_name:
            return (
                False,
                f"Nome '{display_name}' não encontrado no JSON e não identificado automaticamente no Chocolatey.",
            )

        # Limpa cache do Chocolatey
        self.clean_chocolatey_cache(package_name)

        # Reinstala usando Chocolatey
        if self.reinstall_with_chocolatey(package_name):
            return True, f"Software {display_name} reinstalado com sucesso!"
        else:
            return False, f"Falha ao reinstalar {display_name} via Chocolatey"

    def run_interactive_mode(self):
        """Executa modo interativo para seleção e reinstalação de software"""
        if not self.check_admin_privileges():
            print("[ERRO] Este script precisa ser executado como administrador.")
            return

        if not self.check_chocolatey_installed():
            if not self.install_chocolatey():
                print("[ERRO] Chocolatey é necessário para continuar.")
                return

        while True:
            # Limpa tela (Windows)
            os.system("cls" if os.name == "nt" else "clear")

            print("Listando softwares instalados...")
            software_list = self.get_installed_software()

            if not software_list:
                print("Nenhum software encontrado.")
                break

            # Exibe lista numerada
            for i, software in enumerate(software_list):
                print(f"{i} - {software['display_name']}")

            try:
                choice = input(
                    "\nDigite o número do software que deseja desinstalar: "
                ).strip()

                if not choice.isdigit():
                    print("[ERRO] Número inválido!")
                    continue

                index = int(choice)

                if index < 0 or index >= len(software_list):
                    print("[ERRO] Número inválido!")
                    continue

                selected_software = software_list[index]

                # Processa reinstalação
                success, message = self.process_software_reinstall(selected_software)
                print(f"\n{message}")

            except KeyboardInterrupt:
                print("\nOperação cancelada pelo usuário.")
                break
            except Exception as e:
                print(f"[ERRO] Erro inesperado: {e}")

            # Menu de continuação
            print("\n[1] Voltar para a lista")
            print("[S] Sair")
            response = input("Escolha (1/S): ").strip().upper()

            if response == "S":
                break


if __name__ == "__main__":
    manager = SoftwareManager()
    manager.run_interactive_mode()
