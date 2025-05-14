from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Glucova API"
    admin_email: str = "glucova@upc.edu.com"

    class Config:
        env_file = ".env"

settings = Settings()