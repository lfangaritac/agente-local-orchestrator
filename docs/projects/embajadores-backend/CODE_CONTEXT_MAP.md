# CODE_CONTEXT_MAP - embajadores-backend

Mapa inicial de codigo.

## Estructura principal

- `app.py`: aplicacion Flask principal; registra rutas directas y blueprints.
- `main.py`: entrypoint `from app import app`.
- `db.py`: SQLAlchemy/PyMySQL, Azure MySQL, timezone y helpers multi-proyecto.
- `env_loader.py`: acceso a `PINECONE_API_KEY`, `PINECONE_ENDPOINT`, `SESSION_SECRET`.
- `whatsapp_webhook.py`: webhook Meta WhatsApp Cloud API multi-tenant.
- `voiceflow_client.py`: cliente Voiceflow Runtime API multi-proyecto.
- `message_router.py`, `message_queue.py`, `embajadores_adapter.py`: capa de enrutamiento/adaptacion conversacional.
- `routes/`: blueprints modulares.
- `services/`: servicios de negocio e integracion.
- `repositories/`: repositorios de usuarios/reportes/consultas especiales.
- `decorators/`, `utils/`: auth y utilidades.
- `frontend/`: portal admin React/Vite.
- `_scripts/`, `scripts/`, `sql/`: migraciones, mantenimiento, post-merge y utilidades.
- `tests/`: pruebas `test_vf_sync.py` y `test_futbol_endpoints.py`.

## Entrypoints

- Local/dev: `python main.py`.
- Produccion Replit/Azure: `gunicorn --bind 0.0.0.0:5000 main:app`.
- WSGI app: `main:app` importado desde `app.py`.
- Frontend admin: `frontend` con `pnpm build` y Vite; build servido desde `frontend/dist`.

## Blueprints detectados

- `whatsapp` desde `whatsapp_webhook.py`.
- `session_bp` desde control de sesiones.
- `auth_special_bp`
- `special_queries_bp`
- `special_reports_bp`
- `admin_mrp_bp`
- `mrp_upload_bp`
- `especial_navegacion_bp`
- `portal_bp`
- `vf_sync_bp`
- `admin_aliados_bp`
- `admin_usuarios_bp`
- `futbol_bp`

## Dominios y ownership tecnico

- Identidad VF/WA: `app.py` (`/verificar_registro`, `/primer_ingreso`), `embajadores_adapter.py`, `whatsapp_webhook.py`, `session_store.py`, `db.py`, `.agents/skills/voiceflow-project-rules/SKILL.md`.
- Entrega WhatsApp: `whatsapp_webhook.py`, `services/whatsapp_delivery_service.py`, `routes/special_reports_routes.py`, `embajadores_adapter.py`.
- Usuarios especiales/auth: `auth_web.py`, `decorators/require_auth_especial.py`, `routes/auth_special_routes.py`, `repositories/special_users_repository.py`, `services/special_user_*`.
- Reportes especiales: `routes/special_reports_routes.py`, `services/report_*`, `services/azure_blob_service.py`, `services/email_service.py`.
- Consultas agenticas: `routes/special_queries_routes.py`, `services/agentic_query_service.py`, `query_*`, `report_spec_service.py`.
- Formacion/FAQ legacy: rutas directas en `app.py` (`/siguiente_elemento`, `/formacion/*`, `/faq/*`, `/preguntas/*`).
- Futbol: `routes/futbol_routes.py` concentra jornadas, pronosticos, ranking, premios, export y endpoints VF.
- Retos sync/integracion PC: `docs/retos-sync/*` define propuesta y fases; `app.py` mantiene endpoints legacy de retos (`/RetoAnuncio`, `/actualizar_retos_refuerzo*`, exports); aun no existe blueprint productivo `routes/retos_sync_routes.py`.
- MRP/contenido: `routes/admin_mrp_routes.py`, `routes/mrp_upload_routes.py`, `_scripts/task*mrp*`, vistas/SQL y modulos de formacion.
- Admin portal: `frontend/src/app/components/admin/**`, `frontend/src/app/api/**`, `routes/admin_aliados_routes.py`, `routes/admin_usuarios_routes.py`, `routes/portal_routes.py`.
- Voiceflow sync/admin: `routes/voiceflow_sync_routes.py`, `services/voiceflow_sync_*`, `services/voiceflow_normalizer.py`.

