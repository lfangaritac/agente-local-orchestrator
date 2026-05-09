# RUN_INDEX.md

## Propósito
Mapa liviano de runs relevantes por `run_id`.

Regla: no copiar `TRACE.md`, `RUN_SUMMARY.md`, `raw_outputs` ni handoffs completos.

## Runs (referencias)

| run_id | objective (1 línea) | status | key_paths | notes |
|---|---|---|---|---|
| 20260506_122350_1c5cc272 | Validación MCP stdio v0.1 (run sin OpenCode) | ok (docs) | `docs/agent_queue/inbox/20260506_122350_1c5cc272.*`, `docs/agent_runs/20260506_122350_1c5cc272/` | Baseline MCP funcionando |
| 20260506_111238_8e48193b | Flujo diagnóstico base (referenciado en QUICK_START) | ok (ref) | `docs/agent_runs/20260506_111238_8e48193b/` | Evidencia de orquestación inicial |
| 20260506_120851_e8c884cf | Flujo unificado con OpenCode integrado (ref) | diagnostic (ref) | `docs/agent_runs/20260506_120851_e8c884cf/` | Genera agent_outputs/raw_outputs/TRACE/RUN_SUMMARY |
| 20260506_171549_0e258229 | Continue→MCP→OpenCode asíncrono (validado) | diagnostic (obs) | `docs/agent_runs/20260506_171549_0e258229/` | Caso clave para compact-first (timeouts) |
