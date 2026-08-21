# Escopo de Melhorias — Sistema CRM

> Documento de escopo e relatório de melhorias do Sistema CRM (Flask + SQLAlchemy + Flask-Login).
> Gerado após análise do código-fonte. Serve como referência para planejamento, priorização e aceite das entregas.

---

## 1. Contexto

Aplicação CRM para gestão de contatos, funil de vendas, tarefas, automações e relatórios.

**Stack atual**
- Backend: Flask, Flask-SQLAlchemy, Flask-Login
- Frontend: Jinja2 + HTML/CSS/JS em template único, Chart.js (CDN)
- Banco: SQLite (padrão) / configurável via `DATABASE_URL`

**Estado atual:** esqueleto funcional no front-end (dashboard), mas com back-end incompleto. Várias rotas e modelos existem, porém a maioria não persiste dados, contém bugs que quebram navegação e há grande desalinhamento entre os modelos e o template.

---

## 2. Problemas críticos (bugs que quebram ou impedem o uso)

| # | Arquivo:Linha | Descrição | Impacto |
|---|---|---|---|
| B1 | `web/routes/main_routes.py:86` | `url_for("main/dashboard")` usa barra em vez de ponto | `BuildError` → 500 ao criar automação |
| B2 | `web/routes/main_routes.py:98` | `url_for("listar_tarefas")` endpoint inexistente (falta prefixo `main.`) | `BuildError` → 500 ao criar tarefa |
| B3 | `web/routes/main_routes.py:102` | `url_for("main/dashboard")` idem B1 | 500 ao concluir tarefa |
| B4 | `web/routes/main_routes.py:59` | Renderiza `"contato.html"`, mas o template está em `main/` e não existe `contato.html` | `TemplateNotFound` → 500 |
| B5 | `web/routes/main_routes.py:14` | `periodo_funil = Empresa` atribui a **classe** (não instância) | Dado inválido exibido no template |
| B6 | `web/routes/main_routes.py:55` | `info_contatos = Contato` atribui a classe; nunca consulta o banco | Página de detalhe vazia/inválida |
| B7 | `config.py:8` | `FLASK_APP = os.getenv("SECRET_KEY", "run")` lê a variável errada | Config incorreta |
| B8 | `web/__init__.py:19` | `login_view = 'main.login'`, porém não existe rota `login` | Qualquer redirect de login falha |

## 3. Back-end incompleto (funcionalidades prometidas, não implementadas)

| # | Local | Problema |
|---|---|---|
| B9 | `criar_contato` (main_routes.py:63) | Lê o formulário mas **não persiste** no banco |
| B10 | `criar_automacao` (main_routes.py:78) | Não persiste; não existe modelo de Automação |
| B11 | `criar_tarefa` (main_routes.py:96) | Vazia — não lê nem salva dados |
| B12 | `concluir_tarefa` (main_routes.py:101) | Não marca a tarefa como concluída |
| B13 | `buscar` (main_routes.py:44) | Ignora o parâmetro `q` e renderiza template placeholder |
| B14 | README | Promete e-mails automáticos, agendamento e lembretes que não existem no código |
| B15 | Login | Flask-Login configurado, mas sem rota/tela de login, sem senha e sem sessão real |

## 4. Desalinhamento modelo ↔ template (dados que nunca chegam como o template espera)

O `dashboard.html` consome atributos que **não existem nos modelos**:

| Template | Campo usado | Modelo real | Correção sugerida |
|---|---|---|---|
| linha 1088 | `m.label` | `ReceitaMensal` tem `ano/mes/valor/delta` | Criar DTO/dicionário de métricas com `label`, `valor`, `delta` |
| linha 1165 | `t.atrasada` | `Tarefa` não tem | Adicionar property `atrasada` (vencimento < hoje e não concluída) |
| linha 1168 | `t.tipo` | `Tarefa` não tem | Adicionar campo `tipo` |
| linha 1171 | `t.prazo`, `t.contato` | Tem `vencimento`, `contato` (objeto) | Usar `t.vencimento` e `t.contato.nome`; adicionar `prazo` se desejado |
| linha 1235 | `c.etapa_cor` | `Contato.etapa` é objeto `EtapaFunil` | Usar `c.etapa.cor` |
| linha 1238-1245 | `c.ultima_interacao.tipo/.resumo/.data` | `ultima_interacao` é `Date` | Criar modelo `Interacao` ou property formatada |
| linha 1038/1303 | `empresa_nome` | Rota passa `empresa` (lista de `Empresa`) | Passar `empresa_nome` correto ou usar o primeiro registro |
| linha 1111 | `periodo_funil.criado_em` | É a classe `Empresa` | Corrigir variável ou remover |
| linha 19-26 (rota) | `grafico_funil` / `grafico_receita` | Vírgula no final → **tupla**, não dict | Remover vírgulas |

