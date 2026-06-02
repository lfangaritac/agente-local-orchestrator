# HANDOFF_LOG - embajadores-backend

## Handoff inicial - 2026-05-26

- agente_emisor: `Codex`
- agente_receptor_sugerido: `OpenCode context-validator`
- objetivo: validar tecnicamente el alistamiento inicial y preparar siguiente fase de checks no destructivos.
- archivos_revisados:
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
- decision: no ejecutar cambios funcionales; continuar con validaciones read-only/compilacion si el usuario autoriza.
- riesgos:
  - secrets externos y DB productiva.
  - scripts de migracion y SQL.
  - reportes/Excel posiblemente con PII.
  - workflow Replit con side effects.
- pendiente:
  - autorizacion para validaciones.
  - posible handoff a Replit solo si se requiere runtime/preview/secrets reales.

## Revision bridge shell - 2026-05-26

- agente_emisor: `Codex`
- agente_receptor_sugerido: `Continue/Orquestador`
- objetivo: revisar criticamente el ultimo diff `a15042cea53863bef9d08e3619e60e1221ed825b`.
- archivos_revisados:
  - `.gitignore`
  - `orquestador`
  - `scripts/orchestrator_bridge.py`
- decision: aprobar el diff del bridge como mecanismo seguro de transferencia shell hacia el orquestador.
- validacion:
  - `python -B scripts\orchestrator_bridge.py --help`
- riesgos:
  - el wrapper `orquestador` no queda ejecutable en Git si se commitea con mode `100644`; en Replit se mitiga con `chmod +x ./orquestador`.
  - existen archivos del sistema de agentes sin trackear en el repo objetivo; requieren decision separada y no forman parte de este diff.
- pendiente:
  - completar resincronizacion de commits funcionales previos.
  - decidir si los archivos de reglas del orquestador deben versionarse en Embajadores o retirarse/ignorarse.

## Revision critica reportada - fix envio informes WA cross-worker - 2026-05-26

- agente_emisor: `Usuario/Replit`
- agente_receptor_sugerido: `Codex/OpenCode context-validator`
- objetivo: analizar el ajuste reportado para enviar informes al celular activo del usuario administrador cuando hay multiples workers.
- fuentes revisadas:
  - resumen operativo pegado por usuario.
  - codigo visible local tras `git fetch origin`.
  - `routes/special_reports_routes.py`
  - `services/special_user_recognition_service.py`
  - `decorators/require_auth_especial.py`
- decision: aprobacion tecnica con reservas; el diff real ya fue verificado en `origin/main`.
- rango revisado: `a15042cea53863bef9d08e3619e60e1221ed825b..460f557`.
- hallazgos:
  - La solucion DB-session es el enfoque correcto frente al fallo de memoria por worker.
  - El orden Capa 1.3 antes de `TrazaConversacion` es razonable para priorizar la sesion WA activa.
  - La migracion esta versionada en `_scripts/migrar_ue_wa_sessions.py` y usa `CREATE TABLE IF NOT EXISTS` con `PRIMARY KEY (ue_id)`.
  - Riesgo pendiente: la escritura de sesion no ocurre cuando `reconocer_por_celular` retorna desde cache.
  - Riesgo pendiente: si el body trae un celular valido pero stale, Capa 1 retorna antes de Capa 1.3.
  - Riesgo pendiente: Metodo 2 no persiste sesion cuando `wa_celular` se obtiene desde `identity_context` en lugar del body.
- pendiente:
  - Corregir o aceptar explicitamente los riesgos de cache hit/body stale/identity_context.
  - Ejecutar validacion local si se hace pull del remoto o si se crea worktree aislado.

## Handoff a Replit - diagnostico post-hotfix UE WA session - 2026-05-26

- agente_emisor: `Codex`
- agente_receptor_sugerido: `Replit Agent`
- objetivo: diagnosticar en Replit el commit `2812ff0` tras pull.
- archivo_handoff: `docs/handoffs/replit_diagnostic_ue_wa_session_hotfix.md`
- comandos_sugeridos:
  - `git status -sb`
  - `python -m pytest tests/test_resolver_celular_destino.py tests/test_ue_session_persistence.py -q`
  - `python -m pytest tests -q`
- restricciones:
  - no exponer `.env`, tokens, connection strings ni telefonos reales completos.
  - anonimizar telefonos si se reportan evidencias.
