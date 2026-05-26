from typing import Any, Mapping
from httpx import Client, QueryParams


class HttpAdapter:
    def post(
        self,
        url: str,
        params: QueryParams | None = None,
        headers: Mapping[str, str] | None = None,
        body: Any | None = None,
        data: Mapping[str, Any] | None = None,
    ) -> Any:
        with Client(headers=headers, params=params) as client:
            response = client.post(url=url, json=body, data=data)

        response.raise_for_status()
        return response.json()