## 5. Segurança

| # | Local | Problema | Prioridade |
|---|---|---|---|
| S1 | `config.py:7` | `SECRET_KEY` com valor padrão hardcoded e versionado | Alta |
| S2 | `run.py:6` | `debug=True` e `host='0.0.0.0'` (exposição pública) | Alta |
| S3 | Global | Sem proteção CSRF (sem Flask-WTF) em todos os POST | Alta |
| S4 | Rotas POST | Acesso direto a `request.form["campo"]` → `KeyError`/500 se ausente; sem validação | Média |
| S5 | Global | Sem autenticação real (nada `@login_required`) — dashboard público | Alta |
| S6 | `model.py` | Sem hash de senha (nem campo de senha existe no `Usuario`) | Alta |
| S7 | Template | Chart.js carregado de CDN sem SRI (risco de supply-chain) | Baixa |
| S8 | `config.py` | Sem classes de config por ambiente (dev/prod/test); segredos só via env | Média |

## 6. Arquitetura e organização de código

- **Falta `requirements.txt`/`pyproject.toml`** — impossível reproduzir o ambiente (nenhum arquivo de dependências no projeto).
- **Falta `.env.example`** — não há documentação das variáveis de ambiente necessárias.
- **`from web.modules.model import *`** em `main_routes.py` — import curinga; preferir imports explícitos.
- **Lógica de negócio dentro das rotas** — sem camada de serviços/repositórios; rotas crescem sem controle.
- **Sem blueprints além de `main`** — estrutura `routes/` existe, mas só há um blueprint com tudo.
- **Sem tratamento de erros** — nenhum handler de 404/500; falhas viram tela branca.
- **Sem logging** — nenhuma configuração de logs para depuração/produção.
- **Sem migrações** — não há Flask-Migrate/Alembic; evolução de schema sem versionamento.
- **Sem testes** — nenhum `tests/`; sem pipeline de CI.
- **`web/modules/__init__.py` vazio** — módulo só existe para empacotar.
- **`resultado.html`** — placeholder em `lang="en"`, `Title`, sem conteúdo (herdado do scaffold).

## 7. Modelo de dados

- **`Usuario` não possui credenciais** (email, `password_hash`, `ativo`) → autenticação impossível de fato.
- **`Contato.email` com `unique=True` mas sem `index`** e sem constraints de unicidade tratadas.
- **N+1 no funil**: `EtapaFunil.quantidade` e `valor_total` usam `len(self.contatos)`/iteração — carregam todos os contatos na memória. Preferir `func.count()`/`func.sum()` com JOIN.
- **Faltam índices** em `etapa_id`, `contato_id`, `ultima_interacao`, `email`.
- **Sem seed data** — o app abre vazio; gráficos/etapas nunca aparecem.
- **Sem modelo de Interação** (e-mails/ligações) — essencial para o README prometer histórico de interações.
- **Sem modelo de Automação** — apesar de haver rota e modal no front-end.
- **`Tarefa.vencimento`** sem índice e sem campo `tipo`/`concluida_em`.
- **`ReceitaMensal`** sem unicidade `(ano, mes)` — permite duplicatas.

## 8. Front-end

- **`dashboard.html` com ~1.700 linhas** — todo CSS/JS inline, sem `base.html`, sem blocos reutilizáveis.
- **Typo:** linha 13 `rel="fivi-icon"` → `rel="icon"`.
- **Favicon:** `href="static/img/favi-icon.png"` relativo, sem `/` inicial → quebra em sub-rotas.
- **URLs via `url_for`** corretas no template, mas quebram por causa dos bugs de rota (seção 2).
- **Dados fake de gráfico** hardcoded na rota (`[50, 40, 24]`, `[5000, ...]`) — devem vir do banco.
- **`data_atualizacao`** hardcoded `"18/06/2026"` na rota — deve ser dinâmico.
- **Busca global** envia `q` para `/buscar`, que não retorna resultado (B13).
- **Modal de automação/tarefa** envia para rotas que não persistem.
- **Acessibilidade:** boa base (skip-link, aria, reduced-motion) — manter ao refatorar.
- **Responsividade:** já implementada; preservar ao extrair CSS.

