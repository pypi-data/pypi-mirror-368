import re
import uuid
from typing import Iterable, List


UUID_REGEX = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


class UUIDFuzzer:
    def looks_like_uuid(self, value: str) -> bool:
        return bool(UUID_REGEX.fullmatch(value))

    def generate_alternatives(self, original: str, count: int = 8) -> List[str]:
        alts: List[str] = []
        # same version (v4) randoms
        for _ in range(max(1, count - 2)):
            alts.append(str(uuid.uuid4()))

        try:
            parsed = uuid.UUID(original)
            # tweak last 4 hex digits but keep a valid UUID
            hex_str = parsed.hex
            flipped = hex_str[:-4] + ("%04x" % ((int(hex_str[-4:], 16) ^ 0x0FFF) & 0xFFFF))
            alts.append(str(uuid.UUID(flipped)))
        except Exception:
            pass

        # change variant by creating a uuid1
        alts.append(str(uuid.uuid1()))

        # ensure uniqueness
        unique = []
        seen = set()
        for v in alts:
            if v not in seen:
                seen.add(v)
                unique.append(v)
        return unique


