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

Uso esperado desde Continue (compact-first):

1. Ejecutar `run_diagnostic_flow` con `with_opencode=false`.
2. Tomar el `run_id`.
3. Ejecutar `start_opencode_from_handoff_async` con ese `run_id`.
4. Esperar unos segundos.
5. Ejecutar `get_run_status` o `check_opencode_run_status` para confirmar (con **conteos y flags**) si ya existe salida en `agent_outputs/` y `raw_outputs/`.

Nota: `show_latest_run` imprime `RUN_SUMMARY.md` y `TRACE.md` completos y puede ser demasiado verboso para el chat de Continue. Usarlo solo si el usuario pide detalle y en modo **preview-only** (resumen/pedazos cortos).

Esta herramienta devuelve inmediatamente `status: started` y registra logs en:

    docs/agent_runs/<run-id>/background/

<!-- START: MCP_ASYNC_OPENCODE_USAGE_V0_1 -->

---

## Uso recomendado con OpenCode asíncrono desde Continue

Para usar OpenCode real desde Continue, usar el patrón (compact-first):

1. `run_diagnostic_flow` con `with_opencode=false`.
2. `start_opencode_from_handoff_async` con el `run_id`.
3. `check_opencode_run_status` (o `get_run_status`) con el mismo `run_id`.
4. (Opcional) `show_latest_run` solo si se necesita detalle y el usuario lo solicita.

### Herramienta async

    start_opencode_from_handoff_async

### Por qué existe

Las llamadas MCP bloqueantes con OpenCode pueden ser largas o producir salida extensa.

La herramienta async devuelve inmediatamente `status: started` y deja que OpenCode registre resultados en segundo plano.

### Logs

La herramienta escribe logs en:

    docs/agent_runs/<run-id>/background/

### Resultado final

El resultado se consulta preferentemente con:

    check_opencode_run_status

(Respuesta compacta con existencia/conteos.)

Si el usuario requiere detalle, usar:

    show_latest_run

y debe reflejar:

- `agent_outputs/`;
- `raw_outputs/`;
- `TRACE.md`;
- `RUN_SUMMARY.md`.

<!-- END: MCP_ASYNC_OPENCODE_USAGE_V0_1 -->


---

## Herramienta compacta de estado de run

Para evitar que Continue use comandos de terminal o respuestas demasiado extensas, se agregó:

    get_run_status

Uso recomendado desde Continue:

    Usa el MCP agente-local-orchestrator para ejecutar get_run_status con run_id=<run-id>. Devuélveme solo status, opencode_registered, counts, agents_in_trace y files.

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

## Alias semántico para estado de OpenCode

Para facilitar que Continue seleccione la herramienta correcta, se agregó el alias:

    check_opencode_run_status

Esta herramienta usa internamente la misma lógica de `get_run_status`, pero su nombre es más explícito para validar si OpenCode ya dejó resultados registrados.

Uso recomendado desde Continue:

    Usa exclusivamente la herramienta MCP check_opencode_run_status del servidor agente-local-orchestrator con run_id=<run-id>. No uses show_latest_run. No uses terminal. Devuelve solo status, opencode_registered, counts y agents_in_trace.

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

    Usa la herramienta MCP verify_master_files del servidor agente-local-orchestrator. Devuélveme solo summary: total_checked, total_existing, total_missing, all_ok, duplicate_candidates.

### Detección de duplicidad

Si existen tanto `AGENT_ORCHESTRATION.md` en raíz como `docs/AGENT_ORCHESTRATION.md`, la herramienta reporta `duplicate_candidates` con los hashes de ambos archivos para decidir cuál prevalece según el contrato de contexto.

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
