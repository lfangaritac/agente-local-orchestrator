# AGENT_AUTOMATION_PROTOCOL.md

## 1. Propósito

Definir el protocolo de automatización progresiva de la interacción entre agentes dentro del orquestador local `C:\Agente`.

Este protocolo establece cómo evolucionar desde la mini-orquestación manual validada en pruebas hacia una experiencia en la que el usuario pueda operar desde un solo punto de interacción, sin copiar handoffs entre agentes, sin seleccionar modelos manualmente y sin tener que conocer todos los pasos internos de Continue, OpenCode, Go, Zen, Premium o Replit.

La automatización debe mantener transparencia, trazabilidad, control humano en acciones sensibles y visibilidad de los aportes de cada agente.

## 1.1 Alcance y referencias canónicas

Este documento es **canónico** para:
- arquitectura de automatización progresiva y sus fases;
- flujo automatizado (preflight → routing → handoff → validación → registro);
- estructura de runs, trazabilidad y evidencia (campos mínimos, rutas, bitácoras);
- mini-orquestación desde la perspectiva de automatización;
- **Plan/Build y aprobaciones por umbral** (sección 25).

Este documento **referencia (no duplica)**:
- contexto mínimo, niveles de contexto y *context packs*: `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`;
- guía técnica *compact-first* y uso de herramientas MCP: `mcp_server/README.md`;
- roles/arquitectura completa de Continue/OpenCode/MCP: `AGENT_ORCHESTRATION.md`;
- formato detallado de handoff Continue → OpenCode: `.continue/rules/continue-opencode-handoff.md`.

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

Nota: la política canónica de **contexto por referencias**, niveles y *context packs* vive en `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`.

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

El punto de entrada preferido es **Continue dentro de VS Code** como interfaz conversacional, apoyado por una capa ejecutable del orquestador.

- Roles operativos resumidos para Plan/Build: ver **25.6 Roles**.
- Fuente canónica de roles y arquitectura de agentes: `AGENT_ORCHESTRATION.md`.

El usuario debe poder permanecer en Continue salvo que una tarea requiera explícitamente interacción directa con OpenCode, Replit u otra herramienta.

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

Referencias:
- Guía técnica *compact-first* para consulta/operación MCP: `mcp_server/README.md`.
- Política de evidencia por referencias (evitar dumps): `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`.

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

Notas canónicas relacionadas:
- Contexto mínimo / *context packs* / niveles: `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`.
- Formato de handoff Continue → OpenCode: `.continue/rules/continue-opencode-handoff.md`.

## 14. Visibilidad para el usuario

El usuario debe poder consultar:
- un **resumen ejecutivo** del flujo (qué se pidió, qué se consultó, qué se decidió, qué falta, qué requiere autorización);
- y, si lo solicita, el **detalle técnico**.

La trazabilidad debe ser consultable por referencias (por ejemplo: `run_id` + rutas + conteos + previews), evitando pegar artefactos completos salvo necesidad.

Fuente canónica de campos mínimos de trazabilidad: sección 4.
Regla de transparencia progresiva en Plan/Build: sección 25.7.

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

### 15.1 Versionado y retención de evidencia (runs/handoffs/logs)

Esta sección define una política **canónica** de retención/versionado de evidencia sin inflar contexto ni repo.
No duplica niveles de contexto: ver `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md` (niveles 0–4, *context packs* y exclusiones).

Nota (retención no destructiva): la evidencia operacional puede conservarse **localmente** y archivarse en modo *archive-only* (zip) con `scripts/audit_agent_artifacts.py --archive <dir>`, sin borrar ni mover originales.
Destino recomendado (fuera del repo): `C:\Agente_Archives`.
Los archives incluyen `sha256` + `*.manifest.json` con solo rutas/metadatos (sin contenido).
Esto no reemplaza `RUN_INDEX` y la evidencia archivada no es contexto base; se recupera solo por referencia (`run_id` + rutas) cuando haga falta.

**Qué se considera evidencia (por run):** `RUN_SUMMARY.md`, `TRACE.md`, `agent_outputs/`, handoff `docs/agent_queue/inbox/<run_id>.{md,json}`, `raw_outputs/`, logs de background/shell y `validation_output.log`.

