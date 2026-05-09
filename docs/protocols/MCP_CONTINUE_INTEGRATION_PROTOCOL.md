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

**Catálogo técnico canónico de herramientas MCP:** `mcp_server/README.md`.

Esta sección mantiene un **resumen orientado a integración** (Continue → MCP) para evitar duplicar el catálogo completo y reducir deriva entre documentos.

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

### 5.4 show_latest_run (opcional / verboso)

Ejecuta:

`python scripts/show_latest_run.py`

Parámetros opcionales:

- `run_id`

Uso recomendado:
- **No** es compact-first (puede ser verboso).
- Usar solo como **fallback** o cuando el usuario pida **detalle** (*preview-only*), después de consultar estado con `get_run_status` / `check_opencode_run_status`.

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

### 5.7 get_run_status (compact-first)

Herramienta recomendada para consultar estado de un run de forma **compacta** (existencia de artefactos + conteos), sin volcar `TRACE.md`/`RUN_SUMMARY.md` completos.

### 5.8 check_opencode_run_status (compact-first)

Alias recomendado para validar rápidamente si OpenCode ya dejó salida registrada (misma filosofía compact-first que `get_run_status`).

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
6. MCP invoca OpenCode en segundo plano si se autoriza o si es modo diagnóstico permitido.
7. MCP registra resultados.
8. Continue consulta estado con `get_run_status` o `check_opencode_run_status` (**default compact-first**).
9. Solo si hace falta detalle (y bajo solicitud), Continue usa `show_latest_run` como fallback.

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
- `start_opencode_from_handoff_async` (patrón recomendado) **o** `run_diagnostic_flow` con OpenCode diagnóstico;
- `get_run_status` / `check_opencode_run_status` (consulta compact-first)

y recibir respuestas resumidas sin que el usuario copie comandos manualmente en PowerShell.

`show_latest_run` debe existir, pero no es requisito de uso por defecto (puede ser verboso).

## 12. Regla superior

MCP debe aumentar automatización sin reducir control humano, trazabilidad ni seguridad.

<!-- START: MCP_STDIO_VALIDATION_V0_1 -->

---

## Anexo operativo v0.1 — Validación local por stdio

La primera validación local del servidor MCP por stdio fue exitosa.

### Script de prueba

    cd C:\Agente
    python .\mcp_server\test_mcp_stdio.py

### Objetivo de la prueba

Validar el servidor MCP local antes de conectarlo con Continue.

La prueba ejecuta mensajes JSON-RPC mínimos contra `mcp_server/server.py` y comprueba:

- `initialize`
- `tools/list`
- `tools/call orchestrator_preflight`
- `tools/call select_agent_model`
- `tools/call run_diagnostic_flow` sin OpenCode

### Resultado validado

La prueba confirmó:

    initialize_ok: true
    tools_list_ok: true
    preflight_call_ok: true
    select_agent_model_ok: true
    run_diagnostic_flow_ok: true

### Herramientas validadas

#### orchestrator_preflight

Resultado:

- `returncode: 0`
- `status: ok`
- fuentes de contexto cargadas;
- alertas globales cargadas;
- lecciones globales cargadas;
- fuentes faltantes: ninguna.

#### select_agent_model

Resultado:

    scenario: context-validation
    risk: medium
    volume: high
    recommended_agent: context-validator
    recommended_model: opencode-go/qwen3.6-plus
    recommended_line: Go
    requires_authorization: false
    status: diagnostic_recommendation

#### run_diagnostic_flow sin OpenCode

Resultado:

- run generado correctamente;
- paquete de handoff creado;
- `RUN_SUMMARY.md` generado;
- `TRACE.md` generado;
- OpenCode omitido correctamente al no usar `with_opencode`;
- visualización del flujo disponible.

### Run generado por la prueba

La validación MCP por stdio generó:

    run_id: 20260506_122350_1c5cc272

Archivos asociados:

    docs/agent_queue/inbox/20260506_122350_1c5cc272.json
    docs/agent_queue/inbox/20260506_122350_1c5cc272.md
    docs/agent_runs/20260506_122350_1c5cc272/RUN_SUMMARY.md
    docs/agent_runs/20260506_122350_1c5cc272/TRACE.md
    docs/agent_runs/20260506_122350_1c5cc272/agent_outputs/2026-05-06T12-23-50_orchestrator-diagnostic-flow.json

### Alcance validado

Esta validación confirma que el servidor MCP v0.1 puede:

- inicializarse por JSON-RPC;
- listar herramientas;
- ejecutar herramientas diagnósticas;
- envolver scripts locales ya probados;
- devolver resultados estructurados a un cliente MCP.

### Alcance no validado todavía

Aún falta validar:

- conexión real desde Continue;
- configuración MCP en Continue;
- llamada MCP desde chat de Continue;
- ejecución `run_diagnostic_flow` con `with_opencode=true` desde MCP;
- autorización humana integrada;
- manejo de errores de larga duración;
- visualización resumida dentro de Continue.

### Criterio para avanzar a Continue

El servidor puede avanzar a prueba con Continue porque:

- compila correctamente;
- responde por stdio;
- lista herramientas;
- ejecuta herramientas diagnósticas;
- mantiene restricciones de seguridad;
- no permite comandos arbitrarios.

<!-- END: MCP_STDIO_VALIDATION_V0_1 -->

<!-- START: MCP_ASYNC_OPENCODE_CONTINUE_FLOW_V0_1 -->

---

## Anexo operativo v0.2 — Flujo Continue -> MCP -> OpenCode asíncrono

La prueba real desde Continue demostró que el MCP puede ejecutar herramientas del orquestador desde el chat.

También demostró que la invocación bloqueante de OpenCode dentro de `run_diagnostic_flow with_opencode=true` no es la ruta recomendada para Continue.

### Estado validado

Validado desde Continue:

    Continue -> MCP -> orchestrator_preflight: OK
    Continue -> MCP -> run_diagnostic_flow with_opencode=false: OK

Validado por patrón asíncrono:

    Continue/PowerShell -> MCP/scripts -> start_opencode_from_handoff_async: OK
    OpenCode async -> agent_outputs/raw_outputs/TRACE/RUN_SUMMARY: OK

### Herramienta MCP agregada

    start_opencode_from_handoff_async

### Uso recomendado desde Continue

#### Paso 1 — Crear run sin OpenCode

    Usa el MCP agente-local-orchestrator para ejecutar run_diagnostic_flow con project_id=orchestrator, scenario=context-validation, risk=medium, volume=high, with_opencode=false. Devuélveme solo run_id, recommended_agent, recommended_model, status y with_opencode.

#### Paso 2 — Lanzar OpenCode en segundo plano

    Usa el MCP agente-local-orchestrator para ejecutar start_opencode_from_handoff_async con run_id=<run-id>, agent=context-validator, model=opencode-go/qwen3.6-plus. Devuélveme status, run_id, pid y next_action.

#### Paso 3 — Consultar resultado (compact-first)

    Usa el MCP agente-local-orchestrator para ejecutar check_opencode_run_status con run_id=<run-id>. Devuélveme solo status, opencode_registered, counts y agents_in_trace.

    (Opcional) Si el usuario pide detalle, usa show_latest_run con run_id=<run-id> en modo preview-only.

### Por qué usar async

El modo async evita que Continue tenga que esperar toda la ejecución de OpenCode dentro de una sola llamada MCP.

Esto mejora:

- estabilidad del chat;
- tolerancia a salidas largas;
- trazabilidad;
- recuperación si OpenCode tarda;
- capacidad de consultar estado;
- separación entre iniciar trabajo y leer resultado.

### No usar por defecto

No usar como ruta principal desde Continue:

    run_diagnostic_flow with_opencode=true

Este modo puede mantenerse para pruebas desde PowerShell, pero no como flujo principal de Continue.

### Resultado validado

Run usado en validación:

    20260506_171549_0e258229

Resultado:

- `background/`: generado;
- `agent_outputs/`: generado;
- `raw_outputs/`: generado;
- `TRACE.md`: actualizado;
- `RUN_SUMMARY.md`: actualizado;
- `context-validator`: registrado;
- `opencode-go/qwen3.6-plus`: usado.

### Próximo paso

Realizar una prueba final desde Continue con el patrón de tres pasos (default compact-first):

    run_diagnostic_flow with_opencode=false
    -> start_opencode_from_handoff_async
    -> check_opencode_run_status

(Usar `show_latest_run` solo como fallback si se requiere detalle.)

Si la prueba funciona desde Continue sin intervención de PowerShell, MCP v0.1 puede considerarse funcional para diagnóstico con OpenCode asíncrono.

<!-- END: MCP_ASYNC_OPENCODE_CONTINUE_FLOW_V0_1 -->

