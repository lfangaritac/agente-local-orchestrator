<!-- START: CONTINUE_GEMINI_CONTEXT_V0_2 -->

---

## Actualización v0.2 — Continue como copiloto contextual (nota compacta)

Esta nota no es canónica de routing ni de orquestación; su objetivo es recordar el **rol operativo** de Continue.

- Continue opera como **copiloto contextual** (lectura, síntesis, gobierno y preparación de contexto).
- Continue **no** es el ejecutor principal de cambios críticos/multiarchivo: deriva a OpenCode según `AGENT_ORCHESTRATION.md` y `MODEL_ROUTING.md`.
- Si se usan modelos externos (p. ej. Gemini), aplicar `SECURITY_POLICY.md`: **no** incluir `.env`, secrets, tokens, credenciales, PII ni dumps.
- Contexto: preferir **referencias** y “mínimo suficiente” (ver `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`).

Salida esperada (compacta): objetivo, fuentes revisadas, reglas aplicables, riesgos, siguiente paso.

<!-- END: CONTINUE_GEMINI_CONTEXT_V0_2 -->

# CONTINUE_USAGE_PROTOCOL.md

## Propósito

Guía operativa **compacta** para usar Continue en VS Code dentro del orquestador local.

Nota: si el usuario inicia trabajo desde **Codex en VS Code**, Codex asume el rol operativo equivalente a Continue para esa sesión (curación de contexto, clasificación, handoffs y reporte), respetando las mismas reglas y fuentes rectoras.


Este documento **no** es la fuente canónica de políticas extensas (Plan/Build, contexto por niveles, formatos de handoff): debe resumir lo mínimo y **referenciar** las fuentes de verdad.

## Referencias canónicas (fuentes de verdad)

- Plan/Build + aprobaciones por umbral: `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` (sección 25).
- Contexto mínimo, niveles, context pack y exclusiones: `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`.
- Regla Always Applied mínima: `.continue/rules/context-contract-governance.md`.
- Formato Continue → OpenCode (handoff): `.continue/rules/continue-opencode-handoff.md`.

---

## Rol de Continue (operativo)

Regla de superficie activa:
- Si la sesión inicia en Continue: Continue es el copiloto principal.
- Si la sesión inicia en Codex: Codex es el copiloto principal y aplica este mismo protocolo (salvo que el usuario pida explícitamente modo integrado de codificación).

Continue debe:

- leer/organizar contexto y declarar fuentes usadas;
- clasificar la tarea y proponer siguiente paso;
- preparar handoffs compactos (sin dumps);
- hacer ediciones menores **solo** cuando el riesgo sea bajo y el modo lo permita.

Continue no debe:
- ejecutar cambios críticos/multiarchivo sin plan y sin modo **Build**;
- pedir/exponer secrets o pegar `.env`/tokens/credenciales;
- escalar a premium o a Replit sin autorización explícita;
- pegar artefactos voluminosos (TRACE/RUN_SUMMARY/raw/handoffs completos) salvo autorización.

---

## Handoffs y mini-orquestación (resumen)

- **Continue/Codex:** prepara contexto, aplica gobierno (Plan/Build), supervisa y comunica.

- **OpenCode:** valida, planifica/implementa y devuelve evidencia estructurada.
- **MCP/orquestador:** registra, despacha y permite consulta compacta por `run_id`.

No duplicar aquí el formato completo de handoff.
Referencia: `.continue/rules/continue-opencode-handoff.md`.

---

## Modo operativo: Plan vs Build (resumen)

Siempre confirmar el modo con el usuario:
- **Plan:** análisis/diagnóstico/diseño/revisión/handoff. Puede ejecutar **herramientas diagnósticas** y comandos **read-only** necesarios para entender estado (p. ej. Git read-only, preflight MCP/scripts), siempre que no haya side-effects relevantes. **No** modificar archivos ni ejecutar acciones con efectos secundarios.
- **Build:** ejecutar **dentro del alcance autorizado**. No requiere microaprobaciones para acciones ordinarias dentro del alcance. Evitar flujos de edición/diff interactivos que requieran múltiples aceptaciones manuales: el camino preferido es **Continue → MCP → OpenCode → MCP** (OpenCode aplica cambios) + validación Git; consultar al usuario solo por umbral.

Autorización humana explícita requerida (siempre, incluso en Build):
- premium (por costo/criticidad), Replit/entorno externo;
- secrets (acceder/pedir/imprimir/incluir en prompts/archivos);
- deployment, migraciones, acciones destructivas;
- mover/borrar/renombrar archivos maestros;
- ampliar alcance.