**Qué se versiona por defecto:**
- Índices livianos: `docs/context/RUN_INDEX.md`, `docs/context/ACTION_INDEX.md`, `docs/context/DECISION_INDEX.md`, `docs/context/REFERENCE_MAP.md`.
- Runs **curados/baseline**: `RUN_SUMMARY.md`, `TRACE.md`, `agent_outputs/`.
- Handoffs que soportan runs curados o escalamiento formal.

**Qué NO se versiona por defecto:**
- `raw_outputs/**`.
- logs extensos (background stdout/stderr, shell logs, `validation_output.log`).
- runs exploratorios/repetitivos/locales no curados.
- handoffs transitorios sin valor de baseline/decisión/incidente.

**Criterio de curación (run versionable):** un run puede pasar a evidencia versionable si:
- soporta un baseline reproducible o una integración relevante;
- soporta un cambio de herramienta/política/protocolo;
- evidencia un incidente, bloqueo o decisión;
- está referenciado en `RUN_INDEX` y/o relacionado con una entrada en `ACTION_INDEX`/`DECISION_INDEX`.

**Relación con índices (regla práctica):** si un run no está en `docs/context/RUN_INDEX.md` (o no soporta baseline/incidente/decisión), no merece retención larga ni versionado.
- `RUN_INDEX`: solo runs curados.
- `ACTION_INDEX`: solo hitos/cambios relevantes (política/herramienta/protocolo).
- `DECISION_INDEX`: solo decisiones estables de gobierno.
- Los índices no deben copiar `TRACE`, `RUN_SUMMARY`, `raw_outputs` ni logs completos (solo referencias).

**Consulta compact-first:**
- Salud rápida (primera consulta): `run_health_check`.
- Seguimiento específico de OpenCode: `check_opencode_run_status`.
- Diagnóstico ampliado: `get_run_status`.
- `show_latest_run`: solo bajo solicitud explícita y como detalle (*preview-only*; evitar uso por defecto).
- `raw_outputs` y logs: consultar solo en Nivel 3/4 con autorización explícita.

Nota (Build low-risk con OpenCode): en modo no interactivo, OpenCode puede requerir auto-aprobación de permisos para aplicar cambios. Esto solo debe habilitarse con switch explícito + guardrails (risk_level=low + allowed_files acotado) **y** señal explícita adicional `user_authorized_build=true`. Ver `mcp_server/README.md`.

Principio operativo estable (Build): cuando el usuario autoriza **Build por alcance**, Continue debe ejecutar dentro de ese alcance **sin microaprobaciones interactivas** (p. ej. evitar depender de múltiples aceptaciones manuales de diffs/ediciones en VS Code). Preguntar solo cuando se cruce un umbral (alcance/riesgo/seguridad/costo/calidad/política/secrets/deployment/migraciones/infra/destructivo).

**Relación con `.continueignore`:** es mitigación *best-effort*; esta política prevalece aunque la instalación de Continue no soporte ignores.

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

---

## 25. PLAN_BUILD_APPROVAL_AND_BACKGROUND_ORCHESTRATION_POLICY

### 25.1 Principio central

- La orquestación es una regla operativa base, no un mecanismo de escalamiento.
- OpenCode no es “escalamiento”: es el agente técnico natural para codificación, modificación técnica, validación y pruebas.
- Zen, modelos premium y Replit sí son mecanismos de escalamiento o ampliación de capacidad.

Aclaraciones obligatorias (anti-inferencias):

- **Go** significa *OpenCode Go* (línea/proveedor/modelos de primera línea), no el lenguaje de programación Go.
- **Zen** significa *OpenCode Zen* (continuidad pay-as-you-go / escalamiento económico o premium), no una arquitectura técnica, red, bus o framework.

### 25.2 Modo Plan

El modo Plan aplica a:

- análisis;
- diagnóstico;
- diseño;
- revisión;
- propuesta;
- preparación/refinamiento de handoff.

Reglas:

