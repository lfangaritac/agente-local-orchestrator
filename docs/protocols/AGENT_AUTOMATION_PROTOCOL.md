# AGENT_AUTOMATION_PROTOCOL.md

## 1. Propósito

Definir el protocolo de automatización progresiva de la interacción entre agentes dentro del orquestador local `C:\Agente`.

Este protocolo establece cómo evolucionar desde la mini-orquestación manual validada en pruebas hacia una experiencia en la que el usuario pueda operar desde un solo punto de interacción, sin copiar handoffs entre agentes, sin seleccionar modelos manualmente y sin tener que conocer todos los pasos internos de Continue, OpenCode, Go, Zen, Premium o Replit.

La automatización debe mantener transparencia, trazabilidad, control humano en acciones sensibles y visibilidad de los aportes de cada agente.

## 2. Principio central

Las reglas documentales no automatizan por sí solas la interacción entre agentes.

Las reglas definen el comportamiento esperado. La automatización real requiere una capa ejecutable que coordine:

- identificación del proyecto objetivo;
- consulta de contexto;
- consulta de alertas;
- consulta de lecciones;
- selección de agente;
- selección de modelo;
- transferencia de handoffs;
- validación de suficiencia;
- escalamiento;
- autorización humana;
- registro de resultados;
- actualización de índices;
- trazabilidad visible para el usuario.

## 3. Objetivo de experiencia de usuario

El objetivo final es que el usuario pueda mantener la conversación en un solo punto de entrada.

El usuario no debería:

- copiar y pegar respuestas entre Continue y OpenCode;
- mover manualmente handoffs;
- seleccionar manualmente modelos;
- decidir manualmente qué agente debe intervenir;
- recordar qué alertas consultar;
- transferir contexto entre herramientas;
- reconstruir el estado de una mini-orquestación.

El usuario sí debe poder ver:

- qué agente intervino;
- qué modelo se usó;
- qué contexto se consultó;
- qué alertas aplicaron;
- qué lecciones fueron relevantes;
- qué decisión tomó cada agente;
- qué validó OpenCode;
- qué refinó Continue;
- por qué se escaló o no se escaló;
- qué acción requiere autorización humana;
- qué quedó registrado.

## 4. Transparencia del proceso

La automatización no debe ser una caja negra.

Aunque el intercambio entre agentes se automatice, el usuario debe poder revisar una bitácora comprensible del proceso.

Cada paso relevante debe producir una entrada visible o consultable con:

- `run_id`;
- `step_id`;
- `timestamp`;
- `source_agent`;
- `target_agent`;
- `model_used`;
- `project_id`;
- `scenario`;
- `risk_level`;
- `information_volume`;
- `context_sources`;
- `alerts_checked`;
- `lessons_checked`;
- `decision`;
- `summary`;
- `next_action`;
- `requires_user_authorization`;
- `status`.

## 5. Registro visible de pasos

El orquestador debe generar un registro de trazabilidad para cada flujo.

Ubicación propuesta:

- `docs/agent_runs/`
- `docs/agent_runs/<run-id>/RUN_SUMMARY.md`
- `docs/agent_runs/<run-id>/TRACE.md`
- `docs/agent_runs/<run-id>/handoffs/`
- `docs/agent_runs/<run-id>/agent_outputs/`
- `docs/agent_runs/<run-id>/decisions/`
- `docs/agent_runs/<run-id>/escalations/`

El usuario debe poder consultar un resumen ejecutivo del flujo y, cuando sea necesario, el detalle técnico de cada agente.

## 6. Diferencia entre automatización y ocultamiento

Automatizar no significa ocultar.

El sistema debe automatizar:

- pasos repetitivos;
- transferencia de handoffs;
- consulta de contexto;
- selección inicial de agente/modelo;
- registro de trazabilidad;
- actualización de índices;
- verificación de alertas y lecciones;
- preparación de paquetes de escalamiento.

El sistema no debe ocultar:

- errores;
- incertidumbre;
- limitaciones de contexto;
- alertas críticas;
- razones de escalamiento;
- decisiones de modelo;
- bloqueos;
- cambios de archivos;
- uso de herramientas;
- requerimientos de autorización.

## 7. Arquitectura objetivo

La arquitectura objetivo es:

Usuario en un solo punto de interacción
↓
Orquestador local
↓
Preflight de contexto
↓
Consulta de registro, alertas y lecciones
↓
Continue para construcción contextual
↓
OpenCode para validación técnica
↓
Feedback bidireccional si aplica
↓
Selección automática de agente/modelo
↓
Ejecución, diagnóstico, escalamiento o bloqueo
↓
Registro visible de trazabilidad
↓
Actualización de contexto, alertas, lecciones o índices

## 8. Punto de entrada preferido

El punto de entrada preferido será Continue dentro de VS Code, siempre que pueda operar con herramientas del orquestador mediante una capa ejecutable.

