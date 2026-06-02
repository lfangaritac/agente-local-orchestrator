# CODE_CONTEXT_MAP - riskmanager-compliance

Mapa inicial de estructura, entrypoints y rutas principales.

- Estructura: monorepo pnpm con `artifacts/`, `lib/` y `scripts/`.
- Frontend GRC: `artifacts/grc/src/app/`.
- Frontend routes: `artifacts/grc/src/app/routes.ts`.
- UI base: `artifacts/grc/src/components/ui/`.
- API server: `artifacts/api-server/src/` y rutas en `artifacts/api-server/src/routes/`.
- API spec: `lib/api-spec/openapi.yaml`.
- DB schema: `lib/db/src/schema/`.
- Clientes generados/validacion: `lib/api-client-react/`, `lib/api-zod/`.
- Archivos sensibles: `.env`/`DATABASE_URL` no versionados; no ejecutar migraciones ni `db push` sin autorizacion.
