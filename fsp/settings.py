from pydantic import BaseSettings


class Settings(BaseSettings):
    secret: str
    flask_app: str = "./fsp/app.py"
    token_expiration_time_sec: int = 604800
    database_driver: str = "psycopg2"
    database_dialect: str = "postgresql"
    database_admin_username: str = "postgres"
    database_admin_password: str = "password"
    database_url: str = "localhost"
    database_name: str = "postgres"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()
