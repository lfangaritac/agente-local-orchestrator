# MCP Server — Agente Local Orchestrator

## Propósito

Servidor MCP local para exponer herramientas diagnósticas del orquestador `C:\Agente` a Continue.

## Estado

Fase v0.1. Implementación inicial segura.

## Herramientas expuestas

- `orchestrator_preflight`
- `select_agent_model`
- `build_handoff_package`
- `run_diagnostic_flow`
- `show_latest_run`
- `run_opencode_from_handoff`
- `start_opencode_from_handoff_async`
- `get_run_status`
- `check_opencode_run_status`
- `run_health_check`
- `verify_master_files`
- `create_and_dispatch_opencode_handoff`

## Restricciones

Esta fase no permite:

- comandos arbitrarios;
- edición de código funcional;
- secrets;
- deployment;
- migraciones;
- borrado de archivos;
- escalamiento premium automático.

## Prueba local

Ejecutar:

    cd C:\Agente
    python .\mcp_server\tools.py --self-test

Validar sintaxis:

    python -m py_compile .\mcp_server\server.py
    python -m py_compile .\mcp_server\tools.py
    python -m py_compile .\mcp_server\schemas.py

## Ejecución del servidor

    cd C:\Agente
    python .\mcp_server\server.py

El servidor opera por stdio y está pensado para ser invocado por Continue como MCP server local.

## Configuración futura en Continue

La configuración exacta debe validarse contra la versión instalada de Continue.

La idea objetivo será registrar un MCP server local que ejecute:

    python C:\Agente\mcp_server\server.py

## Principio

MCP debe aumentar automatización sin reducir control humano, trazabilidad ni seguridad.

Nota operativa (eficiencia): `docs/agent_runs/**` y `docs/agent_queue/inbox/**` son artefactos **operacionales** (evidencia local/temporal). La trazabilidad versionada debe mantenerse liviana en `docs/context/*` (p. ej. `RUN_INDEX.md`).

<!-- START: MCP_STDIO_VALIDATION_V0_1 -->

---

## Validación local por stdio

Antes de conectar con Continue, validar el servidor MCP local con:

    cd C:\Agente
    python .\mcp_server\test_mcp_stdio.py

### Resultado esperado

La prueba debe devolver:

    initialize_ok: true
    tools_list_ok: true
    preflight_call_ok: true
    select_agent_model_ok: true
    run_diagnostic_flow_ok: true

### Resultado validado

La validación inicial fue exitosa y confirmó que el servidor puede:

- responder `initialize`;
- listar herramientas con `tools/list`;
- ejecutar `orchestrator_preflight`;
- ejecutar `select_agent_model`;
- ejecutar `run_diagnostic_flow` sin OpenCode;
- devolver resultados estructurados por JSON-RPC.

### Run generado en validación

La primera prueba generó:

    run_id: 20260506_122350_1c5cc272

### Próxima prueba

Conectar el servidor MCP local en Continue y validar que desde el chat se puedan invocar herramientas diagnósticas sin copiar comandos manualmente.

<!-- END: MCP_STDIO_VALIDATION_V0_1 -->


---

## Herramienta async para OpenCode

Cuando Continue invoca OpenCode directamente desde una herramienta MCP, la llamada puede tardar demasiado o producir salida extensa.

Para evitar bloqueos se agregó:

    start_opencode_from_handoff_async

Flujo operativo Continue → MCP (patrón async, mensajes sugeridos y regla de fallback): ver `docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md` (sección 9 + anexo async).

Resumen técnico: este tool inicia OpenCode en segundo plano; luego se consulta estado de forma **compact-first** con:

1) `run_health_check` (salud rápida del run)
2) `check_opencode_run_status` (seguimiento específico de OpenCode)
3) `get_run_status` (diagnóstico ampliado)

`show_latest_run` queda como fallback (*preview-only*).

Nota: `show_latest_run` imprime `RUN_SUMMARY.md` y `TRACE.md` completos y puede ser demasiado verboso para el chat de Continue. Usarlo solo si el usuario pide detalle y en modo **preview-only** (resumen/pedazos cortos).

Esta herramienta devuelve inmediatamente `status: started` y registra logs en:

    docs/agent_runs/<run-id>/background/

<!-- START: MCP_ASYNC_OPENCODE_USAGE_V0_1 -->

---

## OpenCode asíncrono (resumen técnico)

- `start_opencode_from_handoff_async` inicia OpenCode en segundo plano y registra logs en `docs/agent_runs/<run-id>/background/`.
- Diagnóstico inicial (default compact-first): `run_health_check`.
- Seguimiento específico de OpenCode: `check_opencode_run_status`.
- Diagnóstico ampliado: `get_run_status`.
- `show_latest_run` queda como **fallback** (*preview-only* y bajo solicitud explícita), porque puede imprimir `TRACE.md`/`RUN_SUMMARY.md` completos.

Flujo operativo Continue → MCP (pasos y mensajes sugeridos): `docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md`.

<!-- END: MCP_ASYNC_OPENCODE_USAGE_V0_1 -->


---

## Herramienta compacta de salud de run (default)

Para diagnóstico rápido de salud (missing/partial/healthy/stale/failed) sin abrir artefactos completos, se agregó:

    run_health_check

Uso: llamar `run_health_check` con `run_id` como **primera consulta**.

---

## Herramienta compacta de estado de run (diagnóstico ampliado)

Para un diagnóstico más amplio (flags/rutas/conteos adicionales), usar:

    get_run_status

