# Handoff Build directo — diagnóstico timeouts MCP

- run_id: 20260508_shell_timeout_fix_6175
- source_agent: shell/manual-supervised
- target_agent: OpenCode builder
- model: opencode-go/kimi-k2.6
- mode: Build autorizado
- risk_level: medium
- scenario: debugging

## Objetivo

Diagnosticar y corregir los timeouts MCP -32001 que afectan el camino Continue → MCP.

Prioridad:
1. check_opencode_run_status / get_run_status
2. verify_master_files
3. orchestrator_preflight

## Contexto

El orquestador ya tiene:
- política Plan/Build formalizada;
- verify_master_files implementado;
- create_and_dispatch_opencode_handoff implementado;
- dispatcher validado por stdio.

El run 20260508_160833_9b543486 quedó bloqueado porque OpenCode rechazó permisos para ejecutar comandos de prueba. Esta ejecución directa busca validar un modo Build controlado.

## Alcance autorizado

Puedes modificar solo:
- mcp_server/server.py
- mcp_server/tools.py
- mcp_server/schemas.py
- mcp_server/README.md
- scripts/orchestrator_preflight.py
- scripts/verify_master_files.py
- scripts/get_run_status.py
- mcp_server/test_mcp_stdio.py
- mcp_server/test_get_run_status_stdio.py
- mcp_server/test_check_opencode_run_status_stdio.py
- mcp_server/test_verify_master_files_stdio.py

## Tareas

1. Reproducir o aislar por qué ciertas tools MCP generan timeout -32001 desde Continue.
2. Comparar scripts directos vs pruebas stdio.
3. Identificar si la causa probable es:
   - payload grande;
   - stdout excesivo;
   - proceso hijo sin cierre;
   - timeout fijo insuficiente;
   - respuesta MCP demasiado pesada;
   - alias inconsistente;
   - parsing lento.
4. Implementar mitigaciones acotadas:
   - respuestas compactas;
   - límites de preview;
   - campos resumidos;
   - timeouts razonables;
   - instrumentación elapsed_ms/stdout_bytes si aplica.
5. Mantener compatibilidad con herramientas existentes.
6. Ejecutar validaciones.

## Validaciones obligatorias

Ejecutar:
- python -m py_compile .\mcp_server\server.py
- python -m py_compile .\mcp_server\tools.py
- python -m py_compile .\mcp_server\schemas.py
- python -m py_compile .\scripts\orchestrator_preflight.py
- python -m py_compile .\scripts\verify_master_files.py
- python -m py_compile .\scripts\get_run_status.py
- python .\mcp_server\test_get_run_status_stdio.py
- python .\mcp_server\test_check_opencode_run_status_stdio.py
- python .\mcp_server\test_verify_master_files_stdio.py

## Restricciones

No secrets.
No premium/Replit.
No deployment.
No migraciones.
No acciones destructivas.
No mover/borrar/renombrar archivos maestros.
No push/merge.
No modificar archivos fuera del alcance.

## Resultado esperado

Reportar:
- causa probable;
- cambios aplicados;
- pruebas ejecutadas;
- resultado de verify_master_files;
- git status --short;
- commit sugerido.
