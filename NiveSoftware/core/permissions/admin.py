"""Execute selected system commands in a separate UAC-elevated worker."""

import ctypes
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
from ctypes import wintypes
from pathlib import Path


ELEVATED_OPERATIONS = {
    "disk_check": ["chkdsk C: /scan"],
    "system_repair": [
        "sfc /scannow",
        "Dism /Online /Cleanup-Image /ScanHealth",
        "Dism /Online /Cleanup-Image /RestoreHealth",
    ],
    "audio_repair": [
        "net stop audiosrv & timeout /t 5 & net start audiosrv & "
        "net start AudioEndpointBuilder & net start wuauserv"
    ],
    "dns_cleanup": [
        "netsh winsock reset",
        "netsh int ip reset",
        "nbtstat -R",
        "nbtstat -RR",
        "arp -d *",
        "net stop dnscache",
        "ipconfig /flushdns",
        "net start dnscache",
        "ipconfig /release",
        "ipconfig /renew",
        "ipconfig /registerdns",
        "netsh winsock reset",
        "netsh int ip reset",
    ],
    "network_renew_ip": ["ipconfig /release && ipconfig /renew"],
    "network_reset": [
        "netsh winsock reset && netsh int ip reset && ipconfig /flushdns && "
        "ipconfig /release && ipconfig /renew && shutdown -r -t 60"
    ],
    "schedule_reboot": ["shutdown -r -t 10"],
    "winsock_reset": ["netsh winsock reset"],
    "network_adapter_restart": [
        "wmic path win32_networkadapter call disable && timeout /t 3 && "
        "wmic path win32_networkadapter call enable"
    ],
    "clean_temp_files": [
        'del /q /f /s "%temp%\\*"',
        'del /q/f/s "C:\\Windows\\Temp\\*"',
        'del /q /f /s "%windir%\\Prefetch\\*"',
        'del /q /f /s "%appdata%\\Microsoft\\Windows\\Recent\\*"',
    ],
    "complete_repair": None,
    "install_chocolatey": None,
    "software_reinstall": None,
    "delete_corrupted_folder": None,
    "optimization_services": None,
    "optimization_scheduled_tasks": None,
    "optimization_telemetry": None,
    "optimization_features": None,
    "optimization_edge": None,
}
_ACTIVE_OPERATIONS = set()
_ACTIVE_OPERATIONS_LOCK = threading.Lock()


def is_user_admin():
    if sys.platform != "win32":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def run_elevated_command(operation, timeout=300, arguments=None, progress_callback=None):
    success, results = run_elevated_operation(
        operation, timeout, arguments, progress_callback
    )
    if not success:
        return False, results
    result = results[0]
    if operation in {"disk_check", "system_repair"}:
        output = "\n".join(
            part for part in (result["stdout"], result["stderr"]) if part
        )
    else:
        output = result["stdout"] or result["stderr"]
    return result["returncode"] == 0, output


def run_elevated_operation(
    operation, timeout=300, arguments=None, progress_callback=None
):
    if not isinstance(operation, str):
        return False, "Identificador de operação elevada inválido."

    with _ACTIVE_OPERATIONS_LOCK:
        if operation in _ACTIVE_OPERATIONS:
            return False, "Esta operação já está em execução."
        _ACTIVE_OPERATIONS.add(operation)
    try:
        return _run_elevated_operation(
            operation, timeout, arguments, progress_callback
        )
    finally:
        with _ACTIVE_OPERATIONS_LOCK:
            _ACTIVE_OPERATIONS.discard(operation)