- no modifica archivos ni código;
- no ejecuta comandos;
- si se detecta necesidad de construir, se debe solicitar **modo Build** o **autorización explícita** del usuario.

### 25.3 Modo Build

El modo Build aplica cuando el usuario autoriza **ejecución dentro de un alcance definido**.

Reglas:

- la autorización es por **alcance**, no por micro-acciones ordinarias;
- el sistema puede coordinar **Continue → MCP → OpenCode** (incluyendo ejecución en segundo plano cuando sea apropiado);
- se mantiene trazabilidad y reporte;
- acciones sensibles siguen requiriendo autorización humana (ver 25.5).

### 25.4 Aprobaciones que NO se requieren en Build (si están dentro del alcance autorizado)

- crear/modificar código ordinario relacionado con la tarea;
- actualizar pruebas asociadas;
- ejecutar validaciones locales **no destructivas**;
- actualizar documentación técnica asociada;
- registrar evidencia ordinaria: `runs`, `TRACE`, `RUN_SUMMARY`, `agent_outputs`, `raw_outputs`.

### 25.5 Aprobaciones que SÍ se requieren siempre

Requieren autorización humana explícita, incluso en modo Build:

- escalar a **modelo premium** (por costo o criticidad);
- usar **Replit** o cualquier entorno externo;
- acceder o modificar **secrets** (incluye pedirlos, imprimirlos o incorporarlos a prompts/archivos);
- **deployment**;
- **migraciones**;
- infraestructura productiva o cambios con impacto en producción;
- **mover, borrar o renombrar archivos maestros** del orquestador;
- cambios arquitectónicos críticos;
- acciones destructivas;
- ampliar el alcance originalmente autorizado;
- `push/merge` si la política del proyecto lo exige.

### 25.6 Roles

- **Continue**: orquestación, contexto, gobierno, clasificación, preparación de handoffs, supervisión, consolidación de resultados y comunicación.
- **OpenCode**: **ejecutor principal** de cambios en Build cuando el alcance es claro (modificación técnica + validación técnica).
- **MCP**: despacho/estado/trazabilidad (herramientas compact-first por `run_id`).
- **Usuario**: define intención, alcance y modo Plan/Build; autoriza acciones sensibles; decide negocio o arquitectura crítica cuando el sistema lo solicite.

Regla operativa: en **Build autorizado** no usar como mecanismo principal la edición interactiva de diffs de VS Code/Continue (múltiples Accept/Reject). El camino preferido es **Continue → MCP → OpenCode → MCP**, con validación Git.

### 25.7 Transparencia progresiva en chat

El chat debe mostrar primero (resumen ejecutivo):

- objetivo;
- etapa actual;
- acción central;
- resultado parcial;
- riesgos o bloqueos;
- si requiere decisión humana;
- próximo paso.

Y dejar disponible como detalle técnico (consultable):

- archivos modificados;
- comandos ejecutados;
- hashes;
- logs;
- `TRACE`;
- `RUN_SUMMARY`;
- `raw_outputs`;
- `agent_outputs`.

### 25.8 Cambio de modelo en OpenCode (routing)

- El routing debe aplicar automáticamente dentro de las **líneas autorizadas** por el usuario y por `MODEL_ROUTING.md`.
- Si el cambio requiere costo/premium, Replit o entorno externo, debe pedir autorización.

Esta política no reemplaza `MODEL_ROUTING.md`; lo operacionaliza en Plan/Build.

### 25.9 Regla de visibilidad (archivos maestros)

Cuando la existencia de archivos maestros sea relevante, debe prevalecer la verificación física vía MCP (`verify_master_files`) por sobre la visibilidad parcial del IDE.

### 25.10 Reglas anti-desviación

- Continue **no implementa** código operativo del orquestador (scripts, `mcp_server`, automatización ejecutable).
- OpenCode **no decide** cambios de gobierno sin contexto y supervisión de Continue.
- MCP **no sustituye** ni a Continue ni a OpenCode: solo ejecuta/verifica/registrar según herramientas expuestas.
- El usuario **no debe transportar handoffs manualmente** como rutina: la orquestación debe tender a automatizar transferencia y trazabilidad.
- La orquestación debe operar “de fondo” cuando corresponda, pero el usuario debe ver un avance comprensible (25.7).

