# PROJECT_REGISTRY.md

## Propósito

Registro maestro de proyectos objetivo habilitados en el orquestador local.

## Estado

Pendiente de poblar mediante el protocolo `ENABLE_TARGET_PROJECT`.

## Campos mínimos por proyecto

- project_id:
- nombre_canónico:
- alias_permitidos:
- ruta_local:
- repositorio_remoto:
- origen: local | replit | github | nuevo | importado
- stack_detectado:
- documentación_principal:
- código_fuente_relevante:
- estado_sincronización:
- alertas_críticas:
- lecciones_locales:
- último_análisis:
- responsable:

## Proyectos registrados

<!--
Nota de parsing (scripts/apply_to_project.py):
- Cada proyecto es un bloque de líneas 'key: value' separado por una línea en blanco.
- alias_permitidos debe ser lista en una sola línea separada por comas.
- Evitar valores multi-línea.
-->

### data-privacy-management-d

project_id: data-privacy-management-d
nombre_canónico: DataPrivacyManagement(D) Workspace
alias_permitidos: dpm, data-privacy-management, dataprivacymanagement-d, dpm-replit
ruta_local:
repositorio_remoto: https://github.com/lfangaritac/DataPrivacyManagement
origen: replit
environment_type: replit-git
repo_url: https://github.com/lfangaritac/DataPrivacyManagement
replit_workspace_path: /home/runner/workspace
local_path: null
stack_detectado: unknown
documentación_principal:
código_fuente_relevante:
estado_sincronización: test_active
alertas_críticas:
lecciones_locales:
último_análisis:
responsable: unknown

### embajadores-backend

project_id: embajadores-backend
nombre_canónico: Embajadores Backend
alias_permitidos: embajadores, embajadores-backend
ruta_local: C:\Users\murfe\source\repos\embajadores-backend
repositorio_remoto: https://github.com/lfangaritac/embajadores-backend.git
origen: github
environment_type: github
repo_url: https://github.com/lfangaritac/embajadores-backend.git
replit_workspace_path: 
replit_join_url: 
local_path: C:\Users\murfe\source\repos\embajadores-backend
stack_detectado: Python 3.11 Flask/Gunicorn + React/Vite admin portal + MySQL/Azure/Replit integrations
documentación_principal: README.md, replit.md, docs/TECHNICAL_DOCUMENTATION.md, frontend/src/app/api/APIContract.md
código_fuente_relevante: main.py, app.py, db.py, env_loader.py, whatsapp_webhook.py, voiceflow_client.py, routes/, services/, frontend/
estado_sincronización: synced_to_88291e9_post_replit_dual_whatsapp_senders
alertas_críticas: docs/projects/embajadores-backend/CRITICAL_ALERTS.md
lecciones_locales: docs/projects/embajadores-backend/LESSONS_LOCAL.md
último_análisis: 2026-06-02
responsable: unknown

### riskmanager-compliance

project_id: riskmanager-compliance
nombre_canónico: RiskManager Compliance
alias_permitidos: riskmanager, riskmanager-compliance, risk-manager-compliance, riskmanagercompliance
ruta_local: C:\Users\murfe\source\repos\Riskmanagercompliance
repositorio_remoto: https://github.com/lfangaritac/Riskmanagercompliance.git
origen: github
environment_type: github
repo_url: https://github.com/lfangaritac/Riskmanagercompliance.git
replit_workspace_path:
replit_join_url:
local_path: C:\Users\murfe\source\repos\Riskmanagercompliance
stack_detectado: pnpm workspace; Node.js 24; TypeScript 5.9; React 18 + Vite + Tailwind v4 + shadcn/ui; Express 5 API; PostgreSQL + Drizzle ORM; OpenAPI/Orval/Zod
documentación_principal: replit.md, package.json, pnpm-workspace.yaml, lib/api-spec/openapi.yaml
código_fuente_relevante: artifacts/grc/src/app/, artifacts/api-server/src/routes/, lib/db/src/schema/, lib/api-spec/openapi.yaml, lib/api-client-react/, lib/api-zod/
estado_sincronización: cloned_clean_main_b8220e7
alertas_críticas: docs/projects/riskmanager-compliance/CRITICAL_ALERTS.md
lecciones_locales: docs/projects/riskmanager-compliance/LESSONS_LOCAL.md
último_análisis: 2026-05-29
responsable: unknown

### analisis-impacto-privacidad

project_id: analisis-impacto-privacidad
nombre_canónico: Plataforma AIP - Analisis de Impacto en Privacidad
alias_permitidos: aip, analisis-impacto-privacidad, analisis_impacto_privacidad, privacidad-aip, privacy-impact-assessment
ruta_local: C:\Users\murfe\source\repos\Analisis_impacto_privacidad
repositorio_remoto: https://github.com/lfangaritac/Analisis_impacto_privacidad.git
origen: github
environment_type: github
repo_url: https://github.com/lfangaritac/Analisis_impacto_privacidad.git
replit_workspace_path:
replit_join_url:
local_path: C:\Users\murfe\source\repos\Analisis_impacto_privacidad
stack_detectado: React 18 + Vite 7 + Express 5 + TypeScript 5.6 + PostgreSQL + Drizzle ORM + OpenAI integrations
documentación_principal: replit.md, docs/DOCUMENTACION_TECNICA.md, docs/test_reports/baseline_validacion_local_aip_20260504.md, docs/test_reports/opencode_diagnostico_typescript_aip_20260504.md, package.json, drizzle.config.ts
código_fuente_relevante: client/src/App.tsx, client/src/components/, client/src/index.css, server/index.ts, server/routes.ts, server/storage.ts, server/ai.ts, server/db.ts, server/docx-generator.ts, shared/schema.ts
estado_sincronización: cloned_clean_main_9c5ed18
alertas_críticas: docs/projects/analisis-impacto-privacidad/CRITICAL_ALERTS.md
lecciones_locales: docs/projects/analisis-impacto-privacidad/LESSONS_LOCAL.md
último_análisis: 2026-06-13
responsable: unknown