Continue debe actuar como interfaz conversacional y copiloto contextual.

OpenCode debe actuar como agente técnico validador, planificador, ejecutor o debugger según corresponda.

El usuario debe poder permanecer en Continue, salvo que una tarea requiera explícitamente interacción directa con OpenCode, Replit u otra herramienta.

## 9. Capa ejecutable requerida

Para que la automatización exista realmente, debe implementarse una capa ejecutable local.

Esta capa puede adoptar progresivamente una de estas formas:

- scripts locales;
- cola de handoffs basada en archivos;
- CLI del orquestador;
- servidor MCP local;
- integración directa con OpenCode si la CLI/API disponible lo permite;
- integración posterior con una interfaz propia.

## 10. Fase inicial — Automatización semiautomática

La primera fase debe reducir el copiado manual, sin asumir todavía integración total.

Debe crear herramientas para:

- preparar handoff automáticamente;
- seleccionar agente/modelo;
- registrar salida de agente;
- validar suficiencia;
- crear paquete de escalamiento;
- actualizar bitácora;
- generar resumen visible para usuario.

Archivos o carpetas sugeridas:

- `docs/agent_queue/inbox/`
- `docs/agent_queue/outbox/`
- `docs/agent_queue/runs/`
- `docs/agent_queue/escalations/`
- `scripts/orchestrator_preflight.py`
- `scripts/select_agent_model.py`
- `scripts/build_handoff_package.py`
- `scripts/record_agent_result.py`

## 11. Fase objetivo — MCP local

La fase objetivo debe considerar un servidor MCP local del orquestador.

El MCP debe exponer herramientas para que Continue pueda invocarlas desde Agent Mode o un mecanismo equivalente.

Herramientas sugeridas:

- `orchestrator.identify_project`
- `orchestrator.preflight_context`
- `orchestrator.load_project_registry`
- `orchestrator.load_context_index`
- `orchestrator.check_global_alerts`
- `orchestrator.check_project_alerts`
- `orchestrator.check_global_lessons`
- `orchestrator.prepare_handoff`
- `orchestrator.validate_handoff_with_opencode`
- `orchestrator.select_agent_model`
- `orchestrator.build_escalation_package`
- `orchestrator.record_agent_result`
- `orchestrator.update_sync_status`
- `orchestrator.record_lesson_candidate`
- `orchestrator.record_alert_candidate`
- `orchestrator.render_user_trace`

## 12. Fase avanzada — Integración con OpenCode

La integración con OpenCode debe validarse técnicamente.

No debe asumirse de entrada que OpenCode puede ser invocado de forma completamente no interactiva.

El orquestador debe evaluar:

- si OpenCode CLI permite ejecución con prompt desde archivo;
- si permite seleccionar modelo/agente desde configuración o flags;
- si permite salida estructurada;
- si permite operar en modo plan/review sin edición;
- si permite registrar diffs;
- si permite ejecutar comandos con permisos;
- si puede integrarse con una cola de archivos;
- si puede consumir handoffs generados por el orquestador;
- si puede devolver resultados a una carpeta de salida.

Hasta confirmar esto, la automatización debe considerarse semiautomática.

## 13. Flujo automatizado propuesto

El flujo automatizado ideal será:

1. Usuario solicita tarea.
2. Orquestador crea `run_id`.
3. Orquestador identifica proyecto objetivo.
4. Orquestador consulta `PROJECT_REGISTRY.md`.
5. Orquestador ejecuta preflight de contexto.
6. Orquestador consulta alertas globales y locales.
7. Orquestador consulta lecciones globales y locales.
8. Continue prepara contexto y handoff.
9. OpenCode valida suficiencia del handoff.
10. Si OpenCode detecta insuficiencia, devuelve feedback estructurado.
11. Continue refina contexto o handoff.
12. OpenCode selecciona o confirma agente/modelo.
13. Orquestador evalúa si Go basta.
14. Si Go basta, se ejecuta o se entrega diagnóstico.
15. Si Go no basta, se construye paquete canónico.
16. Si corresponde, se escala a Zen continuidad, Zen económico, Zen premium o Replit.
17. El usuario autoriza si hay costo, riesgo sensible o acción destructiva.
18. El resultado se registra.
19. Se actualizan índices, alertas, lecciones o sincronización si aplica.
20. Se muestra al usuario un resumen transparente del flujo.

## 14. Visibilidad para el usuario

El usuario debe poder ver un resumen del flujo como:

- solicitud recibida;
- proyecto objetivo identificado;
- fuentes consultadas;
- alertas aplicables;
- lecciones aplicables;
- agente Continue: aportes y límites;
- agente OpenCode: validación y decisión;
- modelo seleccionado;
- decisión de no escalar o escalar;
- acciones realizadas;
- autorizaciones solicitadas;
- archivos modificados, si los hubo;
- resultados;
- pendientes;
- lecciones o alertas propuestas.

