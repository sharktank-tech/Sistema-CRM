# Sistema CRM

Sistema de CRM para centralizar dados de contatos, funil de vendas, histórico de interações, tarefas e métricas comerciais.

## Funcionalidades

- **Gestão de contatos**: cadastro unificado com histórico de interações (e-mail, ligação, nota).
- **Funil de vendas**: visualização das etapas de negociação, da prospecção ao pós-venda, com conversões.
- **Automação de processos**: gatilhos para envio de e-mails, agendamento de tarefas e lembretes automáticos.
- **Tarefas**: gestão de pendências com vencimento, contato relacionado e conclusão.
- **Relatórios e métricas**: gráficos de receita mensal e distribuição do pipeline (Chart.js).
- **Autenticação**: login com proteção CSRF e rate limiting.

## Stack

- Python 3.12 · Flask 3.1 · SQLAlchemy 2 · Flask-SQLAlchemy · Flask-Login · Flask-WTF · Flask-Limiter · Flask-Migrate (Alembic) · pytest

## Requisitos

- Python 3.10+
- Banco SQLite (padrão) ou qualquer banco suportado pelo SQLAlchemy

## Configuração

1. Crie o ambiente virtual e instale as dependências:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt   # inclui pytest
   ```

2. Crie o arquivo `.env` (veja `.env.example`):

   ```env
   SECRET_KEY=uma-chave-aleatoria-longa
   APP_ENV=development
   DATABASE_URL=sqlite:///instance/database.db
   ADMIN_EMAIL=admin@crm.local
   ADMIN_PASSWORD=senha-forte
   SEED_DADOS_EXEMPLO=1
   ```

   Em produção, use `APP_ENV=production` (migrações automáticas desativadas, sem dados de exemplo) e um `SECRET_KEY` forte.

## Migrações

Em `development`/`testing` as migrações são aplicadas automaticamente na inicialização (`AUTO_MIGRATE`).

Para controle manual:

```bash
flask db upgrade
flask db migrate -m "descrição"
flask db downgrade
```

## Execução

```bash
flask run          # usa FLASK_APP=run
python run.py
```

Acesse `http://localhost:5000`. O primeiro usuário (admin) é criado a partir de `ADMIN_EMAIL`/`ADMIN_PASSWORD` do `.env`.

## Testes

```bash
pytest
```

A suíte roda contra um banco isolado (`sqlite:////home/opencode/work/test_pytest.db` em ambiente local) e cobre autenticação, contatos, tarefas, interações, dashboard e integridade dos modelos.

## Estrutura

```
web/
  __init__.py        # app factory, migrações, seeds, context processor e logging
  routes/            # rotas (autenticação, contatos, tarefas, automações, busca)
  services/          # lógica de negócio (funil, métricas, busca)
  modules/model.py   # modelos SQLAlchemy
  templates/         # base.html + páginas
  static/            # CSS e JS
tests/               # suíte pytest
config.py            # configuração por ambiente
migrations/          # migrações Alembic
```

## Rotas principais

| Rota | Descrição |
| --- | --- |
| `/login` | Login (rate limit 5/min) |
| `/` | Dashboard: funil, métricas, contatos, tarefas e gráficos |
| `/buscar?q=...` | Busca por contato/empresa/e-mail (aceita `&formato=json`) |
| `/contato/<id>` | Detalhe do contato e histórico de interações |
| `/tarefas` | Lista de tarefas |
| `/automacao/nova` | Cria automação |