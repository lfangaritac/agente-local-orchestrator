# CURRENT_FRONTIER - embajadores-backend

- last_updated: `2026-05-28`
- status: `context_onboarding_v1_ready`

## Instruccion/objetivo agotado

- Registrar Embajadores Backend en el orquestador.
- Crear scaffold documental.
- Clonar repo en ruta local autorizada.
- Hacer analisis integral inicial sin modificar codigo funcional.

## Resultado hasta el umbral

- Proyecto registrado en `PROJECT_REGISTRY.md`.
- Scaffold creado en `docs/projects/embajadores-backend/`.
- Repo clonado en `C:\Users\murfe\source\repos\embajadores-backend`.
- Stack, estructura, entrypoints, scripts, rutas, variables, integraciones y riesgos iniciales identificados por lectura.
- No se tocaron `.env`, secrets, dependencias, migraciones, deployment, commits ni push.

## Umbral actual

- blocking_threshold: `runtime_or_security_authorization_required`
- why_blocked:
  - El onboarding contextual queda sincronizado hasta `ffb8f3cd76e87601a0487b2043a7e3ff209ed0cf`, pero no sustituye validacion runtime ni decisiones de implementacion.
  - `.env.example` contiene valores aparentemente reales; no debe copiarse ni enviarse a handoffs/modelos externos y requiere saneamiento/rotacion autorizada.
  - Validaciones mas profundas pueden requerir ejecucion de Python/pytest y potencialmente import de app con side effects de bootstrap.
  - Cualquier ejecucion con DB/WhatsApp/Voiceflow/Pinecone/OpenAI/Azure necesita entorno seguro y secrets sin exponer.
  - Cambios funcionales estan fuera del alcance autorizado.

## Proxima accion recomendada

- next_action: para cualquier nueva instruccion, ejecutar `semantic_context_gate`, leer fuentes top y decidir Plan/Build. Para retos periodicos/Puntos Colombia, leer `docs/retos-sync/*` y tratarlo como diagnostico/propuesta hasta autorizacion de diseno/Build. Sanear/rotar secrets expuestos antes de usar entorno real.
- requires_user_action: si, autorizar comandos concretos.
- suggested_agent: `OpenCode context-validator`
- suggested_model_line: `Go` para validacion read-only y cambios acotados; seguridad/secrets requiere revision humana y posible premium si se prepara remediacion de historial.

## Referencias

- `PROJECT_PROFILE.md`
- `CODE_CONTEXT_MAP.md`
- `DOCUMENTATION_AUDIT.md`
- `CRITICAL_ALERTS.md`
- `SYNC_STATUS.md`

## Retoma 2026-05-26

- repo objetivo limpio en `main`.
- HEAD detectado: `a71fa8687c9c928e3b0701394bbaaefdbcad2be8`.
- commits nuevos desde el alistamiento inicial: cambios en `.gitignore`, `README.md`, `app.py`, `routes/special_reports_routes.py`, `tests/test_futbol_endpoints.py`, `whatsapp_webhook.py` y adjuntos en `attached_assets/`.
- alerta nueva: `.env.example` no esta saneado; contiene valores aparentemente reales.

## Revision diff bridge 2026-05-26

- ultimo commit revisado: `a15042cea53863bef9d08e3619e60e1221ed825b` (`Add orchestrator shell bridge`).
- archivos del diff: `.gitignore`, `orquestador`, `scripts/orchestrator_bridge.py`.
- resultado: aprobado con reservas menores; el bridge es de alcance acotado, no activa Replit Agent, no lee `.env`, no ejecuta diagnosticos amplios y genera handoffs en `docs/handoffs/`.
- validacion ejecutada: `python -B scripts\orchestrator_bridge.py --help`.
- hallazgo separado: el workspace local de Embajadores conserva archivos del sistema de agentes sin trackear (`AGENT_RULES.md`, `.continue/`, `REPLIT_HANDOFF.md`, etc.). No forman parte del commit aprobado y deben decidirse explicitamente: ignorar, eliminar de workspace o incorporar en un commit separado.

## Revision fix WA cross-worker 2026-05-26

