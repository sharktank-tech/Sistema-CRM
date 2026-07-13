from datetime import datetime, UTC
from decimal import Decimal

from web import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(120), nullable=False)
    iniciais = db.Column(db.String(5), nullable=False)

    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

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
        return len(self.contatos)

    @property
    def valor_total(self):
        return sum(
            (contato.valor or Decimal("0"))
            for contato in self.contatos
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
    ultima_interacao = db.Column(db.Date)
    etapa_id = db.Column(
        db.Integer,
        db.ForeignKey("etapas_funil.id"),
        nullable=False
    )
    etapa = db.relationship(
        "EtapaFunil",
        back_populates="contatos"
    )

    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

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


class Tarefa(db.Model):
    __tablename__ = "tarefas"

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)

    concluida = db.Column(db.Boolean, default=False)

    vencimento = db.Column(db.Date)

    contato_id = db.Column(
        db.Integer,
        db.ForeignKey("contatos.id")
    )

    contato = db.relationship("Contato")

    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    def __repr__(self):
        return f"<Tarefa {self.titulo}>"


class ReceitaMensal(db.Model):
    __tablename__ = "receitas_mensais"

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