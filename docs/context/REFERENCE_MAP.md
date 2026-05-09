# REFERENCE_MAP.md

## Propósito
Mapa referencial: define qué documento es **canónico** por tema, cuáles son secundarios y qué duplicidades están pendientes.

Regla: evitar duplicidad documental y evitar cargar documentos largos si solo se necesita una regla puntual.

## Mapa (tema → fuente)

| Tema | Canónico | Referencias secundarias | Notas / pendientes |
|---|---|---|---|
| Arquitectura y roles de agentes | `AGENT_ORCHESTRATION.md` | `docs/AGENT_ORCHESTRATION.md` | `docs/AGENT_ORCHESTRATION.md` es **stub/referencia**, no fuente de verdad. |
| Guía operativa de Continue (compacta) | `CONTINUE_USAGE_PROTOCOL.md` | `.continue/rules/context-contract-governance.md`; `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md`; `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md` | Guía operativa; no duplicar políticas canónicas extensas aquí. |
| Automatización, mini-orquestación, dispatch, trazabilidad | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` | `AGENT_ORCHESTRATION.md`; `CONTINUE_USAGE_PROTOCOL.md` | Canónico para automatización. **Plan/Build + umbrales**: ver sección 25. |
| Plan/Build + aprobaciones por umbral | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` (sección 25) | `CONTINUE_USAGE_PROTOCOL.md`; `.continue/rules/context-contract-governance.md` | Umbrales: premium/Replit/secrets/deployment/migraciones/acciones destructivas. |
| Contexto referencial, niveles y context packs | `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md` | `docs/context/ACTION_INDEX.md`; `docs/context/DECISION_INDEX.md`; `docs/context/RUN_INDEX.md`; `docs/context/REFERENCE_MAP.md` | Acciones relevantes se registran como **referencias** (IDs+rutas+conteos+previews), no como contenido completo. |
| Compact-first y herramientas MCP | `mcp_server/README.md` | `docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md` | Default compact-first para runs: `run_health_check` (salud) → `check_opencode_run_status` (OpenCode) → `get_run_status` (ampliado). Evitar `show_latest_run` salvo solicitud explícita o preview-only. |
| Diagnóstico de salud de runs / run health check | `mcp_server/README.md` | `docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md`; `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md`; `scripts/audit_agent_artifacts.py` | `run_health_check` es la **primera consulta** compact-first para salud; `check_opencode_run_status` queda para OpenCode y `get_run_status` para diagnóstico ampliado. |
| Integración Continue–MCP | `docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md` | `mcp_server/README.md`; `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md`; `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md` | Protocolo de interacción Continue→MCP; el catálogo técnico de tools vive en `mcp_server/README.md`; las consultas de estado deben ser compact-first. |
| Formato de handoff Continue → OpenCode | `.continue/rules/continue-opencode-handoff.md` | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` | Este doc define el formato; los protocolos solo deben referenciarlo. |
| Reglas Always Applied (mínimas) | `.continue/rules/context-contract-governance.md` | `CONTINUE_USAGE_PROTOCOL.md` | Debe mantenerse **mínima** y referencial; no crecer con plantillas. |
| Routing modelos/agentes | `MODEL_ROUTING.md` | `AGENT_ORCHESTRATION.md`; `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` | Alinear routing con el flujo automatizado y Plan/Build. |
| Paquete canónico de escalamiento / escalation schema | `AGENT_ORCHESTRATION.md` | `MODEL_ROUTING.md`; `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md`; `.continue/rules/context-contract-governance.md` | El schema vigente usa `first_line_output.*`. `MODEL_ROUTING.md` define reglas/matrices de selección y no debe duplicar schemas extensos. |
| Evidencia, runs y trazabilidad | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` | `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`; `mcp_server/README.md`; `docs/context/RUN_INDEX.md`; `docs/context/ACTION_INDEX.md` | La trazabilidad vive como evidencia por `run_id` + rutas + conteos + artefactos; `raw_outputs/**`, `TRACE.md` y `RUN_SUMMARY.md` completos no son contexto base (consultar solo por referencia o fragmentos). |
| Retención y versionado de evidencia | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md` (sección 15.1) | `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`; `docs/context/RUN_INDEX.md`; `docs/context/ACTION_INDEX.md`; `docs/context/DECISION_INDEX.md`; `.gitignore`; `.continueignore` | Define qué runs/handoffs/logs/raw_outputs se versionan vs locales/temporales; cuándo actualizar índices; y cómo aplicar exclusiones best-effort sin cargar evidencia completa al contexto. |
