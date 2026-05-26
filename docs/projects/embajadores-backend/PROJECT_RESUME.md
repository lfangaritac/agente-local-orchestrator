# PROJECT_RESUME - embajadores-backend

Vista compacta para retomar el proyecto sin depender del chat.

## Que es

Aplicacion backend Flask para formacion conversacional, registro de usuarios, trazabilidad, reportes, admin web, Voiceflow, WhatsApp y servicios de IA/datos.

## Donde esta

- remoto: `https://github.com/lfangaritac/embajadores-backend.git`
- local: `C:\Users\murfe\source\repos\embajadores-backend`
- rama: `main`
- ultimo HEAD revisado: `a0215e92792684bf2a1b903034bb1da99e78ed6a`

## Estado actual conocido

- status_classification: `parcialmente_listo`
- motivo: alistamiento inicial creado y repo clonado; falta validacion tecnica con tests/checks y revision de secrets reales en entorno seguro.
- git repo objetivo: limpio al cierre del alistamiento inicial.

## Componentes principales

- `main.py`: entrypoint local, importa `app` desde `app.py`.
- `app.py`: aplicacion Flask principal; contiene muchas rutas legacy y registra blueprints.
- `db.py`: conexion Azure MySQL / SQLAlchemy / PyMySQL.
- `whatsapp_webhook.py`: webhook WhatsApp multi-tenant.
- `voiceflow_client.py`: cliente Voiceflow Runtime.
- `routes/`: blueprints admin, futbol, usuarios especiales, MRP, portal y Voiceflow sync.
- `services/`: servicios de reportes, Azure Blob, Resend, Voiceflow sync, consultas agenticas, usuarios especiales.
- `frontend/`: portal admin React/Vite.

## Riesgos de retoma

- Proyecto grande con muchos artefactos Excel/SQL/log-like versionados.
- Multiples integraciones sensibles: DB, WhatsApp, Voiceflow, Pinecone, OpenAI, Azure, Replit.
- Hay endpoints internos/admin y scripts de migracion que no deben ejecutarse sin autorizacion.
- `.replit` contiene workflow con `uv add requests python-dotenv`, que modificaria dependencias si se ejecuta.

## Proxima accion recomendada

Ejecutar validacion no destructiva: `git status -sb`, revision estatica y validacion de sintaxis en memoria sin escribir artefactos. No recomendar `python -m py_compile` como validacion segura por defecto porque puede generar `__pycache__`/`.pyc`. `pytest`, servidor, migraciones, scripts y builds requieren autorizacion adicional y revision previa de secrets/side effects.