- resultado_local:
  - pruebas focalizadas: `11 passed`.
  - suite `tests/`: `54 passed, 1 skipped`.
  - suite completa: falla por tests en `_scripts/` que requieren Azure MySQL real.

## Retoma onboarding contextual - 2026-05-27

- agente_emisor: `Codex`
- agente_receptor_sugerido: `Continue/Codex + OpenCode context-validator`
- objetivo: retomar el onboarding de Embajadores con las nuevas reglas de contexto, gate semantico y sincronizacion por referencias.
- fuentes_revisadas:
  - `TARGET_PROJECT_CONTEXT_CONTRACT.md`
  - `PROJECT_REGISTRY.md`
  - `docs/protocols/PROJECT_ENABLEMENT_PROTOCOL.md`
  - `docs/protocols/CONTEXT_SYNC_PROTOCOL.md`
  - `docs/protocols/DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md`
  - `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`
  - `docs/lessons/GLOBAL_LESSONS_LEARNED.md`
  - `docs/projects/embajadores-backend/*`
- decision: onboarding contextual v1 listo para Plan/diagnostico y cambios pequenos acotados; Build funcional requiere gate, lectura focalizada y autorizacion segun umbral.
- validacion:
  - `semantic_context_gate` para la instruccion de retoma -> `status: ok`.
  - `project_context_indexer` read-only -> 13 tags, `changed: False`.
  - repo objetivo en `main...origin/main` sin cambios trackeados; mantiene archivos no trackeados del sistema de agentes.
- pendientes:
  - procesar retorno Replit sobre `2812ff05d88d06b0e03511ecdee974c2bb442e14` si existe.
  - decidir tratamiento de archivos no trackeados del sistema de agentes en el repo objetivo.
  - sanear/rotar secrets de `.env.example` con autorizacion humana.

## Sincronizacion post-pull retos-sync - 2026-05-28

- agente_emisor: `Codex`
- agente_receptor_sugerido: `Continue/Codex + OpenCode context-validator`
- objetivo: incorporar al contexto del orquestador los cambios remotos hasta `ffb8f3c`, con enfasis en integracion de retos periodicos y reglas de contexto.
- fuentes_revisadas:
  - `git log/diff 2812ff0..ffb8f3c`
  - `docs/retos-sync/propuesta_tecnica_integracion_retos.md`
  - `docs/retos-sync/01_inventario_backend_actual.md`
  - `docs/retos-sync/02_brechas_y_riesgos.md`
  - `docs/retos-sync/03_alternativas_integracion.md`
  - `docs/retos-sync/04_modelo_canonico_datos.md`
  - `docs/retos-sync/05_endpoints_servicios_propuestos.md`
  - `docs/retos-sync/07_plan_habilitacion.md`
  - diffs de `app.py`, `whatsapp_webhook.py`, `routes/futbol_routes.py`, `services/ue_session_service.py`, tests relevantes.
- decision: actualizar indices del orquestador y crear tag `retos.sync`; no ejecutar runtime, migraciones, envios, deploy ni tests con dependencias externas.
- validacion:
  - `semantic_context_gate` post-pull -> `status: ok`.
  - `project_context_indexer --apply` -> 14 tags, `retos.sync` agregado.
  - `embajadores-backend` actualizado por fast-forward a `ffb8f3c`.
- pendientes:
  - extraer/revisar PDF con parser autorizado si se requiere fidelidad documental del entregable externo.
  - validar runtime/tests focalizados solo con autorizacion y entorno seguro.
  - tratar secrets expuestos como comprometidos y rotarlos antes de operacion productiva.

## Implementacion doble sender WhatsApp Embajadores - 2026-06-02

- agente_emisor: `Codex`
- agente_receptor_sugerido: `Continue/Codex + OpenCode context-validator`
- objetivo: habilitar simultaneamente el numero WhatsApp actual y el numero legacy de Embajadores como senders independientes, sin mezclar datos ni credenciales de Summum.
- proyecto_objetivo: `embajadores-backend`
- fuentes_revisadas:
  - `AGENT_RULES.md`
  - `CONTINUE_USAGE_PROTOCOL.md`
  - `DEVELOPMENT_CHECKS.md`
  - `docs/protocols/SEMANTIC_CONTEXT_GATE_PROTOCOL.md`
  - `docs/projects/embajadores-backend/SYNC_STATUS.md`
  - `docs/projects/embajadores-backend/HANDOFF_LOG.md`
  - `whatsapp_webhook.py`
  - `app.py`
  - `_scripts/broadcast_reto_trimestral.py`
  - `_scripts/envio_10_30_bogota.py`
