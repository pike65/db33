from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL_ENV: str | None = Field(default=None, validation_alias="DATABASE_URL")

    POSTGRES_USER: str = "neo"
    POSTGRES_PASSWORD: str = "believe123"
    POSTGRES_DB: str = "db3_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_ENV:
            url = self.DATABASE_URL_ENV
            for prefix in ("postgres://", "postgresql://"):
                if url.startswith(prefix):
                    return "postgresql+psycopg2://" + url[len(prefix) :]
            return url
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
