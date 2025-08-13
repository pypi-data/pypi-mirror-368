import random
import uuid
from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class Payload:
    param: str
    value: str
    encoding: Optional[str] = None  # base64|url|hex|none


class PayloadGenerator:
    def __init__(self, seed: Optional[int] = None) -> None:
        self.random = random.Random(seed)

    def generate_numeric_sequence(self, base: int, count: int = 10) -> List[int]:
        return [max(0, base - i) for i in range(1, count // 2 + 1)] + [base + i for i in range(1, count - count // 2 + 1)]

    def generate_high_ids(self, count: int = 5) -> List[int]:
        return [self.random.randint(10_000, 1_000_000) for _ in range(count)]

    def generate_uuid_values(self, count: int = 8) -> List[str]:
        return [str(uuid.uuid4()) for _ in range(count)]

    def wrap_param_payloads(self, param: str, values: Iterable[str]) -> List[Payload]:
        return [Payload(param=param, value=str(v)) for v in values]


