"""Core package for IDOR Finder.

Exports commonly used functions and classes for convenience.
"""

from .banner import print_banner
from .idor_checker import IDORChecker, ScanConfig
from .parameter_extractor import ParameterExtractor
from .payload_generator import PayloadGenerator
from .uuid_fuzzer import UUIDFuzzer
from .auth_handler import AuthHandler
from .crawler import Crawler
from .fuzz_engine import FuzzEngine
from .matcher import Matcher
from .report_generator import ReportGenerator
from .utils import (
    Color,
    colorize,
    stable_content_hash,
    try_base64_decode,
    try_hex_decode,
    ensure_directory,
)

__all__ = [
    "print_banner",
    "IDORChecker",
    "ScanConfig",
    "ParameterExtractor",
    "PayloadGenerator",
    "UUIDFuzzer",
    "AuthHandler",
    "Crawler",
    "FuzzEngine",
    "Matcher",
    "ReportGenerator",
    "Color",
    "colorize",
    "stable_content_hash",
    "try_base64_decode",
    "try_hex_decode",
    "ensure_directory",
]


