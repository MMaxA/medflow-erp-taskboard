import os
class Settings:
    database_url=os.getenv("DATABASE_URL","sqlite:///./medflow.db")
    secret_key=os.getenv("SECRET_KEY","CHANGE_ME_FOR_LOCAL_DEMO_ONLY_32_CHARS_MIN")
    access_token_minutes=int(os.getenv("ACCESS_TOKEN_MINUTES","480"))
    cors_origins=os.getenv("CORS_ORIGINS","http://localhost:5173,http://127.0.0.1:5173").split(",")
settings=Settings()
