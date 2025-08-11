from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    NBQUEUE_SERVER: str = "localhost:50051"
    NBQUEUE_LOG_FILE_PATH: str = "logs/mpi_job_launcher.log"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global
settings = Settings()