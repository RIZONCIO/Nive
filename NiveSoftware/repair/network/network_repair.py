"""
network_repair.py - Reparo da pilha de rede, cache DNS e Winsock.
"""

from typing import List


class NetworkRepair:
    """Comandos para restauração da conectividade de rede."""

    DNS_CLEANUP = [
        "netsh winsock reset",
        "netsh int ip reset",
        "ipconfig /release",
        "ipconfig /renew",
        "ipconfig /flushdns",
        "ipconfig /registerdns",
    ]

    AUDIO_SERVICES = [
        "net stop audiosrv",
        "timeout /t 5",
        "net start audiosrv",
        "net start AudioEndpointBuilder",
        "net start wuauserv",
    ]

    @classmethod
    def get_dns_cleanup_commands(cls) -> List[str]:
        return list(cls.DNS_CLEANUP)

    @classmethod
    def get_audio_repair_commands(cls) -> List[str]:
        return list(cls.AUDIO_SERVICES)