### 25.11 Condición de cierre en Build

Toda ejecución en modo Build debe cerrar con:

- resumen funcional;
- resultado técnico;
- evidencia de validación;
- riesgos residuales;
- acciones pendientes;
- si requiere aprobación adicional;
- estado Git (por ejemplo: `git diff --stat`, `git diff --name-only` y `git status --short`), si aplica.

### 25.12 RESPONSIVIDAD_CONVERSACIONAL_POR_UMBRAL

**Principio:** autonomía no significa asumir en silencio. El sistema debe **avanzar** dentro del alcance autorizado cuando la tarea sea clara, y **preguntar** cuando una decisión pueda afectar efectividad/eficacia/eficiencia, riesgo, seguridad, costo, alcance o calidad del resultado.

**Puede avanzar sin preguntar** (si está dentro del alcance autorizado):
- validaciones y checks;
- cambios documentales/técnicos de bajo riesgo con criterios claros;
- uso de herramientas compact-first;
- auditorías dry-run;
- reportes compactos;
- commit/push **solo** si fueron autorizados y las validaciones pasan.

**Debe preguntar** si:
- objetivo o alcance son ambiguos/insuficientes;
- hay múltiples rutas razonables con tradeoffs;
- implicaría ampliar archivos a modificar;
- podría requerir Premium/Replit o tocar secrets/deployment/migraciones;
- hay acciones destructivas o que afecten evidencia;
- se propone `--all` masivo u operación con crecimiento/riesgo;
- se cambia una política canónica;
- se pasa de diagnóstico a modificación de código funcional.

**Cómo preguntar:** en lenguaje natural, con duda concreta + opciones + implicaciones + recomendación + qué hará si el usuario autoriza.

**Qué no hacer:** no pedir aprobación por microacciones dentro de Build; no detenerse por decisiones triviales; no ejecutar silenciosamente cambios que alteren riesgo o alcance.

---

Referencias:

- `AGENT_ORCHESTRATION.md` (arquitectura y agentes)
- `MODEL_ROUTING.md` (routing y escalamiento)
- `CONTINUE_USAGE_PROTOCOL.md` (uso de Continue en VS Code)

Nota (runbook): los comandos de los anexos asumen ejecución desde `C:\Agente`. Para operación compact-first y consulta por estado/rutas, ver `mcp_server/README.md`.

<!-- START: DIAGNOSTIC_FLOW_OPERATION_V0_1 -->

---

## Anexo operativo v0.1 — Flujo diagnóstico semiautomático

El flujo diagnóstico semiautomático implementa la primera capa operativa del protocolo de automatización entre agentes.

Su función es validar que el orquestador puede ejecutar una secuencia mínima de coordinación sin intervención manual paso a paso.

### Comando oficial

Ejecutar en PowerShell (desde `C:\Agente`):

    python .\scripts\run_diagnostic_flow.py

### Secuencia ejecutada

El script `scripts/run_diagnostic_flow.py` ejecuta:

1. `scripts/orchestrator_preflight.py`
2. `scripts/select_agent_model.py`
3. `scripts/build_handoff_package.py`
4. `scripts/record_agent_result.py`
5. `scripts/show_latest_run.py`

### Responsabilidad de cada script

#### orchestrator_preflight.py

Verifica fuentes transversales obligatorias y extrae automáticamente:

- fuentes de contexto;
- alertas globales;
- lecciones globales;
- estado del preflight;
- fuentes faltantes.

#### select_agent_model.py

Realiza una recomendación diagnóstica de agente/modelo según:

- escenario;
- riesgo;
- volumen;
- solicitud premium, si existiera.

Para el escenario `context-validation`, la recomendación esperada es:

    agent: context-validator
    model: opencode-go/qwen3.6-plus
    line: Go

#### build_handoff_package.py

Crea un paquete de handoff en:

    docs/agent_queue/inbox/

El paquete debe incorporar automáticamente:

