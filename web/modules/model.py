from datetime import date, datetime, UTC
from decimal import Decimal

from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, func
from werkzeug.security import check_password_hash, generate_password_hash

from web import db


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(120), nullable=False)
    iniciais = db.Column(db.String(5), nullable=False)
    email = db.Column(db.String(150), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    def set_password(self, senha):
        self.password_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.password_hash, senha)

    def __repr__(self):
        return f"<Usuario {self.nome}>"


class Empresa(db.Model):
    __tablename__ = "empresas"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    def __repr__(self):
        return f"<Empresa {self.nome}>"


class EtapaFunil(db.Model):
    __tablename__ = "etapas_funil"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    cor = db.Column(db.String(20), nullable=False)
    largura_pct = db.Column(db.Integer, default=100)
    conversao_pct = db.Column(db.Integer, default=0)
    contatos = db.relationship(
        "Contato",
        back_populates="etapa",
        cascade="all, delete-orphan",
        lazy=True
    )

    @property
    def quantidade(self):
        return (
            db.session.query(func.count(Contato.id))
            .filter(Contato.etapa_id == self.id)
            .scalar()
            or 0
        )

    @property
    def valor_total(self):
        return (
            db.session.query(func.coalesce(func.sum(Contato.valor), 0))
            .filter(Contato.etapa_id == self.id)
            .scalar()
        )

    def __repr__(self):
        return f"<EtapaFunil {self.nome}>"


class Contato(db.Model):
    __tablename__ = "contatos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    empresa = db.Column(db.String(120))
    email = db.Column(db.String(150), unique=True)
    telefone = db.Column(db.String(30))
    valor = db.Column(db.Numeric(10, 2), default=0)
    etapa_id = db.Column(
        db.Integer,
        db.ForeignKey("etapas_funil.id"),
        nullable=False,
        index=True,
    )
    etapa = db.relationship(
        "EtapaFunil",
        back_populates="contatos"
    )

    interacoes = db.relationship(
        "Interacao",
        back_populates="contato",
        cascade="all, delete-orphan",
        order_by="Interacao.data.desc(), Interacao.id.desc()",
    )

    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    @property
    def ultima_interacao(self):
        return self.interacoes[0] if self.interacoes else None

    @property
    def iniciais(self):
        nomes = self.nome.split()

        if len(nomes) == 1:
            return nomes[0][0].upper()

        return (
            nomes[0][0] +
            nomes[-1][0]
        ).upper()

    def __repr__(self):
        return f"<Contato {self.nome}>"


class Interacao(db.Model):
    __tablename__ = "interacoes"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # email | ligacao | nota
    resumo = db.Column(db.String(200))
    data = db.Column(db.Date, nullable=False, default=lambda: date.today())
    contato_id = db.Column(
        db.Integer,
        db.ForeignKey("contatos.id"),
        nullable=False,
        index=True,
    )
    contato = db.relationship("Contato", back_populates="interacoes")
    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    def __repr__(self):
        return f"<Interacao {self.tipo} {self.data}>"


class Tarefa(db.Model):
    __tablename__ = "tarefas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(20), default="tarefa")
    concluida = db.Column(db.Boolean, default=False)
    vencimento = db.Column(db.Date, index=True)
    contato_id = db.Column(
        db.Integer,
        db.ForeignKey("contatos.id"),
        index=True,
    )
    contato = db.relationship("Contato", backref="tarefas")
    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    @property
    def atrasada(self):
        if self.concluida or not self.vencimento:
            return False
        return self.vencimento < date.today()

    @property
    def prazo(self):
        if not self.vencimento:
            return "sem prazo"
        return self.vencimento.strftime("%d/%m/%Y")

    def __repr__(self):
        return f"<Tarefa {self.titulo}>"


class ReceitaMensal(db.Model):
    __tablename__ = "receitas_mensais"
    __table_args__ = (
        UniqueConstraint("ano", "mes", name="uq_receitas_ano_mes"),
    )

    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Numeric(12, 2), nullable=False)
    delta = db.Column(db.Integer, nullable=False)
    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    def __repr__(self):
        return f"<ReceitaMensal {self.mes}/{self.ano}>"


class Automacao(db.Model):
    __tablename__ = "automacoes"

    id = db.Column(db.Integer, primary_key=True)
    gatilho = db.Column(db.String(50), nullable=False)
    acao = db.Column(db.String(50), nullable=False)
    prazo_dias = db.Column(db.Integer, default=0)
    ativa = db.Column(db.Boolean, default=True)
    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    def __repr__(self):
        return f"<Automacao {self.gatilho} -> {self.acao}>"