from __future__ import annotations

from typing import Iterable, Optional

from ..uuid_fuzzer import UUIDFuzzer
from ..payload_generator import PayloadGenerator


class UUIDPlugin:
    name = "uuid"

    def __init__(self) -> None:
        self.uf = UUIDFuzzer()
        self.gen = PayloadGenerator()

    def should_handle(self, param: str, base_value: Optional[str], context: str) -> bool:
        return bool(base_value and isinstance(base_value, str) and self.uf.looks_like_uuid(base_value)) or param.lower().endswith(
            ("uuid", "guid")
        )

    def generate_payloads(self, param: str, base_value: Optional[str], seed: int) -> Iterable[str]:
        if base_value and self.uf.looks_like_uuid(base_value):
            for v in self.uf.generate_alternatives(base_value, 8):
                yield v
        else:
            for v in self.gen.generate_uuid_values(6):
                yield v


