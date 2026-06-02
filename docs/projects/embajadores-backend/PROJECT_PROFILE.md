# PROJECT_PROFILE - embajadores-backend

- project_id: `embajadores-backend`
- nombre_canonico: `Embajadores Backend`
- aliases: `embajadores`, `embajadores-backend`
- repo_url: `https://github.com/lfangaritac/embajadores-backend.git`
- local_path: `C:\Users\murfe\source\repos\embajadores-backend`
- origin: `github`
- first_onboarding_analysis: `2026-05-26`
- head_reviewed: `ffb8f3cd76e87601a0487b2043a7e3ff209ed0cf`

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

## Onboarding profundo - 2026-05-26

Estado: `contexto_integral_referencial_v1`.

Cobertura revisada:

- Documentacion raiz y `docs/`: Voiceflow, WhatsApp, FAQ, Formacion, MRP, admin, deploy/logging, imagenes inline, reportes y troubleshooting.
- Reglas locales: `.agents/skills/voiceflow-project-rules/SKILL.md` y `.agents/memory/ue-wa-session-resolver.md`.
- Codigo backend: `app.py`, `db.py`, `whatsapp_webhook.py`, `voiceflow_client.py`, `embajadores_adapter.py`, `session_store.py`, `session_control.py`, `auth_web.py`.
- Blueprints: `routes/admin_*`, `routes/auth_special_routes.py`, `routes/special_*`, `routes/futbol_routes.py`, `routes/voiceflow_sync_routes.py`, `routes/mrp_upload_routes.py`, `routes/portal_routes.py`.
- Servicios: reportes, Azure Blob, email/Resend, Voiceflow sync, normalizer, usuarios especiales, consultas agenticas, entrega WhatsApp, sesiones UE.
- Frontend: `frontend/package.json`, `frontend/src/app/api/*`, `frontend/src/app/components/admin/**`, docs/imports del portal.
- Configuracion/runtime: `.replit`, `gunicorn.conf.py`, `requirements.txt`, `pyproject.toml`, `package.json`, `frontend/package.json`, `.github/workflows/*`.
- Pruebas: `tests/test_vf_sync.py`, `tests/test_futbol_endpoints.py`, `tests/test_resolver_celular_destino.py`, `tests/test_ue_session_persistence.py`.

Indice semantico canonico:

- `SEMANTIC_TAG_INDEX.md` generado por `scripts/project_context_indexer.py --project embajadores-backend --apply`.
- Tags actuales: `admin.portal`, `ai.agentic_reports`, `auth.jwt`, `db.mysql`, `faq.questions`, `football.challenge`, `mrp.content`, `replit.deployment`, `reports.special_users`, `retos.sync`, `training.flow`, `voiceflow.identity`, `voiceflow.sync`, `whatsapp.delivery`.

Suficiencia contextual:

- Nivel: `B+` para diagnostico/Plan y cambios pequenos acotados.
- Sigue requiriendo lectura especifica antes de Build funcional, por tamano del repo y alto acoplamiento con DB/Voiceflow/WhatsApp.

Retoma de sincronizacion:

- `2812ff05d88d06b0e03511ecdee974c2bb442e14` queda como HEAD revisado para la documentacion de retoma.
- El hotfix UE WA session esta documentado por referencia; cualquier cambio posterior debe iniciar con `semantic_context_gate` y lectura focalizada de fuentes top.

## Sincronizacion post-pull - 2026-05-28

Estado: `synced_to_ffb8f3c_context_retoma`.

Cobertura nueva revisada:

- Rango `2812ff05d88d06b0e03511ecdee974c2bb442e14..ffb8f3cd76e87601a0487b2043a7e3ff209ed0cf`.
- Documentos `docs/retos-sync/*`: inventario actual del modulo Retos, brechas, alternativas API Push/SFTP/Azure Blob, modelo canonico, endpoints propuestos, preguntas para Puntos Colombia y plan por fases.
- Cambios funcionales asociados: `routes/futbol_routes.py`, `whatsapp_webhook.py`, `services/ue_session_service.py`, `app.py`, `tests/test_resolver_celular_destino.py`, `tests/test_ue_webhook_session.py`.
- Script operativo nuevo `_scripts/envio_10_30_bogota.py`: envio programado de `lanzamiento_reto_solo_texto` + imagen inline `opcion2`; requiere secrets Meta y no debe ejecutarse sin autorizacion.

Nota sobre insumo externo:

- PDF local `C:\Users\murfe\Downloads\Embajadores - Alternativas de integrción Retos periodicos.pdf` identificado como insumo relevante. No se extrajo texto por falta de parser PDF local; se uso como fuente complementaria indirecta junto con la documentacion Markdown versionada que cubre el mismo tema.