- `context_sources`;
- `alerts_checked`;
- `lessons_checked`;
- `preflight_status`;
- `missing_files`.

#### record_agent_result.py

Registra el resultado del agente o del flujo en:

    docs/agent_runs/<run-id>/agent_outputs/
    docs/agent_runs/<run-id>/TRACE.md
    docs/agent_runs/<run-id>/RUN_SUMMARY.md

#### show_latest_run.py

Muestra al usuario el último flujo registrado, incluyendo:

- run_id;
- objetivo;
- contexto consultado;
- alertas consultadas;
- lecciones consultadas;
- resumen del run;
- traza del run;
- rutas relevantes.

### Criterio de éxito

El flujo se considera exitoso cuando devuelve:

    status: ok
    preflight_status: ok
    context_sources_count > 0
    alerts_checked_count > 0
    lessons_checked_count > 0
    recommended_agent definido
    recommended_model definido
    RUN_SUMMARY.md generado
    TRACE.md generado

### Resultado validado

La primera ejecución validada produjo:

    run_id: 20260506_111238_8e48193b
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

### Transparencia para el usuario

El flujo debe permitir que el usuario revise el proceso sin abrir manualmente cada JSON o Markdown.

Consulta compact-first (recomendado desde Continue vía MCP):

- `run_health_check` (salud rápida)
- `check_opencode_run_status` (seguimiento OpenCode)
- `get_run_status` (diagnóstico ampliado)

Fallback (terminal, detalle excepcional / *preview-only*):

    python .\scripts\show_latest_run.py

### Estado de automatización

Este flujo representa automatización semiautomática.

Ya automatiza:

- preflight;
- selección diagnóstica de agente/modelo;
- creación de paquete;
- registro de resultado;
- resumen visible;
- traza visible.

Todavía no automatiza:

- invocación real de Continue;
- invocación real de OpenCode;
- transferencia MCP;
- selección de modelo dentro de OpenCode;
- ejecución de agentes reales;
- autorización humana integrada;
- escalamiento real a Zen, premium o Replit.

### Próxima evolución

La siguiente evolución debe ser una de estas dos rutas:

1. Integrar el flujo semiautomático como herramienta MCP para Continue.
2. Validar invocación controlada de OpenCode desde archivo/CLI si la instalación local lo permite.

Hasta que exista esa integración, el flujo semiautomático debe considerarse una base operativa de trazabilidad y no una orquestación completamente autónoma.

<!-- END: DIAGNOSTIC_FLOW_OPERATION_V0_1 -->

<!-- START: OPENCODE_REAL_INTEGRATION_OPERATION_V0_1 -->

---

## Anexo operativo v0.2 — Integración real controlada con OpenCode

La integración real controlada con OpenCode extiende el flujo diagnóstico semiautomático y permite invocar OpenCode desde un paquete de handoff previamente generado.

Esta fase confirma que OpenCode puede participar en la orquestación real sin que el usuario copie manualmente el handoff en el chat de OpenCode.

### Comando oficial

Ejecutar en PowerShell (desde `C:\Agente`):

    python .\scripts\run_opencode_from_handoff.py --run-id <run-id>

Ejemplo validado:

    python .\scripts\run_opencode_from_handoff.py --run-id 20260506_111238_8e48193b

### Dependencia operativa en Windows

En Windows debe usarse:

    opencode.cmd

No debe usarse directamente:

    opencode

Motivo: PowerShell puede bloquear el shim `opencode.ps1` por política de ejecución de scripts. `opencode.cmd` evita ese bloqueo.

### Capacidades confirmadas de OpenCode CLI

La instalación local confirmó soporte para:

- `opencode.cmd --help`
- `opencode.cmd models`
- `opencode.cmd run`
- `--agent`
- `--model`
- `--file`
- `--format json`

También se confirmó que OpenCode devuelve eventos JSONL con tipos como:

- `step_start`
- `text`
- `step_finish`

Esto permite capturar y procesar la salida de forma programática.

### Script operativo

El script responsable es:

    scripts/run_opencode_from_handoff.py