- contexto_previo:
  - `semantic_context_gate` ejecutado para la instruccion de doble sender WhatsApp -> `status: ok`, tag principal `whatsapp.delivery`.
  - `project_context_indexer --apply` ejecutado -> `changed: False`, 14 tags, sin cambios necesarios en `SEMANTIC_TAG_INDEX.md`.
- cambios:
  - `whatsapp_webhook.py`: se agregaron senders `EMBAJADORES_PRIMARY` y `EMBAJADORES_LEGACY`; ambos con `proyecto_id=1`; `SUMMUM` queda condicionado por `SUMMUM_WA_ENABLED`.
  - `whatsapp_webhook.py`: `send_template_message(...)` acepta `project_config` o `sender_label`; sin argumento usa `get_default_sender_config()`.
  - `whatsapp_webhook.py`: logs y metadata incluyen `sender_label`.
  - `app.py`: health/debug/broadcast usan sender default y exponen `default_sender`.
  - scripts proactivos: `_scripts/broadcast_reto_trimestral.py` y `_scripts/envio_10_30_bogota.py` usan `get_default_sender_config()`.
- validacion:
  - `python -m py_compile whatsapp_webhook.py app.py _scripts/broadcast_reto_trimestral.py _scripts/envio_10_30_bogota.py` -> exitoso.
  - `git diff --cached --name-only` antes del commit -> solo cuatro archivos del alcance.
  - `git push origin main` inicial -> rechazado por remoto adelantado; se hizo `git fetch origin main` + `git rebase origin/main`.
  - cambio local ajeno `routes/futbol_routes.py` preservado temporalmente con stash y restaurado despues del rebase.
- commit:
  - `a9e5efb Support dual WhatsApp senders for Embajadores`
  - push: `origin/main` actualizado de `f18d1be` a `a9e5efb`.
- estado_final:
  - repo objetivo `main...origin/main`.
  - persiste cambio local ajeno en `routes/futbol_routes.py`.
  - persisten archivos no trackeados del sistema de agentes en repo objetivo.
- pendientes:
  - configurar en Replit los secrets `EMBAJADORES_WA_LEGACY_PHONE_NUMBER_ID`, `EMBAJADORES_WA_LEGACY_WABA_ID`, `EMBAJADORES_WA_LEGACY_ACCESS_TOKEN`, `EMBAJADORES_WA_LEGACY_APP_SECRET`.
  - validar runtime real de inbound PRIMARY/LEGACY en Replit sin exponer secrets.
  - decidir tratamiento de archivos no trackeados del sistema de agentes en `embajadores-backend`.

## Sincronizacion post-Replit doble sender WhatsApp - 2026-06-02

- agente_emisor: `Codex`
- agente_receptor_sugerido: `Continue/Codex + OpenCode context-validator`
- objetivo: sincronizar el repositorio local de Embajadores despues de que `origin/main` avanzara con commits remotos posteriores al commit local `a9e5efb`.
- proyecto_objetivo: `embajadores-backend`
- contexto_previo:
  - repo objetivo local estaba en `a9e5efb`.
  - `git fetch origin main` detecto avance remoto hasta `88291e9`.
  - comparacion `main...origin/main`: `0 7`, local sin commits pendientes y remoto 7 commits adelante.
  - archivos remotos modificados no incluian `routes/futbol_routes.py`, que permanecia como cambio local ajeno.
- accion:
  - `git pull --ff-only origin main`.
- resultado:
  - fast-forward exitoso `a9e5efb..88291e9`.
  - nuevo HEAD local/remoto: `88291e9 Merge remote-tracking branch 'origin/main'`.
- estado_final:
  - `embajadores-backend`: `main...origin/main`.
  - persiste cambio local ajeno en `routes/futbol_routes.py`.
  - persisten archivos no trackeados del sistema de agentes en repo objetivo.
- pendientes:
  - revisar si los commits remotos posteriores agregaron validaciones/runtime relevantes para los dos senders.
  - decidir tratamiento de `routes/futbol_routes.py` local antes de futuras operaciones Git sensibles.
