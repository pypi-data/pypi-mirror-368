from __future__ import annotations

from typing import Iterable, Optional, Protocol


class FuzzerPlugin(Protocol):
    name: str

    def should_handle(self, param: str, base_value: Optional[str], context: str) -> bool:
        ...

    def generate_payloads(self, param: str, base_value: Optional[str], seed: int) -> Iterable[str]:
        ...


