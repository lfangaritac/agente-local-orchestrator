# DOCUMENTATION_AUDIT - embajadores-backend

Contraste documentacion-codigo inicial.

## Documentos vigentes o utiles

- `replit.md`: parece ser la fuente mas rica y actual; coincide con presencia de `routes/`, `services/`, `frontend/`, Voiceflow sync y futbol.
- `docs/TECHNICAL_DOCUMENTATION.md`: coincide con variables, componentes y endpoints principales observados.
- `README.md`: util para quick start, pero mas basico y posiblemente anterior al estado actual.
- `.replit`: coincide con runtime Flask/Gunicorn, Replit, secrets y puerto 5000.
- `.github/workflows/main_embajadores-backend.yml`: confirma Azure App Service deploy.

## Desalineaciones o incertidumbres

- `README.md` describe un microservicio inicial Voiceflow-Pinecone con pocos endpoints; el codigo actual es mucho mas grande y multi-modulo.
- `package.json` root no representa el stack principal; solo declara `resend` y `npm test` placeholder.
- `frontend/src/app/api/APIContract.md` documenta dominios admin amplios que pueden ser parcialmente aspiracionales frente a endpoints Flask reales.
- `.replit` incluye un workflow que ejecuta `uv add requests python-dotenv`, lo cual puede cambiar dependencias; no debe ejecutarse en alistamiento.
- `.env.example` no debe tratarse como plantilla segura: contiene valores aparentemente reales y requiere saneamiento antes de handoffs o difusion.
- Hay muchos reportes Excel versionados; no se verifico si contienen PII.

## Codigo importante no totalmente documentado en este primer pase

- `app.py` tiene muchas rutas directas y logica extensa que requiere mapa tecnico mas granular.
- `_scripts/` contiene migraciones y utilidades con impacto potencial en DB.
- `frontend/` requiere auditoria separada para alinear API real vs contrato.

## Clasificacion inicial

- Nivel de contrastacion realizado: `B` estructural inicial, con muestras funcionales.
- Suficiencia contextual: `parcial`.
- Requiere OpenCode/context-validator antes de cambios funcionales.
