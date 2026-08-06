# Stévillis Sousa - Learning Hub

Sistema de gestão de trajetória técnica, registro de cursos, certificações e formações acadêmicas. Desenvolvido com Python (Django 5.2), PostgreSQL, Django REST Framework, WhiteNoise e Tailwind CSS v4.

---

## ✨ Principais Funcionalidades

- 📊 **Dashboard de Aprendizado**: Exibição de métricas gerais e progresso de cursos concluídos e em andamento.
- 🎓 **Gestão Completa de Cursos, Formações e Certificações**: Registro, visualização e acompanhamento detalhado de histórico acadêmico e técnico.
- 🌐 **Internacionalização Completa (i18n)**: Suporte bilíngue (Português `pt-BR` e Inglês `en`) com persistência de idioma.
- ⚡ **API REST & Autenticação JWT**: Endpoints padronizados com Django REST Framework (`djangorestframework`) e autenticação via `djangorestframework-simplejwt`.
- 🎨 **Interface Moderna & Responsiva**: Design escuro glassmórfico em Tailwind CSS v4 Standalone (compilação rápida sem necessidade de Node.js).
- ⚡ **Desenvolvimento com Hot Reload**: Recarregamento automático dos templates e CSS via `django-browser-reload`.
- 📦 **Gerenciamento de Dependências Moderno (`uv`)**: Resolução de dependências extremamente rápida e reprodutível via `pyproject.toml`.
- 🐳 **Deploy Containerizado com Docker**: Suporte a containerização multi-stage e Docker Compose com Gunicorn.

---

## 📐 Modelo de Dados (Diagrama ER)

![Entity Relationship Diagram](https://github.com/stevillis/stevillearning/blob/master/DER/DER.jpg?raw=true)

---

## 🚀 Quick Start

### 1. Pré-requisitos

- [uv](https://github.com/astral-sh/uv) (`pip install uv`)
- Docker & Docker Compose (opcional para execução em contêiner)

### 2. Configuração do Ambiente

```bash
# Sincronizar dependências no .venv
uv sync

# Configurar variáveis de ambiente (.env)
cp .env-example .env

# Executar as migrações do banco de dados
uv run python manage.py migrate
```

### 3. Compilar o Tailwind CSS (Standalone)

```bash
# Compilar o arquivo CSS em modo único:
uv run python manage.py tailwind build

# Ou iniciar o observador (watcher) para recompilação automática:
uv run python manage.py tailwind start
```

### 4. Executar Servidor Local

```bash
# Servidor Django com recarregamento em tempo real:
uv run python manage.py runserver
```

Acesse [http://127.0.0.1:8000/](http://127.0.0.1:8000/) no seu navegador.

---

## 🧪 Testes e Qualidade de Código

O projeto utiliza `pytest`, `coverage`, `ruff`, `djlint` e `pre-commit` para garantia de qualidade:

```bash
# Executar a suíte de testes
uv run pytest

# Executar com relatório de cobertura
uv run coverage run -m pytest
uv run coverage report

# Verificar linting e formatação Python
uv run ruff check --fix
uv run ruff format

# Instalar hooks do pre-commit no Git local
uv run pre-commit install
```

---

## 📚 Guias de Referência

- 📖 [Guia de Desenvolvimento Local (`DEVELOPMENT_GUIDES.md`)](DEVELOPMENT_GUIDES.md)
- 🚀 [Guia de Deploy em Produção (`DEPLOYMENT_GUIDES.md`)](DEPLOYMENT_GUIDES.md)
- 🗄️ [Guia de Banco de Dados & Backups (`DATABASE_GUIDES.md`)](DATABASE_GUIDES.md)
- 🎯 [Visão do Produto (`PRODUCT.md`)](PRODUCT.md)
- 🎨 [Diretrizes de Design (`DESIGN.md`)](DESIGN.md)
