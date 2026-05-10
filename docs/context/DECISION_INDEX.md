# DECISION_INDEX.md

## Propósito
Decisiones de gobierno/contexto en formato liviano para evitar re-derivar criterios.

Regla: no duplicar políticas largas; referenciar el documento canónico.

## Decisiones vigentes (resumen)

| decision_id | date | decision | status | canonical_ref | notes |
|---|---|---|---|---|---|
| DEC-0001 | 2026-05 | OpenCode no es escalamiento; es agente técnico natural | active | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25` | Zen/premium/Replit sí son escalamiento |
| DEC-0002 | 2026-05 | Build autoriza por alcance, no micro-aprobaciones | active | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25` | Se mantienen umbrales de aprobación humana |
| DEC-0003 | 2026-05 | Usuario no debe transportar handoffs manualmente como rutina | active | `mcp_server/README.md` | Usar run_id + rutas + herramientas MCP |
| DEC-0004 | 2026-05 | Compact-first para runs (estado compacto > traza completa) | active | `mcp_server/README.md` | Preferir `run_health_check` (salud) → `check_opencode_run_status` (OpenCode) → `get_run_status` (ampliado). |
| DEC-0005 | 2026-05 | Excluir runs/handoffs/raw_outputs del contexto normal | active | `CONTINUE_USAGE_PROTOCOL.md` | Son evidencia; se recuperan bajo demanda |
| DEC-0006 | 2026-05 | Contexto persistente no equivale a contexto cargado | active | `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md` | Índices livianos + recuperación selectiva |
| DEC-0007 | 2026-05-09 | No versionar evidencia operacional (runs/handoffs/raw_outputs/logs); mantener trazabilidad por índices livianos | active | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#15.1` | Git ignora `docs/agent_runs/*` y `docs/agent_queue/inbox/*`; los IDs y rutas viven en `docs/context/RUN_INDEX.md` |
| DEC-0008 | 2026-05-09 | Responsividad conversacional por umbral (avanzar si claro; preguntar si cambia riesgo/alcance/costo/calidad) | active | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25.12` | Evita asumir silenciosamente; no requiere micro-aprobaciones dentro de Build autorizado |
| DEC-0009 | 2026-05-09 | `run_health_check` es la primera consulta compact-first para salud de runs | active | `mcp_server/README.md` | `check_opencode_run_status` queda para seguimiento OpenCode; `get_run_status` para diagnóstico ampliado; `show_latest_run` es fallback/preview-only |
| DEC-0010 | 2026-05-09 | Build autorizado ejecuta por alcance sin microaprobaciones interactivas; preguntar solo por umbral | active | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25` | Evitar depender de múltiples aceptaciones manuales de diffs en VS Code durante Build; usar validación + cierre con git diff/stat/status |
| DEC-0011 | 2026-05-09 | En Builds autorizados, el ejecutor principal de cambios es OpenCode vía MCP (Continue no aplica diffs interactivos) | active | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25` | Patrón oficial: Continue orquesta/valida; MCP despacha; OpenCode ejecuta; Git verifica |
