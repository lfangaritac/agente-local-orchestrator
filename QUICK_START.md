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

