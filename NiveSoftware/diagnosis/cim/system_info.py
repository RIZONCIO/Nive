import subprocess
import platform
import psutil
from datetime import datetime


class SystemInfo:
    def __init__(self):
        self.system_data = {}

    def run_wmic(self, wmic_class, properties):
        try:
            result = subprocess.run(
                ["wmic", wmic_class, "get", ",".join(properties), "/format:list"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
            if result.returncode == 0:
                return self.parse_wmic_output(result.stdout)
            return {}
        except Exception as e:
            return {"Erro": f"Falha no WMIC: {str(e)}"}

    def parse_wmic_output(self, output):
        data = {}
        for line in output.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()
        return data

    def run_wmic_multi(self, wmic_class, properties):
        try:
            result = subprocess.run(
                ["wmic", wmic_class, "get", ",".join(properties), "/format:csv"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            if result.returncode != 0:
                return []

            lines = result.stdout.strip().splitlines()
            if len(lines) < 2:
                return []

            headers = [h.strip() for h in lines[0].split(",")]
            instances = []

            for line in lines[1:]:
                values = [v.strip() for v in line.split(",", len(headers) - 1)]
                if len(values) != len(headers):
                    continue
                instances.append(dict(zip(headers, values)))

            return instances
        except Exception as e:
            return [{"Erro": f"Falha no WMIC: {str(e)}"}]

    def get_system_info(self):
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        return {
            "Sistema Operacional": f"{platform.system()} {platform.release()}",
            "Versão": platform.version(),
            "Nome da Máquina": platform.node(),
            "Arquitetura": platform.machine(),
            "Último Boot": boot_time.strftime("%d/%m/%Y %H:%M:%S"),
        }

    def get_cpu_info(self):
        cpu_data = self.run_wmic(
            "cpu",
            [
                "Name",
                "Caption",
                "MaxClockSpeed",
                "NumberOfCores",
                "NumberOfLogicalProcessors",
            ],
        )
        return {
            "Nome Comercial": cpu_data.get("Name", platform.processor()),
            "Descrição": cpu_data.get("Caption", "N/A"),
            "Núcleos Físicos": cpu_data.get(
                "NumberOfCores", psutil.cpu_count(logical=False)
            ),
            "Núcleos Lógicos": cpu_data.get(
                "NumberOfLogicalProcessors", psutil.cpu_count(logical=True)
            ),
            "Frequência Máxima": f"{cpu_data.get('MaxClockSpeed', 'N/A')} MHz",
        }

    def get_memory_info(self):
        memory = psutil.virtual_memory()
        return {
            "Total": f"{memory.total / (1024**3):.2f} GB",
            "Disponível": f"{memory.available / (1024**3):.2f} GB",
            "Usado": f"{memory.used / (1024**3):.2f} GB",
            "Porcentagem Usada": f"{memory.percent}%",
        }

    def get_disk_info(self):
        disk_info = {}
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[f"Disco {partition.device}"] = {
                    "Sistema de Arquivos": partition.fstype,
                    "Total": f"{usage.total / (1024**3):.2f} GB",
                    "Usado": f"{usage.used / (1024**3):.2f} GB",
                    "Livre": f"{usage.free / (1024**3):.2f} GB",
                    "Porcentagem Usada": f"{(usage.used / usage.total * 100):.1f}%",
                }
            except Exception as e:
                disk_info[f"Disco {partition.device}"] = {"Erro": str(e)}
        return disk_info

    def get_network_info(self):
        nics = self.run_wmic_multi(
            "nic", ["Name", "AdapterType", "MACAddress", "Speed"]
        )
        nic_list = []
        for nic in nics:
            nic_list.append(
                {
                    "Nome": nic.get("Name", "N/A"),
                    "Tipo": nic.get("AdapterType", "N/A"),
                    "MAC": nic.get("MACAddress", "N/A"),
                    "Velocidade": nic.get("Speed", "N/A"),
                }
            )
        return nic_list

    def get_gpu_info(self):
        gpus = self.run_wmic_multi(
            "path Win32_VideoController",
            ["Name", "Caption", "AdapterRAM", "DriverVersion"],
        )

        gpu_list = []
        for gpu in gpus:
            ram = gpu.get("AdapterRAM", "")
            try:
                ram_gb = int(ram) / (1024**3)
                ram_str = f"{ram_gb:.2f} GB"
            except:
                ram_str = "N/A" if not ram else ram

            gpu_list.append(
                {
                    "Nome": gpu.get("Name", "N/A"),
                    "Descrição": gpu.get("Caption", "N/A"),
                    "Memória de Vídeo": ram_str,
                    "Versão do Driver": gpu.get("DriverVersion", "N/A"),
                }
            )

        # Se WMIC não retornou nada, tenta via PowerShell
        if not gpu_list:
            try:
                ps_command = [
                    "powershell",
                    "-Command",
                    "Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion,Caption | ConvertTo-Json",
                ]
                result = subprocess.run(
                    ps_command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                )
                import json

                ps_gpus = json.loads(result.stdout)

                if isinstance(ps_gpus, dict):  # apenas 1 GPU
                    ps_gpus = [ps_gpus]

                for gpu in ps_gpus:
                    ram = gpu.get("AdapterRAM", "")
                    try:
                        ram_gb = int(ram) / (1024**3)
                        ram_str = f"{ram_gb:.2f} GB"
                    except:
                        ram_str = "N/A" if not ram else ram

                    gpu_list.append(
                        {
                            "Nome": gpu.get("Name", "N/A"),
                            "Descrição": gpu.get("Caption", "N/A"),
                            "Memória de Vídeo": ram_str,
                            "Versão do Driver": gpu.get("DriverVersion", "N/A"),
                        }
                    )
            except Exception as e:
                gpu_list.append({"Erro": f"Falha no PowerShell: {str(e)}"})

        return gpu_list

    def get_motherboard_info(self):
        mb = self.run_wmic(
            "baseboard", ["Manufacturer", "Product", "SerialNumber", "Version"]
        )
        return {
            "Fabricante": mb.get("Manufacturer", "N/A"),
            "Produto": mb.get("Product", "N/A"),
            "Número de Série": mb.get("SerialNumber", "N/A"),
            "Versão": mb.get("Version", "N/A"),
        }

    def get_memory_details(self):
        modules = self.run_wmic_multi(
            "memorychip",
            [
                "Capacity",
                "Speed",
                "Manufacturer",
                "PartNumber",
                "DeviceLocator",
                "SerialNumber",
            ],
        )
        mem_list = []
        for module in modules:
            capacity = module.get("Capacity", "0")
            try:
                capacity_gb = int(capacity) / (1024**3)
                capacity_str = f"{capacity_gb:.2f} GB"
            except:
                capacity_str = capacity
            mem_list.append(
                {
                    "Capacidade": capacity_str,
                    "Velocidade": f"{module.get('Speed', 'N/A')} MHz",
                    "Fabricante": module.get("Manufacturer", "N/A"),
                    "Número da Peça": module.get("PartNumber", "N/A"),
                    "Localizador": module.get("DeviceLocator", "N/A"),
                    "Número de Série": module.get("SerialNumber", "N/A"),
                }
            )
        return mem_list

    def get_bios_info(self):
        bios = self.run_wmic(
            "bios", ["Manufacturer", "Version", "ReleaseDate", "SMBIOSBIOSVersion"]
        )
        return {
            "Fabricante": bios.get("Manufacturer", "N/A"),
            "Versão": bios.get("Version", "N/A"),
            "Data de Lançamento": bios.get("ReleaseDate", "N/A"),
            "Versão SMBIOS": bios.get("SMBIOSBIOSVersion", "N/A"),
        }

    def get_all_info(self):
        return {
            "Sistema": self.get_system_info(),
            "Processador": self.get_cpu_info(),
            "Placa Mãe": self.get_motherboard_info(),
            "Memória": self.get_memory_info(),
            "Detalhes da Memória RAM": self.get_memory_details(),
            "Discos": self.get_disk_info(),
            "Placas de Vídeo": self.get_gpu_info(),
            "BIOS": self.get_bios_info(),
            "Rede": self.get_network_info(),
        }

    def format_info_for_display(self, info_dict, indent=0):
        formatted_text = ""
        indent_str = "  " * indent
        for key, value in info_dict.items():
            if isinstance(value, dict):
                formatted_text += f"{indent_str}{key}:\n"
                formatted_text += self.format_info_for_display(value, indent + 1)
            elif isinstance(value, list):
                formatted_text += f"{indent_str}{key}:\n"
                for item in value:
                    if isinstance(item, dict):
                        formatted_text += self.format_info_for_display(item, indent + 1)
                    else:
                        formatted_text += f"{indent_str}  {item}\n"
            else:
                formatted_text += f"{indent_str}{key}: {value}\n"
        return formatted_text


def get_pc_info():
    sys_info = SystemInfo()
    return sys_info.get_all_info()


def get_pc_info_formatted():
    sys_info = SystemInfo()
    all_info = sys_info.get_all_info()
    return sys_info.format_info_for_display(all_info)
