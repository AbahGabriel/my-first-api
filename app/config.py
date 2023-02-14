from pydantic import BaseSettings

class Settings(BaseSettings):
    database_host_server: str
    database_username: str
    database_password: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expires_in: int

    class Config():
        env_file = '.env'

settings = Settings()