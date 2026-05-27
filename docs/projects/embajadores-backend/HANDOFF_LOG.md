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
