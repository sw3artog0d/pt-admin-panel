from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    
    DB_URL: str = 'sqlite:///./instance/database.db'

    ITEMS_PER_PAGE: int = 10

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()