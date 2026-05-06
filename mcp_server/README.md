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