def _run_elevated_operation(operation, timeout, arguments, progress_callback):
    if sys.platform != "win32":
        return False, "A elevação UAC só está disponível no Windows."

    if operation not in ELEVATED_OPERATIONS:
        return False, f"Operação elevada não reconhecida: {operation}"

    if operation == "software_reinstall":
        if not isinstance(arguments, dict) or not isinstance(
            arguments.get("software"), dict
        ):
            return False, "Dados do software selecionado estão inválidos."
    elif operation == "delete_corrupted_folder":
        folder_path = arguments.get("path") if isinstance(arguments, dict) else None
        if not isinstance(folder_path, str) or not Path(folder_path).is_absolute():
            return False, "O caminho da pasta selecionada é inválido."
    elif arguments is not None:
        return False, "Esta operação não aceita argumentos."

    if is_user_admin():
        return True, _execute_operation(
            operation, timeout, arguments, progress_callback
        )

    request_dir = Path(tempfile.mkdtemp(prefix="scriptnive-uac-"))
    request_path = request_dir / "request.json"
    result_path = request_dir / "result.json"
    progress_path = request_dir / "progress.json"

    try:
        request_path.write_text(
            json.dumps(
                {
                    "operation": operation,
                    "arguments": arguments,
                    "cwd": os.getcwd(),
                    "result_path": str(result_path),
                    "progress_path": str(progress_path),
                    "timeout": timeout,
                }
            ),
            encoding="utf-8",
        )
        return _launch_worker(
            request_path, result_path, progress_path, progress_callback
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, f"Não foi possível iniciar a operação elevada: {e}"
    finally:
        try:
            request_path.unlink(missing_ok=True)
            result_path.unlink(missing_ok=True)
            progress_path.unlink(missing_ok=True)
            request_dir.rmdir()
        except OSError:
            pass


def _launch_worker(request_path, result_path, progress_path, progress_callback):
    class ShellExecuteInfo(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("fMask", wintypes.ULONG),
            ("hwnd", wintypes.HWND),
            ("lpVerb", wintypes.LPCWSTR),
            ("lpFile", wintypes.LPCWSTR),
            ("lpParameters", wintypes.LPCWSTR),
            ("lpDirectory", wintypes.LPCWSTR),
            ("nShow", ctypes.c_int),
            ("hInstApp", wintypes.HINSTANCE),
            ("lpIDList", ctypes.c_void_p),
            ("lpClass", wintypes.LPCWSTR),
            ("hkeyClass", wintypes.HKEY),
            ("dwHotKey", wintypes.DWORD),
            ("hIconOrMonitor", wintypes.HANDLE),
            ("hProcess", wintypes.HANDLE),
        ]

    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    shell32.ShellExecuteExW.argtypes = [ctypes.POINTER(ShellExecuteInfo)]
    shell32.ShellExecuteExW.restype = wintypes.BOOL
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.GetExitCodeProcess.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    parameters = subprocess.list2cmdline(
        [str(Path(__file__).resolve()), "--worker", str(request_path)]
    )
    info = ShellExecuteInfo()
    info.cbSize = ctypes.sizeof(info)
    info.fMask = 0x00000040
    info.lpVerb = "runas"
    info.lpFile = sys.executable
    info.lpParameters = parameters
    info.lpDirectory = str(Path(__file__).resolve().parents[2])
    info.nShow = 0

    if not shell32.ShellExecuteExW(ctypes.byref(info)):
        error = ctypes.get_last_error()
        if error == 1223:
            return False, "A solicitação de privilégios foi recusada no UAC."
        return False, f"Falha ao iniciar processo elevado (erro {error})."

    try:
        last_progress = None
        while True:
            wait_result = kernel32.WaitForSingleObject(info.hProcess, 250)
            if progress_path.exists():
                try:
                    progress = progress_path.read_text(encoding="utf-8")
                    if progress and progress != last_progress:
                        last_progress = progress
                        if progress_callback:
                            percentage, description = json.loads(progress)
                            progress_callback(percentage, description)
                except (OSError, ValueError):
                    pass
            if wait_result == 0:
                break
            if wait_result != 0x00000102:
                return False, "Falha ao aguardar o processo elevado."

        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(info.hProcess, ctypes.byref(exit_code)):
            return False, "Não foi possível obter o resultado do processo elevado."
        if not result_path.exists():
            return False, f"O processo elevado terminou sem resultado (código {exit_code.value})."

        result = json.loads(result_path.read_text(encoding="utf-8"))
        return True, result
    finally:
        kernel32.CloseHandle(info.hProcess)


def _run_command(command, timeout):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "returncode": 1,
            "stdout": e.stdout or "",
            "stderr": f"Timeout após {timeout} segundos.",
        }


