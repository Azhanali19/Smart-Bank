# app/config.py
# Simple config loader using python-dotenv + os.getenv so this works regardless of pydantic version.

import os
from dotenv import load_dotenv

# load .env from project root if present
load_dotenv()

class Settings:
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "SmartBank")

    # JWT / auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "6f8a2d1e4b9c3f5a7d8e6f2a1b4c3d5e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))

    # FastAPI / misc
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

# single settings instance used across the app
settings = Settings()