## Rutas principales

- Health: `/`, `/api`, `/health`, `/health/db`, `/health/vf`, `/health/wa`, `/deploy-status`.
- WhatsApp: `/webhook/whatsapp`, `/webhook/whatsapp/status`, `/webhook/whatsapp/test`, `/enviar-plantilla`, `/enviar-plantilla-masivo`.
- Formacion: `/siguiente_elemento`, `/registrar_evento`, `/formacion/lista`, `/formacion/modulo`, `/formacion/pregunta`, `/formacion/validar_respuesta`.
- Registro: `/primer_ingreso`, `/verificar_registro`, `/registro/validar_input`, `/registro/verificar_id`.
- FAQ/Preguntas: `/faq/*`, `/preguntas/escritas`, `/preguntas/test`.
- Admin: `/admin/usuarios/*`, `/admin/aliados/*`, `/admin/mrp/*`, `/admin/voiceflow/*`.
- Especial: `/auth/*`, `/especial/consultas/*`, `/especial/reportes/*`, `/especial/navegacion/confirmar-alcance`.
- Futbol: `/futbol/*`.
- Export/download: multiples `/export/*` y `/download/*`.
- Portal: `/portal/`.
- Internos/envio: `/internal/broadcast-reto-trimestral`, `/enviar_mensaje_whatsapp`, `/enviar_imagen_whatsapp`, `/RetoAnuncio`.
- Admin masivo/data: `/api/validar-archivo`, `/api/procesar-actualizacion`, `/api/descargar-resultado`, `/admin/bulk-formaparro`, `/actualizar_retos_refuerzo*`.
- Retos sync propuestos (documentados, no implementados): `/api/retos/sync/lanzamiento`, `/api/retos/sync/seguimiento`, `/api/retos/sync/cierre`, `/api/retos/sync/cargas`, `/api/admin/retos/*`.

## Scripts disponibles

- Root `package.json`: `npm test` placeholder que falla intencionalmente.
- `frontend/package.json`: `pnpm dev`, `pnpm build`.
- `.replit`: run con Gunicorn; build con `pip install -r requirements.txt`; workflow `flask_server` ejecuta `uv add requests python-dotenv` (side effect).
- `build.sh`: script de build (pendiente de lectura antes de ejecutar).
- `orquestador`: wrapper shell versionado para transferir intencion hacia el orquestador local sin activar Replit Agent.
- `scripts/orchestrator_bridge.py`: genera handoffs JSON/MD en `docs/handoffs/`; no ejecuta Replit Agent, no lee `.env` y no modifica codigo funcional.
- `_scripts/*`: multiples migraciones y utilidades; no ejecutar sin autorizacion explicita.
- `_scripts/envio_10_30_bogota.py`: envio real por WhatsApp Cloud API; solo ejecutar con autorizacion explicita, secrets cargados y destinatarios confirmados.
- `tests/`: suite focalizada para futbol, Voiceflow sync y resolver UE WA; preferir tests especificos antes que suite total si hay dependencias externas.
- Root `pyproject.toml` y `requirements.txt` no estan perfectamente deduplicados; `requirements.txt` incluye `pytest`, `azure-storage-blob`, `Pillow`, `reportlab`, `resend`.
- Frontend: `frontend/package.json` usa Vite 6, React peer 18.3.1, MUI/Radix/Recharts/lucide/motion.

## Archivos sensibles o de cuidado

- `.env` esta ignorado y no existe en el clone; no crear ni leer si aparece.
- `.env.example` existe y solo debe usarse para nombres de variables.
- `certs/DigiCertGlobalRootCA.crt.pem` es certificado CA publico.
- Archivos `.xlsx`, `.json`, `.txt`, SQL y logs/reportes pueden contener datos reales o PII; revisar con cautela.
- `_scripts/*migrar*`, `migration_*.sql`, `fix_*.sql`, `admin_script_dual_compatibility.sql` pueden modificar DB.
