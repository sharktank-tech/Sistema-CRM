from web import db
from web.modules.model import Contato, Interacao


def test_pagina_contato(autenticado, app_ctx):
    contato = Contato.query.filter_by(nome="Ana Ribeiro").first()
    resposta = autenticado.get(f"/contato/{contato.id}")
    assert resposta.status_code == 200
    assert "Ana Ribeiro" in resposta.get_data(as_text=True)


def test_criar_interacao(autenticado, app_ctx):
    contato = Contato.query.filter_by(nome="Carla Mendes").first()
    resposta = autenticado.post(
        f"/contato/{contato.id}/interacao/nova",
        data={"tipo": "nota", "resumo": "Ligação agendada", "data": ""},
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert "Ligação agendada" in resposta.get_data(as_text=True)

    Interacao.query.filter_by(contato_id=contato.id, resumo="Ligação agendada").delete()
    db.session.commit()


def test_interacao_vira_ultima_no_dashboard(autenticado, app_ctx):
    contato = Contato.query.filter_by(nome="Carla Mendes").first()
    autenticado.post(
        f"/contato/{contato.id}/interacao/nova",
        data={"tipo": "ligacao", "resumo": "Contato recente", "data": ""},
        follow_redirects=True,
    )
    html = autenticado.get("/").get_data(as_text=True)
    assert "Contato recente" in html

    Interacao.query.filter_by(contato_id=contato.id, resumo="Contato recente").delete()
    db.session.commit()


def test_interacao_sem_resumo_rejeitada(autenticado, app_ctx):
    contato = Contato.query.filter_by(nome="Carla Mendes").first()
    total = Interacao.query.count()
    resposta = autenticado.post(
        f"/contato/{contato.id}/interacao/nova",
        data={"tipo": "email", "resumo": "", "data": ""},
        follow_redirects=True,
    )
    assert "Informe um resumo" in resposta.get_data(as_text=True)
    assert Interacao.query.count() == total


def test_interacao_tipo_invalido_rejeitada(autenticado, app_ctx):
    contato = Contato.query.filter_by(nome="Carla Mendes").first()
    total = Interacao.query.count()
    resposta = autenticado.post(
        f"/contato/{contato.id}/interacao/nova",
        data={"tipo": "fax", "resumo": "Tipo errado", "data": ""},
        follow_redirects=True,
    )
    assert "Tipo de interação inválido" in resposta.get_data(as_text=True)
    assert Interacao.query.count() == total


def test_interacao_data_invalida_rejeitada(autenticado, app_ctx):
    contato = Contato.query.filter_by(nome="Carla Mendes").first()
    total = Interacao.query.count()
    resposta = autenticado.post(
        f"/contato/{contato.id}/interacao/nova",
        data={"tipo": "email", "resumo": "Data errada", "data": "31/02/2026"},
        follow_redirects=True,
    )
    assert "Data da interação inválida" in resposta.get_data(as_text=True)
    assert Interacao.query.count() == total