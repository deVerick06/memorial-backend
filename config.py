from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()