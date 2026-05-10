# ACTION_INDEX.md

## Propósito
Índice liviano de **acciones relevantes** para operar por referencias (no por volcado de contenido).

Sirve para:
- reconstruir estado con metadatos + rutas + `run_id`;
- armar *context packs* mínimos por tarea;
- evitar que `docs/agent_runs/**`, `docs/agent_queue/**`, `TRACE/RUN_SUMMARY/raw_outputs` entren al contexto normal.

## Reglas de mantenimiento
- Registrar **metadatos y referencias**, no contenido.
- No pegar `TRACE.md`, `RUN_SUMMARY.md`, handoffs ni `raw_outputs`.
- Si se necesita detalle: consultar por fragmentos (Nivel 2/3 del protocolo).

## Acciones (resumen)

| action_id | date | type | objective | status | owner | mode | refs (paths/run_id) | notes |
|---|---|---|---|---|---|---|---|---|
| ACT-0001 | 2026-05 | policy | Plan/Build + umbrales de autorización | done | docs | Plan | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25` | Build por alcance; premium/Replit/secrets requieren aprobación |
| ACT-0002 | 2026-05 | mcp_tooling | `verify_master_files` como anclaje físico | done | MCP | Plan | `mcp_server/README.md` | Verificación física supera visibilidad del IDE |
| ACT-0003 | 2026-05 | mcp_tooling | `create_and_dispatch_opencode_handoff` evita transporte manual | done | MCP | Build | `mcp_server/README.md` | Handoffs se referencian por run_id + rutas |
| ACT-0004 | 2026-05 | policy | Compact-first: preferir `run_health_check`/`check_opencode_run_status`/`get_run_status` | done | docs | Plan | `mcp_server/README.md` | Evitar `show_latest_run` en chat salvo necesidad (fallback/preview-only) |
| ACT-0005 | 2026-05 | policy | `CONTEXT_BUDGET_AND_MINIMAL_MODE_POLICY` | done | Continue | Plan | `CONTINUE_USAGE_PROTOCOL.md` | run_id+rutas+conteos; no pegar artefactos grandes |
| ACT-0006 | 2026-05 | policy | `.continueignore` best-effort para exclusiones | done | Continue | Build | `.continueignore` | Soporte no confirmado; política es fallback |
| ACT-0007 | 2026-05 | policy | Reducir Always Applied a mínimo v0.5 | done | Continue | Build | `.continue/rules/context-contract-governance.md` | Reglas permanentes deben ser cortas |
| ACT-0008 | 2026-05 | policy | Protocolo de contexto referencial + índices livianos | done | Continue | Build | `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md` | Contexto persistente ≠ contexto cargado |
| ACT-0009 | 2026-05-09 | ops | Baseline E2E orquestación automática validado + control de artefactos | done | orchestrator | Build | run_id `20260509_103815_2841ce6d`; `.gitignore`; `.continueignore`; `docs/context/RUN_INDEX.md` | No versionar runs/handoffs/raw_outputs/logs; trazabilidad liviana por índices |
| ACT-0010 | 2026-05-09 | ops_tooling | Retención no destructiva: archive-only de runs/handoffs (zip) | done | scripts | Build | `scripts/audit_agent_artifacts.py`; `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#15.1` | No borra ni mueve originales; evidencia archivada no es contexto base |
| ACT-0011 | 2026-05-09 | ops_policy | Destino oficial de archives fuera del repo: `C:\Agente_Archives` | done | orchestrator | Build | `scripts/audit_agent_artifacts.py`; `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#15.1` | Evita zips untracked dentro del repo; separación código/docs vs evidencia local |
| ACT-0012 | 2026-05-09 | ops_tooling | Archive manifest + SHA256 para evidencia archivada | done | scripts | Build | `scripts/audit_agent_artifacts.py`; `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#15.1` | `*.manifest.json` con rutas/metadatos + hash del zip; no incluye contenido |
| ACT-0013 | 2026-05-09 | policy | Formalizar responsividad conversacional por umbral | done | docs | Build | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md#25.12`; `CONTINUE_USAGE_PROTOCOL.md`; `.continue/rules/context-contract-governance.md` | Avanzar si claro; preguntar cuando el umbral afecta riesgo/alcance/costo/calidad |
| ACT-0014 | 2026-05-09 | mcp_tooling | Exponer `run_health_check` compacto como tool MCP | done | MCP | Build | `mcp_server/tools.py`; `mcp_server/schemas.py`; `scripts/audit_agent_artifacts.py` | Wrapper MCP sobre `audit_agent_artifacts.py --health` (compact-first; sin abrir artefactos completos) |
| ACT-0015 | 2026-05-09 | docs | Alinear docs operativas: `run_health_check` como diagnóstico inicial de salud de runs | done | docs | Build | `mcp_server/README.md`; `docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md`; `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md`; `CONTINUE_USAGE_PROTOCOL.md`; `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`; `QUICK_START.md` | `check_opencode_run_status`=OpenCode; `get_run_status`=ampliado; `show_latest_run`=fallback/preview-only |
| ACT-0016 | 2026-05-09 | opencode_integration | Habilitar Build low-risk real: auto-aprobación explícita de permisos OpenCode + guardrails | done | orchestrator | Build | `scripts/run_opencode_from_handoff.py`; `scripts/create_and_dispatch_opencode_handoff.py`; MCP tool `create_and_dispatch_opencode_handoff` | Permitir edición real en modo no interactivo SOLO con `auto_approve_permissions=true` + `build_authorized=true` + `risk_level=low` + `allowed_files` acotado |
| ACT-0017 | 2026-05-09 | opencode_integration | Endurecer guardrail: exigir `user_authorized_build=true` para auto-approve de permisos | done | orchestrator | Build | `scripts/run_opencode_from_handoff.py`; `scripts/create_and_dispatch_opencode_handoff.py`; `mcp_server/tools.py`; `mcp_server/schemas.py` | Defensa en profundidad: `auto_approve_permissions` requiere build_authorized+user_authorized_build+low+allowed_files+post-check diff |
| ACT-0018 | 2026-05-09 | docs | Formalizar OpenCode vía MCP como ejecutor principal de Builds (sin microaprobaciones de diffs) | done | docs | Build | `docs/protocols/AGENT_AUTOMATION_PROTOCOL.md`; `CONTINUE_USAGE_PROTOCOL.md`; `.continue/rules/continue-opencode-handoff.md`; `docs/context/DECISION_INDEX.md` | Patrón oficial: Continue orquesta/valida; OpenCode ejecuta cambios; Git verifica; preguntar solo por umbral |
| ACT-0019 | 2026-05-10 | ops_tooling | Runner local reproducible como gate antes de Builds low-risk | done | scripts | Build | `scripts/run_local_checks.py`; `QUICK_START.md`; `docs/context/DECISION_INDEX.md` | `quick`/`full` sin side-effects; MCP stdio tests solo con `--include-mcp-stdio-tests` |
