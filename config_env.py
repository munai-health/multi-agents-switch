from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    KEYCLOAK_URL: str = ""
    KEYCLOAK_REALM_ID: str = ""
    KEYCLOAK_CLIENT_ID: str = ""
    KEYCLOAK_CLIENT_SECRET: str = ""

    FHIR_URL: str = ""
    FHIR_PARTITION: str = ""

    OPENAI_API_KEY: str = ""

    PINECONE_API_KEY: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_SESSION_TOKEN: str = ""


config_env = Settings()
