from web import create_app


def test_pagina_login_acessivel(client):
    resposta = client.get("/login")
    assert resposta.status_code == 200
    assert "CRM" in resposta.get_data(as_text=True)


def test_login_credenciais_incorretas(client):
    resposta = client.post(
        "/login",
        data={"email": "admin@crm.local", "senha": "senha-errada"},
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert "E-mail ou senha inválidos" in resposta.get_data(as_text=True)


def test_login_correto_redireciona(client):
    resposta = client.post(
        "/login",
        data={"email": "admin@crm.local", "senha": "crm-dev-2026"},
        follow_redirects=False,
    )
    assert resposta.status_code == 302
    assert "/" in resposta.headers["Location"]


def test_rota_protegida_exige_login(client):
    resposta = client.get("/")
    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_logout(client):
    client.post(
        "/login",
        data={"email": "admin@crm.local", "senha": "crm-dev-2026"},
    )
    resposta = client.post("/logout", follow_redirects=False)
    assert resposta.status_code == 302

    pagina = client.get("/")
    assert pagina.status_code == 302
    assert "/login" in pagina.headers["Location"]


def test_csrf_ativo_rejeita_post_sem_token():
    app_csrf = create_app()
    app_csrf.config["WTF_CSRF_ENABLED"] = True
    cliente = app_csrf.test_client()
    resposta = cliente.post("/logout")
    assert resposta.status_code == 400