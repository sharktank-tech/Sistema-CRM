from datetime import date, datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.orm import joinedload

from web import db, limiter
from web.modules.model import (
    Automacao,
    Contato,
    EtapaFunil,
    Interacao,
    Tarefa,
    Usuario,
)
from web.services.busca import buscar_contatos, serializar_contato
from web.services.funil import dados_funil, grafico_funil
from web.services.metricas import dados_metricas

main_bp = Blueprint('main', __name__)


# ====== Autenticação =======

@main_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    erro = None
    if request.method == "POST":
        email = (request.form.get("email") or '').strip().lower()
        senha = request.form.get("senha") or ''

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_password(senha):
            login_user(usuario)
            proxima = request.args.get("next")
            if proxima and not proxima.startswith(("/", "http://", "https://")):
                proxima = None
            return redirect(proxima or url_for("main.dashboard"))

        erro = "E-mail ou senha inválidos."

    return render_template("main/login.html", erro=erro)


@main_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("main.login"))


# ====== Principal =======

@main_bp.route('/')
@login_required
def dashboard():
    funil = dados_funil()
    metricas, grafico_receita = dados_metricas()

    contatos = Contato.query.options(
        joinedload(Contato.etapa),
        joinedload(Contato.interacoes),
    ).all()
    tarefas = Tarefa.query.order_by(Tarefa.criado_em.desc()).all()

    return render_template(
        "main/dashboard.html",
        contatos=contatos,
        funil=funil,
        metricas=metricas,
        grafico_funil=grafico_funil(funil),
        grafico_receita=grafico_receita,
        tarefas=tarefas,
    )


@main_bp.route('/buscar')
@login_required
def buscar():
    termo = request.args.get('q') or ''
    resultados = buscar_contatos(termo)

    if request.args.get('formato') == 'json':
        return jsonify({
            "termo": termo,
            "total": len(resultados),
            "resultados": [serializar_contato(c) for c in resultados],
        })

    return render_template(
        'main/resultado.html',
        termo=termo,
        resultados=resultados,
    )


# ===== Contato =====

@main_bp.route('/contato/<int:contato_id>')
@login_required
def contato_detalhe(contato_id):
    contato = Contato.query.options(
        joinedload(Contato.interacoes)
    ).get_or_404(contato_id)
    tarefas = Tarefa.query.filter_by(contato_id=contato_id).all()
    return render_template(
        "main/contato.html",
        contato=contato,
        tarefas=tarefas,
        interacoes=contato.interacoes,
    )


@main_bp.route("/contato/<int:contato_id>/interacao/nova", methods=["POST"])
@login_required
def criar_interacao(contato_id):
    contato = Contato.query.get_or_404(contato_id)

    tipo = request.form.get("tipo")
    resumo = (request.form.get("resumo") or '').strip()
    data_raw = request.form.get("data")

    if tipo not in ("email", "ligacao", "nota"):
        flash("Tipo de interação inválido.", "error")
        return redirect(url_for("main.contato_detalhe", contato_id=contato.id))

    if not resumo:
        flash("Informe um resumo da interação.", "error")
        return redirect(url_for("main.contato_detalhe", contato_id=contato.id))

    data = date.today()
    if data_raw:
        try:
            data = datetime.strptime(data_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Data da interação inválida.", "error")
            return redirect(url_for("main.contato_detalhe", contato_id=contato.id))

    interacao = Interacao(contato=contato, tipo=tipo, resumo=resumo, data=data)
    db.session.add(interacao)
    db.session.commit()
    flash("Interação registrada com sucesso.", "success")
    return redirect(url_for("main.contato_detalhe", contato_id=contato.id))


@main_bp.route("/contato/novo", methods=["POST"])
@login_required
def criar_contato():
    nome = (request.form.get("nome") or '').strip()
    empresa = (request.form.get("empresa") or '').strip()
    email = (request.form.get("email") or '').strip()
    telefone = (request.form.get("telefone") or '').strip()
    etapa_nome = request.form.get("etapa")

    if not nome:
        flash("O nome do contato é obrigatório.", "error")
        return redirect(url_for("main.dashboard", _anchor="contatos"))

    if email and Contato.query.filter_by(email=email).first():
        flash("Já existe um contato cadastrado com este e-mail.", "error")
        return redirect(url_for("main.dashboard", _anchor="contatos"))

    etapa = (
        EtapaFunil.query.filter_by(nome=etapa_nome).first()
        or EtapaFunil.query.order_by(EtapaFunil.ordem).first()
    )
    if not etapa:
        flash("Não há etapas configuradas. Configure o funil primeiro.", "error")
        return redirect(url_for("main.dashboard", _anchor="contatos"))

    contato = Contato(
        nome=nome,
        empresa=empresa or None,
        email=email or None,
        telefone=telefone or None,
        etapa_id=etapa.id,
    )
    db.session.add(contato)
    db.session.commit()
    flash(f"Contato \"{contato.nome}\" criado com sucesso.", "success")
    return redirect(url_for("main.dashboard", _anchor="contatos"))


# ===== Automação =====

@main_bp.route("/automacao/nova", methods=["POST"])
@login_required
def criar_automacao():
    gatilho = request.form.get("gatilho")
    acao = request.form.get("acao")
    prazo_dias = request.form.get("prazo_dias") or 0

    if not gatilho or not acao:
        flash("Informe o gatilho e a ação da automação.", "error")
        return redirect(url_for("main.dashboard"))

    try:
        prazo_dias = int(prazo_dias)
    except (TypeError, ValueError):
        prazo_dias = 0

    automacao = Automacao(
        gatilho=gatilho,
        acao=acao,
        prazo_dias=prazo_dias,
    )
    db.session.add(automacao)
    db.session.commit()
    flash("Automação criada com sucesso.", "success")
    return redirect(url_for("main.dashboard"))


# ===== Tarefas =====

@main_bp.route("/tarefas")
@login_required
def listar_tarefas():
    tarefas = Tarefa.query.order_by(Tarefa.vencimento).all()
    return render_template("main/tarefas.html", tarefas=tarefas)


@main_bp.route("/tarefas/nova", methods=["POST"])
@login_required
def criar_tarefa():
    titulo = (request.form.get("titulo") or '').strip()
    descricao = (request.form.get("descricao") or '').strip()
    tipo = request.form.get("tipo") or "tarefa"
    vencimento_raw = request.form.get("vencimento")
    contato_id = request.form.get("contato_id")

    if not titulo:
        flash("O título da tarefa é obrigatório.", "error")
        return redirect(url_for("main.dashboard", _anchor="tarefas"))

    vencimento = None
    if vencimento_raw:
        try:
            vencimento = datetime.strptime(vencimento_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Data de vencimento inválida.", "error")
            return redirect(url_for("main.dashboard", _anchor="tarefas"))

    try:
        contato_id = int(contato_id) if contato_id else None
    except (TypeError, ValueError):
        contato_id = None

    tarefa = Tarefa(
        titulo=titulo,
        descricao=descricao or None,
        tipo=tipo if tipo in ("tarefa", "lembrete", "automacao") else "tarefa",
        vencimento=vencimento,
        contato_id=contato_id,
    )
    db.session.add(tarefa)
    db.session.commit()
    flash("Tarefa criada com sucesso.", "success")
    return redirect(url_for("main.dashboard", _anchor="tarefas"))


@main_bp.route("/tarefas/<int:id>/concluir")
@login_required
def concluir_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    tarefa.concluida = True
    db.session.commit()
    flash(f"Tarefa \"{tarefa.titulo}\" concluída.", "success")
    return redirect(url_for("main.dashboard", _anchor="tarefas"))