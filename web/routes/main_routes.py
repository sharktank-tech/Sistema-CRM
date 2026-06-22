from flask import Blueprint, render_template, redirect,request, url_for

main_bp = Blueprint('main', __name__)

# ====== Principal =======

# ===== Rota principal dashboard
@main_bp.route('/')
def dashboard():
    return render_template(
        "main/dashboard.html",

        empresa_nome="Minha Empresa",
        usuario={
            "nome": "Danilo",
            "iniciais": "DC"
        },

        periodo_funil="Junho 2026",

        funil=[
            {
                "nome": "Prospecção",
                "quantidade": 50,
                "valor_total": "35.000",
                "largura_pct": 100,
                "cor": "blue",
                "conversao_pct": 80
            },
            {
                "nome": "Qualificação",
                "quantidade": 40,
                "valor_total": "28.000",
                "largura_pct": 80,
                "cor": "amber",
                "conversao_pct": 60
            },
            {
                "nome": "Fechamento",
                "quantidade": 24,
                "valor_total": "18.000",
                "largura_pct": 50,
                "cor": "green",
                "conversao_pct": 0
            }
        ],

        metricas=[
            {
                "label": "Receita",
                "valor": "R$ 18.000",
                "delta": 12
            },
            {
                "label": "Novos contatos",
                "valor": 50,
                "delta": 8
            },
            {
                "label": "Conversões",
                "valor": 24,
                "delta": -3
            },
            {
                "label": "Ticket médio",
                "valor": "R$ 750",
                "delta": 5
            }
        ],

        contatos=[],
        tarefas=[],

        grafico_funil={
            "labels": ["Prospecção", "Qualificação", "Fechamento"],
            "valores": [50, 40, 24]
        },

        grafico_receita={
            "labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
            "valores": [5000, 7000, 10000, 13000, 15000, 18000]
        },

        data_atualizacao="18/06/2026"
    )

# Rota para buscar informações par ao front-end
@main_bp.route('/buscar')
def buscar():
    termo = request.args.get('q')
    return render_template('main/resultado.html')

# ===== Contato =====

# Rota para contato
@main_bp.route('/contato/<id>')
def contato_detalhe(contato_id):
    # consultar banco
    return render_template(
        "contato.html",
        contato={}
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

    return redirect(url_for("dashboard"))

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