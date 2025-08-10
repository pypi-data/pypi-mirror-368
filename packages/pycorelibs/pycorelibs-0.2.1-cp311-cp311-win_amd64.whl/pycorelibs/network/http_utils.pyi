from _typeshed import Incomplete
from enum import Enum
from typing import Any

logger: Incomplete

class HTTPMethod(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'

def is_url(s: str) -> bool: ...
def fetch_url(url: str, method: HTTPMethod = ..., headers: dict[str, str] | None = None, params: dict[str, Any] | None = None, data: dict[str, Any] | str | None = None, json_data: dict[str, Any] | None = None, timeout: int = 10, max_retries: int = 3, backoff_factor: float = 0.5, verify_ssl: bool = True, proxies: dict[str, str] | None = None) -> dict[str, Any]: ...
async def async_fetch_url(url: str, method: HTTPMethod = ..., headers: dict[str, str] | None = None, params: dict[str, Any] | None = None, data: dict[str, Any] | str | None = None, json_data: dict[str, Any] | None = None, timeout: int = 10, max_retries: int = 3, backoff_factor: float = 0.5, verify_ssl: bool = True, proxy: str | None = None) -> dict[str, Any]: ...
async def main() -> None: ...
