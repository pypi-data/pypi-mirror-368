import datetime
from _typeshed import Incomplete
from pycorelibs.security.base64s import b64encode as b64encode
from pycorelibs.security.md5s import md5 as md5
from typing import Any

class UniCodeGenerator:
    prefix_date: Incomplete
    random_length: Incomplete
    charset: Incomplete
    separator: Incomplete
    def __init__(self, prefix_date: bool = True, random_length: int = 6, charset: str = ..., separator: str = '-') -> None: ...
    def generate(self, date: datetime.date = None) -> str: ...

def json_dumps_bytes(obj: dict[str, Any]) -> bytes: ...
def json_loads_bytes(b: bytes) -> dict[str, Any]: ...
