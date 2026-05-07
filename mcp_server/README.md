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

Uso esperado desde Continue:

1. Ejecutar `run_diagnostic_flow` con `with_opencode=false`.
2. Tomar el `run_id`.
3. Ejecutar `start_opencode_from_handoff_async` con ese `run_id`.
4. Esperar unos segundos.
5. Ejecutar `show_latest_run` para revisar `TRACE.md`, `RUN_SUMMARY.md`, `agent_outputs/` y `raw_outputs/`.

Esta herramienta devuelve inmediatamente `status: started` y registra logs en:

    docs/agent_runs/<run-id>/background/

<!-- START: MCP_ASYNC_OPENCODE_USAGE_V0_1 -->

---

## Uso recomendado con OpenCode asíncrono desde Continue

Para usar OpenCode real desde Continue, usar el patrón en tres pasos:

1. `run_diagnostic_flow` con `with_opencode=false`.
2. `start_opencode_from_handoff_async` con el `run_id`.
3. `show_latest_run` con el mismo `run_id`.

### Herramienta async

    start_opencode_from_handoff_async

### Por qué existe

Las llamadas MCP bloqueantes con OpenCode pueden ser largas o producir salida extensa.

La herramienta async devuelve inmediatamente `status: started` y deja que OpenCode registre resultados en segundo plano.

### Logs

La herramienta escribe logs en:

    docs/agent_runs/<run-id>/background/

### Resultado final

El resultado se consulta con:

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
