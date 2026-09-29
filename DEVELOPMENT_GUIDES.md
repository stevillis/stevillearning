# Development Guide - Stévillis Sousa Learning Hub

Este guia detalha o fluxo de desenvolvimento local, inicialização do projeto, internacionalização e comandos comuns.

---

## 1. Tecnologias Base

- **Gerenciador de Dependências**: `uv`
- **Backend**: Python 3.12+ (Django 5.2, Django REST Framework, SimpleJWT)
- **Frontend**: Django Templates + Tailwind CSS (v4 Standalone CLI)
- **Banco de Dados Local**: PostgreSQL via Docker (ou SQLite para testes rápidos)
- **Servidor de Arquivos Estáticos**: WhiteNoise (`whitenoise.storage.CompressedStaticFilesStorage`)

---

## 2. Configuração Inicial do Ambiente

Siga os passos abaixo para preparar o ambiente local pela primeira vez:

1. **Instale o `uv`** (se ainda não tiver):

   ```bash
   pip install uv
   ```

2. **Sincronize as dependências**:

   ```bash
   uv sync
   ```

   Isso criará o ambiente virtual `.venv` e instalará todos os pacotes definidos no `pyproject.toml`.

3. **Configure as Variáveis de Ambiente**:
   - Copie o arquivo `.env-example` para `.env`:

     ```bash
     cp .env-example .env
     ```

   - No arquivo `.env`, ajuste as configurações de banco de dados (`PGDATABASE`, `PGUSER`, `PGPASSWORD`, etc.) de acordo com seu ambiente local.

4. **Execute as migrações iniciais**:

   ```bash
   uv run python manage.py migrate
   ```

---

## 3. Comandos Frequentes de Desenvolvimento

### Rodar o Servidor Django

Sempre utilize o prefixo `uv run` para garantir que o comando execute no ambiente virtual correto, ou ative o `.venv` localmente.

```bash
uv run python manage.py runserver
```