### Funciones del script

El script:

1. Localiza el handoff Markdown por `--run-id` o toma el más reciente.
2. Lee el paquete JSON asociado.
3. Determina `run_id`.
4. Determina agente objetivo.
5. Determina modelo.
6. Invoca `opencode.cmd run`.
7. Adjunta el archivo de handoff con `--file`.
8. Usa `--format json`.
9. Captura stdout/stderr.
10. Procesa la salida JSONL.
11. Extrae eventos tipo `text`.
12. Captura `session_id`.
13. Captura tokens y costo si OpenCode los devuelve.
14. Registra salida procesada en `agent_outputs/`.
15. Registra salida cruda en `raw_outputs/`.
16. Actualiza `TRACE.md`.
17. Actualiza `RUN_SUMMARY.md`.
18. Ejecuta `show_latest_run.py` para mostrar trazabilidad visible.

### Carpetas usadas

Salida procesada:

    docs/agent_runs/<run-id>/agent_outputs/

Salida cruda:

    docs/agent_runs/<run-id>/raw_outputs/

Bitácora:

    docs/agent_runs/<run-id>/TRACE.md

Resumen visible:

    docs/agent_runs/<run-id>/RUN_SUMMARY.md

### Prompt base del script

El prompt base indica a OpenCode:

    Lee el archivo de handoff adjunto. Actúa en modo diagnóstico.
    No modifiques archivos. No ejecutes comandos.
    Responde con un JSON corto con estas claves:
    status, agent, model, file_read, summary, next_action.

### Criterio de éxito

La integración se considera exitosa cuando:

- OpenCode responde por CLI;
- OpenCode lee el archivo adjunto;
- la respuesta queda registrada en `agent_outputs/`;
- la salida cruda queda registrada en `raw_outputs/`;
- `TRACE.md` se actualiza;
- `RUN_SUMMARY.md` se actualiza;
- `show_latest_run.py` muestra el resultado;
- Git queda controlado después de versionar los archivos relevantes.

### Resultado validado

La primera ejecución real validada produjo:

    run_id: 20260506_111238_8e48193b
    agent: context-validator
    model: opencode-go/qwen3.6-plus
    status: diagnostic
    handoff_path: docs/agent_queue/inbox/20260506_111238_8e48193b.md
    OpenCode session: capturada
    events_count: capturado
    tokens: capturados
    cost: capturado
    output procesado: agent_outputs/
    output crudo: raw_outputs/

### Restricciones

Esta integración no debe entenderse como autorización general de ejecución.

Debe seguir operando bajo estas restricciones:

- modo diagnóstico por defecto;
- no modificar archivos salvo autorización explícita;
- no ejecutar comandos de proyecto salvo autorización explícita;
- no acceder a secrets;
- no hacer deployment;
- no hacer migraciones;
- no aplicar cambios destructivos;
- no escalar a premium sin autorización;
- no ocultar costo, tokens, sesión o salida del agente.

### Transparencia

El resultado de OpenCode debe ser visible para el usuario con consulta compact-first (recomendado desde Continue vía MCP):

- `run_health_check`
- `check_opencode_run_status`
- `get_run_status`

Fallback (terminal, detalle excepcional / *preview-only*):

    python .\scripts\show_latest_run.py

El usuario debe poder ver:

- qué handoff se usó;
- qué agente intervino;
- qué modelo se usó;
- qué respondió OpenCode;
- qué costo/tokens reportó OpenCode, si están disponibles;
- qué quedó en `TRACE.md`;
- qué quedó en `RUN_SUMMARY.md`;
- dónde está la salida cruda.

### Relación con la automatización futura

Esta integración es un paso intermedio entre la cola semiautomática y una orquestación más avanzada.

Ya permite:

    paquete de handoff
    → OpenCode real
    → captura estructurada
    → bitácora visible

Todavía falta:

- MCP local para Continue;
- invocación automática de Continue;
- transferencia bidireccional completa Continue ↔ OpenCode;
- autorización humana integrada;
- routing automático completo según `MODEL_ROUTING.md`;
- soporte para proyectos objetivo habilitados;
- ejecución controlada de cambios reales.

