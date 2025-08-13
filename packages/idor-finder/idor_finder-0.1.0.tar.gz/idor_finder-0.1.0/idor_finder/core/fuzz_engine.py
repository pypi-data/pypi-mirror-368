from __future__ import annotations

import asyncio
import json
import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

import httpx

from .auth_handler import AuthHandler
from .matcher import MatchResult, Matcher


@dataclass
class FuzzTarget:
    method: str
    url: str
    base_headers: Dict[str, str]
    base_cookies: Dict[str, str]
    base_body: Optional[str] = None  # raw body (form-encoded or JSON)


class FuzzEngine:
    def __init__(
        self,
        auth: AuthHandler,
        matcher: Matcher,
        concurrency: int = 20,
        rate_limit_per_s: float = 0.0,
        timeout_s: float = 15.0,
    ) -> None:
        self.auth = auth
        self.matcher = matcher
        self.semaphore = asyncio.Semaphore(concurrency)
        self.rate_limit_interval = 1.0 / rate_limit_per_s if rate_limit_per_s > 0 else 0.0
        self.timeout_s = timeout_s
        self._last_request_time = 0.0

    async def _send(self, client: httpx.AsyncClient, req: httpx.Request) -> httpx.Response:
        async with self.semaphore:
            # rate limit
            if self.rate_limit_interval > 0:
                now = asyncio.get_event_loop().time()
                elapsed = now - self._last_request_time
                if elapsed < self.rate_limit_interval:
                    await asyncio.sleep(self.rate_limit_interval - elapsed)
                self._last_request_time = asyncio.get_event_loop().time()

            await self.auth.apply(client, req)
            # simple retries with backoff and jitter
            backoff = 0.5
            for attempt in range(3):
                try:
                    resp = await client.send(req, timeout=self.timeout_s, follow_redirects=True)
                    if resp.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    await self.auth.maybe_reauth(client, resp)
                    return resp
                except httpx.HTTPError as e:
                    if attempt >= 2:
                        return httpx.Response(599, request=req, text=str(e))
                    await asyncio.sleep(backoff)
                    backoff *= 2

    @staticmethod
    def _update_url_param(url: str, name: str, value: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        query[name] = [value]
        new_query = urllib.parse.urlencode(query, doseq=True)
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))

    async def fuzz_param_on_target(
        self,
        client: httpx.AsyncClient,
        target: FuzzTarget,
        param_name: str,
        payload_values: Iterable[str],
    ) -> List[MatchResult]:
        results: List[MatchResult] = []

        base_req = client.build_request(
            target.method.upper(), target.url, headers=target.base_headers, cookies=target.base_cookies, content=target.base_body
        )
        base_resp = await self._send(client, base_req)
        self.matcher.register_baseline(target, base_resp)

        for payload in payload_values:
            # URL query fuzzing
            fuzz_url = self._update_url_param(target.url, param_name, payload)
            req = client.build_request(target.method.upper(), fuzz_url, headers=target.base_headers, cookies=target.base_cookies, content=target.base_body)
            resp = await self._send(client, req)
            m = self.matcher.compare(target, param_name, payload, base_resp, resp)
            if m.is_vuln:
                results.append(m)

            # If JSON body contains the param name, fuzz it too
            if target.base_body and target.base_headers.get("Content-Type", "").lower().startswith("application/json"):
                try:
                    body_obj = json.loads(target.base_body)
                except Exception:
                    body_obj = None
                if isinstance(body_obj, dict) and param_name in body_obj:
                    body_obj[param_name] = payload
                    req = client.build_request(
                        target.method.upper(), target.url, headers=target.base_headers, cookies=target.base_cookies, json=body_obj
                    )
                    resp = await self._send(client, req)
                    m = self.matcher.compare(target, param_name, payload, base_resp, resp)
                    if m.is_vuln:
                        results.append(m)

        return results


