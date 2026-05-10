# QUICK_START.md

## Uso rapido del orquestador local

Este repositorio contiene el nucleo base para activar el sistema operativo de agentes en proyectos locales, proyectos existentes y proyectos conectados a Replit.

## Comandos principales

### Activar o validar sistema de agentes

```powershell
.\activate-agents.bat
python .\scripts\check_env.py
git status
```

### Validación local recomendada (gate antes de Builds low-risk)

Runner local reproducible:

```powershell
# Iteración rápida (sin side-effects)
python .\scripts\run_local_checks.py --mode quick

# Antes de Build low-risk o commit relevante (sin side-effects por defecto)
python .\scripts\run_local_checks.py --mode full --include-git-status

# Validación MCP ampliada (side-effects opt-in: puede crear runs/handoffs de prueba ignorados por Git)
python .\scripts\run_local_checks.py --mode full --include-git-status --include-mcp-stdio-tests

# Requerir working tree limpio
python .\scripts\run_local_checks.py --mode full --include-git-status --require-clean
```

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

### Post-run: diagnóstico rápido del run (compact-first)

Para diagnóstico rápido **sin dumps** y sin abrir artefactos completos, usar desde Continue (vía MCP) este orden:

1) `run_health_check` (salud del run)
2) `check_opencode_run_status` (seguimiento específico de OpenCode)
3) `get_run_status` (diagnóstico ampliado)
4) `show_latest_run` solo como **fallback / preview-only** bajo solicitud explícita o necesidad justificada

Fallback (terminal, detalle excepcional):

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

### Seguimiento del run (compact-first) + fallback

Recomendado desde Continue (vía MCP), en este orden:

1) `run_health_check` (salud del run)
2) `check_opencode_run_status` (si se espera evidencia de OpenCode)
3) `get_run_status` (si hace falta diagnóstico ampliado)

Solo si hace falta detalle (y como **preview-only**), usar en terminal:

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

<!-- START: UNIFIED_DIAGNOSTIC_WITH_OPENCODE_V0_1 -->

---

## Comando unificado con OpenCode integrado

El orquestador ya permite ejecutar un flujo diagnóstico completo con OpenCode real integrado mediante un solo comando.

### Comando oficial

Ejecutar en PowerShell:

    cd C:\Agente
    python .\scripts\run_diagnostic_flow.py --with-opencode

### Qué ejecuta este comando

El comando realiza la secuencia completa:

1. Ejecuta preflight transversal.
2. Consulta fuentes de contexto.
3. Consulta alertas globales.
4. Consulta lecciones globales.
5. Selecciona agente/modelo.
6. Crea paquete de handoff.
7. Registra resultado diagnóstico inicial.
8. Invoca OpenCode real mediante `opencode.cmd run`.
9. Adjunta el handoff Markdown.
10. Captura salida JSONL de OpenCode.
11. Extrae la respuesta útil.
12. Registra resultado procesado en `agent_outputs/`.
13. Registra salida cruda en `raw_outputs/`.
14. Actualiza `TRACE.md`.
15. Actualiza `RUN_SUMMARY.md`.
16. Muestra el flujo visible al usuario.

### Resultado esperado

Un resultado exitoso debe incluir valores equivalentes a:

    status: ok
    with_opencode: true
    recommended_agent: context-validator
    recommended_model: opencode-go/qwen3.6-plus
    context_sources_count: 13
    alerts_checked_count: 10
    lessons_checked_count: 11

### Resultado validado

La ejecución validada produjo:

    run_id: 20260506_120851_e8c884cf
    agent: context-validator
    model: opencode-go/qwen3.6-plus
    status: diagnostic
    handoff: docs/agent_queue/inbox/20260506_120851_e8c884cf.md
    TRACE.md: actualizado
    RUN_SUMMARY.md: actualizado
    agent_outputs: actualizado
    raw_outputs: actualizado

### Restricciones

Aunque OpenCode se invoca realmente, el flujo sigue operando en modo diagnóstico controlado.

No debe:

- modificar archivos funcionales;
- ejecutar comandos de proyecto;
- acceder a secrets;
- hacer deployment;
- hacer migraciones;
- aplicar cambios destructivos;
- escalar a premium sin autorización.

### Seguimiento del run (compact-first) + fallback

Recomendado desde Continue (vía MCP), en este orden:

1) `run_health_check`
2) `check_opencode_run_status`
3) `get_run_status`

