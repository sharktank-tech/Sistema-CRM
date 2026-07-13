from flask import Blueprint, render_template, redirect,request, url_for
from web.modules.model import *
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

# ====== Principal =======

# ===== Rota principal dashboard
@main_bp.route('/')
def dashboard():
    empresa_nome = Empresa.query.all()
    usuario = current_user
    periodo_funil = "Junho 2026"
    funil = EtapaFunil.query.all()
    metricas = ReceitaMensal.query.all()
    contatos = Contato.query.all()
    tarefas = Tarefa.query.all()
    grafico_funil = {
        "labels": ["Prospecção", "Qualificação", "Fechamento"],
        "valores": [50, 40, 24]
    },
    grafico_receita = {
        "labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        "valores": [5000, 7000, 10000, 13000, 15000, 18000]
    },
    data_atualizacao = "18/06/2026"

    return render_template(
        "main/dashboard.html",
        empresa=empresa_nome,
        usuario=usuario,
        periodo_funil=periodo_funil,
        contatos=contatos,
        funil=funil,
        metricas=metricas,
        grafico_receita=grafico_receita,
        data_atualizacao=data_atualizacao,
        tarefas=tarefas,
        grafico_funil=grafico_funil
    )

# Rota para buscar informações par ao front-end
@main_bp.route('/buscar')
def buscar():
    termo = request.args.get('q')
    return render_template('main/resultado.html')

# ===== Contato =====

# Rota para contato
@main_bp.route('/contato/<contato_id>')
def contato_detalhe(contato_id):
    # consultar banco
    info_contatos  = Contato
    print(info_contatos)
    return render_template(
        "contato.html",
        contato={info_contatos},
    )

# Rota para criar o contato
@main_bp.route("/contato/novo", methods=["POST"])
def criar_contato():
    nome = request.form["nome"]
    empresa = request.form["empresa"]
    email = request.form["email"]
    telefone = request.form["telefone"]
    etapa = request.form["etapa"]

    # salvar no banco

    return redirect(url_for("main.dashboard"))

# ===== Automação =====

# Rota para criação de uma nova automação
@main_bp.route("/automacao/nova", methods=["POST"])
def criar_automacao():
    gatilho = request.form["gatilho"]
    acao = request.form["acao"]
    prazo_dias = request.form["prazo_dias"]

    # salvar no banco

    return redirect(url_for("main/dashboard"))

# ==== Tarefas ====

# Rota para adicionar tarefa
@main_bp.route("/tarefas")
def listar_tarefas():
    return render_template("tarefa/tarefas.html")

# Rota para criar tarefa
@main_bp.route("/tarefas/nova", methods=["POST"])
def criar_tarefa():
    return redirect(url_for("listar_tarefas"))

# Rota para conclusão de terefas
@main_bp.route("/tarefas/<int:id>/concluir")
def concluir_tarefa(id):
    return redirect(url_for("main/dashboard"))