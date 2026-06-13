# SEMANTIC_TAG_INDEX - analisis-impacto-privacidad

Indice semantico compacto por referencias.

## privacy.aip.lifecycle

- criticality: critico antes de Build
- status: vigente
- signals: AIP, ciclo de vida, datos personales, recoleccion, almacenamiento, relacionamiento, procesamiento, disposicion, tarjetas, No Aplica
- sources:
  - `replit.md`
  - `docs/DOCUMENTACION_TECNICA.md`
  - `client/src/App.tsx`
  - `client/src/components/section-view.tsx`

## privacy.aip.risks

- criticality: critico antes de Build
- status: vigente
- signals: riesgos, titular, organizacion, riesgo inherente, residual teorico, residual practico, concepto de riesgo, catalogo corporativo
- sources:
  - `replit.md`
  - `docs/DOCUMENTACION_TECNICA.md`
  - `client/src/components/risks-view.tsx`
  - `client/src/data/catalogo-corporativo.ts`
  - `server/ai.ts`

## privacy.aip.documents

- criticality: recomendado para Plan, critico antes de Build si cambia generacion documental
- status: vigente
- signals: autorizaciones, acuerdos, transferencia, transmision, informes, DOCX, HTML, PDF, Word
- sources:
  - `client/src/components/report-builder-view.tsx`
  - `client/src/components/authorizations-view-optimized.tsx`
  - `client/src/components/agreements-view.tsx`
  - `server/docx-generator.ts`
  - `server/html-generator.ts`

## ai.openai.assistant

- criticality: critico antes de Build
- status: vigente
- signals: OpenAI, assistant, vector store, file_search, OPENAI_ASSISTANT_ID, OPENAI_VECTOR_STORE_IDS, AI_INTEGRATIONS_OPENAI_API_KEY
- sources:
  - `server/ai.ts`
  - `server/setup-assistant.ts`
  - `server/update-assistant-vs.ts`
  - `SECRETS_MANIFEST.md`
  - `docs/SECRETS_SETUP.md`

## db.postgres.drizzle

- criticality: critico antes de Build
- status: vigente
- signals: DATABASE_URL, PostgreSQL, Drizzle, db:push, schema, migracion, iniciativas, archivos, users
- sources:
  - `drizzle.config.ts`
  - `server/db.ts`
  - `shared/schema.ts`
  - `package.json`
  - `scripts/post-merge.sh`
  - `.env.example`

## runtime.secrets

- criticality: critico antes de Build
- status: vigente
- signals: secrets, env, .env, DATABASE_URL, OPENAI_API_KEY, Replit Secrets, start-dev, check_env, PORT, NODE_ENV
- sources:
  - `.env.example`
  - `.env.replit.example`
  - `SECRETS_MANIFEST.md`
  - `docs/SECRETS_SETUP.md`
  - `scripts/check_env.py`
  - `scripts/start-dev.ps1`
  - `.gitignore`

## frontend.tailwind.precompiled

- criticality: recomendado para Plan, critico antes de Build visual
- status: vigente segun documentacion
- signals: Tailwind, CSS, index.css, utilidades, estilos, responsive, UI
- sources:
  - `docs/DOCUMENTACION_TECNICA.md`
  - `client/src/index.css`
  - `tailwind.config.ts`
  - `postcss.config.js`

## typescript.debt

- criticality: critico antes de Build
- status: requiere revision actual antes de corregir
- signals: npm run check, TypeScript, TS2802, errores de tipos, section-view, App, interfaces, casts
- sources:
  - `docs/test_reports/baseline_validacion_local_aip_20260504.md`
  - `docs/test_reports/opencode_diagnostico_typescript_aip_20260504.md`
  - `tsconfig.json`
  - `client/src/App.tsx`
  - `client/src/components/section-view.tsx`
