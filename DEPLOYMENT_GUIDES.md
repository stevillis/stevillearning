# Deployment Guide - Stévillis Learning Hub

Este guia descreve os processos para implantação da aplicação em ambiente de produção (Docker / VPS / Railway / PaaS) utilizando o banco de dados PostgreSQL.

---

## Arquitetura de Produção

- **Domínio / Subdomínio**: `<https://learning.stevillis.com.br>`
- **App Server**: Container Docker rodando `gunicorn` em `0.0.0.0:8003`.
- **Gerenciador de Pacotes**: `uv` (compilação do Tailwind CSS standalone e `collectstatic` são executados automaticamente durante o build do `Dockerfile`).
- **Arquivos Estáticos**: WhiteNoise (`whitenoise.storage.CompressedStaticFilesStorage`).
- **Banco de Dados**: PostgreSQL em nuvem (Railway / Supabase / Neon / VPS).

---

## 1. Variáveis de Ambiente em Produção (`.env`)

No ambiente de produção, configure as variáveis essenciais:

```env
SECRET_KEY=sua_secret_key_de_producao_super_segura
DEBUG=False
ALLOWED_HOSTS=learning.stevillis.com.br,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://learning.stevillis.com.br

# Conexão com Banco de Dados PostgreSQL Cloud (Supabase / Neon / Railway)
DATABASE_URL=postgresql://postgres.YOUR_REF:YOUR_PASSWORD@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require

# Ou via campos individuais:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=stevillis
# DB_USER=postgres
# DB_PASSWORD=sua_senha
# DB_HOST=seu_host_postgresql
# DB_PORT=5432

# Sincronização Automática via Webhook (RAG em stevillis.com.br)
STEVILLIS_WEBHOOK_URL=https://stevillis.com.br/api/webhooks/learning-hub/
STEVILLIS_WEBHOOK_SECRET=sua_webhook_secret_compartilhada
```

### Como gerar as chaves e segredos

#### 1. Gerar a SECRET_KEY do Django

Execute no terminal:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
# ou
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 2. Gerar a STEVILLIS_WEBHOOK_SECRET (Webhook Secret)

Esta chave compartilhada autentica os envios de webhook entre o `stevillearning` e o `stevillis.com.br`:

```bash
python -c "import secrets; print(secrets.token_urlsafe())"
```

> [!IMPORTANT]
> Defina exatamente o mesmo valor em `STEVILLIS_WEBHOOK_SECRET` (no `.env` do `stevillearning`) e em `LEARNING_HUB_WEBHOOK_SECRET` (no `.env` do `stevillis.com.br`).

#### 3. Gerar JWT Token para Sincronização Manual

Caso precise de um token JWT para executar o comando `python manage.py sync_learning_hub` manualmente a partir do `stevillis.com.br`:

```bash
# Executar no servidor/container do stevillearning:
uv run python manage.py shell -c "from rest_framework_simplejwt.tokens import RefreshToken; from django.contrib.auth import get_user_model; u = get_user_model().objects.filter(is_superuser=True).first(); print(str(RefreshToken.for_user(u).access_token))"
```

Ou via requisição HTTP POST para `/api/token/`:

```bash
curl -X POST https://learning.stevillis.com.br/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "seu_admin", "password": "sua_password"}'
```

---

## 2. Build da Imagem Docker, Segurança (CVEs) e Envio para o Docker Hub

O `Dockerfile` do projeto realiza o build multi-stage: instala as dependências via `uv`, compila o Tailwind CSS (`tailwind build`), coleta os estáticos (`collectstatic --no-input`) e aplica atualizações de segurança no sistema operacional e pacotes Python automaticamente durante o build.

### Passo 2.1: Manutenção de Dependências Python e SO

Para garantir zero vulnerabilidades conhecidas (CVEs) nas bibliotecas e na imagem base:

```bash
# Atualizar travas de dependências Python para versões corrigidas
uv lock --upgrade

# Executar os testes automatizados para garantir integridade
uv run pytest
```

### Passo 2.2: Build da Imagem Docker e Varredura com Docker Scout

