# AGENTS.md

Bootstrap mínimo para agentes en este repositorio orquestador.

Este archivo no redefine políticas. Su función es dirigir a Codex, Continue,
OpenCode u otros agentes hacia las fuentes canónicas ya existentes antes de
actuar sobre este orquestador o sobre un proyecto objetivo.

## Fuentes canónicas iniciales

Antes de tareas de complejidad media o superior, revisar por referencia:

- `AGENT_RULES.md`
- `PROJECT_CONTEXT.md`
- `CONTINUE_USAGE_PROTOCOL.md`
- `DEVELOPMENT_CHECKS.md`
- `MODEL_ROUTING.md`
- `SECURITY_POLICY.md`
- `PROJECT_REGISTRY.md`
- `TARGET_PROJECT_CONTEXT_CONTRACT.md`
- `docs/protocols/SEMANTIC_CONTEXT_GATE_PROTOCOL.md`

Si la tarea tiene proyecto objetivo confirmado, revisar también:

- `docs/projects/<project_id>/PROJECT_PROFILE.md`
- `docs/projects/<project_id>/CONTEXT_INDEX.md`
- `docs/projects/<project_id>/CODE_CONTEXT_MAP.md`
- `docs/projects/<project_id>/CRITICAL_ALERTS.md`
- `docs/projects/<project_id>/SYNC_STATUS.md`
- `docs/projects/<project_id>/HANDOFF_LOG.md`
- `docs/projects/<project_id>/SEMANTIC_TAG_INDEX.md`

## Secuencia operativa resumida

1. Resolver o declarar el proyecto objetivo.
2. Ejecutar lectura contextual mínima según `CONTINUE_USAGE_PROTOCOL.md`.
3. Ejecutar `semantic_context_gate` antes de editar, diagnosticar con impacto o tocar integraciones/rutas/datos/secrets/runtime.
4. Actuar solo dentro del alcance autorizado.
5. Validar según `DEVELOPMENT_CHECKS.md`.
6. Si cambió contexto reutilizable, actualizar:
   - `docs/projects/<project_id>/HANDOFF_LOG.md`
   - `docs/projects/<project_id>/SYNC_STATUS.md`
   - `docs/projects/<project_id>/SEMANTIC_TAG_INDEX.md` mediante `scripts/project_context_indexer.py --apply`, solo si aplica.
7. Reportar fuentes revisadas, validaciones, diff/commit/push y pendientes.

No pegar secrets, `.env`, dumps, logs voluminosos ni PII en prompts, handoffs o documentación.
