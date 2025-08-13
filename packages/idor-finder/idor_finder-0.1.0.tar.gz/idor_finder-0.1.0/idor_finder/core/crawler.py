from __future__ import annotations

import asyncio
import re
from typing import Iterable, List, Set

import httpx
from bs4 import BeautifulSoup
from yarl import URL


class Crawler:
    def __init__(self, max_pages: int = 100, concurrency: int = 10, same_host: bool = True) -> None:
        self.max_pages = max_pages
        self.concurrency = concurrency
        self.same_host = same_host

    async def crawl(self, client: httpx.AsyncClient, roots: Iterable[str]) -> List[str]:
        start_urls = [str(URL(r)) for r in roots]
        seen: Set[str] = set()
        found: List[str] = []
        q: asyncio.Queue[str] = asyncio.Queue()
        for u in start_urls:
            await q.put(u)
        host = URL(start_urls[0]).host if (self.same_host and start_urls) else None

        async def worker() -> None:
            while len(found) < self.max_pages:
                try:
                    url = await asyncio.wait_for(q.get(), timeout=0.2)
                except asyncio.TimeoutError:
                    if q.empty():
                        return
                    continue
                if url in seen:
                    q.task_done()
                    continue
                seen.add(url)
                try:
                    resp = await client.get(url, follow_redirects=True)
                    if resp.status_code >= 400:
                        q.task_done()
                        continue
                    found.append(url)
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for tag in soup.find_all(["a", "form"]):
                        href = tag.get("href") or tag.get("action")
                        if not href:
                            continue
                        try:
                            next_url = str(URL(href) if re.match(r"https?://", href) else URL(url) / href)
                        except Exception:
                            continue
                        if self.same_host and host and URL(next_url).host != host:
                            continue
                        if next_url not in seen and len(seen) + q.qsize() < self.max_pages:
                            await q.put(next_url)
                finally:
                    q.task_done()

        workers = [asyncio.create_task(worker()) for _ in range(self.concurrency)]
        await q.join()
        for w in workers:
            w.cancel()
        return found


