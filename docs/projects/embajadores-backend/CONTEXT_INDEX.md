# CONTEXT_INDEX - embajadores-backend

Indice de contexto por referencias. No reemplaza fuentes originales.

## Semantic Tag Index

- `SEMANTIC_TAG_INDEX.md`: indice canonico de etiquetas semanticas del proyecto. Fuente prioritaria para `semantic_context_gate` antes de busqueda libre.
- Cobertura v1: Voiceflow identity, WhatsApp delivery, usuarios especiales/reportes, auth/JWT, Azure MySQL, formacion, FAQ, futbol, retos-sync, MRP, Voiceflow sync, consultas agenticas, portal admin y Replit deployment.

## Documentacion encontrada

- `README.md`: quick start, endpoints iniciales, variables base y despliegue Replit/Azure.
- `replit.md`: vision mas actualizada; documenta arquitectura Flask, portal admin, Voiceflow, WhatsApp, Futbol, reportes, usuarios especiales, MRP y transcripcion VF.
- `docs/TECHNICAL_DOCUMENTATION.md`: documentacion tecnica extensa; contiene variables, arquitectura, endpoints y flujos.
- `frontend/src/app/api/APIContract.md`: contrato aspiracional/portal admin por dominios funcionales.
- Multiples documentos `.md` de troubleshooting e implementaciones Voiceflow/WhatsApp/FAQ/MRP.
- `.agents/skills/voiceflow-project-rules/SKILL.md`: reglas locales de Voiceflow; tratar como fuente relevante para flujos VF.
- `.agents/memory/ue-wa-session-resolver.md`: memoria local sobre resolver de telefono destino UE y `ue_wa_sessions`.
- `docs/handoffs/replit_diagnostic_ue_wa_session_hotfix.md`: handoff de diagnostico Replit para hotfix WA session.
- `frontend/src/docs/*` y `frontend/src/imports/*`: arquitectura/implementacion del portal admin; tratar como utiles pero potencialmente generados/aspiracionales.
- `_scripts/*.md`: documentacion operativa de formacion/Voiceflow/MRP; revisar antes de ejecutar scripts.
- `docs/retos-sync/*`: diagnostico y propuesta de integracion de retos periodicos con Puntos Colombia. Fuentes top: `propuesta_tecnica_integracion_retos.md`, `01_inventario_backend_actual.md`, `02_brechas_y_riesgos.md`, `03_alternativas_integracion.md`, `04_modelo_canonico_datos.md`, `05_endpoints_servicios_propuestos.md`, `06_preguntas_para_puntos_colombia.md`, `07_plan_habilitacion.md`.
- PDF local complementario: `C:\Users\murfe\Downloads\Embajadores - Alternativas de integrción Retos periodicos.pdf`; revisar si se instala/autoriza extractor PDF, no copiar valores sensibles.

## Codigo y configuracion encontrados

- `app.py`: Flask principal y gran concentracion de rutas legacy.
- `main.py`: entrypoint.
- `db.py`: conexion DB y helpers multi-proyecto.
- `whatsapp_webhook.py`: webhook y envio WhatsApp.
- `voiceflow_client.py`: cliente Voiceflow Runtime.
- `routes/`: blueprints separados.
- `services/`: servicios de IA, reportes, blob, email, sync y usuarios especiales.
- `frontend/`: portal admin React/Vite.
- `.replit`: Replit autoscale, Gunicorn, Python/Node/Postgres modules, workflows.
- `.github/workflows/main_embajadores-backend.yml`: deploy Azure Web App via OIDC.
- `auth_web.py`: login web especial, roles/JWT y permisos de alcance.
- `routes/futbol_routes.py`: dominio futbol completo (jornadas, pronosticos, ranking, premios, recalculos).
- `routes/voiceflow_sync_routes.py`: admin de sync/snapshots/diff/config/logs de Voiceflow.
- `routes/special_reports_routes.py`: generacion/entrega de reportes para usuarios especiales.
- `services/ue_session_service.py`: persistencia cross-worker de `ue_wa_sessions`.
- `services/voiceflow_normalizer.py`: normalizacion/diagnostico de API steps VF.
- `_scripts/task*.py`: migraciones/operaciones MRP con verificacion y rollback logico; no ejecutar sin autorizacion.
- `_scripts/envio_10_30_bogota.py`: script de envio WhatsApp programado a 10:30 Bogota para template `lanzamiento_reto_solo_texto` + imagen inline `opcion2`; requiere Meta secrets y tiene side effects externos.
- `docs/retos-sync/*`: no implementa endpoints; documenta modelo canonico propuesto (`retos_ciclos`, `retos_seguimiento`, `retos_cierre`, `retos_ganadores`, `retos_cargas_audit`) y rutas conceptuales `/api/retos/sync/*`.

## Fuentes ruidosas o sensibles

- Muchos `.xlsx`, `.txt`, `.json` versionados parecen reportes, trazabilidad o respuestas; no cargarlos al contexto normal.
- `.env.example` fue marcado como sensible; no copiar valores.
- `attached_assets/`, `tmp_reportes/`, `_archive/`, `.venv/` y caches no son contexto base.

## Evidencia operativa

- `git status -sb` en repo objetivo: limpio tras clonacion.
- `git status -sb` en orquestador: cambios esperados en registry y scaffold.
