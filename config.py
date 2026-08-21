import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development").lower()


class Config:
    # ============== Flask =================
    SECRET_KEY = os.getenv("SECRET_KEY")
    FLASK_APP = os.getenv("FLASK_APP", "run")

    # ============== Database =================
    DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///database.db"

    # ============= SQLAlchemy ==================
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============== Usuário administrador inicial =================
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    # ============== Dados de exemplo =================
    SEED_DADOS_EXEMPLO = os.getenv("SEED_DADOS_EXEMPLO", "1").lower() in ("1", "true", "yes")


class DevelopmentConfig(Config):
    DEBUG = True
    AUTO_MIGRATE = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    AUTO_MIGRATE = True


class ProductionConfig(Config):
    DEBUG = False
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")
    AUTO_MIGRATE = False
    SEED_DADOS_EXEMPLO = False


def get_config_class():
    mapping = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    if APP_ENV not in mapping:
        raise RuntimeError(
            f"APP_ENV inválido: '{APP_ENV}'. Use: development, testing ou production."
        )
    return mapping[APP_ENV]


if not Config.SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY não definida. Crie um arquivo .env a partir de .env.example "
        "com um valor aleatório para SECRET_KEY."
    )