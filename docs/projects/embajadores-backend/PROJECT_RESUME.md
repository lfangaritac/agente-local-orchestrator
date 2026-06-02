# PROJECT_RESUME - embajadores-backend

Vista compacta para retomar el proyecto sin depender del chat.

## Que es

Aplicacion backend Flask para formacion conversacional, registro de usuarios, trazabilidad, reportes, admin web, Voiceflow, WhatsApp y servicios de IA/datos.

## Donde esta

- remoto: `https://github.com/lfangaritac/embajadores-backend.git`
- local: `C:\Users\murfe\source\repos\embajadores-backend`
- rama: `main`
- ultimo HEAD revisado: `ffb8f3cd76e87601a0487b2043a7e3ff209ed0cf`

## Estado actual conocido

- status_classification: `parcialmente_listo`
- motivo: onboarding contextual integral v1 sincronizado hasta `ffb8f3cd76e87601a0487b2043a7e3ff209ed0cf`; incluye retoma de docs `retos-sync` y cambios recientes de futbol/WhatsApp/UE sessions. Falta validacion runtime completa en entorno seguro y saneamiento/rotacion de secrets expuestos.
- git repo objetivo: `main...origin/main` limpio en cambios trackeados; conserva archivos no trackeados del sistema de agentes copiados por alistamiento.

## Componentes principales

- `main.py`: entrypoint local, importa `app` desde `app.py`.
- `app.py`: aplicacion Flask principal; contiene muchas rutas legacy y registra blueprints.
- `db.py`: conexion Azure MySQL / SQLAlchemy / PyMySQL.
- `whatsapp_webhook.py`: webhook WhatsApp multi-tenant.
- `voiceflow_client.py`: cliente Voiceflow Runtime.
- `routes/`: blueprints admin, futbol, usuarios especiales, MRP, portal y Voiceflow sync.
- `services/`: servicios de reportes, Azure Blob, Resend, Voiceflow sync, consultas agenticas, usuarios especiales.
- `frontend/`: portal admin React/Vite.

## Dominios funcionales indexados

- `voiceflow.identity`: `{userId}` literal, `wa_id`, `wa_from`, `identity_context`, `/verificar_registro`, `/primer_ingreso`.
- `whatsapp.delivery`: webhook, entrega multimedia/documentos, reportes por WhatsApp, limites de formato.
- `reports.special_users`: usuarios especiales, reportes, alcance, roles, entrega por WA/email.
- `auth.jwt`: login web especial, JWT, roles, permisos y decoradores.
- `db.mysql`: Azure MySQL, PyMySQL/SQLAlchemy, scripts SQL, migraciones y tablas criticas.
- `training.flow`: formacion, modulos, recursos, preguntas, eventos y validacion.
- `faq.questions`: FAQ, preguntas escritas, siguiente pregunta y respuestas.
- `football.challenge`: jornadas, pronosticos, ranking, premios y recalculos.
- `retos.sync`: integracion de retos periodicos con Puntos Colombia, alternativas API Push/SFTP/Azure Blob, modelo canonico, auditoria de cargas y plan de habilitacion.
- `mrp.content`: MRP por aliado, orden de contenidos, uploads, migraciones `_scripts/task*`.
- `voiceflow.sync`: snapshots, api steps, diff, diagnostics y webhook `project-published`.
- `ai.agentic_reports`: consultas agenticas/OpenAI, specs de reporte y ejecucion SQL controlada.
- `admin.portal`: portal React/Vite, modulos admin, API client y contrato aspiracional.
- `replit.deployment`: Replit autoscale/Gunicorn, workflow con side effect, post-merge.

## Riesgos de retoma

- Proyecto grande con muchos artefactos Excel/SQL/log-like versionados.
- Multiples integraciones sensibles: DB, WhatsApp, Voiceflow, Pinecone, OpenAI, Azure, Replit.
- Hay endpoints internos/admin y scripts de migracion que no deben ejecutarse sin autorizacion.
- `.replit` contiene workflow con `uv add requests python-dotenv`, que modificaria dependencias si se ejecuta.
- `README.md` es historico/parcial; `replit.md`, `docs/TECHNICAL_DOCUMENTATION.md` y reglas `.agents` son fuentes de mayor actualidad.
- `frontend/src/app/api/APIContract.md` es util pero puede ser aspiracional frente a endpoints Flask reales.
- `routes/futbol_routes.py` y `_scripts/task*mrp*` contienen logica con impacto DB; requieren revision puntual antes de tocar.
- El caso UE WA cross-worker depende de `ue_wa_sessions` y de reglas Voiceflow sobre `{userId}`; revisar `SEMANTIC_TAG_INDEX.md`, `.agents/memory/ue-wa-session-resolver.md` y skill local antes de cambios.
- Los documentos `docs/retos-sync/*` son diagnostico/propuesta; no equivalen a implementacion aprobada. Migraciones, endpoints `/api/retos/sync/*`, jobs Blob/SFTP y seleccion de ganadores requieren decision humana y autorizacion.
- `_scripts/envio_10_30_bogota.py` envia mensajes WhatsApp reales; no ejecutarlo sin confirmar destinatarios, horario, templates y secrets Meta.

## Proxima accion recomendada

Para cualquier instruccion nueva: ejecutar `semantic_context_gate` primero. Si el gate devuelve tags relevantes, leer fuentes top. Para Build funcional: validar alcance, revisar side effects y usar tests focalizados; no correr migraciones, workflows, endpoints de envio ni deploy sin autorizacion.
