import os

os.environ.setdefault("APP_ENV", "testing")
os.environ["DATABASE_URL"] = "sqlite:////home/opencode/work/test_pytest.db"
os.environ.setdefault("SECRET_KEY", "teste-secreto")
os.environ.setdefault("ADMIN_EMAIL", "admin@crm.local")
os.environ.setdefault("ADMIN_PASSWORD", "crm-dev-2026")

import pytest

from web import create_app

BANCO = "/home/opencode/work/test_pytest.db"

ADMIN_EMAIL = os.environ["ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]


@pytest.fixture(scope="session")
def app():
    if os.path.exists(BANCO):
        os.remove(BANCO)
    application = create_app()
    yield application


@pytest.fixture()
def app_ctx(app):
    with app.app_context():
        yield


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def autenticado(client):
    resposta = client.post(
        "/login",
        data={"email": ADMIN_EMAIL, "senha": ADMIN_PASSWORD},
        follow_redirects=False,
    )
    assert resposta.status_code == 302, "Login do admin deve redirecionar"
    return client