from web import db
from web.modules.model import Tarefa


def test_listar_tarefas(autenticado):
    html = autenticado.get("/tarefas").get_data(as_text=True)
    assert "Follow-up com Ana" in html


def test_criar_tarefa(autenticado, app_ctx):
    resposta = autenticado.post(
        "/tarefas/nova",
        data={"titulo": "Tarefa de teste", "tipo": "lembrete", "descricao": ""},
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert Tarefa.query.filter_by(titulo="Tarefa de teste").first() is not None

    Tarefa.query.filter_by(titulo="Tarefa de teste").delete()
    db.session.commit()


def test_criar_tarefa_sem_titulo_rejeitado(autenticado, app_ctx):
    total = Tarefa.query.count()
    resposta = autenticado.post(
        "/tarefas/nova",
        data={"titulo": ""},
        follow_redirects=True,
    )
    assert "obrigatório" in resposta.get_data(as_text=True)
    assert Tarefa.query.count() == total


def test_concluir_tarefa(autenticado, app_ctx):
    tarefa = Tarefa.query.first()
    assert tarefa is not None

    resposta = autenticado.get(f"/tarefas/{tarefa.id}/concluir", follow_redirects=True)
    assert resposta.status_code == 200
    assert Tarefa.query.get(tarefa.id).concluida is True

    Tarefa.query.get(tarefa.id).concluida = False
    db.session.commit()