## 15. Bitácora de agentes

Cada agente debe producir una salida separada y trazable.

Ejemplo de estructura:

- `01_continue_context.md`
- `02_opencode_validation.md`
- `03_continue_refinement.md`
- `04_opencode_plan.md`
- `05_escalation_package.md`
- `06_final_result.md`

Esto permite que el usuario vea la interacción real entre agentes sin tener que operar manualmente la transferencia.

## 16. Control humano

La automatización debe detenerse y pedir autorización humana cuando exista:

- uso de modelos premium con costo;
- cambios destructivos;
- edición de archivos sensibles;
- acceso a secrets;
- deployment;
- migraciones;
- cambios de producción;
- eliminación de archivos;
- modificación de seguridad, auth o permisos;
- tratamiento de datos personales reales;
- incertidumbre crítica;
- contradicción entre agentes no resuelta.

## 17. Decisión automática de modelo

El usuario no debe seleccionar modelos manualmente en el estado final.

El orquestador debe seleccionar modelo según:

- escenario;
- riesgo;
- volumen;
- sensibilidad;
- disponibilidad de Go;
- necesidad de continuidad Zen;
- necesidad de premium;
- costo de equivocarse;
- instrucciones del usuario;
- reglas de `MODEL_ROUTING.md`;
- alertas y lecciones aplicables.

La selección debe quedar registrada y visible.

## 18. Decisión automática de agente

El usuario no debe seleccionar agente manualmente en el estado final.

El orquestador debe seleccionar entre:

- `classifier`;
- `context-validator`;
- `planner`;
- `architect-planner`;
- `builder`;
- `light-builder`;
- `debugger`;
- `critical-debugger`;
- `diff-reviewer`;
- `security-reviewer`;
- `handoff-writer`;
- `documentation-writer`;
- `model-evaluator`.

La selección debe justificarse.

## 19. Modos operativos

### 19.1 Modo diagnóstico

Aplica cuando:

- falta contexto;
- falta proyecto objetivo;
- hay contradicción;
- falta autorización;
- el handoff es insuficiente;
- hay alerta crítica;
- no se puede verificar una fuente obligatoria.

No permite ejecución.

### 19.2 Modo planificación

Aplica cuando el contexto es suficiente para proponer plan, pero no para ejecutar.

### 19.3 Modo ejecución controlada

Aplica cuando:

- el contexto es suficiente;
- el agente/modelo está justificado;
- no hay bloqueo;
- existe autorización cuando aplica;
- las alertas fueron consultadas.

### 19.4 Modo escalamiento

Aplica cuando Go no basta, Go se agotó, hay complejidad, riesgo, volumen o solicitud del usuario.

### 19.5 Modo Replit

Aplica cuando se requiere entorno real, preview, runtime, deployment o secrets reales.

## 20. Reglas de transparencia mínima

Todo flujo automatizado debe declarar:

- modo operativo;
- proyecto objetivo;
- fuentes revisadas;
- fuentes no revisadas;
- alertas consultadas;
- lecciones consultadas;
- agente usado;
- modelo usado;
- decisión de routing;
- decisión de escalamiento;
- si hubo autorización humana;
- resultado final.

## 21. Relación con protocolos existentes

Este protocolo depende de:

- `TARGET_PROJECT_CONTEXT_CONTRACT.md`
- `PROJECT_REGISTRY.md`
- `PROJECT_ENABLEMENT_PROTOCOL.md`
- `CONTEXT_SYNC_PROTOCOL.md`
- `DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md`
- `AGENT_RULES.md`
- `MODEL_ROUTING.md`
- `AGENT_ORCHESTRATION.md`
- `CONTINUE_USAGE_PROTOCOL.md`
- `REPLIT_HANDOFF.md`
- `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`
- `docs/lessons/GLOBAL_LESSONS_LEARNED.md`

## 22. Lección transversal asociada

La automatización debe registrar como aprendizaje transversal que:

Las reglas definen comportamiento esperado, pero no producen automatización real por sí solas. Para lograr interacción transparente entre agentes se requiere una capa ejecutable de orquestación.

## 23. Criterio de éxito

La automatización se considerará exitosa cuando:

- el usuario pueda iniciar una tarea desde un solo chat;
- el sistema identifique el proyecto objetivo;
- el sistema consulte contexto, alertas y lecciones;
- Continue prepare contexto;
- OpenCode valide y actúe;
- el router seleccione agente/modelo;
- el usuario no copie handoffs manualmente;
- el usuario no seleccione modelos manualmente;
- el usuario vea un resumen transparente de cada paso;
- las acciones sensibles requieran autorización;
- los resultados queden documentados;
- los índices y lecciones se actualicen cuando aplique.

## 24. Regla superior

La automatización debe reducir carga operativa del usuario sin reducir transparencia, trazabilidad, control humano ni calidad técnica.
