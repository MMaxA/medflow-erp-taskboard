import os
import secrets

class Settings:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./medflow.db")
    secret_key = os.getenv("SECRET_KEY", "")
    access_token_minutes = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
    cors_origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()]
    bootstrap_admin_email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
    bootstrap_admin_password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
    environment = os.getenv("APP_ENV", "development").lower()
    demo_seed = os.getenv("DEMO_SEED", "false").lower() == "true"

    def validate(self):
        if len(self.secret_key) < 32 or any(marker in self.secret_key.upper() for marker in ("CHANGE", "REPLACE", "EXAMPLE", "PLACEHOLDER")):
            raise RuntimeError("SECRET_KEY must be set to a unique random value of at least 32 characters")
        if not 1 <= self.access_token_minutes <= 1440:
            raise RuntimeError("ACCESS_TOKEN_MINUTES must be between 1 and 1440")
        if self.environment == "production" and self.demo_seed:
            raise RuntimeError("DEMO_SEED cannot be enabled in production")
        if bool(self.bootstrap_admin_email) != bool(self.bootstrap_admin_password):
            raise RuntimeError("Set both BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD, or neither")
        if self.bootstrap_admin_password and len(self.bootstrap_admin_password) < 14:
            raise RuntimeError("BOOTSTRAP_ADMIN_PASSWORD must be at least 14 characters")

settings = Settings()

def validate_settings():
    settings.validate()

def generate_secret_key():
    return secrets.token_urlsafe(48)
