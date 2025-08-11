from pycorelibs.system.cpu import CPUInfo as CPUInfo
from pycorelibs.system.mainboard import MainboardInfo as MainboardInfo
from pycorelibs.system.netadapter import NetAdapterInfo as NetAdapterInfo
from pycorelibs.system.osinfo import OSInfo as OSInfo
from typing import Any

class SystemInfo:
    def __init__(self, include_virtual: bool = False, include_loopback: bool = False, only_up: bool = True, require_ip: bool = False, prefer_non_laa: bool = True) -> None: ...
    def get_data(self) -> dict[str, Any]: ...
