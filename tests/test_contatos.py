from web import db
from web.modules.model import Contato


def test_seed_contatos(app_ctx):
    nomes = {c.nome for c in Contato.query.all()}
    assert {"Ana Ribeiro", "Bruno Castro", "Carla Mendes", "Diego Farias"} <= nomes


def test_criar_contato(autenticado, app_ctx):
    resposta = autenticado.post(
        "/contato/novo",
        data={
            "nome": "Ester Lima",
            "empresa": "Solaris",
            "email": "ester@example.com",
            "etapa": "Qualificação",
        },
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert Contato.query.filter_by(email="ester@example.com").first() is not None

    Contato.query.filter_by(email="ester@example.com").delete()
    db.session.commit()


def test_contato_sem_nome_rejeitado(autenticado, app_ctx):
    total = Contato.query.count()
    resposta = autenticado.post(
        "/contato/novo",
        data={"nome": "", "empresa": "X", "etapa": "Qualificação"},
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert "obrigatório" in resposta.get_data(as_text=True)
    assert Contato.query.count() == total


def test_contato_email_duplicado_rejeitado(autenticado):
    resposta = autenticado.post(
        "/contato/novo",
        data={"nome": "Duplicado", "email": "ana@technova.com", "etapa": "Prospecção"},
        follow_redirects=True,
    )
    assert "Já existe um contato" in resposta.get_data(as_text=True)


def test_contato_etapa_inexistente_cai_na_primeira(autenticado, app_ctx):
    total = Contato.query.count()
    resposta = autenticado.post(
        "/contato/novo",
        data={"nome": "Etapa Inválida", "empresa": "X", "etapa": "Inexistente"},
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert Contato.query.count() == total + 1
    novo = Contato.query.filter_by(nome="Etapa Inválida").first()
    assert novo.etapa.nome == "Prospecção"

    Contato.query.filter_by(nome="Etapa Inválida").delete()
    db.session.commit()