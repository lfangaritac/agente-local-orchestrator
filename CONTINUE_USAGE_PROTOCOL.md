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

Este documento **no** es la fuente canónica de políticas extensas (Plan/Build, contexto por niveles, formatos de handoff): debe resumir lo mínimo y **referenciar** las fuentes de verdad.

## Referencias canónicas (fuentes de verdad)

- Plan/Build + aprobaciones por umbral: `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` (sección 25).
- Contexto mínimo, niveles, context pack y exclusiones: `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`.
- Regla Always Applied mínima: `.continue/rules/context-contract-governance.md`.
- Formato Continue → OpenCode (handoff): `.continue/rules/continue-opencode-handoff.md`.

---

## Rol de Continue (operativo)

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

- **Continue:** prepara contexto, aplica gobierno (Plan/Build), supervisa y comunica.
- **OpenCode:** valida, planifica/implementa y devuelve evidencia estructurada.
- **MCP/orquestador:** registra, despacha y permite consulta compacta por `run_id`.

No duplicar aquí el formato completo de handoff.
Referencia: `.continue/rules/continue-opencode-handoff.md`.

---

## Modo operativo: Plan vs Build (resumen)

Siempre confirmar el modo con el usuario:
- **Plan:** análisis/diagnóstico/diseño/revisión/handoff. **No** modificar archivos ni ejecutar comandos.
- **Build:** ejecutar **dentro del alcance autorizado**. No requiere microaprobaciones para acciones ordinarias dentro del alcance.

Autorización humana explícita requerida (siempre, incluso en Build):
- premium (por costo/criticidad), Replit/entorno externo;
- secrets (acceder/pedir/imprimir/incluir en prompts/archivos);
- deployment, migraciones, acciones destructivas;
- mover/borrar/renombrar archivos maestros;
- ampliar alcance.

Política canónica: `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` (sección 25).

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
4) **Compact-first (MCP):** preferir `get_run_status` / `check_opencode_run_status`; evitar `show_latest_run` salvo solicitud explícita o *preview-only*.
5) **Pedir autorización** antes de subir el nivel de contexto (lectura profunda / múltiples secciones / pegado de documentos o logs).
6) Mantener la regla Always Applied mínima vigente: `.continue/rules/context-contract-governance.md`.

Fuente canónica: `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`.

---

## Exclusiones configurables para Continue (best-effort)

Este repositorio incluye `.continueignore` para reducir contaminación de contexto.

Limitación: **no hay evidencia dentro del repo** de que la versión instalada de Continue lo lea. Si no surte efecto, mantener esta política y configurar exclusiones/ignore en la configuración real de Continue (fuera del repo), según la versión instalada.
