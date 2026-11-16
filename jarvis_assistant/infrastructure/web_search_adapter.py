import re
from collections.abc import Callable
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse

import requests

from ..domain.ports import WebSearchPort


class DuckDuckGoWebSearchAdapter(WebSearchPort):
    """Legacy DuckDuckGo and Wikipedia fallback search implementation."""

    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )

    def __init__(
        self,
        enabled: Callable[[], bool],
        *,
        get: Callable = requests.get,
    ) -> None:
        self._enabled = enabled
        self._get = get

    def search(self, query: str, max_results: int = 3) -> dict:
        if not self._enabled():
            return {"status": "error", "error": "Web search is disabled in settings."}
        if not query:
            return {"status": "error", "error": "Empty search query."}

        headers = {"User-Agent": self.USER_AGENT}
        try:
            response = self._get(
                "https://duckduckgo.com/html/",
                params={"q": query},
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            html = response.text
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

        results = self._parse_duckduckgo_results(html, max_results)
        if results:
            return {"status": "success", "query": query, "results": results}

        try:
            response = self._get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "opensearch",
                    "search": query,
                    "limit": max_results,
                    "namespace": 0,
                    "format": "json",
                },
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            titles = data[1] if len(data) > 1 else []
            snippets = data[2] if len(data) > 2 else []
            urls = data[3] if len(data) > 3 else []
            for title, snippet, url in zip(titles, snippets, urls):
                if title and url:
                    results.append({"title": title, "url": url, "snippet": snippet})
        except Exception as exc:
            return {"status": "error", "error": f"No results found. {exc}"}

        if not results:
            return {"status": "error", "error": "No results found."}
        return {"status": "success", "query": query, "results": results}

    @staticmethod
    def _parse_duckduckgo_results(html: str, max_results: int) -> list[dict]:
        results = []
        pattern = re.compile(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
            r'(?:<a[^>]+class="result__snippet"[^>]*>|<div[^>]+class="result__snippet"[^>]*>)(.*?)</',
            re.DOTALL,
        )
        for match in pattern.finditer(html):
            href = match.group(1)
            title = unescape(re.sub(r"<.*?>", "", match.group(2))).strip()
            snippet = unescape(re.sub(r"<.*?>", "", match.group(3))).strip()
            result_url = href
            parsed = urlparse(href)
            if parsed.path == "/l/" and "uddg" in parse_qs(parsed.query):
                result_url = unquote(parse_qs(parsed.query)["uddg"][0])
            if title and result_url:
                results.append({"title": title, "url": result_url, "snippet": snippet})
            if len(results) >= max_results:
                break
        return results
