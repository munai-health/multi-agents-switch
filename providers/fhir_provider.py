from datetime import datetime, timezone
from adapters.http_adapter import HttpAdapter
from typing import Any, Mapping, TypedDict
from config_env import config_env


class Token(TypedDict):
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str


class FhirProvider:
    token: Token | None = None
    last_login_date: float | None = None
    http_adapter: HttpAdapter

    def __init__(self, http_adapter: HttpAdapter):
        self.http_adapter = http_adapter

    def login(self, credentials: Mapping[str, str]) -> Token:
        self.last_login_date = datetime.now(timezone.utc).timestamp()

        return self.http_adapter.post(
            f"{config_env.KEYCLOAK_URL}/auth/realms/{config_env.KEYCLOAK_REALM_ID}/protocol/openid-connect/token",
            data=credentials,
        )

    def get_access_token(self) -> str:
        if self.token is None or self.last_login_date is None:
            credentials: Mapping[str, str] = {
                "grant_type": "client_credentials",
                "client_id": config_env.KEYCLOAK_CLIENT_ID,
                "client_secret": config_env.KEYCLOAK_CLIENT_SECRET,
            }

            self.token = self.login(credentials)
            return self.token["access_token"]

        else:
            now = datetime.now(timezone.utc).timestamp()

            if now < (self.last_login_date + self.token["expires_in"]):
                return self.token["access_token"]

            elif now < (self.last_login_date + self.token["refresh_expires_in"]):
                credentials: Mapping[str, str] = {
                    "grant_type": "refresh_token",
                    "client_id": config_env.KEYCLOAK_CLIENT_ID,
                    "client_secret": config_env.KEYCLOAK_CLIENT_SECRET,
                    "refresh_token": self.token["refresh_token"],
                }

                self.token = self.login(credentials)
                return self.token["access_token"]

            else:
                credentials: Mapping[str, str] = {
                    "grant_type": "client_credentials",
                    "client_id": config_env.KEYCLOAK_CLIENT_ID,
                    "client_secret": config_env.KEYCLOAK_CLIENT_SECRET,
                }

                self.token = self.login(credentials)
                return self.token["access_token"]

    def bundle(self, bundle: dict[str, Any]) -> dict[str, Any]:
        access_token = self.get_access_token()

        headers = {
            "Accept": "Application/json+fhir",
            "Authorization": f"Bearer {access_token}",
        }

        return self.http_adapter.post(
            url=f"{config_env.FHIR_URL}/{config_env.FHIR_PARTITION}/",
            headers=headers,
            body=bundle,
        )