Solo si hace falta detalle (y como **preview-only**), usar en terminal:

    cd C:\Agente
    python .\scripts\show_latest_run.py

### Estado actual

Este comando representa la primera mini-orquestación real de punta a punta:

    preflight
    -> routing agente/modelo
    -> handoff
    -> OpenCode real
    -> captura estructurada
    -> bitácora visible
    -> resumen visible

Todavía falta integrar MCP para que Continue pueda invocar este flujo desde un único chat sin intervención manual de terminal.

<!-- END: UNIFIED_DIAGNOSTIC_WITH_OPENCODE_V0_1 -->

<!-- START: CONTINUE_MCP_OPENCODE_ASYNC_V0_1 -->

---

## Flujo recomendado desde Continue con OpenCode asíncrono

Cuando el usuario opera desde Continue, el flujo recomendado para usar OpenCode real no debe invocar OpenCode dentro de una única llamada bloqueante.

La prueba demostró que:

- Continue puede invocar el MCP local correctamente.
- Continue puede ejecutar `orchestrator_preflight`.
- Continue puede ejecutar `run_diagnostic_flow` sin OpenCode.
- La llamada bloqueante `run_diagnostic_flow` con `with_opencode=true` puede fallar o quedar incompleta por duración, salida extensa o límites del cliente.
- La solución correcta es usar patrón asíncrono.

### Patrón correcto

Desde Continue:

1. Ejecutar `run_diagnostic_flow` con `with_opencode=false`.
2. Tomar el `run_id` generado.
3. Ejecutar `start_opencode_from_handoff_async` con ese `run_id`.
4. Esperar unos segundos.
5. Ejecutar `run_health_check` con ese `run_id` para diagnóstico rápido de salud.
6. Si hace falta seguimiento específico de OpenCode: `check_opencode_run_status`.
7. Solo si se necesita detalle excepcional: `show_latest_run` (*preview-only*).

### Mensaje sugerido para Continue — Paso 1

    Usa el MCP agente-local-orchestrator para ejecutar run_diagnostic_flow con project_id=orchestrator, scenario=context-validation, risk=medium, volume=high, with_opencode=false. Devuélveme solo run_id, recommended_agent, recommended_model, status y with_opencode.

### Mensaje sugerido para Continue — Paso 2

Reemplazar `<run-id>` por el valor devuelto en el paso anterior.

    Usa el MCP agente-local-orchestrator para ejecutar start_opencode_from_handoff_async con run_id=<run-id>, agent=context-validator, model=opencode-go/qwen3.6-plus. Devuélveme status, run_id, pid y next_action.

### Mensaje sugerido para Continue — Paso 3 (diagnóstico rápido)

    Usa el MCP agente-local-orchestrator para ejecutar run_health_check con run_id=<run-id>. Devuélveme: health_status, latest_status, exists, opencode_registered, agent_outputs_count, raw_outputs_count, issues (máx 3), recommendations (máx 3).

### Mensaje sugerido para Continue — Paso 4 (seguimiento OpenCode)

    Usa el MCP agente-local-orchestrator para ejecutar check_opencode_run_status con run_id=<run-id>. Devuélveme: exists, opencode_registered, agent_outputs_count, raw_outputs_count, latest_status.

### Mensaje sugerido para Continue — Paso 5 (fallback / preview-only)

    Solo si necesito detalle, usa el MCP agente-local-orchestrator para ejecutar show_latest_run con run_id=<run-id>. Devuélveme un resumen corto (sin pegar TRACE/RUN_SUMMARY completos).

### Resultado validado

La prueba asíncrona validada produjo:

    run_id: 20260506_171549_0e258229
    OpenCode async: started
    agent: context-validator
    model: opencode-go/qwen3.6-plus
    agent_outputs: generado
    raw_outputs: generado
    TRACE.md: actualizado
    RUN_SUMMARY.md: actualizado

### Regla operativa

Para Continue, usar por defecto:

    run_diagnostic_flow with_opencode=false
    -> start_opencode_from_handoff_async
    -> run_health_check

Si se espera OpenCode:

    -> check_opencode_run_status

Y solo si hace falta detalle:

    -> show_latest_run  (fallback / preview-only)

Evitar por ahora:

    run_diagnostic_flow with_opencode=true

salvo pruebas controladas desde PowerShell.

<!-- END: CONTINUE_MCP_OPENCODE_ASYNC_V0_1 -->

