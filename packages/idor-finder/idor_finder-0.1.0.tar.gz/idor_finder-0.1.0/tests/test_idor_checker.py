import pytest

from idor_finder.core.idor_checker import IDORChecker, ScanConfig


@pytest.mark.asyncio
async def test_checker_wordlist_loading():
    cfg = ScanConfig(urls=["https://example.com"], method="GET")
    checker = IDORChecker(cfg)
    names = checker._load_wordlist_params(None)
    assert "user_id" in names
    assert "order_id" in names


