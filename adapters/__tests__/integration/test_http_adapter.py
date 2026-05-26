import pytest
from httpx import HTTPStatusError
from adapters.http_adapter import HttpAdapter

def test_http_adapter():
    http_adapter = HttpAdapter()

    with pytest.raises(HTTPStatusError):
        http_adapter.post("https://google.com")