Política canónica: `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` (sección 25).

---

## Operación por instrucciones generales (runbook mínimo)

### Regla general
El usuario define **objetivo**, **proyecto objetivo** (o confirma que no lo está) y la **frontera segura** deseada. El agente aplica internamente la secuencia estándar y **no exige checklists extensos** para tareas ordinarias; solo pide autorización cuando se cruza un umbral real.

### Interpretación de instrucciones generales (ejemplos)
- “**Diagnostica este proyecto**” → modo **Plan** con diagnóstico local (read-only). Si falta acceso local o se requiere entorno real, proponer escalamiento a Replit.
- “**Avanza hasta la siguiente frontera segura**” → resolver proyecto → preflight → clasificar modo/riesgo/volumen → **intentar cumplir la instrucción en su integridad**; avanzar hasta el **máximo seguro** y solo detenerse ante un umbral real (autorización/ambigüedad/riesgo/etc.). `next_frontier` se emite al cierre o al bloquearse por umbral (no como microfase).
- “**Prepara una operación low-risk**” → Plan (definir alcance/rollback/allowed_files) y, si el usuario autoriza Build, ejecutar dentro de ese alcance con validación Git.
- “**Evalúa si requiere Replit o modelo premium**” → evaluar activadores (riesgo, volumen, runtime, seguridad, solicitud del usuario, costo de equivocarse) y devolver decisión + retorno esperado.
- “**Procesa este retorno externo**” → normalizar retorno, clasificar estado y decidir `no_escalate` / `replit_needed` / `premium_needed` + `next_frontier` (ver template de returns).

### Selección, salto y retoma de proyecto (con lenguaje natural)

Objetivo: que el usuario pueda decir en Continue cosas como “cambia a dpm”, “salta a orchestrator” o “retoma el anterior” sin tener que recordar tool names.

Soporte (MCP):
- `plan_general_instruction` / `run_general_instruction_flow` intentan extraer `project_query` desde el propio texto (p. ej. "cambia a <alias>") y soportan “retoma/volver” usando sesión si existe.
- Para habilitar “retomar”, el flujo debe haber fijado una vez el proyecto activo con:
  - `set_active_project(project_id=...)`
  - y se consulta con `get_active_project()`.

Onboarding mínimo al vincular un proyecto:
- Si `plan_general_instruction` devuelve `status=onboarding_required`, ejecutar:
  - `init_project_onboarding_scaffold(project_id=..., dry_run=false)`
  - y luego reintentar el plan/dispatch.

### Secuencia estándar interna (aplicar por defecto)
1) Resolver/confirmar **proyecto objetivo** (si no está confirmado: operar en diagnóstico). Referencias: `PROJECT_REGISTRY.md`, `docs/protocols/PROJECT_ENABLEMENT_PROTOCOL.md`.
2) Ejecutar **preflight** (fuentes mínimas, alertas, lecciones) y declarar suficiencia. Referencias: `TARGET_PROJECT_CONTEXT_CONTRACT.md`, `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`, `docs/lessons/GLOBAL_LESSONS_LEARNED.md`.
3) Clasificar **modo** (Plan/Build) + **riesgo/volumen** + **alcance**.
4) Decidir **executor**: Continue (contexto), OpenCode (validación/ejecución), Replit (entorno real), premium (seguridad/arquitectura/criticidad). Referencias: `MODEL_ROUTING.md`, `AGENT_ORCHESTRATION.md`.
5) Identificar **autorizaciones requeridas** (premium/Replit/secrets/deployment/migraciones/destructivo/ampliación de alcance). Referencia: `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25`.
6) Actuar solo dentro de la frontera segura; si se cruza umbral: **detenerse y preguntar**.
7) Validar y cerrar con evidencia mínima + `next_frontier` **solo al final** (o al detectar bloqueo/umbral), sin dumps; por referencias. Referencia: `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`.

### Aclaración: Plan vs comandos diagnósticos/read-only
La política canónica de Plan/Build vive en `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25`.

- En **Plan**, se permite ejecutar herramientas diagnósticas y comandos **read-only** cuando sean necesarios para entender estado y **no tengan side-effects relevantes**.
  - Ejemplos típicos permitidos: `git status`, `git status -sb`, `git log -1`, `git remote -v`, lectura de manifiestos/config, scripts internos declarados como diagnóstico/read-only, herramientas MCP compact-first (`run_health_check`, `get_run_status`, etc.).
