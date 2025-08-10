import datetime
from _typeshed import Incomplete
from typing import Any

class UniCodeGenerator:
    prefix_date: Incomplete
    random_length: Incomplete
    charset: Incomplete
    separator: Incomplete
    def __init__(self, prefix_date: bool = True, random_length: int = 6, charset: str = ..., separator: str = '-') -> None: ...
    def generate(self, date: datetime.date = None) -> str: ...

def get_md5(text: Any, length: int = 32, hex: bool = True) -> tuple[bool, str | None]: ...
def get_base64(text: Any, encoding: str = 'utf-8') -> tuple[bool, str | None]: ...
