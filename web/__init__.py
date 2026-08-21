import logging
import os
from datetime import datetime

from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy.exc import OperationalError

import config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()

ETAPAS_DEFAULT = [
    {"nome": "Prospecção", "ordem": 1, "cor": "blue", "largura_pct": 100, "conversao_pct": 0},
    {"nome": "Qualificação", "ordem": 2, "cor": "amber", "largura_pct": 80, "conversao_pct": 25},
    {"nome": "Fechamento", "ordem": 3, "cor": "green", "largura_pct": 55, "conversao_pct": 50},
    {"nome": "Pós-venda", "ordem": 4, "cor": "violet", "largura_pct": 35, "conversao_pct": 80},
]

DADOS_EXEMPLO_RECEITAS = [
    (1, 52000, 4),
    (2, 58000, 12),
    (3, 61000, 5),
    (4, 65500, 7),
    (5, 72000, 10),
    (6, 79000, 9),
]

DADOS_EXEMPLO_CONTATOS = [
    ("Ana Ribeiro", "TechNova", "ana@technova.com", "Prospecção", 12000),
    ("Bruno Castro", "MercadoAzul", "bruno@mercadoazul.com", "Qualificação", 8500),
    ("Carla Mendes", "Inovatech", "carla@inovatech.com", "Fechamento", 23000),
    ("Diego Farias", "BetaCorp", "diego@betacorp.com", "Pós-venda", 9900),
]


def _aplicar_migracoes(app):
    if not app.config.get("AUTO_MIGRATE", False):
        return
    diretorio = os.path.join(app.root_path, "..", "migrations")
    if not os.path.isdir(diretorio):
        return
    from flask_migrate import upgrade
    upgrade(directory=diretorio)


def _seed_etapas(app):
    from web.modules.model import EtapaFunil

    try:
        if EtapaFunil.query.count() == 0:
            db.session.add_all(EtapaFunil(**etapa) for etapa in ETAPAS_DEFAULT)
            db.session.commit()
    except OperationalError:
        print("[aviso] Tabelas ainda não criadas. Execute 'flask db upgrade'.")


def _seed_admin(app):
    from web.modules.model import Usuario

    email = app.config.get("ADMIN_EMAIL")
    senha = app.config.get("ADMIN_PASSWORD")

    if not (email and senha):
        return

    try:
        if Usuario.query.filter_by(email=email).first():
            return

        if Usuario.query.count() == 0:
            admin = Usuario(nome="Administrador", iniciais="AD", email=email)
            admin.set_password(senha)
            db.session.add(admin)
            db.session.commit()
    except OperationalError:
        print("[aviso] Tabelas ainda não criadas. Execute 'flask db upgrade'.")


def _seed_dados_exemplo(app):
    if not app.config.get("SEED_DADOS_EXEMPLO", False):
        return

    from web.modules.model import (
        Contato,
        Empresa,
        EtapaFunil,
        Interacao,
        ReceitaMensal,
        Tarefa,
    )

    try:
        if Contato.query.count() > 0 or ReceitaMensal.query.count() > 0:
            return

        db.session.add(Empresa(nome="TechNova Ltda"))

        for mes, valor, delta in DADOS_EXEMPLO_RECEITAS:
            db.session.add(ReceitaMensal(ano=2026, mes=mes, valor=valor, delta=delta))

        etapas = {etapa.nome: etapa for etapa in EtapaFunil.query.all()}
        for nome, empresa, email, etapa_nome, valor in DADOS_EXEMPLO_CONTATOS:
            db.session.add(
                Contato(
                    nome=nome,
                    empresa=empresa,
                    email=email,
                    valor=valor,
                    etapa=etapas[etapa_nome],
                )
            )

        db.session.flush()

        ana = Contato.query.filter_by(email="ana@technova.com").first()
        bruno = Contato.query.filter_by(email="bruno@mercadoazul.com").first()

        if ana:
            db.session.add_all([
                Interacao(contato=ana, tipo="email", resumo="Proposta enviada", data=datetime(2026, 6, 10).date()),
                Interacao(contato=ana, tipo="ligacao", resumo="Aguardando retorno do cliente", data=datetime(2026, 6, 15).date()),
                Tarefa(titulo="Follow-up com Ana", tipo="tarefa", vencimento=datetime(2026, 6, 22).date(), contato=ana),
            ])

        if bruno:
            db.session.add_all([
                Interacao(contato=bruno, tipo="ligacao", resumo="Primeiro contato", data=datetime(2026, 6, 12).date()),
                Tarefa(titulo="Enviar orçamento para Bruno", tipo="lembrete", vencimento=datetime(2026, 6, 20).date(), contato=bruno),
            ])

        db.session.commit()
    except OperationalError:
        print("[aviso] Tabelas ainda não criadas. Execute 'flask db upgrade'.")


def _definir_empresa(app):
    from web.modules.model import Empresa

    empresa = Empresa.query.first()
    app.config["EMPRESA_NOME"] = empresa.nome if empresa else "Painel Comercial"


def _configurar_logging(app):
    nivel = logging.DEBUG if app.debug else logging.INFO

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    handler.setLevel(nivel)

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(nivel)

    @app.after_request
    def _log_requisicao(response):
        app.logger.info("%s %s -> %s", request.method, request.path, response.status_code)
        return response


def create_app():
    app = Flask(__name__)

    app.config.from_object(config.get_config_class())

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    from web.routes.main_routes import main_bp
    from web.modules import model  # noqa: F401  garante que todos os modelos sejam registrados

    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    app.register_blueprint(main_bp)

    from web.modules.model import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(Usuario, int(user_id))
        except (ValueError, TypeError):
            return None

    @app.errorhandler(404)
    def not_found(error):
        return (
            render_template("main/erro.html", codigo=404, mensagem="Página não encontrada."),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error("Erro interno: %s", error, exc_info=True)
        return (
            render_template("main/erro.html", codigo=500, mensagem="Erro interno do servidor."),
            500,
        )

    @app.context_processor
    def contexto_global():
        return {
            "empresa_nome": app.config.get("EMPRESA_NOME", "Painel Comercial"),
            "data_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    _configurar_logging(app)

    with app.app_context():
        _aplicar_migracoes(app)
        _seed_etapas(app)
        _seed_admin(app)
        _seed_dados_exemplo(app)
        _definir_empresa(app)

    app.logger.info("Aplicação iniciada (APP_ENV=%s)", config.APP_ENV)

    return app