from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    session_secret: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30
    database_url: str
    frontend_url: str
    google_client_id: str
    google_client_secret: str
    deployment_type: str

    class Config:
        env_file = ".env"


settings = Settings()  # ty:ignore[missing-argument]
