# QUICK_START.md

## Uso rapido del orquestador local

Este repositorio contiene el nucleo base para activar el sistema operativo de agentes en proyectos locales, proyectos existentes y proyectos conectados a Replit.

## Comandos principales

### Activar o validar sistema de agentes

`powershell
.\activate-agents.bat
python .\scripts\check_env.py
git status
`",
",


Cuando el orquestador se aplica a un proyecto externo, scripts/check_env.py se copia como plantilla inicial.

Cada proyecto destino debe ajustar ese archivo segun sus propias variables reales, stack e integraciones, y debe actualizar SECRETS_MANIFEST.md sin incluir valores sensibles.

<!-- START: SEMIAUTOMATED_DIAGNOSTIC_FLOW_V0_1 -->

---

## Flujo diagnóstico semiautomático del orquestador

El orquestador cuenta con un flujo diagnóstico semiautomático que permite validar, en una sola orden, la capa inicial de coordinación entre contexto, alertas, lecciones, selección de agente/modelo, paquete de handoff, bitácora y visualización del flujo.

Este flujo no invoca modelos, no ejecuta agentes reales, no modifica código funcional y no realiza acciones sensibles. Opera en modo diagnóstico.

### Comando recomendado

Ejecutar en PowerShell:

    cd C:\Agente
    python .\scripts\run_diagnostic_flow.py

### Resultado esperado

El flujo debe ejecutar:

1. Preflight transversal del orquestador.
2. Consulta automática de fuentes de contexto.
3. Consulta automática de alertas globales.
4. Consulta automática de lecciones globales.
5. Selección diagnóstica de agente y modelo.
6. Creación de paquete de handoff.
7. Registro de resultado de agente simulado/diagnóstico.
8. Generación de TRACE.md.
9. Generación de RUN_SUMMARY.md.
10. Visualización del flujo completo para el usuario.

### Validación esperada

Un resultado correcto debe mostrar valores equivalentes a:

    status: ok
    project_id: orchestrator
    scenario: context-validation
    risk: medium
    volume: high
    recommended_agent: context-validator
    recommended_model: opencode-go/qwen3.6-plus
    context_sources_count: 13
    alerts_checked_count: 10
    lessons_checked_count: 11

### Ver último flujo registrado

Para revisar el último flujo sin abrir manualmente archivos JSON o Markdown:

    cd C:\Agente
    python .\scripts\show_latest_run.py

### Archivos generados por flujo

Cada flujo puede generar:

    docs/agent_queue/inbox/<run-id>.json
    docs/agent_queue/inbox/<run-id>.md
    docs/agent_runs/<run-id>/RUN_SUMMARY.md
    docs/agent_runs/<run-id>/TRACE.md
    docs/agent_runs/<run-id>/agent_outputs/*.json

### Criterio de transparencia

El usuario debe poder ver:

- qué fuente de contexto fue consultada;
- qué alertas fueron consultadas;
- qué lecciones fueron consultadas;
- qué agente fue recomendado;
- qué modelo fue recomendado;
- qué estado reportó el flujo;
- dónde está la bitácora;
- dónde está el resumen del run.

### Alcance actual

Este flujo es semiautomático y diagnóstico. Todavía no reemplaza la futura integración MCP ni la invocación automática real de OpenCode.

Su propósito es validar la base operativa antes de avanzar hacia automatización más profunda.

<!-- END: SEMIAUTOMATED_DIAGNOSTIC_FLOW_V0_1 -->

<!-- START: OPENCODE_REAL_INTEGRATION_V0_1 -->

---

## Integración real controlada con OpenCode desde handoff

El orquestador ya cuenta con una integración real controlada con OpenCode usando CLI no interactiva.

Esta integración permite tomar un paquete de handoff previamente generado en `docs/agent_queue/inbox/`, invocar `opencode.cmd run`, capturar la salida JSONL de OpenCode, extraer la respuesta útil, registrar el resultado en la bitácora del run, actualizar `TRACE.md`, actualizar `RUN_SUMMARY.md` y mostrar el flujo al usuario.

### Comando recomendado

Ejecutar en PowerShell:

    cd C:\Agente
    python .\scripts\run_opencode_from_handoff.py --run-id <run-id>

Ejemplo validado:

    cd C:\Agente
    python .\scripts\run_opencode_from_handoff.py --run-id 20260506_111238_8e48193b

### Alcance actual

Esta integración:

- invoca OpenCode real;
- usa `opencode.cmd` para evitar bloqueo de PowerShell sobre `opencode.ps1`;
- trabaja con un handoff Markdown existente;
- usa agente `context-validator` si el paquete lo indica o si no se pasa otro agente;
- usa modelo `opencode-go/qwen3.6-plus` por defecto;
- ejecuta OpenCode en modo diagnóstico;
- solicita explícitamente no modificar archivos ni ejecutar comandos;
- captura salida JSONL;
- registra salida procesada en `agent_outputs/`;
- registra salida cruda en `raw_outputs/`;
- actualiza `TRACE.md`;
- actualiza `RUN_SUMMARY.md`;
- muestra el flujo actualizado al usuario.

### Resultado validado

La primera ejecución real validada de OpenCode desde handoff produjo:

    agent: context-validator
    model: opencode-go/qwen3.6-plus
    status: diagnostic
    handoff: docs/agent_queue/inbox/20260506_111238_8e48193b.md
    OpenCode CLI: operativo
    file_read: confirmado
    resultado registrado: agent_outputs/
    salida cruda registrada: raw_outputs/
    TRACE.md: actualizado
    RUN_SUMMARY.md: actualizado

### Archivos generados o actualizados

La integración puede crear o actualizar:

    docs/agent_runs/<run-id>/agent_outputs/*_opencode.json
    docs/agent_runs/<run-id>/raw_outputs/*_opencode_raw.json
    docs/agent_runs/<run-id>/TRACE.md
    docs/agent_runs/<run-id>/RUN_SUMMARY.md

### Restricciones vigentes

Esta integración todavía debe operar bajo restricciones de seguridad:

- no modificar archivos salvo que el usuario lo autorice expresamente;
- no ejecutar comandos de proyecto salvo autorización;
- no exponer secrets;
- no hacer deployment;
- no hacer migraciones;
- no aplicar cambios destructivos;
- no escalar a modelos premium sin autorización;
- no asumir que la validación de OpenCode equivale a ejecución aprobada.

### Ver el resultado del último flujo

Después de ejecutar OpenCode desde handoff:

    cd C:\Agente
    python .\scripts\show_latest_run.py

### Estado de automatización

Esta integración representa un avance desde la fase puramente semiautomática hacia una orquestación real controlada.

Ya existe:

    handoff package
    → OpenCode real por CLI
    → captura JSONL
    → extracción de texto
    → registro estructurado
    → TRACE.md
    → RUN_SUMMARY.md
    → visualización para usuario

Aún falta:

- integración MCP con Continue;
- transferencia automática Continue → OpenCode sin intervención manual;
- selección automática completa de modelo dentro de OpenCode según paquete;
- autorización humana integrada;
- validación de flujos con proyectos objetivo reales;
- ejecución controlada de cambios de código bajo permisos.

<!-- END: OPENCODE_REAL_INTEGRATION_V0_1 -->

