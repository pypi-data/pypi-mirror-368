from pycorelibs.utils.environment.system.cpu import CPUInfo as CPUInfo
from pycorelibs.utils.environment.system.mainboard import MainboardInfo as MainboardInfo
from pycorelibs.utils.environment.system.netadapter import NetAdapterInfo as NetAdapterInfo

class SystemInfo:
    def __init__(self, include_virtual: bool = False, include_loopback: bool = False, only_up: bool = True, require_ip: bool = False, prefer_non_laa: bool = True) -> None: ...
    def get_info(self): ...
