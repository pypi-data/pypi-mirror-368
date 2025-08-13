from pathlib import Path
from typing import Any, Iterable

def save_uploaded_file(file: Any, subdir: str = 'uploads', filename_predix: str = '', *, allowed_exts: Iterable[str] | None = None, min_size: int | None = None, max_size: int | None = None, hash_alg: str | None = None, chunk_size: int = ..., return_info: bool = False) -> Path | dict[str, Any]: ...
