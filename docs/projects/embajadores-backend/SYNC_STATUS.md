# SYNC_STATUS - embajadores-backend

- project_id: `embajadores-backend`
- local_path: `C:\Users\murfe\source\repos\embajadores-backend`
- repo_url: `https://github.com/lfangaritac/embajadores-backend.git`
- branch: `main`
- head_reviewed: `88291e9`
- current_head_detected: `88291e9`
- last_sync: `2026-06-02`
- sync_type: `post_docs_update_dual_whatsapp_senders`
- agent: `Codex`
- status: `parcialmente_listo`

## Contexto revisado

- Documentacion explicita: `README.md`, `replit.md`, `docs/TECHNICAL_DOCUMENTATION.md`, `frontend/src/app/api/APIContract.md`, docs `.md` principales por inventario.
- Configuracion: `.replit`, `.github/workflows/main_embajadores-backend.yml`, `package.json`, `pyproject.toml`, `requirements.txt`, `frontend/package.json`, `.gitignore`, `.env.example`.
- Codigo: `main.py`, `app.py`, `db.py`, `env_loader.py`, `whatsapp_webhook.py`, `voiceflow_client.py`, inventario de `routes/`, `services/`, `repositories/`, `tests/`.
- Retoma post-pull: `docs/retos-sync/*`, `_scripts/envio_10_30_bogota.py`, `routes/futbol_routes.py`, `whatsapp_webhook.py`, `services/ue_session_service.py`, `tests/test_ue_webhook_session.py`.
- Cambio reciente validado: `a9e5efb Support dual WhatsApp senders for Embajadores`, posteriormente sincronizado por fast-forward hasta `88291e9 Merge remote-tracking branch 'origin/main'`.
- Documentacion reciente actualizada: `docs/TECHNICAL_DOCUMENTATION.md`, `replit.md`, `docs/retos-sync/01_inventario_backend_actual.md` para politica `EMBAJADORES_PRIMARY` / `EMBAJADORES_LEGACY`.

## Estado Git

- Orquestador: cambios esperados en `PROJECT_REGISTRY.md` y `docs/projects/embajadores-backend/*`.
- Repo objetivo: `main...origin/main` tras pull `--ff-only` hasta `88291e9`; conserva cambio local ajeno en `routes/futbol_routes.py` y archivos no trackeados del sistema de agentes.
- Desfase detectado: no hay desfase entre `head_reviewed` y `current_head_detected` al cierre de esta retoma; ambos apuntan a `88291e9`.
- Bridge shell: `orquestador` y `scripts/orchestrator_bridge.py` estan versionados en HEAD y responden ayuda localmente.
- Workspace local: existen archivos no trackeados del sistema de agentes copiados por alistamiento (`AGENT_RULES.md`, `.continue/`, `REPLIT_HANDOFF.md`, etc.); no deben mezclarse con cambios funcionales.
- Fix WA cross-worker reportado por Replit: visible en `origin/main` tras `git fetch origin`; revisado con reservas.
- Hotfix persistencia UE WA session: `2812ff0` pusheado a `origin/main`; incluye handoff de diagnostico para Replit.

## Pendientes

- Procesar retorno de diagnostico Replit sobre `2812ff05d88d06b0e03511ecdee974c2bb442e14` cuando exista.
- Decidir tratamiento de archivos no trackeados del sistema de agentes en el repo objetivo.
- Mantener `semantic_context_gate` como primer paso de toda nueva instruccion sobre Embajadores.
- Para tareas de WhatsApp, usar tag `whatsapp.delivery` y revisar `whatsapp_webhook.py`, `app.py` y scripts proactivos antes de modificar.
- Versionar cambios documentales de Embajadores cuando se autorice commit/push.
- Si la tarea menciona retos periodicos, Puntos Colombia, API Push, SFTP/MFT, Azure Blob, ganadores o auditoria de cargas, usar tag `retos.sync` y leer `docs/retos-sync/*` antes de planificar.
- Sanear `.env.example` y rotar/revocar credenciales si aplican, con autorizacion humana.
- Ejecutar validaciones no destructivas autorizadas.
- Completar mapa granular de rutas de `app.py`.
- Auditar si archivos versionados `.xlsx/.txt/.json` contienen PII o datos sensibles.
- Validar contrato frontend API vs endpoints reales.
- Definir comandos seguros por entorno local/Replit/Azure.
