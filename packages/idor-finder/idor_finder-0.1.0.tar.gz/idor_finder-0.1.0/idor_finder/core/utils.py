import base64
import hashlib
import json
import os
import re
import time
from typing import Any, Dict, Optional
try:
    from importlib.resources import files as ir_files  # py3.9+: backported via importlib_resources not used here
except Exception:  # pragma: no cover
    ir_files = None  # type: ignore


class Color:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


def colorize(text: str, color: str) -> str:
    if os.name == "nt":
        return text
    return f"{color}{text}{Color.RESET}"


def stable_content_hash(content: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(content)
    return hasher.hexdigest()


def try_base64_decode(value: str) -> Optional[str]:
    try:
        padding = '=' * (-len(value) % 4)
        decoded = base64.urlsafe_b64decode((value + padding).encode("utf-8"))
        return decoded.decode("utf-8", errors="ignore")
    except Exception:
        try:
            decoded = base64.b64decode(value.encode("utf-8"))
            return decoded.decode("utf-8", errors="ignore")
        except Exception:
            return None


def try_hex_decode(value: str) -> Optional[str]:
    value_no_prefix = value[2:] if value.lower().startswith("0x") else value
    if re.fullmatch(r"[0-9a-fA-F]+", value_no_prefix) and len(value_no_prefix) % 2 == 0:
        try:
            return bytes.fromhex(value_no_prefix).decode("utf-8", errors="ignore")
        except Exception:
            return None
    return None


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_json_file(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_resource_text(package: str, name: str) -> Optional[str]:
    try:
        if ir_files is None:
            return None
        return ir_files(package).joinpath(name).read_text(encoding="utf-8")
    except Exception:
        return None


def rate_limited_sleep(last_time: float, min_interval_s: float) -> float:
    if min_interval_s <= 0:
        return time.monotonic()
    now = time.monotonic()
    elapsed = now - last_time
    if elapsed < min_interval_s:
        time.sleep(min_interval_s - elapsed)
        return time.monotonic()
    return now


