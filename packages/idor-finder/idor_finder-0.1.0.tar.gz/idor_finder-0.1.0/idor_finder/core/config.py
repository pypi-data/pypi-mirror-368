from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class AuthConfigModel(BaseModel):
    type: str = Field(default="none")  # none|basic|bearer|cookie|form
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    login_url: Optional[HttpUrl] = None
    login_payload: Optional[Dict] = None
    cookie_name: Optional[str] = None
    cookie_value: Optional[str] = None


class ScanConfigModel(BaseModel):
    urls: List[HttpUrl]
    method: str = Field(default="GET")
    headers: Dict[str, str] = Field(default_factory=dict)
    cookies: Dict[str, str] = Field(default_factory=dict)
    body: Optional[str] = None
    concurrency: int = 20
    rate_limit_per_s: float = 0.0
    timeout_s: float = 15.0
    crawl: bool = False
    max_crawl_pages: int = 50
    auth: Optional[AuthConfigModel] = None
    wordlist_path: Optional[str] = None
    sensitive_keywords_path: Optional[str] = None
    max_retries: int = 2
    backoff_initial_s: float = 0.5


