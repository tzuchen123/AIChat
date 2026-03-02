from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PORT: int = 8000
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "ai_chat_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    JWT_SECRET: str = "your_secret_key"
    JWT_EXPIRES_DAYS: int = 7
    OPENAI_API_KEY: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
