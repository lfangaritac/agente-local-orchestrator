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