Uso: llamar `get_run_status` con `run_id` cuando `run_health_check` no sea suficiente.

Esta herramienta devuelve un JSON compacto con:

- existencia de handoff;
- existencia de RUN_SUMMARY.md;
- existencia de TRACE.md;
- conteo de agent_outputs;
- conteo de raw_outputs;
- conteo de background logs;
- agentes detectados en TRACE;
- si OpenCode quedó registrado.

---

## Herramienta compacta para estado de OpenCode (seguimiento específico)

Para consultar rápido (y sin payloads grandes) si OpenCode ya dejó resultados registrados, usar:

    check_opencode_run_status

Esta herramienta es **compact-first** por defecto y evita lecturas completas de `raw_outputs/**`, `TRACE.md` o `RUN_SUMMARY.md` (solo usa prefijos cortos para inferir `latest_status`).

Uso: llamar `check_opencode_run_status` con `run_id` como **seguimiento** cuando se espera salida de OpenCode.

---

## Herramienta de anclaje de realidad: verify_master_files

Para reducir el riesgo de alucinaciones o diagnósticos falsos por visibilidad parcial del IDE, se agregó:

    verify_master_files

Esta herramienta verifica físicamente la existencia e integridad SHA-256 de los archivos maestros críticos del orquestador.

### Archivos verificados por defecto

- `TARGET_PROJECT_CONTEXT_CONTRACT.md`
- `PROJECT_REGISTRY.md`
- `AGENT_RULES.md`
- `MODEL_ROUTING.md`
- `AGENT_ORCHESTRATION.md`
- `docs/AGENT_ORCHESTRATION.md`
- `CONTINUE_USAGE_PROTOCOL.md`
- `REPLIT_HANDOFF.md`
- `docs/protocols/PROJECT_ENABLEMENT_PROTOCOL.md`
- `docs/protocols/CONTEXT_SYNC_PROTOCOL.md`
- `docs/protocols/DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md`
- `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md`
- `docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md`
- `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`
- `docs/lessons/GLOBAL_LESSONS_LEARNED.md`

### Uso desde Continue

Por defecto, `verify_master_files` devuelve un **output compacto** (compact-first) para minimizar payload y evitar timeouts.

- Modo compacto (default): `mode="compact"`
- Modo completo (solo si hace falta detalle): `mode="full"`

Ejemplo (compact):

    Usa la herramienta MCP verify_master_files del servidor agente-local-orchestrator. mode="compact". Devuélveme: total_checked, total_existing, total_missing, all_ok, accepted_reference_pairs_count.

### Detección de duplicidad

- `accepted_reference_pairs`: pares canónico→referencia/stub **aceptados** (p. ej. `AGENT_ORCHESTRATION.md` → `docs/AGENT_ORCHESTRATION.md`).
- `duplicate_candidates`: duplicidades **potencialmente problemáticas** (no aceptadas) con hashes para evaluación.

### Restricciones

- No mueve, elimina ni renombra archivos.
- Bloquea rutas fuera de ROOT.
- Opera únicamente en modo lectura.

---

## Herramienta de despacho de handoffs a OpenCode

Para eliminar la manualidad de transportar handoffs entre Continue y OpenCode, se agregó:

    create_and_dispatch_opencode_handoff

Esta herramienta:

1. Crea un paquete de handoff en `docs/agent_queue/inbox` (JSON + MD).
2. Inicializa `TRACE.md` y `RUN_SUMMARY.md` en `docs/agent_runs/<run_id>/`.
3. Si requiere autorización y no fue concedida, devuelve `waiting_authorization` sin despachar.
4. Si está autorizada, despacha OpenCode en segundo plano y devuelve `dispatched`.

### Input mínimo

- `project_id`
- `objective`
- `target_agent`
- `model`
- `risk_level`
- `scenario`

### Opcional

- `handoff_body`
- `allowed_files`
- `validation_commands`
- `requires_authorization`
- `authorization_granted`

**Build low-risk (peligroso; default false):**

- `auto_approve_permissions` (si true, usa internamente `opencode.cmd run --dangerously-skip-permissions`)
- `build_authorized` (debe ser true si `auto_approve_permissions=true`)
- `user_authorized_build` (debe ser true si `auto_approve_permissions=true`)

Guardrails: solo debe usarse con `risk_level=low` y `allowed_files` no vacío y acotado a rutas exactas (sin wildcards). Además requiere `build_authorized=true` y `user_authorized_build=true`. Si los guardrails fallan, el dispatch queda `blocked`.

Nota operativa: en **Build autorizado**, preferir este camino (Continue → MCP → OpenCode) en lugar de aplicar diffs interactivos en VS Code/Continue que requieran múltiples Accept/Reject.

### Output

- `ok`
- `status` (`waiting_authorization` o `dispatched`)
- `run_id`
- `handoff_json_path`
- `handoff_md_path`
- `run_dir`
- `trace_path`
- `summary_path`
- `background_meta_path`
- `target_agent`
- `model`
- `next_tool` (`check_opencode_run_status`)
- `user_message`

### Uso desde Continue

    Usa la herramienta MCP create_and_dispatch_opencode_handoff con project_id=orchestrator, objective="Revisar diff de seguridad", target_agent=security-reviewer, model=opencode-go/qwen3.6-plus, risk_level=high, scenario=security, requires_authorization=true, authorization_granted=false.

Si está en espera de autorización, Continue debe pedir confirmación al usuario y reintentar con `authorization_granted=true`.