### Regla superior

La integración con OpenCode debe aumentar automatización sin reducir transparencia, trazabilidad ni control humano.

<!-- END: OPENCODE_REAL_INTEGRATION_OPERATION_V0_1 -->

<!-- START: UNIFIED_DIAGNOSTIC_WITH_OPENCODE_OPERATION_V0_1 -->

---

## Anexo operativo v0.3 — Comando unificado con OpenCode integrado

El comando unificado con OpenCode integrado permite ejecutar una mini-orquestación diagnóstica real de punta a punta.

### Comando oficial

Ejecutar en PowerShell (desde `C:\Agente`):

    python .\scripts\run_diagnostic_flow.py --with-opencode

### Script principal

    scripts/run_diagnostic_flow.py

### Flag operativo

    --with-opencode

Cuando se usa este flag, el flujo invoca:

    scripts/run_opencode_from_handoff.py

### Secuencia completa

El comando ejecuta:

1. `orchestrator_preflight.py`
2. `select_agent_model.py`
3. `build_handoff_package.py`
4. `record_agent_result.py`
5. `run_opencode_from_handoff.py`
6. `show_latest_run.py`

### Diferencia frente al modo base

Modo base:

    python .\scripts\run_diagnostic_flow.py

- No invoca OpenCode real.
- Valida preflight, routing, handoff, bitácora y visualización.
- Es diagnóstico semiautomático.

Modo con OpenCode:

    python .\scripts\run_diagnostic_flow.py --with-opencode

- Invoca OpenCode real.
- Lee el handoff generado.
- Captura respuesta JSONL.
- Registra salida procesada y cruda.
- Actualiza bitácora y resumen.
- Mantiene restricciones de diagnóstico.

### Resultado validado

La ejecución validada produjo:

    run_id: 20260506_120851_e8c884cf
    project_id: orchestrator
    scenario: context-validation
    risk: medium
    volume: high
    agent: context-validator
    model: opencode-go/qwen3.6-plus
    status: diagnostic
    handoff: docs/agent_queue/inbox/20260506_120851_e8c884cf.md

### Archivos generados

