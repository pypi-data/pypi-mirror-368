from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


@dataclass
class AuthConfig:
    type: str  # none|basic|bearer|cookie|form
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    login_url: Optional[str] = None
    login_payload: Optional[Dict[str, Any]] = None
    cookie_name: Optional[str] = None
    cookie_value: Optional[str] = None


class AuthHandler:
    def __init__(self, auth_config: Optional[Dict[str, Any]] = None) -> None:
        cfg = auth_config or {"type": "none"}
        self.config = AuthConfig(**cfg)
        self._lock = asyncio.Lock()

    async def apply(self, client: httpx.AsyncClient, request: httpx.Request) -> None:
        if self.config.type == "basic" and self.config.username and self.config.password:
            request.headers["Authorization"] = httpx.BasicAuth(self.config.username, self.config.password).auth_header
        elif self.config.type == "bearer" and self.config.token:
            request.headers["Authorization"] = f"Bearer {self.config.token}"
        elif self.config.type == "cookie" and self.config.cookie_name and self.config.cookie_value:
            request.headers["Cookie"] = f"{self.config.cookie_name}={self.config.cookie_value}"

    async def ensure_authenticated(self, client: httpx.AsyncClient) -> None:
        if self.config.type != "form":
            return
        async with self._lock:
            if not self.config.login_url or not self.config.login_payload:
                return
            await client.post(self.config.login_url, json=self.config.login_payload)

    async def maybe_reauth(self, client: httpx.AsyncClient, response: httpx.Response) -> None:
        if response.status_code in (401, 403):
            await self.ensure_authenticated(client)


