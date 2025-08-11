from typing import Any

class RunTimeInfo:
    @staticmethod
    def get_boot_time(fmt: str | None = None) -> dict[str, Any]: ...
    @staticmethod
    def get_uptime(start_mono: float = ..., fmt: str | None = None) -> dict[str, Any]: ...
