# Continue Rule — Context Contract Governance (Minimal) v0.5

## Propósito

Regla **permanente** (Always Applied) y por tanto **mínima**.

Objetivo: evitar sobrecarga de contexto/tokens y aplicar el contrato multi‑proyecto sin duplicar documentación.

## 1) Identidad del sistema (no inventar proyecto objetivo)

- **Proyecto orquestador:** `C:\Agente` / `agente-local-orchestrator`.
- **Proyecto objetivo:** repo/carpeta/workspace sobre el que recae la tarea.

Reglas:
- Si el proyecto objetivo no está confirmado, declarar literalmente: `Proyecto objetivo no confirmado.`
- Si aparece un nombre posible, tratarlo como: `posible alias no confirmado`.

## 2) Fuentes mínimas obligatorias (cobertura, no volumen)

Para tareas de complejidad **media o superior** relacionadas con orquestación, modelos, Continue/OpenCode/MCP o contexto:

- Revisar (o declarar no visibles):
  - `TARGET_PROJECT_CONTEXT_CONTRACT.md`
  - `PROJECT_REGISTRY.md`
  - `AGENT_RULES.md`
  - `MODEL_ROUTING.md`
  - `AGENT_ORCHESTRATION.md` **o** `docs/AGENT_ORCHESTRATION.md`
  - `CONTINUE_USAGE_PROTOCOL.md`
  - `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`
  - `docs/lessons/GLOBAL_LESSONS_LEARNED.md`

Si alguna fuente no es visible, **no inventar** su contenido y declarar:
- visible / no visible;
- alternativa usada;
- pendiente de verificación por OpenCode/MCP;
- impacto en suficiencia contextual.

## 3) Presupuesto de contexto (modo mínimo)

Aplicar: `CONTINUE_USAGE_PROTOCOL.md` → **CONTEXT_BUDGET_AND_MINIMAL_MODE_POLICY**.

En particular:
- No cargar al chat artefactos voluminosos (`docs/agent_runs/**`, `docs/agent_queue/**`, `raw_outputs/**`, `TRACE.md`, `RUN_SUMMARY.md`, logs).
- Usar `run_id` + rutas + conteos + previews cortos.

## 4) Alertas críticas (recordatorio compacto)

- No confundir **OpenCode Go** con el lenguaje Go.
- No confundir **OpenCode Zen** con una arquitectura/red/framework.
- No escalar a premium ni a Replit sin activador/autorización.
- No solicitar ni exponer secrets.

## 5) Handoffs

No duplicar formatos aquí.

Para formato de handoff y restricciones: ver `.continue/rules/continue-opencode-handoff.md` y `CONTINUE_USAGE_PROTOCOL.md`.

