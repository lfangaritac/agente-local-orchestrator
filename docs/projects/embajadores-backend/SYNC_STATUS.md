# SYNC_STATUS - embajadores-backend

- project_id: `embajadores-backend`
- local_path: `C:\Users\murfe\source\repos\embajadores-backend`
- repo_url: `https://github.com/lfangaritac/embajadores-backend.git`
- branch: `main`
- head_reviewed: `a0215e92792684bf2a1b903034bb1da99e78ed6a`
- current_head_detected: `2812ff0`
- last_sync: `2026-05-26`
- sync_type: `initial_enablement_plus_retoma_readonly`
- agent: `Codex`
- status: `parcialmente_listo`

## Contexto revisado

- Documentacion explicita: `README.md`, `replit.md`, `docs/TECHNICAL_DOCUMENTATION.md`, `frontend/src/app/api/APIContract.md`, docs `.md` principales por inventario.
- Configuracion: `.replit`, `.github/workflows/main_embajadores-backend.yml`, `package.json`, `pyproject.toml`, `requirements.txt`, `frontend/package.json`, `.gitignore`, `.env.example`.
- Codigo: `main.py`, `app.py`, `db.py`, `env_loader.py`, `whatsapp_webhook.py`, `voiceflow_client.py`, inventario de `routes/`, `services/`, `repositories/`, `tests/`.

## Estado Git

- Orquestador: cambios esperados en `PROJECT_REGISTRY.md` y `docs/projects/embajadores-backend/*`.
- Repo objetivo: limpio en `main` al momento de retoma.
- Desfase detectado: `current_head_detected` no coincide con `head_reviewed`; se reviso el ultimo commit de bridge, pero aun falta resincronizacion completa de todos los commits nuevos desde `head_reviewed`.
- Bridge shell: `orquestador` y `scripts/orchestrator_bridge.py` estan versionados en HEAD y responden ayuda localmente.
- Workspace local: existen archivos no trackeados del sistema de agentes copiados por alistamiento (`AGENT_RULES.md`, `.continue/`, `REPLIT_HANDOFF.md`, etc.); no deben mezclarse con cambios funcionales.
- Fix WA cross-worker reportado por Replit: visible en `origin/main` tras `git fetch origin`; revisado con reservas.
- Hotfix persistencia UE WA session: `2812ff0` pusheado a `origin/main`; incluye handoff de diagnostico para Replit.

## Pendientes

- Resincronizar documentacion del orquestador contra cambios `a0215e92792684bf2a1b903034bb1da99e78ed6a..2812ff0`.
- Decidir tratamiento de archivos no trackeados del sistema de agentes en el repo objetivo.
- Esperar retorno de diagnostico Replit sobre `2812ff0`.
- Sanear `.env.example` y rotar/revocar credenciales si aplican, con autorizacion humana.
- Ejecutar validaciones no destructivas autorizadas.
- Completar mapa granular de rutas de `app.py`.
- Auditar si archivos versionados `.xlsx/.txt/.json` contienen PII o datos sensibles.
- Validar contrato frontend API vs endpoints reales.
- Definir comandos seguros por entorno local/Replit/Azure.