Acesse [http://127.0.0.1:8000/](http://127.0.0.1:8000/) no seu navegador.

### Compilar o Tailwind CSS (Standalone CLI)

O projeto utiliza Tailwind v4 via `django-tailwind` no **modo standalone binary** (não exige Node.js/npm).

- **Modo Observador (Watcher)** (recomendado em desenvolvimento):

  ```bash
  uv run python manage.py tailwind start
  ```

- **Build Único** (para produção ou verificação estática):

  ```bash
  uv run python manage.py tailwind build
  ```

### Migrações de Banco de Dados

Sempre que alterar seus modelos em `models.py`:

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Criar Superusuário

Para acessar o painel administrativo (`/admin/`):

```bash
uv run python manage.py createsuperuser
```

---

## 4. Testes e Qualidade de Código

O projeto possui uma suíte de testes automatizados com `pytest-django`, medição de cobertura de código, linters (`ruff`, `djlint`) e integração com `pre-commit`.

### Executar a Suíte de Testes

```bash
# Executar toda a suíte de testes
uv run pytest

# Executar arquivos de teste específicos
uv run pytest learning_hub/test_api.py
uv run pytest learning_hub/tests_dashboard.py
```

### Relatório de Cobertura de Testes

```bash
# Executar testes com coleta de cobertura
uv run coverage run -m pytest

# Exibir relatório no terminal
uv run coverage report -m

# Exibir relatório HTML interativo no navegador (porta 8080)
uv run coverage html && uv run python -m http.server 8080
```

### Linters e Formatadores

#### Python (Ruff)

```bash
# Verifica e corrige problemas de linting (incluindo ordenação de imports)
uv run ruff check --fix

# Formata o código de acordo com o padrão PEP8
uv run ruff format
```

#### Templates HTML (djLint)

```bash
uv run djlint learning_hub/templates/ stevillearning/templates/ theme/templates/
```

#### Hooks do Pre-Commit

```bash
# Instalar os hooks no repositório git local
uv run pre-commit install

# Executar manualmente os hooks em todos os arquivos
uv run pre-commit run --all-files
```

---

## 5. Modos de Execução (Local vs Docker)

### Opção A: Desenvolvimento Rápido Local (Recomendado)

Roda o Django e o Tailwind diretamente na máquina local com hot reload:

1. Inicie o servidor Django:

   ```bash
   uv run python manage.py runserver
   ```

2. Em outro terminal, rode o observador do Tailwind CSS:

   ```bash
   uv run python manage.py tailwind start
   ```

### Opção B: Simulação de Produção em Contêiner Docker

Sobe o contêiner da aplicação rodando com Gunicorn:

1. Inicie a aplicação via Docker Compose:

   ```bash
   docker compose up --build
   ```

2. Acesse a aplicação em: [http://localhost:8003/](http://localhost:8003/)

---

## 6. Arquitetura de Estáticos e Templates

A estrutura estática está dividida da seguinte forma:

- **Estáticos do Tema (`theme/static/`)**:
  - `theme/static/css/dist/styles.css`: CSS final gerado pelo Tailwind CSS standalone binary.
- **Estáticos da Aplicação (`static/` e `learning_hub/static/`)**:
  - Imagens, logos e ativos do projeto.
- **Configuração no `settings.py`**:

  ```python
  STATIC_URL = "/static/"
  STATIC_ROOT = BASE_DIR / "staticfiles"
  STATICFILES_DIRS = [
      BASE_DIR / "theme" / "static",
      BASE_DIR / "static",
  ]
  STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
  ```

---

## 7. Internacionalização (i18n)

 O projeto suporta Português (`pt-BR`) e Inglês (`en`).

### Gerar arquivos de tradução (`.po`)

```bash
uv run python manage.py makemessages -l pt_BR -i ".venv"
uv run python manage.py makemessages -l en -i ".venv"
```

### Compilar traduções (`.mo`)

```bash
uv run python manage.py compilemessages
```

---

## 8. Banco de Dados, Backups e Restauração

Para instruções detalhadas sobre backup (dump), restauração (import), sincronização de migrações (`python manage.py migrate --fake`) e resolução de problemas comuns de banco de dados, consulte o guia dedicado:

- 🗄️ [Guia de Operações de Banco de Dados (`DATABASE_GUIDES.md`)](DATABASE_GUIDES.md)

---

## 9. Sincronização e Webhook com stevillis.com.br (RAG Chatbot)

O `stevillearning` sincroniza automaticamente cursos e certificações com o site de portfólio `stevillis.com.br` para alimentar a base de vetores (pgvector) do assistente de IA (MarIA).

### Geração de Chaves e Segredos

#### 1. Gerar a Chave Secreta do Webhook (`STEVILLIS_WEBHOOK_SECRET`)

Para que o `stevillearning` envie webhooks autenticados (com assinatura HMAC-SHA256) para o `stevillis.com.br`:

```bash
python -c "import secrets; print(secrets.token_urlsafe())"
```

Configure a chave resultante no `.env`:

- No `stevillearning/.env`:

  ```env
  STEVILLIS_WEBHOOK_URL=http://127.0.0.1:8001/api/webhooks/learning-hub/
  STEVILLIS_WEBHOOK_SECRET=sua_chave_gerada_aqui
  ```

- No `stevillis.com.br/.env`:

  ```env
  LEARNING_HUB_WEBHOOK_SECRET=sua_chave_gerada_aqui
  ```

#### 2. Gerar JWT Token para Sincronização Manual via CLI

Se preferir ou precisar rodar a sincronização completa manualmente através do management command `sync_learning_hub` do `stevillis.com.br`:

- **Via Django Shell (Mais rápido — não exige digitar senha):**

  ```bash
  uv run python manage.py shell -c "from rest_framework_simplejwt.tokens import RefreshToken; from django.contrib.auth import get_user_model; u = get_user_model().objects.filter(is_superuser=True).first(); print(str(RefreshToken.for_user(u).access_token))"
  ```

- **Via cURL / HTTP POST para `/api/token/`:**

  ```bash
  curl -X POST http://127.0.0.1:8000/api/token/ \
    -H "Content-Type: application/json" \
    -d '{"username": "seu_admin", "password": "sua_password"}'
  ```

#### 3. Sincronização sob Demanda pelo Django Admin

No Django Admin (`/admin/`), ao visualizar a listagem de Cursos ou Certificações, você pode selecionar os itens desejados e escolher a ação **"Sync selected items to stevillis.com.br (RAG)"** no menu dropdown de ações em massa para sincronizá-los imediatamente sem precisar acessar o terminal.
