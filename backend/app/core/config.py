"""
Pepper Clinical Infinity V6 — Config
© 2026 Lamya F. H. Ali — All Rights Reserved
"""
import os
from functools import lru_cache


class Settings:
    APP_NAME = "Pepper Clinical Infinity V6"
    APP_VERSION = "6.0.0"
    ENV = os.environ.get("ENV", "development")

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-jwt-change-me")
    JWT_ALG = "HS256"
    ACCESS_MIN = 30
    REFRESH_DAYS = 7
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "dev-enc-key-change-me-32byteslong")

    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/pepper.db")

    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    BCRYPT_ROUNDS = 12
    RATE_LIMIT_PER_MINUTE = 60

    @property
    def is_production(self):
        return self.ENV == "production"

    @property
    def origins_list(self):
        return os.environ.get("ALLOWED_ORIGINS", "*").split(",")

    @property
    def hosts_list(self):
        return os.environ.get("ALLOWED_HOSTS", "*").split(",")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