## 9. Plano de execução sugerido (fases)

### Fase 1 — Correções críticas (estabiliza o app)
- [ ] Corrigir `url_for` em `main_routes.py:86,98,102` e template de detalhe (`main/contato.html` ou remoção da rota).
- [ ] Corrigir `periodo_funil` (B5) e `info_contatos` (B6).
- [ ] Corrigir `config.py` (`FLASK_APP`, `SECRET_KEY` só via env) e criar `.env.example`.
- [ ] Criar `requirements.txt` com pin de versões.
- [ ] Persistir contato, tarefa (incluindo `concluir_tarefa`) e automação no banco.
- [ ] Alinhar template ↔ modelos (seção 4) para eliminar atributos inexistentes.
- [ ] Adicionar handler de 404/500 e validação básica de formulários (retornar erro amigável).

### Fase 2 — Segurança e autenticação
- [ ] Implementar autenticação real: campos `email` + `password_hash` em `Usuario`, rota/tela de login/logout, `@login_required` nas rotas.
- [ ] CSRF (Flask-WTF) nos formulários.
- [ ] `debug=False` por padrão; separar config por ambiente.
- [ ] Rate limiting de login (ex.: Flask-Limiter).

### Fase 3 — Modelos e dados
- [ ] Modelo `Interacao` (email/ligação/nota) ligado ao `Contato`.
- [ ] Modelo `Automacao` (gatilho, ação, prazo_dias).
- [ ] `Tarefa.tipo` e `Tarefa.atrasada` (property).
- [ ] Unicidade `(ano, mes)` em `ReceitaMensal`; `EtapaFunil` com `func.count/sum` (eliminar N+1).
- [ ] Índices nas FKs e campos filtrados.
- [ ] Migrações com Flask-Migrate; seed de etapas do funil e dados de exemplo.

### Fase 4 — Arquitetura e qualidade
- [ ] Extrair CSS/JS do template; criar `base.html` com blocos.
- [ ] Camada de serviços; remover `import *`.
- [ ] Testes (pytest): rotas, modelos, autenticação, persistência.
- [ ] Logging estruturado.
- [ ] `/buscar` retornando resultados reais (JSON + página de resultados).
- [ ] Atualizar README para refletir a realidade; documentar setup em `.env.example`.

## 10. Critérios de aceite (definição de pronto)

1. Todas as rotas respondem sem `BuildError`/`TemplateNotFound`.
2. Contato, tarefa e automação são persistidos e reaparecem no dashboard após reload.
3. `SECRET_KEY` e config de produção vêm 100% de variáveis de ambiente; `debug=False` em produção.
4. Autenticação funcional: login/logout com senha com hash; rotas protegidas.
5. Templates não referenciam mais atributos inexistentes nos modelos.
6. Sem `N+1` nas métricas do funil.
7. `pytest` cobrindo rotas e modelos passa; lint/typecheck sem erros.
8. `requirements.txt` permite `pip install -r requirements.txt` reproduzir o ambiente.

---

## 11. Resumo executivo (destaques)

- **3 bugs de rota causam erro 500** (B1/B2/B3) e **1 quebra de template** (B4) — bloqueiam as funções centrais (criar contato, tarefa, automação, ver detalhe).
- **Nenhuma operação de escrita persiste dados** — o sistema hoje é somente leitura com telas.
- **Autenticação é fictícia** — Flask-Login configurado sem login real; sem proteção das rotas.
- **Dados de relatório são fake/hardcoded** — gráficos não refletem o banco.
- **Falta o mínimo de engenharia de software**: `requirements.txt`, testes, migrações, tratamento de erros, logging e validação de entrada.
- **Prioridade imediata:** Fase 1 (estabilizar) → Fase 2 (segurança) → Fase 3 (dados) → Fase 4 (arquitetura).