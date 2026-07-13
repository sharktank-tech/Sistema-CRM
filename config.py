import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    # ============== Flask =================
    SECRET_KEY = os.getenv("SECRET_KEY", "rjh393sn1958ffn")
    FLASK_APP = os.getenv("SECRET_KEY", "run")

    # ============== Database =================
    DATABASE_URL = os.getenv("DATABASE_URL") or 'sqlite:///database.db'

    # ============= SQLAlchemy ==================
    SQLALCHEMY_DATABASE_URI = (
        DATABASE_URL
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False