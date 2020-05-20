from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    pg_dsn: str

    class Config:
        env_file = ".env"


async def main():
    settings = Settings()
    print(settings)
