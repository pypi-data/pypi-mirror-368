from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import httpx

from .auth_handler import AuthHandler
from .fuzz_engine import FuzzEngine, FuzzTarget
from .matcher import MatchResult, Matcher
from .parameter_extractor import ParameterExtractor
from .payload_generator import PayloadGenerator
from .report_generator import ReportGenerator
from .uuid_fuzzer import UUIDFuzzer
from .utils import ensure_directory, load_resource_text
from .plugins.numeric_plugin import NumericFuzzer
from .plugins.uuid_plugin import UUIDPlugin


@dataclass
class ScanConfig:
    urls: List[str]
    method: str = "GET"
    headers: Dict[str, str] = None
    cookies: Dict[str, str] = None
    body: Optional[str] = None
    concurrency: int = 20
    rate_limit_per_s: float = 0.0
    timeout_s: float = 15.0
    crawl: bool = False
    max_crawl_pages: int = 50
    auth: Optional[Dict] = None
    wordlist_path: Optional[str] = None
    sensitive_keywords_path: Optional[str] = None


class IDORChecker:
    def __init__(self, config: ScanConfig) -> None:
        self.config = config
        self.extractor = ParameterExtractor()
        self.payloads = PayloadGenerator()
        self.uuid_fuzzer = UUIDFuzzer()
        self.plugins = [NumericFuzzer(), UUIDPlugin()]

        # Load sensitive keywords
        sensitive_keywords: List[str] = []
        if config.sensitive_keywords_path and os.path.exists(config.sensitive_keywords_path):
            with open(config.sensitive_keywords_path, "r", encoding="utf-8") as f:
                sensitive_keywords = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        else:
            text = load_resource_text("idor_finder.data", "sensitive_keywords.txt")
            if text:
                sensitive_keywords = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
        self.matcher = Matcher(sensitive_keywords=sensitive_keywords)

        # Reporting
        ensure_directory("output/logs")
        ensure_directory("output/reports")
        self.reporter = ReportGenerator("output/reports")

        # Auth
        self.auth = AuthHandler(config.auth)

    async def run(self) -> List[MatchResult]:
        urls = list(self.config.urls)
        headers = self.config.headers or {}
        cookies = self.config.cookies or {}
        body = self.config.body

        # Build targets
        targets = [
            FuzzTarget(method=self.config.method, url=u, base_headers=headers, base_cookies=cookies, base_body=body) for u in urls
        ]

        results: List[MatchResult] = []
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=max(20, self.config.concurrency))
        async with httpx.AsyncClient(limits=limits) as client:
            await self.auth.ensure_authenticated(client)

            # Build param list from wordlist
            param_names = self._load_wordlist_params(self.config.wordlist_path)

            # Fuzz each target for each parameter
            for target in targets:
                # Extract existing params to get baseline hints
                base_params = self.extractor.extract_from_url(target.url)
                # For convenience, prioritize discovered names
                discovered = [p.name for p in base_params]
                prioritized = discovered + [p for p in param_names if p not in discovered]

                # Prepare payloads using plugins
                for name in prioritized:
                    base_value = next((p.value for p in base_params if p.name == name and p.value), None)
                    payload_values: List[str] = []
                    for plugin in self.plugins:
                        try:
                            if plugin.should_handle(name, base_value, context="query"):
                                payload_values.extend(list(plugin.generate_payloads(name, base_value, seed=1337)))
                        except Exception:
                            continue

                    # Fallbacks if no plugin produced values
                    if not payload_values:
                        if base_value and base_value.isdigit():
                            base_num = int(base_value)
                            payload_values.extend([str(v) for v in self.payloads.generate_numeric_sequence(base_num, 10)])
                        payload_values.extend([str(v) for v in self.payloads.generate_high_ids(3)])
                        payload_values.extend(self.payloads.generate_uuid_values(2))

                    # Deduplicate
                    seen = set()
                    payload_values = [v for v in payload_values if not (v in seen or seen.add(v))]

                    res = await self._fuzz_single(client, target, name, payload_values)
                    results.extend(res)

        return results

    async def _fuzz_single(
        self, client: httpx.AsyncClient, target: FuzzTarget, name: str, payload_values: Iterable[str]
    ) -> List[MatchResult]:
        engine = FuzzEngine(
            auth=self.auth,
            matcher=self.matcher,
            concurrency=self.config.concurrency,
            rate_limit_per_s=self.config.rate_limit_per_s,
            timeout_s=self.config.timeout_s,
        )
        return await engine.fuzz_param_on_target(client, target, name, payload_values)

    def _load_wordlist_params(self, path: Optional[str]) -> List[str]:
        if path:
            default_path = path
        else:
            default_path = None
        names: List[str] = []
        if default_path and os.path.exists(default_path):
            try:
                with open(default_path, "r", encoding="utf-8") as f:
                    for line in f:
                        s = line.strip()
                        if not s or s.startswith("#"):
                            continue
                        names.append(s)
            except FileNotFoundError:
                names = []
        if not names:
            text = load_resource_text("idor_finder.data", "idor_wordlist.txt")
            if text:
                for line in text.splitlines():
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    names.append(s)
        if not names:
            names = ["id", "user_id", "account_id", "profile_id", "uuid", "guid", "order_id", "invoice_id"]
        # normalize and expand a little
        names = self.extractor.normalize_param_names(names)
        return names


