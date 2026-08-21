from web.modules.model import ReceitaMensal


def _formatar_valor_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def dados_metricas():
    receitas = ReceitaMensal.query.order_by(
        ReceitaMensal.ano, ReceitaMensal.mes
    ).all()

    metricas = [
        {
            "label": f"Receita {r.mes:02d}/{r.ano}",
            "valor": _formatar_valor_br(r.valor),
            "delta": r.delta,
        }
        for r in receitas
    ]

    grafico = {
        "labels": [f"{r.mes:02d}/{r.ano}" for r in receitas],
        "valores": [float(r.valor) for r in receitas],
    }

    return metricas, grafico