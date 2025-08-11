from pycorelibs.network.search.duckduckgo import SearchResult as SearchResult, Worker as Worker

class Engine:
    @staticmethod
    def search(query: str, *, max_results: int = 5, region: str = 'wt-wt', safesearch: str = 'moderate', timelimit: str | None = None, proxy: str | None = None, timeout: int = 5, verify: bool = True, as_dict: bool = True) -> list[SearchResult] | list[dict[str, str]]: ...
