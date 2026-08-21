from sqlalchemy.exc import IntegrityError

from web import db
from web.modules.model import Contato, ReceitaMensal, Usuario
from web.services.funil import dados_funil


def test_usuario_check_password(app_ctx):
    usuario = Usuario.query.filter_by(email="admin@crm.local").first()
    assert usuario is not None
    assert usuario.check_password("crm-dev-2026")
    assert not usuario.check_password("senha-errada")
    assert usuario.iniciais == "AD"


def test_receita_unicidade_ano_mes(app_ctx):
    duplicata = ReceitaMensal(ano=2026, mes=1, valor=99999, delta=0)
    db.session.add(duplicata)
    try:
        db.session.commit()
        raise AssertionError("Duplicata de (ano, mes) deveria falhar")
    except IntegrityError:
        db.session.rollback()


def test_contato_ultima_interacao(app_ctx):
    contato = Contato.query.filter_by(nome="Ana Ribeiro").first()
    assert contato.ultima_interacao is not None
    assert contato.ultima_interacao.tipo == "ligacao"


def test_funil_agregado(app_ctx):
    funil = dados_funil()
    total_contatos = Contato.query.count()
    assert sum(etapa["quantidade"] for etapa in funil) == total_contatos


def test_contato_sem_interacao(app_ctx):
    contato = Contato.query.filter_by(nome="Carla Mendes").first()
    assert contato.interacoes == []