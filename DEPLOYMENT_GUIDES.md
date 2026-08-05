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
STEVILLIS_SITE_RUNNING_LOCAL=False
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
```

---

## 2. Build da Imagem Docker e Envio para o Docker Hub

O `Dockerfile` do projeto realiza o build multi-stage: instala as dependências via `uv`, compila o Tailwind CSS (`tailwind build`) e coleta os estáticos (`collectstatic --no-input`) automaticamente durante a etapa de build da imagem.

### Passo 2.1: Autenticar no Docker Hub (Máquina Local)

Se ainda não realizou o login no Docker Hub na sua máquina:

```bash
docker login
# Informe seu usuário (ex: stevillis) e sua senha/Personal Access Token
```

### Passo 2.2: Build sem Cache e Push para o Docker Hub

Para garantir que todas as atualizações de código, dependências e compilação do Tailwind CSS sejam incluídas na imagem:

```bash
# 1. Build da imagem sem cache
docker compose build --no-cache

# (Opcional) Build direto via CLI do Docker indicando a tag:
# docker build --no-cache -t stevillis/stevillearning:latest .

# 2. Enviar a imagem para o Docker Hub
docker push stevillis/stevillearning:latest
```

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

## 3. Configuração do Nginx e SSL (VPS / Host Linux)

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

## 4. Migrações e Inicialização em Produção

Após subir o container em produção, execute as migrações do banco de dados no container rodando:

```bash
# Executar migrações do Django
docker compose exec web python manage.py migrate

# Criar superusuário administrativo em produção
docker compose exec web python manage.py createsuperuser
```

---

## 5. Resolução de Problemas (Troubleshooting)

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