- estado: `verificado_en_origin_main_con_reservas`
- rango revisado: `a15042cea53863bef9d08e3619e60e1221ed825b..460f557`
- commit principal: `74a77c40a455afa6e5a4e34aec9e91f25fd6c432` (`Implement cross-worker communication for user session management`).
- objetivo funcional: enviar informes WhatsApp al `wa_from` activo del administrador aun cuando Gunicorn atienda el reporte desde otro worker.
- implementacion verificada: tabla/migracion `ue_wa_sessions`, servicio `services/ue_session_service.py`, escritura desde reconocimiento por celular, escritura desde `require_auth_especial` Metodo 2 con celular valido, Capa 1.3 del resolver antes de `TrazaConversacion`, test T08 para cross-worker.
- dictamen: arquitectura correcta para el fallo cross-worker; no se detecto regresion obvia en el flujo principal reportado.
- reservas tecnicas:
  - `reconocer_por_celular` retorna desde cache antes de refrescar `ue_wa_sessions`; una conversacion activa cercana al TTL podria perder la sesion DB cross-worker.
  - La Capa 1 del body sigue precediendo a la sesion DB; si VF envia un celular valido pero stale, la sesion activa no gana.
  - `require_auth_especial` escribe sesion DB cuando Metodo 2 recibe celular valido, pero no cuando recupera `wa_celular` desde `identity_context`.
  - Logs internos aun imprimen telefonos completos; no copiar a handoffs externos sin anonimizar.

## Hotfix persistencia UE WA session 2026-05-26

- estado: `implementado_y_pusheado`
- commit: `2812ff0` (`Refresh UE WhatsApp session persistence`)
- objetivo: cerrar los huecos residuales de persistencia cross-worker sin asumir que `{userId}` de Voiceflow se sustituye como telefono.
- documentacion consultada antes del ajuste:
  - `docs/TECHNICAL_DOCUMENTATION.md`: `{userId}` no se sustituye en API blocks; identidad por `TipoId + NumeroId`.
  - `.agents/skills/voiceflow-project-rules/SKILL.md`: no crear/inferir variables de telefono; `wa_from` real lo captura el webhook.
- cambios:
  - cache-hit de `reconocer_por_celular` refresca `_ue_session_phone` y `ue_wa_sessions`.
  - Capa 1.6 de `require_auth_especial` persiste `wa_from` en `ue_wa_sessions` cuando lo resuelve desde `identity_context`.
  - agregado `tests/test_ue_session_persistence.py`.
  - agregado handoff `docs/handoffs/replit_diagnostic_ue_wa_session_hotfix.md` para que Replit diagnostique el resultado.
- validaciones:
  - `python -m pytest tests/test_resolver_celular_destino.py tests/test_ue_session_persistence.py -q` -> `11 passed`.
  - `python -m pytest tests -q` -> `54 passed, 1 skipped`.
  - `python -m pytest -q` -> falla por `_scripts/test_*` que intentan Azure MySQL/engine real; no atribuible al hotfix.

## Retoma onboarding contexto 2026-05-27

- estado: `context_onboarding_v1_ready`
- HEAD objetivo detectado/revisado: `2812ff05d88d06b0e03511ecdee974c2bb442e14`.
- `semantic_context_gate` ejecutado para la instruccion de retoma; fuentes top: `SEMANTIC_TAG_INDEX.md`, `PROJECT_RESUME.md`, `CURRENT_FRONTIER.md`, `CODE_CONTEXT_MAP.md`, `DOCUMENTATION_AUDIT.md`, `docs/TECHNICAL_DOCUMENTATION.md` y `.agents/skills/voiceflow-project-rules/SKILL.md`.
- `project_context_indexer` ejecutado en modo read-only; resultado: 13 tags, `changed: False`.
- siguiente frontera segura: operar por referencias y lectura focalizada; no hacer Build funcional, runtime, migraciones, deploy, endpoints de envio ni manejo de secrets sin autorizacion.

## Sincronizacion post-pull retos-sync 2026-05-28

- estado: `synced_to_ffb8f3c_context_retoma`
- HEAD objetivo detectado/revisado: `ffb8f3cd76e87601a0487b2043a7e3ff209ed0cf`.
- rango incorporado: 27 commits desde `2812ff0`; incluye docs `docs/retos-sync/*`, ajustes futbol, refresco UE session desde webhook, script de envio WhatsApp programado y assets adjuntos.
- `semantic_context_gate` para retoma post-pull: fuentes top `docs/retos-sync/propuesta_tecnica_integracion_retos.md`, `03_alternativas_integracion.md`, `07_plan_habilitacion.md`, `CURRENT_FRONTIER.md`, `CODE_CONTEXT_MAP.md`, `CONTEXT_INDEX.md`.
- `project_context_indexer --apply`: 14 tags; nuevo tag `retos.sync`; se ajustaron reglas para evitar falsos positivos de tags AIP/privacy.
- PDF adjunto identificado en Downloads; no extraido por falta de parser PDF local. Usar como insumo complementario y preferir Markdown versionado para trazabilidad.
