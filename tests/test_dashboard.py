from web.modules.model import ReceitaMensal
from web.services.funil import dados_funil, grafico_funil
from web.services.metricas import dados_metricas


def test_dashboard_200(autenticado):
    resposta = autenticado.get("/")
    assert resposta.status_code == 200


def test_dashboard_monta_conteudo(autenticado):
    html = autenticado.get("/").get_data(as_text=True)
    assert "Funil de vendas" in html
    assert "TechNova Ltda" in html
    assert "id=\"dados-graficos\"" in html
    assert "/static/css/dashboard.css" in html
    assert "/static/js/dashboard.js" in html


def test_funil_quatro_etapas(app_ctx):
    funil = dados_funil()
    assert len(funil) == 4
    assert funil[0]["nome"] == "Prospecção"


def test_funil_agregacoes(app_ctx):
    funil = dados_funil()
    por_nome = {etapa["nome"]: etapa for etapa in funil}
    assert por_nome["Prospecção"]["quantidade"] == 1
    assert por_nome["Prospecção"]["valor_total"] == 12000


def test_grafico_funil(app_ctx):
    funil = dados_funil()
    grafico = grafico_funil(funil)
    assert len(grafico["labels"]) == 4
    assert len(grafico["valores"]) == 4


def test_metricas_seis_meses(app_ctx):
    metricas, grafico = dados_metricas()
    assert ReceitaMensal.query.count() == 6
    assert len(metricas) == 6
    assert metricas[0]["label"] == "Receita 01/2026"
    assert metricas[0]["valor"].startswith("R$ 52.000,00")
    assert len(grafico["labels"]) == 6


def test_buscar_json(autenticado):
    resposta = autenticado.get("/buscar?q=ana&formato=json")
    dados = resposta.get_json()
    assert resposta.status_code == 200
    assert dados["total"] == 1
    assert dados["resultados"][0]["nome"] == "Ana Ribeiro"


def test_buscar_json_sem_resultado(autenticado):
    resposta = autenticado.get("/buscar?q=zzzz&formato=json")
    dados = resposta.get_json()
    assert dados["total"] == 0
    assert dados["resultados"] == []


def test_buscar_html(autenticado):
    resposta = autenticado.get("/buscar?q=ana")
    assert resposta.status_code == 200
    assert "Ana Ribeiro" in resposta.get_data(as_text=True)