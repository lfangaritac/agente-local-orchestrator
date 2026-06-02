# CONTEXT_INDEX - riskmanager-compliance

Indice de contexto por referencias.

## Documentacion encontrada

- `replit.md` - descripcion de producto, comandos, stack, ubicacion de modulos y gotchas.
- `package.json` - scripts raiz de workspace: `build`, `typecheck`, `typecheck:libs`.
- `pnpm-workspace.yaml` - estructura de paquetes del monorepo.
- `artifacts/grc/src/app/components/shared/README.md` - notas del componente compartido.

## Indice semantico

- Ver: `SEMANTIC_TAG_INDEX.md`

## Decisiones relevantes

- React Router v7 con `createHashRouter` para evitar problemas de base-path.
- Datos mock en `artifacts/grc/src/app/data/` hasta conectar APIs reales.
- Modulo de cumplimiento separado bajo rutas `/cumplimiento/*`.
- OpenAPI en `lib/api-spec/openapi.yaml` como fuente de contratos.

## Runs / evidencia

- 2026-05-29: vinculacion inicial y clonacion local. HEAD `b8220e7`; sin instalacion de dependencias ni ejecucion de app.
