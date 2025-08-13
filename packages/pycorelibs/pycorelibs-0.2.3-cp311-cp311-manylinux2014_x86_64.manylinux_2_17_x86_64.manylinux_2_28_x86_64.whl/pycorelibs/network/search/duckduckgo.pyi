import types
from _typeshed import Incomplete
from dataclasses import dataclass
from typing import Any

@dataclass
class SearchResult:
    title: str
    href: str
    body: str
    @classmethod
    def from_raw(cls, d: dict[str, Any]) -> SearchResult: ...

class DuckError(RuntimeError):
    message: Incomplete
    query: Incomplete
    backend: Incomplete
    params: Incomplete
    cause: Incomplete
    def __init__(self, message: str, *, query: str = None, backend: str = None, params: dict = None, cause: Exception = None) -> None: ...

class Worker:
    def __init__(self, *, proxy: str | None = None, timeout: int = 10, verify: bool = True) -> None: ...
    def search(self, query: str, *, max_results: int = 20, region: str = 'wt-wt', safesearch: str = 'moderate', timelimit: str | None = None, as_dict: bool = True) -> list[SearchResult] | list[dict[str, str]]: ...
    def close(self) -> None: ...
    def __enter__(self) -> Worker: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: types.TracebackType | None) -> None: ...
