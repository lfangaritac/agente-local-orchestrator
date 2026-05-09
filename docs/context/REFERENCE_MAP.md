# REFERENCE_MAP.md

## Propósito
Mapa referencial: define qué documento es **canónico** por tema, cuáles son secundarios y qué duplicidades están pendientes.

Regla: evitar duplicidad documental y evitar cargar documentos largos si solo se necesita una regla puntual.

## Mapa (tema → fuente)

| Tema | Canónico | Referencias secundarias | Notas / pendientes |
|---|---|---|---|
| Plan/Build + autorizaciones | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` (sección 25) | `CONTINUE_USAGE_PROTOCOL.md` | Umbrales: premium/Replit/secrets/deployment/migraciones |
| Budget de contexto mínimo | `CONTINUE_USAGE_PROTOCOL.md` (CONTEXT_BUDGET_AND_MINIMAL_MODE_POLICY) | `.continue/rules/context-contract-governance.md` | Política operativa base |
| Contexto por referencias (niveles 0–4) | `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md` | `CONTINUE_USAGE_PROTOCOL.md` | Contexto persistente ≠ contexto cargado |
| MCP compact-first | `mcp_server/README.md` | `docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md` | Evitar `show_latest_run` en chat salvo necesidad |
| Routing modelos/agentes | `MODEL_ROUTING.md` | `AGENT_ORCHESTRATION.md` | Alinear con paquetes canónicos |
| Arquitectura de agentes / orquestación | `AGENT_ORCHESTRATION.md` | `docs/AGENT_ORCHESTRATION.md` | **Resuelto**: `docs/AGENT_ORCHESTRATION.md` es stub/referencia; no es fuente de verdad. |
| Reglas Always Applied (mínimas) | `.continue/rules/context-contract-governance.md` | `.continue/rules/continue-opencode-handoff.md` | Mantener reglas permanentes cortas |