Construa a imagem forçando a busca pela versão mais recente da imagem base (`--pull`) e execute a auditoria de segurança com o Docker Scout:

```bash
# Fazer o build buscando atualizações da imagem base python:3.12-slim
docker build --pull -t stevillis/stevillearning:latest .

# Auditar vulnerabilidades (CVEs) da imagem com o Docker Scout
docker scout cves stevillis/stevillearning:latest

# Obter recomendações automáticas de atualização de imagem base
docker scout recommendations stevillis/stevillearning:latest

# Enviar a imagem corrigida para o Docker Hub
docker push stevillis/stevillearning:latest
```

> [!TIP]
> **Por que ocorrem CVEs e como são corrigidos?**
>
> - **Vulnerabilidades do Sistema Operacional (`deb / debian`)**: O `Dockerfile` inclui `apt-get upgrade -y --no-install-recommends` para atualizar bibliotecas do sistema.
> - **Vulnerabilidades de Pacotes Python da Imagem Base (`pypi / pip` / `setuptools`)**: O `Dockerfile` inclui `python -m pip install --no-cache-dir --upgrade pip setuptools wheel msgpack` para atualizar ferramentas pré-instaladas da imagem base.
> - **Recomendações Automáticas**: O comando `docker scout recommendations <imagem>` sugere as melhores tags de imagem base atualizadas.
> - **Vulnerabilidades Não Corrigíveis (`Fixed version: not fixed`)**: Pacotes do SO com status *not fixed* no repositório do Debian representam vulnerabilidades teóricas sem patch lançado pelo Debian. No painel do Docker Hub, utilize o filtro **Fixable** para visualizar apenas os itens com correção disponível.

---

## 3. Inicialização no Servidor de Produção (VPS / Docker Host)

### Passo 3.1: No Servidor de Produção (Pull e Start)

Na VPS ou servidor de hospedagem, navegue até a pasta da aplicação e execute:

```bash
# Baixar a versão mais recente da imagem publicada no Docker Hub
docker compose pull

# Subir a aplicação em modo detached (background)
docker compose up -d
```

---

## 4. Configuração do Nginx e SSL (VPS / Host Linux)

Se estiver implantando em uma VPS própria (ex: Oracle Cloud, DigitalOcean, Hetzner) atrás de um Nginx reverse proxy:

1. **Criar configuração `/etc/nginx/sites-available/learning-hub`**:

   ```nginx
   server {
       listen 80;
       server_name learning.stevillis.com.br;

       client_max_body_size 20M;

       location / {
           proxy_pass http://127.0.0.1:8003;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

2. **Ativar o site e recarregar o Nginx**:

   ```bash
   sudo ln -s /etc/nginx/sites-available/learning-hub /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **Gerar certificado SSL gratuito via Certbot**:

   ```bash
   sudo certbot --nginx -d learning.stevillis.com.br
   ```

---

## 5. Migrações e Inicialização em Produção

Após subir o container em produção, execute as migrações do banco de dados no container rodando:

```bash
# Executar migrações do Django
docker compose exec web python manage.py migrate

# Criar superusuário administrativo em produção
docker compose exec web python manage.py createsuperuser
```

---

## 6. Resolução de Problemas (Troubleshooting)

### Migrações Pendentes na Plataforma de Hospedagem (ex: Railway)

Se ao acessar o ambiente de produção for retornado erro de tabela não encontrada (`ProgrammingError: relation "..." does not exist`):

1. Acesse o painel da sua plataforma de hospedagem (ex: **Railway Dashboard**).
2. Abra o menu do serviço **web** e selecione **SSH** (ou terminal remoto).
3. Execute manualmente o comando de migração:

   ```bash
   python manage.py migrate
   ```

### Arquivos Estáticos Não Carregando (WhiteNoise / Nginx)

1. Certifique-se de que `python manage.py collectstatic --no-input` rodou durante a construção da imagem Docker.
2. Verifique se `STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"` está configurado em `settings.py`.
3. Verifique o status das rotas estáticas via `curl`:

   ```bash
   curl -I http://localhost:8003/static/css/dist/styles.css
   ```
