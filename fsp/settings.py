from pydantic import BaseSettings

class Settings(BaseSettings):
    secret: str
    flask_app: str = './fsp/app.py'
    database_driver: str = 'psycopg2'
    database_dialect: str = 'postgresql'
    database_admin_username: str = 'postgres'
    database_admin_password: str = 'password'
    database_url: str = 'localhost'
    database_name: str = 'postgres'

config = Settings()

print(f'Config: {config}')