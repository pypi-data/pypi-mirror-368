from idor_finder.core.parameter_extractor import ParameterExtractor


def test_extract_query_params():
    pe = ParameterExtractor()
    params = pe.extract_from_url("https://x.test/items?user_id=5&order_id=10")
    names = {p.name for p in params}
    assert "user_id" in names
    assert "order_id" in names


def test_extract_uuid_in_path():
    pe = ParameterExtractor()
    params = pe.extract_from_url(
        "https://x.test/api/v1/users/123e4567-e89b-12d3-a456-426614174000/profile"
    )
    assert any(p.name == "uuid_path" for p in params)


