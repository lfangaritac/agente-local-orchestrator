# CODE_CONTEXT_MAP - analisis-impacto-privacidad

Mapa inicial por referencias.

## Estructura

- `client/src/`: frontend React/Vite.
- `client/src/components/`: vistas y componentes funcionales.
- `server/`: Express, API, IA, DB, generacion documental.
- `shared/`: schema/modelos compartidos Drizzle/Zod.
- `docs/`: documentacion tecnica y reportes historicos.
- `scripts/`: utilidades/checks del proyecto.
- `muestra-docs-aip/`: muestra/documentacion exportable.

## Entrypoints

- Frontend: `client/src/main.tsx`, `client/src/App.tsx`.
- Backend: `server/index.ts`.
- Rutas API: `server/routes.ts`.
- DB: `server/db.ts`, `shared/schema.ts`, `drizzle.config.ts`.
- IA: `server/ai.ts`, `server/setup-assistant.ts`, `server/update-assistant-vs.ts`.
- Docs: `server/docx-generator.ts`, `server/html-generator.ts`.

## Archivos sensibles / de alto impacto

- `drizzle.config.ts`: requiere `DATABASE_URL`; no ejecutar push sin autorizacion.
- `server/db.ts`: requiere `DATABASE_URL`.
- `server/ai.ts`: usa `OPENAI_API_KEY`, `AI_INTEGRATIONS_OPENAI_API_KEY`, `AI_INTEGRATIONS_OPENAI_BASE_URL`, `OPENAI_ASSISTANT_ID`.
- `server/setup-assistant.ts` y `server/update-assistant-vs.ts`: scripts de configuracion OpenAI/vector stores; requieren secrets.
- `script/build.ts`: build del proyecto.
- `scripts/post-merge.sh`: contiene `npm run db:push`; no ejecutar automaticamente.

## Componentes clave

- `client/src/components/section-view.tsx`: componente central grande; alto riesgo de cambios.
- `client/src/components/agent-layout.tsx`: chat IA y creacion de tarjetas.
- `client/src/components/risks-view.tsx`: flujo de riesgos AIP.
- `client/src/components/report-builder-view.tsx`: informes.
- `client/src/components/policies-view-refactored.tsx`: politicas de terceros.
- `client/src/components/authorizations-view-optimized.tsx`: autorizaciones.
- `client/src/components/agreements-view.tsx`: acuerdos.
- `client/src/components/registro-view.tsx`: gestion de casos.

