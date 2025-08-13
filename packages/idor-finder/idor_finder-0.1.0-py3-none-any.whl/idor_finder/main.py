from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import List

from .core import IDORChecker, ScanConfig, print_banner
from .core.config import ScanConfigModel, AuthConfigModel


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="IDOR Finder")
    p.add_argument("urls", nargs="*", help="Target URL(s)")
    p.add_argument("--url-file", help="Path to file containing URLs, one per line")
    p.add_argument("--method", default="GET")
    p.add_argument("--headers", help="JSON string of headers")
    p.add_argument("--cookies", help="JSON string of cookies")
    p.add_argument("--body", help="Raw request body or @path/to/file to load")
    p.add_argument("--concurrency", type=int, default=20)
    p.add_argument("--rate", type=float, default=0.0, help="Rate limit requests per second")
    p.add_argument("--timeout", type=float, default=15.0)
    p.add_argument("--crawl", action="store_true")
    p.add_argument("--max-crawl-pages", type=int, default=50)
    p.add_argument("--auth-config", help="Path to auth config JSON file")
    p.add_argument("--config", help="Unified scan config (JSON/TOML)")
    p.add_argument("--wordlist", help="Path to IDOR parameter wordlist")
    p.add_argument("--sensitive", help="Path to sensitive keywords file")
    p.add_argument("--report-format", choices=["json", "csv", "html"], default="html")
    return p.parse_args()


def load_body(value: str | None) -> str | None:
    if not value:
        return None
    if value.startswith("@") and os.path.exists(value[1:]):
        with open(value[1:], "r", encoding="utf-8") as f:
            return f.read()
    return value


async def main_async() -> int:
    print_banner()
    args = parse_args()

    urls: List[str] = list(args.urls)
    if args.url_file and os.path.exists(args.url_file):
        with open(args.url_file, "r", encoding="utf-8") as f:
            urls.extend([line.strip() for line in f if line.strip() and not line.startswith("#")])

    if not urls:
        print("No URLs provided.")
        return 2

    headers = json.loads(args.headers) if args.headers else None
    cookies = json.loads(args.cookies) if args.cookies else None
    body = load_body(args.body)
    auth_cfg = None
    if args.auth_config and os.path.exists(args.auth_config):
        with open(args.auth_config, "r", encoding="utf-8") as f:
            auth_cfg = json.load(f)

    # Optional unified config overrides
    if args.config and os.path.exists(args.config):
        try:
            import tomllib  # py311+
        except Exception:
            tomllib = None  # type: ignore
        with open(args.config, "rb") as f:
            raw = f.read()
        cfg_obj = None
        try:
            cfg_obj = json.loads(raw.decode("utf-8"))
        except Exception:
            if tomllib:
                cfg_obj = tomllib.loads(raw.decode("utf-8"))
        if isinstance(cfg_obj, dict):
            urls = cfg_obj.get("urls", urls) or urls
            headers = cfg_obj.get("headers", headers) or headers
            cookies = cfg_obj.get("cookies", cookies) or cookies
            body = cfg_obj.get("body", body) or body
            auth_cfg = cfg_obj.get("auth", auth_cfg) or auth_cfg
            if not args.wordlist:
                args.wordlist = cfg_obj.get("wordlist_path")
            if not args.sensitive:
                args.sensitive = cfg_obj.get("sensitive_keywords_path")
            args.method = cfg_obj.get("method", args.method)
            args.concurrency = cfg_obj.get("concurrency", args.concurrency)
            args.rate = cfg_obj.get("rate_limit_per_s", args.rate)
            args.timeout = cfg_obj.get("timeout_s", args.timeout)
            args.crawl = cfg_obj.get("crawl", args.crawl)
            args.max_crawl_pages = cfg_obj.get("max_crawl_pages", args.max_crawl_pages)

    # Validate and normalize with Pydantic
    cfg_dict = {
        "urls": urls,
        "method": args.method,
        "headers": headers or {},
        "cookies": cookies or {},
        "body": body,
        "concurrency": args.concurrency,
        "rate_limit_per_s": args.rate,
        "timeout_s": args.timeout,
        "crawl": args.crawl,
        "max_crawl_pages": args.max_crawl_pages,
        "auth": auth_cfg,
        "wordlist_path": args.wordlist,
        "sensitive_keywords_path": args.sensitive,
    }
    model = ScanConfigModel(**cfg_dict)

    cfg = ScanConfig(
        urls=[str(u) for u in model.urls],
        method=model.method,
        headers=dict(model.headers or {}),
        cookies=dict(model.cookies or {}),
        body=model.body,
        concurrency=model.concurrency,
        rate_limit_per_s=model.rate_limit_per_s,
        timeout_s=model.timeout_s,
        crawl=model.crawl,
        max_crawl_pages=model.max_crawl_pages,
        auth=(model.auth.model_dump() if model.auth else None),
        wordlist_path=model.wordlist_path,
        sensitive_keywords_path=model.sensitive_keywords_path,
    )

    checker = IDORChecker(cfg)
    results = await checker.run()

    from .core import ReportGenerator

    reporter = ReportGenerator()
    if args.report_format == "json":
        path = reporter.to_json(results)
    elif args.report_format == "csv":
        path = reporter.to_csv(results)
    else:
        path = reporter.to_html(results)
    print(f"Report written to {path}")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(main_async()))


if __name__ == "__main__":
    main()