def _run_worker(request_path):
    request = json.loads(Path(request_path).read_text(encoding="utf-8"))
    operation = request.get("operation")
    if operation not in ELEVATED_OPERATIONS:
        raise ValueError("A solicitação de operação elevada é inválida.")

    def report_progress(percentage, description):
        progress_path = Path(request["progress_path"])
        temp_path = progress_path.with_suffix(".tmp")
        temp_path.write_text(
            json.dumps([percentage, description]), encoding="utf-8"
        )
        temp_path.replace(progress_path)

    worker_output = io.StringIO()
    try:
        with contextlib.redirect_stdout(worker_output), contextlib.redirect_stderr(
            worker_output
        ):
            results = _execute_operation(
                operation,
                request.get("timeout", 300),
                request.get("arguments"),
                report_progress,
                request.get("cwd"),
            )
    except Exception as e:
        results = [{"returncode": 1, "stdout": "", "stderr": str(e)}]

    captured_output = worker_output.getvalue()
    if captured_output and results:
        results[0]["stdout"] = captured_output + results[0]["stdout"]

    result_path = Path(request["result_path"])
    temp_path = result_path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(results), encoding="utf-8")
    temp_path.replace(result_path)


def _execute_operation(
    operation, timeout, arguments=None, progress_callback=None, cwd=None
):
    project_root = str(Path(__file__).resolve().parents[2])
    repo_root = str(Path(__file__).resolve().parents[3])
    for p in (project_root, repo_root):
        if p not in sys.path:
            sys.path.insert(0, p)

    optimization_operations = {
        "optimization_services": (
            ["optimization.startup.services", "core.services", "NiveSoftware.optimization.startup.services"],
            "DesabilitadorServicos",
            "executar_desabilitacao_servicos",
        ),
        "optimization_scheduled_tasks": (
            ["optimization.startup.tasks", "core.tasks", "NiveSoftware.optimization.startup.tasks"],
            "DesabilitadorTweaks",
            "executar_desabilitacao_tweaks",
        ),
        "optimization_telemetry": (
            ["optimization.performance.telemetry", "core.telemetry", "NiveSoftware.optimization.performance.telemetry"],
            "RemoverTelemetria",
            "executar_remocao_completa",
        ),
        "optimization_features": (
            ["optimization.startup.features", "core.features", "NiveSoftware.optimization.startup.features"],
            "RemoverFeatures",
            "executar_remocao_features",
        ),
        "optimization_edge": (
            ["optimization.performance.edge", "core.edge", "NiveSoftware.optimization.performance.edge"],
            "OtimizadorEdge",
            "executar_otimizacao_edge",
        ),
    }
    if operation in optimization_operations:
        import importlib

        candidate_modules, class_name, method_name = optimization_operations[operation]
        module = None
        for mod_name in candidate_modules:
            try:
                module = importlib.import_module(mod_name)
                break
            except ImportError:
                continue
        if module is None:
            raise ImportError(f"Não foi possível importar módulo para {operation}")
        operation_output = io.StringIO()
        with contextlib.redirect_stdout(operation_output):
            optimizer = getattr(module, class_name)()
            success, successes, errors = getattr(optimizer, method_name)()
        return [
            {
                "returncode": 0 if success else 1,
                "stdout": operation_output.getvalue(),
                "stderr": "",
                "data": {"successes": successes, "errors": errors},
            }
        ]

    if operation == "complete_repair":
        try:
            from repair.complete_repair import get_complete_repair
        except ImportError:
            try:
                from NiveSoftware.repair.complete_repair import get_complete_repair
            except ImportError:
                from core.repair import get_complete_repair
        try:
            from audit.logging.logger import Logger
        except ImportError:
            try:
                from NiveSoftware.audit.logging.logger import Logger
            except ImportError:
                from utils.logger import Logger

        repair = get_complete_repair(Logger())
        succeeded, message = repair.run_complete_repair(progress_callback)
        return [
            {
                "returncode": 0 if succeeded else 1,
                "stdout": message if succeeded else "",
                "stderr": "" if succeeded else message,
            }
        ]

    if operation == "install_chocolatey":
        try:
            from shared.utilities.software import SoftwareManager
        except ImportError:
            try:
                from NiveSoftware.shared.utilities.software import SoftwareManager
            except ImportError:
                from core.software import SoftwareManager

        succeeded = SoftwareManager().install_chocolatey()
        return [
            {
                "returncode": 0 if succeeded else 1,
                "stdout": "Chocolatey instalado." if succeeded else "",
                "stderr": "" if succeeded else "Falha na instalação do Chocolatey.",
            }
        ]

    if operation == "software_reinstall":
        try:
            from shared.utilities.software import SoftwareManager
        except ImportError:
            try:
                from NiveSoftware.shared.utilities.software import SoftwareManager
            except ImportError:
                from core.software import SoftwareManager

        manager = SoftwareManager()
        requested = arguments["software"]
        selected = next(
            (
                item
                for item in manager.get_installed_software()
                if item.get("display_name") == requested.get("display_name")
                and item.get("uninstall_string") == requested.get("uninstall_string")
            ),
            None,
        )
        if selected is None:
            return [
                {
                    "returncode": 1,
                    "stdout": "",
                    "stderr": "O software selecionado não está mais instalado.",
                }
            ]
        succeeded, message = manager.process_software_reinstall(selected)
        return [
            {
                "returncode": 0 if succeeded else 1,
                "stdout": message if succeeded else "",
                "stderr": "" if succeeded else message,
            }
        ]

    if operation == "delete_corrupted_folder":
        try:
            from core.task_queue.commands import SystemCommands
        except ImportError:
            try:
                from NiveSoftware.core.task_queue.commands import SystemCommands
            except ImportError:
                from core.commands import SystemCommands
        try:
            from audit.logging.logger import Logger
        except ImportError:
            try:
                from NiveSoftware.audit.logging.logger import Logger
            except ImportError:
                from utils.logger import Logger

        deleted = SystemCommands(Logger()).delete_corrupted_folder(
            arguments["path"]
        )
        return [
            {
                "returncode": 0 if deleted else 1,
                "stdout": "Pasta removida." if deleted else "",
                "stderr": "" if deleted else "A pasta continua existindo.",
            }
        ]

    commands = ELEVATED_OPERATIONS[operation]
    if operation in {"disk_check", "system_repair"}:
        results = []
        for command in commands:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                command_result = {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            except subprocess.TimeoutExpired as e:
                stdout = e.stdout or ""
                if isinstance(stdout, bytes):
                    stdout = stdout.decode(errors="replace")
                command_result = {
                    "returncode": 1,
                    "stdout": stdout,
                    "stderr": f"Timeout após {timeout} segundos.",
                }
            except OSError as e:
                command_result = {
                    "returncode": 1,
                    "stdout": "",
                    "stderr": str(e),
                }

            results.append(command_result)
            if command_result["returncode"] != 0:
                break

        return [
            {
                "returncode": results[-1]["returncode"],
                "stdout": "\n".join(
                    result["stdout"] for result in results if result["stdout"]
                ),
                "stderr": "\n".join(
                    result["stderr"] for result in results if result["stderr"]
                ),
            }
        ]

    if operation == "dns_cleanup":
        results = []
        primary_count = len(commands) - 2
        for index, command in enumerate(commands):
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                results.append(
                    {
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    }
                )
            except (OSError, subprocess.TimeoutExpired) as e:
                failure = {
                    "returncode": 1,
                    "stdout": "",
                    "stderr": f"Timeout após {timeout} segundos."
                    if isinstance(e, subprocess.TimeoutExpired)
                    else str(e),
                }
                results.append(failure)
                if index < primary_count:
                    failure["aborted"] = True
                    return results
        return results

    results = []
    for command in commands:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            results.append(
                {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            )
        except subprocess.TimeoutExpired as e:
            results.append(
                {
                    "returncode": 1,
                    "stdout": e.stdout or "",
                    "stderr": f"Timeout após {timeout} segundos.",
                }
            )
    return results


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "--worker":
    try:
        _run_worker(sys.argv[2])
    except Exception:
        raise SystemExit(1)
