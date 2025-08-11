from _typeshed import Incomplete
from newspaper import Article
from pycorelibs.network.requests import HTTPMethod as HTTPMethod, fetch_url as fetch_url, is_url as is_url

class HTMLContent(Article):
    markdown: Incomplete
    text: Incomplete
    def __init__(self, url, **kwargs) -> None: ...
    @staticmethod
    def safe_html2md(html: str, pure_text: bool = False) -> str: ...
    def fetch_html(self, url: str, headers: dict = None, proxies: dict = None) -> None: ...
