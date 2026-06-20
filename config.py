import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BOGOTA_OFFSET = timedelta(hours=-5)


def bogota_now() -> datetime:
    return datetime.utcnow() + BOGOTA_OFFSET

DB_HOST = os.getenv("DB_HOST", "aws-1-us-west-2.pooler.supabase.com")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres.bfpxpvophaixbvvluxaq")
DB_PASSWORD = os.getenv("DB_PASSWORD", "bXo76SLW1sozXDmY")
DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_change_in_production_2026")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
