# SYNC_STATUS - embajadores-backend

- project_id: `embajadores-backend`
- local_path: `C:\Users\murfe\source\repos\embajadores-backend`
- repo_url: `https://github.com/lfangaritac/embajadores-backend.git`
- branch: `main`
- head_reviewed: `a0215e92792684bf2a1b903034bb1da99e78ed6a`
- last_sync: `2026-05-26`
- sync_type: `initial_enablement`
- agent: `Codex`
- status: `parcialmente_listo`

## Contexto revisado

- Documentacion explicita: `README.md`, `replit.md`, `docs/TECHNICAL_DOCUMENTATION.md`, `frontend/src/app/api/APIContract.md`, docs `.md` principales por inventario.
- Configuracion: `.replit`, `.github/workflows/main_embajadores-backend.yml`, `package.json`, `pyproject.toml`, `requirements.txt`, `frontend/package.json`, `.gitignore`, `.env.example`.
- Codigo: `main.py`, `app.py`, `db.py`, `env_loader.py`, `whatsapp_webhook.py`, `voiceflow_client.py`, inventario de `routes/`, `services/`, `repositories/`, `tests/`.

## Estado Git

- Orquestador: cambios esperados en `PROJECT_REGISTRY.md` y `docs/projects/embajadores-backend/*`.
- Repo objetivo: limpio al momento de la verificacion final del alistamiento.

## Pendientes

- Ejecutar validaciones no destructivas autorizadas.
- Completar mapa granular de rutas de `app.py`.
- Auditar si archivos versionados `.xlsx/.txt/.json` contienen PII o datos sensibles.
- Validar contrato frontend API vs endpoints reales.
- Definir comandos seguros por entorno local/Replit/Azure.

