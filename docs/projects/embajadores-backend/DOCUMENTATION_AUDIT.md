# DOCUMENTATION_AUDIT - embajadores-backend

Contraste documentacion-codigo inicial.

## Documentos vigentes o utiles

- `replit.md`: parece ser la fuente mas rica y actual; coincide con presencia de `routes/`, `services/`, `frontend/`, Voiceflow sync y futbol.
- `docs/TECHNICAL_DOCUMENTATION.md`: coincide con variables, componentes y endpoints principales observados.
- `README.md`: util para quick start, pero mas basico y posiblemente anterior al estado actual.
- `.replit`: coincide con runtime Flask/Gunicorn, Replit, secrets y puerto 5000.
- `.github/workflows/main_embajadores-backend.yml`: confirma Azure App Service deploy.
- `docs/retos-sync/*`: documentacion vigente de diagnostico/propuesta para integracion de retos periodicos con Puntos Colombia, generada en 2026-05-28 y alineada con el estado actual de tabla `retos`, endpoints legacy y servicios Azure Blob.

## Desalineaciones o incertidumbres

- `README.md` describe un microservicio inicial Voiceflow-Pinecone con pocos endpoints; el codigo actual es mucho mas grande y multi-modulo.
- `package.json` root no representa el stack principal; solo declara `resend` y `npm test` placeholder.
- `frontend/src/app/api/APIContract.md` documenta dominios admin amplios que pueden ser parcialmente aspiracionales frente a endpoints Flask reales.
- `.replit` incluye un workflow que ejecuta `uv add requests python-dotenv`, lo cual puede cambiar dependencias; no debe ejecutarse en alistamiento.
- `.env.example` no debe tratarse como plantilla segura: contiene valores aparentemente reales y requiere saneamiento antes de handoffs o difusion.
- Hay muchos reportes Excel versionados; no se verifico si contienen PII.
- `pyproject.toml` y `requirements.txt` tienen dependencias solapadas y posibles duplicados (`pytest`, `azure-storage-blob`); preferir `requirements.txt` para deploy Replit actual.
- `.agents/skills/voiceflow-project-rules/SKILL.md` contiene reglas confirmadas por logs que corrigen supuestos de docs historicas; debe prevalecer en temas VF.
- `frontend/src/imports/**` y `pasted_text/**` parecen material importado/generado; utiles para contexto de diseño, no necesariamente contrato vigente.

## Codigo importante no totalmente documentado en este primer pase

- `app.py` tiene muchas rutas directas y logica extensa que requiere mapa tecnico mas granular.
- `_scripts/` contiene migraciones y utilidades con impacto potencial en DB.
- `frontend/` requiere auditoria separada para alinear API real vs contrato.
- `routes/futbol_routes.py` es un subdominio grande con reglas propias de negocio y endpoints publicos/admin; requiere lectura focalizada antes de cambios.
- `routes/special_reports_routes.py` y servicios `report_*` tienen flujos de generacion, storage, limpieza y entrega multicanal; riesgo alto de side effects.
- `voiceflow_sync_routes.py`/`voiceflow_normalizer.py` agregan una capa admin de inspeccion VF que no esta reflejada en README basico.
- `docs/retos-sync/*` propone endpoints, tablas y jobs que aun no estan implementados; tratarlos como diseno/diagnostico, no como contrato productivo.
- El PDF adjunto de alternativas de integracion debe considerarse insumo de negocio/entrega; la fuente tecnica versionada revisable en codigo es `docs/retos-sync/propuesta_tecnica_integracion_retos.md`.

## Clasificacion inicial

- Nivel de contrastacion realizado: `B+` estructural profundo por referencias, con indexacion semantica v1.
- Nivel post-pull 2026-05-28: `B+` para contexto/documentacion de retos-sync; cambios funcionales revisados por diff, no por runtime.
- Suficiencia contextual: `buena_para_plan_y_diagnostico`; `parcial_para_build_funcional`.
- Requiere OpenCode/context-validator antes de cambios funcionales.

## Fuentes canonicas por tema

- Voiceflow API blocks/variables: `.agents/skills/voiceflow-project-rules/SKILL.md`.
- Arquitectura tecnica general: `docs/TECHNICAL_DOCUMENTATION.md` + `replit.md`.
- UE WA session resolver: `.agents/memory/ue-wa-session-resolver.md`.
- Portal admin: `frontend/src/docs/*`, `frontend/src/app/api/*`, `frontend/src/app/components/admin/**`.
- Replit runtime: `.replit`, `gunicorn.conf.py`, `replit.md`.
- Azure deploy: `.github/workflows/main_embajadores-backend.yml`.
- Retos periodicos / Puntos Colombia: `docs/retos-sync/propuesta_tecnica_integracion_retos.md` + documentos `01` a `07`; validar contra codigo antes de implementar.
