# MCP_CONTINUE_INTEGRATION_PROTOCOL.md

## 1. Propósito

Definir el protocolo técnico para integrar el orquestador local `C:\Agente` con Continue mediante un servidor MCP local.

El objetivo es que el usuario pueda operar desde un solo chat en VS Code, usando Continue como punto de entrada, mientras el orquestador ejecuta herramientas locales para:

- identificar proyecto objetivo;
- consultar contexto;
- consultar alertas;
- consultar lecciones;
- seleccionar agente/modelo;
- crear paquetes de handoff;
- invocar OpenCode de forma controlada;
- registrar resultados;
- mostrar trazabilidad;
- solicitar autorización humana cuando aplique.

## 2. Principio central

La integración MCP no reemplaza el gobierno documental ni la capa semiautomática existente.

El MCP debe exponer como herramientas las capacidades que ya fueron probadas por scripts locales.

El objetivo no es saltar directamente a ejecución autónoma, sino permitir que Continue invoque esas capacidades de forma controlada desde un único chat.

## 3. Estado actual

Actualmente existen scripts operativos:

- `scripts/orchestrator_preflight.py`
- `scripts/select_agent_model.py`
- `scripts/build_handoff_package.py`
- `scripts/record_agent_result.py`
- `scripts/show_latest_run.py`
- `scripts/run_diagnostic_flow.py`
- `scripts/run_opencode_from_handoff.py`

También existe integración real controlada con OpenCode mediante:

- `opencode.cmd run`
- `--agent`
- `--model`
- `--file`
- `--format json`

## 4. Objetivo de la fase MCP v0.1

La fase MCP v0.1 debe exponer herramientas de solo diagnóstico y trazabilidad.

No debe permitir todavía:

- edición de código;
- ejecución de comandos de proyecto;
- migraciones;
- deployment;
- acceso a secrets;
- cambios destructivos;
- escalamiento premium automático.

## 5. Herramientas MCP mínimas

### 5.1 orchestrator_preflight

Ejecuta:

`python scripts/orchestrator_preflight.py`

Debe devolver:

- estado del preflight;
- fuentes de contexto;
- alertas globales;
- lecciones globales;
- fuentes faltantes;
- modo operativo.

### 5.2 select_agent_model

Ejecuta:

`python scripts/select_agent_model.py`

Parámetros:

- `scenario`
- `risk`
- `volume`
- `user_premium`

Debe devolver:

- agente recomendado;
- modelo recomendado;
- línea recomendada;
- si requiere autorización;
- razón de escalamiento si aplica.

### 5.3 build_handoff_package

Ejecuta:

`python scripts/build_handoff_package.py`

Parámetros:

- `project_id`
- `source_agent`
- `target_agent`
- `scenario`
- `risk`
- `volume`
- `objective`

Debe devolver:

- `run_id`;
- ruta del paquete JSON;
- ruta del paquete Markdown;
- estado de preflight;
- conteo de fuentes;
- conteo de alertas;
- conteo de lecciones.

### 5.4 show_latest_run

Ejecuta:

`python scripts/show_latest_run.py`

Parámetros opcionales:

- `run_id`

Debe devolver un resumen visible del flujo.

### 5.5 run_diagnostic_flow

Ejecuta:

`python scripts/run_diagnostic_flow.py`

Parámetros:

- `project_id`
- `scenario`
- `risk`
- `volume`
- `objective`
- `with_opencode`

Debe devolver:

- `run_id`;
- agente recomendado;
- modelo recomendado;
- conteos de contexto, alertas y lecciones;
- estado final;
- rutas del run.

### 5.6 run_opencode_from_handoff

Ejecuta:

`python scripts/run_opencode_from_handoff.py`

Parámetros:

- `run_id`
- `agent`
- `model`
- `prompt`

Debe devolver:

- estado;
- agente;
- modelo;
- ruta del resultado procesado;
- ruta del resultado crudo;
- resumen de OpenCode;
- costos/tokens si están disponibles.

## 6. Reglas de seguridad MCP

El servidor MCP debe operar con permisos mínimos.

Debe bloquear o exigir autorización humana para:

- modificar archivos fuera de carpetas permitidas;
- editar código funcional;
- ejecutar comandos de proyecto;
- acceder a `.env`;
- leer secrets;
- hacer deployment;
- ejecutar migraciones;
- borrar archivos;
- escalar a modelos premium;
- enviar datos a servicios externos no autorizados.

## 7. Herramientas permitidas en v0.1

Permitidas:

- lectura de documentos de contexto;
- ejecución de scripts diagnósticos del orquestador;
- creación de paquetes de handoff;
- creación de bitácoras;
- invocación de OpenCode en modo diagnóstico;
- lectura de resultados;
- visualización de runs.

No permitidas:

- edición de código de proyectos objetivo;
- comandos arbitrarios;
- acceso a secrets;
- deployment;
- migraciones;
- borrado de archivos;
- operaciones premium automáticas.

## 8. Transparencia para usuario

Cada herramienta MCP debe informar:

- qué hizo;
- qué script ejecutó;
- qué archivos leyó;
- qué archivos creó o actualizó;
- qué agente/modelo recomendó o invocó;
- si hubo OpenCode real;
- si hubo costo/tokens;
- dónde está el `RUN_SUMMARY.md`;
- dónde está el `TRACE.md`.

## 9. Flujo objetivo desde Continue

El flujo deseado será:

1. Usuario escribe en Continue.
2. Continue identifica que debe usar herramienta MCP.
3. MCP ejecuta preflight.
4. MCP selecciona agente/modelo.
5. MCP crea handoff.
6. MCP invoca OpenCode si se autoriza o si es modo diagnóstico permitido.
7. MCP registra resultados.
8. MCP devuelve resumen visible a Continue.
9. Continue comunica al usuario el resultado sin que el usuario copie handoffs manualmente.

## 10. Implementación sugerida

Crear:

- `mcp_server/`
- `mcp_server/server.py`
- `mcp_server/tools.py`
- `mcp_server/schemas.py`
- `mcp_server/README.md`

La implementación inicial puede usar Python y ejecutar internamente los scripts existentes con `subprocess`.

## 11. Criterio de éxito v0.1

La integración MCP v0.1 será exitosa cuando Continue pueda invocar al menos:

- `orchestrator_preflight`
- `run_diagnostic_flow` sin OpenCode;
- `run_diagnostic_flow` con OpenCode diagnóstico;
- `show_latest_run`

y recibir respuestas resumidas sin que el usuario copie comandos manualmente en PowerShell.

## 12. Regla superior

MCP debe aumentar automatización sin reducir control humano, trazabilidad ni seguridad.
