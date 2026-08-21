from decimal import Decimal

from sqlalchemy import func

from web import db
from web.modules.model import Contato, EtapaFunil


def dados_funil():
    funil = EtapaFunil.query.order_by(EtapaFunil.ordem).all()

    linhas = db.session.query(
        Contato.etapa_id,
        func.count(Contato.id),
        func.coalesce(func.sum(Contato.valor), 0),
    ).group_by(Contato.etapa_id).all()
    agregados = {etapa_id: (qtd, valor) for etapa_id, qtd, valor in linhas}

    dados = []
    for etapa in funil:
        qtd, valor = agregados.get(etapa.id, (0, Decimal("0")))
        dados.append({
            "nome": etapa.nome,
            "cor": etapa.cor,
            "largura_pct": etapa.largura_pct,
            "conversao_pct": etapa.conversao_pct,
            "quantidade": qtd,
            "valor_total": valor,
        })
    return dados


def grafico_funil(dados):
    return {
        "labels": [etapa["nome"] for etapa in dados],
        "valores": [etapa["quantidade"] for etapa in dados],
    }