- En **Plan**, NO se permite: modificar archivos, installs, migraciones/DB push, build/dev/test que cambie estado, commit/push, deployment, tocar secrets, ni comandos con efectos secundarios.
- Cualquier transición a **Build** o a acciones sensibles requiere autorización humana explícita.

### Replit y modelos premium (sin sesgo)
Replit y premium **pueden usarse para cualquier tarea** si existe un activador válido, valor claro y autorización cuando aplique. No están prohibidos ni reservados a un tipo de remediación; simplemente **no son el default**. Todo uso externo/premium debe devolver retorno estructurado (ver `REPLIT_HANDOFF.md` y el schema/paquete canónico en `AGENT_ORCHESTRATION.md`).

### Autonomía y umbrales
- No pedir microaprobaciones para pasos read-only o acciones ordinarias dentro del alcance autorizado.
- Detenerse por: ambigüedad, ampliación de alcance, riesgo alto/crítico, secrets, DB/migraciones, deployment, irreversibilidad, costo premium, Replit/entorno externo.

### Anti-deriva
- Decisiones/contexto de pilotos son **locales** salvo que se eleven explícitamente como política global.
- No continuar un piloto solo por inercia cuando el objetivo de validación ya se cumplió.

---

## Responsividad conversacional por umbral (operativo)

Regla: avanzar con autonomía **cuando está claro**, preguntar **cuando cambia el umbral**.

- **Avanza sin preguntar**: validaciones, compact-first tools, auditorías dry-run, reportes compactos, cambios de bajo riesgo dentro del alcance.
- **Pregunta antes de ejecutar**: ambigüedad de objetivo/alcance, múltiples rutas con tradeoffs, ampliación de archivos a tocar, premium/Replit/secrets/deployment/migraciones/destructivo, cambios de política canónica, o pasar a modificar código funcional.
- **Forma de pregunta**: duda concreta + 2–3 opciones + implicaciones + recomendación + “si autorizas haré X”.

Fuente canónica: `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25.12`.

---

## Transparencia progresiva en chat (resumen)

En Plan o Build, reportar primero:
- objetivo; etapa; acción central; resultado parcial; riesgos/bloqueos; decisión humana requerida; próximo paso.

Detalle técnico **solo bajo demanda** y preferentemente por referencias:
- `run_id` + rutas + conteos + previews (no TRACE/RUN_SUMMARY/raw completos).

---

## Archivos de contexto a considerar (según tarea)

Antes de trabajar sobre un proyecto activado, considerar (y declarar si no se revisaron):

```text
AGENT_RULES.md
PROJECT_CONTEXT.md
MODEL_ROUTING.md
SECURITY_POLICY.md
REPLIT_HANDOFF.md
PROJECT_ACTIVATION_PROTOCOL.md
SECRETS_MANIFEST.md
QUICK_START.md
```

---

## CONTEXT_BUDGET_AND_MINIMAL_MODE_POLICY (checklist)

Objetivo: minimizar tokens y riesgo de inconsistencias usando **contexto por referencias**.

Checklist operativo:
1) **No usar Active File** para documentos largos/artefactos (handoffs, TRACE, RUN_SUMMARY, logs) salvo necesidad puntual.
2) **No pegar completos**: `raw_outputs/**`, `TRACE.md`, `RUN_SUMMARY.md`, `docs/agent_runs/**`, `docs/agent_queue/**`, handoffs `.md`, logs.
3) Usar primero **`run_id` + rutas + conteos + previews** (fragmentos mínimos).
4) **Compact-first (MCP):** preferir `run_health_check` (salud rápida); luego `check_opencode_run_status` (seguimiento OpenCode) y/o `get_run_status` (diagnóstico ampliado). Evitar `show_latest_run` salvo solicitud explícita o *preview-only*.
5) **Pedir autorización** antes de subir el nivel de contexto (lectura profunda / múltiples secciones / pegado de documentos o logs).
6) Mantener la regla Always Applied mínima vigente: `.continue/rules/context-contract-governance.md`.

Fuente canónica: `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`.

---

## Exclusiones configurables para Continue (best-effort)

Este repositorio incluye `.continueignore` para reducir contaminación de contexto.

Limitación: **no hay evidencia dentro del repo** de que la versión instalada de Continue lo lea. Si no surte efecto, mantener esta política y configurar exclusiones/ignore en la configuración real de Continue (fuera del repo), según la versión instalada.
