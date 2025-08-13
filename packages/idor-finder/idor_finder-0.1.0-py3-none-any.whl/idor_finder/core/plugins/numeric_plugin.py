from __future__ import annotations

from typing import Iterable, Optional

from ..payload_generator import PayloadGenerator


class NumericFuzzer:
    name = "numeric"

    def __init__(self, seed: int = 1337) -> None:
        self.gen = PayloadGenerator(seed=seed)

    def should_handle(self, param: str, base_value: Optional[str], context: str) -> bool:
        return base_value is None or (base_value.isdigit() if isinstance(base_value, str) else False)

    def generate_payloads(self, param: str, base_value: Optional[str], seed: int) -> Iterable[str]:
        # Prefer sequences near base_value when available
        values = []
        if base_value and base_value.isdigit():
            base_num = int(base_value)
            values.extend([str(v) for v in self.gen.generate_numeric_sequence(base_num, 12)])
        values.extend([str(v) for v in self.gen.generate_high_ids(6)])
        # dedupe
        seen = set()
        for v in values:
            if v not in seen:
                seen.add(v)
                yield v


