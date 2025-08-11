from enum import Enum
from pathlib import Path

class EnumFileSizeUnit(Enum):
    BYTES = 'B'
    KILOBYTES = 'KB'
    MEGABYTES = 'MB'
    GIGABYTES = 'GB'
    TERABYTES = 'TB'

class FilesInfo:
    @staticmethod
    def get_file_size(file_name: str, unit: EnumFileSizeUnit = ...) -> float: ...
    @staticmethod
    def line_count(file_name: str) -> int: ...
    @staticmethod
    def get_directory_last_modified_time(directory: Path | str) -> str: ...
    @staticmethod
    def get_directory_last_modified_timestamp(directory: Path | str) -> int: ...
