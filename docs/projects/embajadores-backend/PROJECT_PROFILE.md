# PROJECT_PROFILE - embajadores-backend

- project_id: `embajadores-backend`
- nombre_canonico: `Embajadores Backend`
- aliases: `embajadores`, `embajadores-backend`
- repo_url: `https://github.com/lfangaritac/embajadores-backend.git`
- local_path: `C:\Users\murfe\source\repos\embajadores-backend`
- origin: `github`
- first_onboarding_analysis: `2026-05-26`
- head_reviewed: `a0215e92792684bf2a1b903034bb1da99e78ed6a`

## Objetivo

Backend Flask para la plataforma Embajadores / Ruta Embajadora. Integra Voiceflow, WhatsApp Cloud API, Pinecone Assistant, Azure MySQL, Azure Blob Storage, Replit y un portal administrativo React/Vite servido desde Flask.

## Fuentes primarias revisadas

- `README.md`
- `replit.md`
- `docs/TECHNICAL_DOCUMENTATION.md`
- `.replit`
- `.github/workflows/main_embajadores-backend.yml`
- `package.json`
- `pyproject.toml`
- `requirements.txt`
- `main.py`
- `app.py`
- `db.py`
- `env_loader.py`
- `whatsapp_webhook.py`
- `voiceflow_client.py`
- `routes/*`
- `services/*`
- `frontend/package.json`
- `frontend/src/app/api/*`
- `.env.example`
- `.gitignore`

## Stack detectado

- Backend: Python 3.11, Flask, Gunicorn.
- Base de datos: Azure MySQL / MySQL via SQLAlchemy, PyMySQL y mysql-connector-python.
- Frontend admin: React + TypeScript + Vite + Tailwind/MUI/Radix, servido en `/portal/`.
- Runtime/hosting: Replit autoscale y Azure App Service via GitHub Actions.
- Integraciones: Voiceflow Runtime/API, Meta WhatsApp Cloud API, Pinecone Assistant, Azure Blob Storage, OpenAI, Resend/Replit Connectors.

## Estado inicial

- Repo clonado localmente y limpio.
- Analisis inicial de solo lectura completado.
- No se instalaron dependencias.
- No se ejecuto la aplicacion.
- No se ejecutaron tests, migraciones ni deployment.

