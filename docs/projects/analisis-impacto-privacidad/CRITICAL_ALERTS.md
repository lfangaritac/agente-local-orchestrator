# CRITICAL_ALERTS - analisis-impacto-privacidad

Alertas criticas locales del proyecto.

## Secrets / entorno

- No imprimir ni copiar valores de `DATABASE_URL`, `OPENAI_API_KEY`, `AI_INTEGRATIONS_OPENAI_API_KEY`, `AI_INTEGRATIONS_OPENAI_BASE_URL`, `OPENAI_ASSISTANT_ID` ni `OPENAI_VECTOR_STORE_IDS`.
- `server/setup-assistant.ts` puede imprimir IDs operativos de OpenAI/vector stores; tratar salidas como sensibles por contexto.

## DB / migraciones

- `package.json` expone `db:push`: `drizzle-kit push`.
- `drizzle.config.ts` requiere `DATABASE_URL`.
- No ejecutar `npm run db:push`, `drizzle-kit push`, migraciones ni scripts DB sin autorizacion explicita.
- `scripts/post-merge.sh` contiene `npm run db:push`; no ejecutarlo automaticamente.

## TypeScript

- Baseline historico: `npm run check` falla con 146 errores TS en 18 archivos.
- No corregir masivamente tipos, interfaces o casts sin plan por bloques.
- Cambios en `client/src/App.tsx` y `client/src/components/section-view.tsx` tienen alto impacto.

## CSS / Tailwind

- Tailwind esta precompilado en `client/src/index.css`.
- No asumir generacion dinamica de utilidades por `tailwind.config.ts`.

## Runtime externo

- No usar Replit, OpenAI, base de datos, deployment ni premium sin autorizacion explicita.