El flujo puede generar:

    docs/agent_queue/inbox/<run-id>.json
    docs/agent_queue/inbox/<run-id>.md
    docs/agent_runs/<run-id>/RUN_SUMMARY.md
    docs/agent_runs/<run-id>/TRACE.md
    docs/agent_runs/<run-id>/agent_outputs/*_opencode.json
    docs/agent_runs/<run-id>/raw_outputs/*_opencode_raw.json

### Validación de éxito

Un flujo exitoso debe demostrar:

- `preflight_status: ok`;
- fuentes de contexto cargadas;
- alertas globales cargadas;
- lecciones globales cargadas;
- agente recomendado;
- modelo recomendado;
- OpenCode invocado;
- respuesta capturada;
- salida procesada registrada;
- salida cruda registrada;
- `TRACE.md` actualizado;
- `RUN_SUMMARY.md` actualizado;
- visualización disponible con `show_latest_run.py`.

### Seguridad

El flujo integrado no es autorización general de ejecución.

OpenCode debe operar con prompt diagnóstico, sin edición ni ejecución de comandos, salvo instrucción explícita posterior.

Cualquier transición hacia ejecución real debe requerir:

- proyecto objetivo confirmado;
- contexto suficiente;
- alertas consultadas;
- autorización humana si aplica;
- plan de cambios;
- control de Git;
- validación de diffs;
- pruebas.

### Problema corregido

Durante la validación se detectó un error de encoding en Windows/Python al imprimir caracteres reemplazados. Se corrigió mediante:

- `PYTHONUTF8=1`;
- `PYTHONIOENCODING=utf-8`;
- `sys.stdout.reconfigure(... errors="replace")`;
- `safe_print(...)`.

Esta corrección debe conservarse para evitar fallos de consola en Windows.

### Relación con automatización futura

Este comando ya conecta la cola semiautomática con OpenCode real.

El siguiente paso arquitectónico es exponer este flujo como herramienta MCP para que Continue pueda invocarlo desde un único chat.

<!-- END: UNIFIED_DIAGNOSTIC_WITH_OPENCODE_OPERATION_V0_1 -->

<!-- START: ASYNC_OPENCODE_OPERATION_V0_1 -->

---

## Anexo operativo v0.4 — Ejecución asíncrona de OpenCode vía MCP

La ejecución asíncrona de OpenCode vía MCP resuelve el problema de llamadas bloqueantes desde Continue.

### Problema identificado

El flujo:

    Continue -> MCP -> run_diagnostic_flow with_opencode=true

puede fallar o quedar incompleto porque la invocación real de OpenCode:

- puede tardar más que una llamada MCP cómoda para el cliente;
- puede generar salida JSONL extensa;
- puede bloquear la experiencia del chat;
- puede exceder límites de tiempo o tolerancia del cliente;
- puede impedir que Continue reciba respuesta limpia.

### Solución definida

Separar la orquestación en tres pasos:

    Continue -> MCP -> run_diagnostic_flow with_opencode=false
    Continue -> MCP -> start_opencode_from_handoff_async
    Continue -> MCP -> show_latest_run

### Herramienta asíncrona

La herramienta agregada es:

    start_opencode_from_handoff_async

Script asociado:

    scripts/start_opencode_from_handoff_async.py

### Función de la herramienta

La herramienta:

1. Recibe un `run_id` existente.
2. Valida que exista `docs/agent_runs/<run-id>/`.
3. Lanza en segundo plano:

       python scripts/run_opencode_from_handoff.py --run-id <run-id>

4. Devuelve inmediatamente:

       status: started
       run_id
       pid
       agent
       model
       stdout_path
       stderr_path
       meta_path
       next_action

5. Registra logs en:

       docs/agent_runs/<run-id>/background/

6. Permite consultar luego el resultado con:

       show_latest_run

### Carpetas usadas

La ejecución asíncrona puede generar:

    docs/agent_runs/<run-id>/background/
    docs/agent_runs/<run-id>/agent_outputs/
    docs/agent_runs/<run-id>/raw_outputs/
    docs/agent_runs/<run-id>/TRACE.md
    docs/agent_runs/<run-id>/RUN_SUMMARY.md

### Resultado validado

La prueba validada produjo:

    run_id: 20260506_171549_0e258229
    agent: context-validator
    model: opencode-go/qwen3.6-plus
    status: diagnostic
    background: generado
    agent_outputs: generado
    raw_outputs: generado
    TRACE.md: actualizado
    RUN_SUMMARY.md: actualizado

### Regla operativa para Continue

Desde Continue, no usar como ruta principal:

    run_diagnostic_flow with_opencode=true

Usar como ruta principal:

    run_diagnostic_flow with_opencode=false
    -> start_opencode_from_handoff_async
    -> show_latest_run

### Regla de transparencia

La ejecución asíncrona no debe ocultar el proceso.

El usuario debe poder ver:

- el `run_id`;
- el `pid`;
- la ruta de logs de background;
- el agente usado;
- el modelo usado;
- la salida procesada;
- la salida cruda;
- el resumen del run;
- la traza del run.

### Restricciones

La ejecución asíncrona conserva las mismas restricciones:

- modo diagnóstico por defecto;
- no editar archivos funcionales salvo autorización;
- no ejecutar comandos arbitrarios;
- no acceder a secrets;
- no hacer deployment;
- no hacer migraciones;
- no escalar a premium sin autorización;
- no ocultar errores de OpenCode.

### Criterio de éxito

El patrón async se considera exitoso cuando:

- `start_opencode_from_handoff_async` devuelve `status: started`;
- se crea metadata en `background/`;
- OpenCode registra salida en `agent_outputs/`;
- la salida cruda queda en `raw_outputs/`;
- `TRACE.md` incluye intervención de `context-validator`;
- `RUN_SUMMARY.md` muestra más de una salida de agente;
- `show_latest_run` permite visualizar el resultado.

<!-- END: ASYNC_OPENCODE_OPERATION_V0_1 -->

