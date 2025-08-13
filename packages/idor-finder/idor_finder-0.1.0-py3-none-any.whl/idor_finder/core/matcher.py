from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

from .utils import stable_content_hash


@dataclass
class MatchResult:
    is_vuln: bool
    reason: str
    target_url: str
    method: str
    param: str
    payload: str
    status_base: int
    status_new: int
    len_base: int
    len_new: int


class Matcher:
    def __init__(self, sensitive_keywords: Optional[List[str]] = None, length_delta_ratio: float = 0.15) -> None:
        self.length_delta_ratio = length_delta_ratio
        self.sensitive_keywords = [kw.lower() for kw in (sensitive_keywords or [])]
        self._baselines: Dict[str, Dict[str, Any]] = {}

    def _key(self, method: str, url: str) -> str:
        return f"{method.upper()} {url}"

    def register_baseline(self, target: Any, response: httpx.Response) -> None:
        key = self._key(target.method, target.url)
        try:
            body = response.content
        except Exception:
            body = b""
        self._baselines[key] = {
            "status": response.status_code,
            "length": len(body or b""),
            "hash": stable_content_hash(body or b""),
        }

    def compare(
        self,
        target: Any,
        param: str,
        payload: str,
        base_resp: httpx.Response,
        new_resp: httpx.Response,
    ) -> MatchResult:
        try:
            base_body = base_resp.content or b""
        except Exception:
            base_body = b""
        try:
            new_body = new_resp.content or b""
        except Exception:
            new_body = b""

        base_len = len(base_body)
        new_len = len(new_body)

        # Rule 1: status code anomaly
        if base_resp.status_code in (401, 403) and new_resp.status_code == 200:
            return MatchResult(True, "403->200 anomaly", target.url, target.method, param, payload, base_resp.status_code, new_resp.status_code, base_len, new_len)

        # Rule 2: length delta
        if base_len > 0:
            delta = abs(new_len - base_len) / max(base_len, 1)
            if delta >= self.length_delta_ratio and new_resp.status_code == 200:
                return MatchResult(True, f"content length changed {delta:.0%}", target.url, target.method, param, payload, base_resp.status_code, new_resp.status_code, base_len, new_len)

        # Rule 3: sensitive keyword leakage
        if self.sensitive_keywords and new_resp.status_code == 200:
            text = (new_body.decode("utf-8", errors="ignore")).lower()
            for kw in self.sensitive_keywords:
                if re.search(rf"\b{re.escape(kw)}\b", text):
                    return MatchResult(True, f"keyword '{kw}' present", target.url, target.method, param, payload, base_resp.status_code, new_resp.status_code, base_len, new_len)

        return MatchResult(False, "no anomaly", target.url, target.method, param, payload, base_resp.status_code, new_resp.status_code, base_len, new_len)


