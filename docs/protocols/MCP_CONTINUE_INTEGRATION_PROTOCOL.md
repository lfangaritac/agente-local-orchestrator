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

## 5. Herramientas MCP mínimas (sin duplicar catálogo)

**Catálogo técnico canónico de herramientas MCP (lista completa + detalles):** `mcp_server/README.md`.

Este protocolo **no duplica** el catálogo. Solo referencia herramientas por nombre cuando son necesarias para describir el flujo Continue → MCP.

Herramientas mínimas típicas para la integración (ver sección 9):

- `orchestrator_preflight`
- `run_diagnostic_flow` (**recomendado** con `with_opencode=false` para crear el run/handoff)
- `start_opencode_from_handoff_async` (**recomendado** para ejecución OpenCode sin bloquear Continue)
- `get_run_status` / `check_opencode_run_status` (**default compact-first**)
- `show_latest_run` (**fallback** / *preview-only* bajo solicitud explícita; no default)
- `verify_master_files` (anclaje físico de existencia/integridad de fuentes)

Regla compact-first: consultar primero estado y conteos con `get_run_status`/`check_opencode_run_status`; solo después (y bajo solicitud) usar `show_latest_run`.

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

## Anexo operativo v0.1 — Validación local por stdio (referencia histórica)

Esta validación existió para confirmar que el servidor MCP responde por stdio antes de la integración con Continue.

- Script de prueba: `python .\mcp_server\test_mcp_stdio.py`
- Run generado: `20260506_122350_1c5cc272` (ver `docs/context/RUN_INDEX.md`)

Detalle técnico (canónico) de self-tests/validación: `mcp_server/README.md` (sección “Validación local por stdio” + “Prueba local”).

<!-- END: MCP_STDIO_VALIDATION_V0_1 -->

<!-- START: MCP_ASYNC_OPENCODE_CONTINUE_FLOW_V0_1 -->

---

## Anexo operativo v0.2 — Flujo Continue -> MCP -> OpenCode asíncrono (referencia histórica)

Hallazgo: para Continue, evitar `run_diagnostic_flow with_opencode=true` (llamada bloqueante). Preferir el patrón asíncrono:

- crear run/handoff sin OpenCode;
- iniciar OpenCode en segundo plano;
- consultar estado con herramientas compact-first.

Run validado: `20260506_171549_0e258229` (ver `docs/context/RUN_INDEX.md`).

Detalle técnico de herramientas, comportamiento y guías compact-first: `mcp_server/README.md`.
Flujo operativo Continue → MCP (y regla de `show_latest_run` como fallback): ver sección 9 de este protocolo.

<!-- END: MCP_ASYNC_OPENCODE_CONTINUE_FLOW_V0_1 -->

